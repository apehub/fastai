"""Peek into the project to get a quick overview."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections import Counter
from fastai.tools.SCM import SCM


@dataclass(slots=True, frozen=True)
class GlanceFacts:
    """The facts gathered by the Glance."""

    workspace: str
    topLevelDirectories: list[str]
    topLevelFiles: list[str]
    fileTypeCounts: dict[str, int]
    scm: SCM


COMMON_IGNORED_DIRS = {
    ".git",
    ".svn",
    "__pycache__",
    ".venv",
    ".DS_Store",
    ".gitignore",
    ".svnignore",
    ".worktrees",
    "node_modules",
}


class Glance:
    """Glance into the project to get a quick overview."""

    @staticmethod
    def run(workspace: Path) -> GlanceFacts:
        """Glance into the project to get a quick overview."""

        scm = SCM.detect(workspace)

        # get the top level directories and files
        base = workspace
        topLevelDirs = sorted(
            path.relative_to(base) for path in workspace.iterdir() if path.is_dir()
        )
        topLevelFiles = sorted(
            path.relative_to(base) for path in workspace.iterdir() if path.is_file()
        )

        # get the ignored directories and files
        ignoredDirs = sorted(
            path.relative_to(base)
            for path in workspace.iterdir()
            if path.is_dir()
            and (
                path.name.startswith(".")
                or path.name in COMMON_IGNORED_DIRS
                or scm.ignored(path)
            )
        )
        ignoredDirSet = set(ignoredDirs)

        def isIgnoredPath(path: Path) -> bool:
            rel = path.relative_to(base)
            return any(
                part.startswith(".") or part in COMMON_IGNORED_DIRS
                for part in rel.parts[:-1]
            ) or any(parent in ignoredDirSet for parent in rel.parents)

        # get file counts by type(skip ignored files from SCM ignore list)
        fileTypeCounts = dict(
            sorted(
                Counter(
                    path.suffix or "<no-ext>"
                    for path in workspace.rglob("*")
                    if path.is_file() and not isIgnoredPath(path)
                ).items()
            )
        )

        return GlanceFacts(
            workspace=workspace.as_posix(),
            topLevelDirectories=topLevelDirs,
            topLevelFiles=topLevelFiles,
            fileTypeCounts=fileTypeCounts,
            scm=scm,
        )
