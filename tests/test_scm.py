"""Tests for SCM detection."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastai.tools.SCM import Git, SCM, SCMError, Subversion


class ScmTests(unittest.TestCase):
    def test_each_scm_class_exposes_its_marker(self):
        self.assertEqual(".git", Git.MARKER)
        self.assertEqual(".svn", Subversion.MARKER)

    def test_detect_returns_matching_scm_instance(self):
        with tempfile.TemporaryDirectory(prefix="fastai-scm-") as temp_dir:
            workspace = Path(temp_dir)
            (workspace / ".git").mkdir()

            with patch.object(Git, "repo", return_value="git@example.com:repo.git"):
                detected = SCM.detect(workspace)

        self.assertIsInstance(detected, Git)
        self.assertEqual(workspace, detected.workbase)
        self.assertEqual("git@example.com:repo.git", detected.url)

    def test_detect_returns_none_when_workspace_has_no_supported_marker(self):
        with tempfile.TemporaryDirectory(prefix="fastai-scm-") as temp_dir:
            workspace = Path(temp_dir)

            detected = SCM.detect(workspace)

        self.assertIsNone(detected)

    def test_run_returns_text_by_default(self):
        scm = Git(Path("/tmp/workspace"))

        with patch("fastai.tools.SCM.subprocess.run") as fake_run:
            fake_run.return_value = SimpleNamespace(stdout="first\nsecond\n")

            result = scm.run(["git", "status"])

        self.assertEqual("first\nsecond", result)
        fake_run.assert_called_once_with(
            ["git", "status"],
            capture_output=True,
            text=True,
            check=True,
            cwd=scm.workbase,
            shell=False,
        )

    def test_run_can_return_lines(self):
        scm = Git(Path("/tmp/workspace"))

        with patch("fastai.tools.SCM.subprocess.run") as fake_run:
            fake_run.return_value = SimpleNamespace(stdout="first\nsecond\n")

            result = scm.run(["git", "status"], lines=True)

        self.assertEqual(["first", "second"], result)

    def test_run_wraps_subprocess_failure_with_scm_error(self):
        scm = Git(Path("/tmp/workspace"))
        original_error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "status"],
            stderr="fatal: not a git repository",
        )

        with patch("fastai.tools.SCM.subprocess.run", side_effect=original_error):
            with self.assertRaises(SCMError) as context:
                scm.run(["git", "status"])

        self.assertIn("git status", str(context.exception))
        self.assertIs(original_error, context.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
