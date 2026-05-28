"""Tests for quick workspace glance facts."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastai.recon.glance import Glance


class FakeSCM:
    def __init__(self, ignored_paths: set[Path]):
        self.ignored_paths = ignored_paths

    def ignored(self, path: Path) -> bool:
        return path in self.ignored_paths


class GlanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fastai-glance-"))
        self.workspace = self.temp_dir / "workspace"
        self.workspace.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_file_type_counts_skip_common_and_scm_ignored_directories(self):
        (self.workspace / "src").mkdir()
        (self.workspace / "src" / "app.py").write_text("print('hello')\n")
        (self.workspace / "src" / "notes.md").write_text("# Notes\n")
        (self.workspace / "node_modules").mkdir()
        (self.workspace / "node_modules" / "package.js").write_text("module.exports = {}\n")
        (self.workspace / ".venv").mkdir()
        (self.workspace / ".venv" / "site.py").write_text("# generated\n")
        (self.workspace / ".cache").mkdir()
        (self.workspace / ".cache" / "cached.json").write_text("{}\n")
        (self.workspace / "build").mkdir()
        (self.workspace / "build" / "artifact.bin").write_text("binary\n")
        scm = FakeSCM({self.workspace / "build"})

        with patch("fastai.recon.glance.SCM.detect", return_value=scm):
            facts = Glance.run(self.workspace)

        self.assertEqual({".md": 1, ".py": 1}, facts.fileTypeCounts)


if __name__ == "__main__":
    unittest.main()
