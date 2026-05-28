"""Tests for the recon command."""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReconCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fastai-recon-"))
        self.workspace = self.temp_dir / "workspace"
        shutil.copytree(REPO_ROOT, self.workspace, ignore=shutil.ignore_patterns(".git", ".worktrees", "__pycache__"))

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

    def test_recon_writes_system_overview_document(self):
        completed = self.run_cli("recon")
        output_path = self.workspace / "docs" / "system-overview.md"

        self.assertEqual(0, completed.returncode)
        self.assertTrue(output_path.exists())
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("# System Overview", content)
        self.assertIn("## Documentation", content)
        self.assertIn("## Python Modules", content)

    def test_recon_summarizes_existing_docs_and_modules(self):
        completed = self.run_cli("recon")
        output_path = self.workspace / "docs" / "system-overview.md"
        content = output_path.read_text(encoding="utf-8")

        self.assertEqual(0, completed.returncode)
        self.assertIn("FastAI_Product_Overview.md", content)
        self.assertIn("fastai/fastai.py", content)
        self.assertIn("fastai/commands/recon/__init__.py", content)

    def test_recon_helpers_live_with_command_module(self):
        module = importlib.import_module("fastai.commands.recon")

        self.assertTrue(callable(module.build_system_overview))
        self.assertTrue(callable(module.iter_markdown_files))
        self.assertTrue(callable(module.iter_python_modules))


if __name__ == "__main__":
    unittest.main()
