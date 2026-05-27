"""Tests for CLI command wiring."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fastai-cli-"))
        self.workspace = self.temp_dir / "workspace"
        shutil.copytree(
            REPO_ROOT,
            self.workspace,
            ignore=shutil.ignore_patterns(".git", ".worktrees", "__pycache__"),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = {"PYTHONPATH": str(self.workspace), **dict()}
        return subprocess.run(
            [sys.executable, "-m", "fastai", *args],
            cwd=self.workspace,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_help_lists_recon_command(self):
        completed = self.run_cli("--help")

        self.assertEqual(0, completed.returncode)
        self.assertIn("recon", completed.stdout)

    def test_recon_uses_workspace_option(self):
        workspace = self.workspace / "docs"
        completed = self.run_cli("--workspace", str(workspace), "recon")

        self.assertEqual(0, completed.returncode)
        self.assertIn("system overview", completed.stdout.lower())

    def test_recon_accepts_output_option(self):
        output_path = self.workspace / "tmp" / "overview.md"
        completed = self.run_cli("--workspace", str(self.workspace), "recon", "--output", str(output_path))

        self.assertEqual(0, completed.returncode)
        self.assertTrue(output_path.exists())
        self.assertIn(str(output_path), completed.stdout)


if __name__ == "__main__":
    unittest.main()
