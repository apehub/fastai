from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
from typing import ClassVar


class SCMError(RuntimeError):
    """SCM command execution failed."""


# Base class for SCM tools.
class SCM(ABC):
    """SCM tools: git, svn, cvs, hg, etc."""

    MARKER: ClassVar[str] = ""
    workbase: Path

    def __init__(self, workbase: Path):
        self.workbase = workbase

    @staticmethod
    def detect(workbase: Path) -> SCM | None:
        """Detect the SCM type in the workspace."""
        for scm in (Git, Subversion, Mercurial):
            if (workbase / scm.MARKER).exists():
                return scm(workbase)
        return None

    def run(self, command: list[str], *, lines: bool = False) -> str | list[str]:
        """Run a command in the workspace."""
        try:
            output = subprocess.run(
                command,
                shell=False,
                capture_output=True,
                text=True,
                check=True,
                cwd=self.workbase,
            ).stdout.strip()
        except subprocess.CalledProcessError as error:
            command_text = " ".join(command)
            raise SCMError(f"SCM command failed: {command_text}") from error
        if lines:
            return output.splitlines()
        return output

    @abstractmethod
    def repo(self) -> str:
        """Get the repository URL."""
        raise NotImplementedError


# Git SCM tool.
class Git(SCM):
    """Git SCM tool."""

    MARKER: ClassVar[str] = ".git"

    def repo(self) -> str:
        """Get the repository URL."""
        return self.run(["git", "config", "--get", "remote.origin.url"])


# Subversion SCM tool.
class Subversion(SCM):
    """Subversion SCM tool."""

    MARKER: ClassVar[str] = ".svn"

    def repo(self) -> str:
        """Get the repository URL."""
        return self.run(["svn", "info", "--show-item", "url"])


# Mercurial SCM tool.
class Mercurial(SCM):
    """Mercurial SCM tool."""

    MARKER: ClassVar[str] = ".hg"

    def repo(self) -> str:
        """Get the repository URL."""
        return self.run(["hg", "showconfig", "paths.default"])
