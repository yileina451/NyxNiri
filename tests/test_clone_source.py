"""Contract tests for the NYXURI_REPO override and its legacy fallback."""

import subprocess
import sys
import unittest


class TestCloneSourceOverride(unittest.TestCase):
    def _registry_with_env(self, env_value=None):
        env_assignment = (
            f"os.environ['NYXNIRI_REPO']={env_value!r};" if env_value is not None else "os.environ.pop('NYXNIRI_REPO', None);"
        )
        code = (
            "import os;" + env_assignment +
            "from nyxuri import constants;"
            "print(constants.REPO_URL);"
            "print(constants.GIT_MIRROR_REGISTRY)"
        )
        res = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, check=True,
        )
        lines = res.stdout.strip().splitlines()
        return lines[0], lines[1]

    def test_override_collapses_to_single_custom_mirror(self):
        custom = "https://git.internal/NyxNiri.git"
        repo_url, registry = self._registry_with_env(custom)
        self.assertEqual(registry, f"[('Custom', '{custom}')]")

    def test_display_repo_url_uses_personal_repo_even_when_overridden(self):
        repo_url, _ = self._registry_with_env("https://git.internal/NyxNiri.git")
        self.assertEqual(repo_url, "https://github.com/yileina451/NyxNiri.git")

    def test_default_without_env_uses_only_personal_repo_mirrors(self):
        repo_url, registry = self._registry_with_env(None)
        self.assertEqual(repo_url, "https://github.com/yileina451/NyxNiri.git")
        self.assertIn("https://github.com/yileina451/NyxNiri.git", registry)
        self.assertIn("gh-proxy.org/https://github.com/yileina451/NyxNiri.git", registry)
        self.assertNotIn("ech678/Nyxuri", registry)
        self.assertIn("gh-proxy.org", registry)

    def _clone_behavior_with_env(self, env_value):
        """Run clone_repo_with_fallback in a fresh interpreter with the env set."""
        env_assignment = (
            f"os.environ['NYXNIRI_REPO']={env_value!r};" if env_value is not None else "os.environ.pop('NYXNIRI_REPO', None);"
        )
        code = (
            "import os, tempfile\n"
            "from pathlib import Path\n"
            + env_assignment.rstrip(";") + "\n" +
            "from unittest.mock import patch\n"
            "from nyxuri.network import clone_repo_with_fallback\n"
            "with tempfile.TemporaryDirectory() as td:\n"
            "    with patch('nyxuri.network.git_clone_timeout') as gct:\n"
            "        result = clone_repo_with_fallback(Path(td))\n"
            "    print(result)\n"
            "    print(gct.call_args_list)\n"
        )
        res = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, check=True,
        )
        lines = res.stdout.strip().splitlines()
        return lines[0], lines[1]

    def test_invalid_custom_repo_fails_closed_without_git_call(self):
        result, git_calls = self._clone_behavior_with_env("file:///tmp/evil")
        self.assertEqual(result, "False")
        self.assertEqual(git_calls, "[]")

    def test_invalid_custom_repo_never_falls_back_to_official(self):
        """单源直连语义:非法地址不能静默换回官方镜像,必须拒绝。"""
        result, git_calls = self._clone_behavior_with_env("/local/path")
        self.assertEqual(result, "False")
        self.assertEqual(git_calls, "[]")

    def test_valid_custom_repo_clones_single_source(self):
        result, git_calls = self._clone_behavior_with_env("ssh://git.internal/NyxNiri.git")
        self.assertEqual(result, "True")
        self.assertIn("ssh://git.internal/NyxNiri.git", git_calls)

    def test_nyxuri_repo_takes_precedence_over_nyxniri_repo(self):
        code = (
            "import os;"
            "os.environ['NYXURI_REPO']='https://git.primary/Nyxuri.git';"
            "os.environ['NYXNIRI_REPO']='https://git.secondary/NyxNiri.git';"
            "from nyxuri import constants;"
            "print(constants.GIT_MIRROR_REGISTRY)"
        )
        res = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, check=True,
        )
        self.assertIn("https://git.primary/Nyxuri.git", res.stdout)
        self.assertNotIn("https://git.secondary/NyxNiri.git", res.stdout)


if __name__ == "__main__":
    unittest.main()
