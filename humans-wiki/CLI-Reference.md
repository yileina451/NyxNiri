`nyxuri` manages install, snapshots and diagnostics. Interactive deployments create a snapshot in `~/.config/nyxuri/backups/` by default.

> Legacy Bash users must run the bootstrap entrypoint before using these commands. The old `nyxniri update` cannot perform the directory migration.

---

## Top-level

| Command | Description |
| :--- | :--- |
| `nyxuri` | Interactive menu |
| `nyxuri test` | Developer test deploy (no backup, keep monitor.kdl) |

---

## Deploy

| Command | Description |
| :--- | :--- |
| `nyxuri install [full\|config]` | Deploy everything, or sync configs only |
| `nyxuri update [--force\|--no-deploy]` | Update source; force config deployment or skip it |

---

## Snapshots

| Command | Description |
| :--- | :--- |
| `nyxuri snapshot [note]` | Save current config state |
| `nyxuri snapshot delete [idx]` | Delete snapshots (multi-select if no index) |
| `nyxuri rollback [index]` | Restore a snapshot |
| `nyxuri list` | List snapshots |

---

## System

| Command | Description |
| :--- | :--- |
| `nyxuri doctor` | Dependency + system health check |
| `nyxuri deps` | Open dependency check & install menu |
| `nyxuri apps` | Category-grouped recommended apps installer (Brave, Steam, WeChat, ...) |
| `nyxuri wallpapers` | Download the full wallpaper & video pack from the external repo |
| `nyxuri theme [toggle\|dark\|light\|sync\|status]` | Switch or sync system dark/light theme |
| `nyxuri bug` / `nyxuri report` | Generate diagnostic bug report |

---

## Uninstall

| Command | Description |
| :--- | :--- |
| `nyxuri uninstall [--all\|standard\|restore\|purge]` | Checkbox uninstall — pick what to remove (configs, CLI, modules, snapshots, wallpapers); defaults to the standard range |
| `nyxuri purge` | Shorthand for `uninstall --all` |

---

## Extensions

| Command | Description |
| :--- | :--- |
| `nyxuri fcitx [install\|status\|uninstall]` | NyxMellow fcitx5 skin |
| `nyxuri greeter [install\|status\|uninstall]` | Noctalia Greeter (login screen) |
| `nyxuri gtk [install\|status\|uninstall]` | Material You GTK3/4 theme |
| `nyxuri fisher [install\|status\|uninstall]` | fisher plugin manager for Fish |

---

## Cheatsheet nyxhelp

`nyxhelp` is a compact fzf-based reference for the CLI, shell helpers, and core keybindings:

| Command | Description |
| :--- | :--- |
| `nyxhelp` | Interactive dual-panel cheatsheet |
| `nyxhelp keys` | Niri keybindings |
| `nyxhelp proxy` | Proxy controls (`proxy_on [port/address]`, `proxy_off`, `proxy_status`) |
| `nyxhelp pkg` | Package shortcuts (`up`, `in`, `se`, `un`, `clean`) |
| `nyxhelp all` | Full cheatsheet |

Without arguments, `proxy_on` scans local loopback TCP listeners and identifies HTTP CONNECT / SOCKS5 proxies by protocol handshake. Start the proxy client first; if multiple candidates are found, specify one with `proxy_on <port/address>`. The toggle updates the current terminal and the D-Bus / systemd user-session environment for applications subsequently launched by those services. Applications spawned directly by niri or the desktop shell may not inherit the new values, and already-running browsers or games do not switch immediately. Use the proxy client's TUN / global mode to cover all desktop traffic.
