#!/usr/bin/env python3
"""Discover local HTTP CONNECT and SOCKS5 proxy listeners."""

from concurrent.futures import ThreadPoolExecutor
import ipaddress
import re
import socket
import subprocess
import sys

_SOCKET_TIMEOUT = 0.2
_HTTP_PROXY_CODES = {200, 407, 502, 503, 504}


def _parse_listeners(output: str) -> list[tuple[str, int]]:
    listeners = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 4 or fields[0] != "LISTEN":
            continue

        local_address = fields[3]
        if local_address.startswith("["):
            host, separator, port = local_address[1:].partition("]:")
            if not separator:
                continue
        else:
            host, separator, port = local_address.rpartition(":")
            if not separator:
                continue

        if not port.isdigit():
            continue
        if host in {"*", "0.0.0.0"}:
            host = "127.0.0.1"
        elif host == "::":
            host = "::1"
        else:
            try:
                if not ipaddress.ip_address(host).is_loopback:
                    continue
            except ValueError:
                continue
        listeners.add((host, int(port)))

    return sorted(listeners, key=lambda item: (item[1], item[0]))


def _probe_socks5(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=_SOCKET_TIMEOUT) as connection:
            connection.settimeout(_SOCKET_TIMEOUT)
            connection.sendall(b"\x05\x02\x00\x02")
            response = connection.recv(2)
        return len(response) == 2 and response[0] == 5 and response[1] != 255
    except OSError:
        return False


def _probe_http_connect(host: str, port: int) -> bool:
    request = (
        b"CONNECT example.com:443 HTTP/1.1\r\n"
        b"Host: example.com:443\r\n"
        b"Proxy-Connection: Keep-Alive\r\n\r\n"
    )
    try:
        with socket.create_connection((host, port), timeout=_SOCKET_TIMEOUT) as connection:
            connection.settimeout(_SOCKET_TIMEOUT)
            connection.sendall(request)
            response = bytearray()
            while b"\r\n" not in response and len(response) < 256:
                chunk = connection.recv(256 - len(response))
                if not chunk:
                    break
                response.extend(chunk)
        match = re.match(rb"HTTP/1\.[01] (\d{3})\b", response)
        return bool(match and int(match.group(1)) in _HTTP_PROXY_CODES)
    except OSError:
        return False


def _probe_listener(listener: tuple[str, int]) -> tuple[tuple[str, int], bool, bool]:
    host, port = listener
    return listener, _probe_http_connect(host, port), _probe_socks5(host, port)


def _format_endpoint(scheme: str, listener: tuple[str, int]) -> str:
    host, port = listener
    if ":" in host:
        host = f"[{host}]"
    return f"{scheme}://{host}:{port}"


def discover() -> tuple[str, str]:
    result = subprocess.run(
        ["ss", "-H", "-ltn"],
        capture_output=True,
        text=True,
        timeout=3,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("无法读取本机监听端口 (需要 ss/iproute2)")

    listeners = _parse_listeners(result.stdout)
    if not listeners:
        raise RuntimeError("本机没有可探测的 TCP 监听端口")

    with ThreadPoolExecutor(max_workers=32) as executor:
        probed = list(executor.map(_probe_listener, listeners))

    http_listeners = {listener for listener, is_http, _ in probed if is_http}
    socks_listeners = {listener for listener, _, is_socks in probed if is_socks}
    if len(http_listeners) > 1 or len(socks_listeners) > 1:
        candidates = sorted(http_listeners | socks_listeners, key=lambda item: (item[1], item[0]))
        rendered = ", ".join(f"{host}:{port}" for host, port in candidates)
        raise RuntimeError(f"检测到多个代理端口 ({rendered})，请用 proxy_on <端口/地址> 指定")
    if not http_listeners and not socks_listeners:
        raise RuntimeError("未检测到 HTTP CONNECT 或 SOCKS5 代理，请先启动代理客户端")

    http_listener = next(iter(http_listeners or socks_listeners))
    socks_listener = next(iter(socks_listeners or http_listeners))
    return (
        _format_endpoint("http", http_listener),
        _format_endpoint("socks5h", socks_listener),
    )


def main() -> int:
    try:
        http_proxy, socks_proxy = discover()
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"[!] {error}", file=sys.stderr)
        return 1

    print(f"http={http_proxy}")
    print(f"socks={socks_proxy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())