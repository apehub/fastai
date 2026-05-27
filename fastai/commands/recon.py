"""Project reconnaissance command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastai.commands.base import BaseCommand, Command, CommandContext, CommandOption


def iter_markdown_files(workspace: Path) -> list[Path]:
    """Return markdown files relative to the workspace."""

    return sorted(
        path.relative_to(workspace)
        for path in workspace.rglob("*.md")
        if ".git" not in path.parts and ".worktrees" not in path.parts
    )


def iter_python_modules(workspace: Path) -> list[Path]:
    """Return Python source files relative to the workspace."""

    return sorted(
        path.relative_to(workspace)
        for path in workspace.rglob("*.py")
        if ".git" not in path.parts
        and ".worktrees" not in path.parts
        and "__pycache__" not in path.parts
    )


def build_system_overview(workspace: Path) -> str:
    """Build a minimal system overview document for the workspace."""

    markdown_files = iter_markdown_files(workspace)
    python_modules = iter_python_modules(workspace)

    lines = [
        "# System Overview",
        "",
        "## Project Summary",
        "",
        f"- Workspace: `{workspace}`",
        f"- Markdown files: {len(markdown_files)}",
        f"- Python modules: {len(python_modules)}",
        "",
        "## Documentation",
        "",
    ]

    if markdown_files:
        lines.extend(f"- `{path.as_posix()}`" for path in markdown_files)
    else:
        lines.append("- No markdown documents found.")

    lines.extend(["", "## Python Modules", ""])

    if python_modules:
        lines.extend(f"- `{path.as_posix()}`" for path in python_modules)
    else:
        lines.append("- No Python modules found.")

    lines.append("")
    return "\n".join(lines)


@Command(
    name="recon",
    description="Project reconnaissance.",
    usage="Scan project docs and module structure",
    options=[
        CommandOption(
            name="output",
            flags=("--output",),
            annotation=Path | None,
            default=None,
            help="Write the generated system overview to this path.",
        )
    ],
)
class ReconCommand(BaseCommand):
    """
    Inspect the current project at a high level.

    Basic flow:
    1. check .git, .svn, .cvs, .hg, etc, to determine the repository type
    2. invoke native SCM tool (e.g. git, svn, cvs, hg) to get the repository URL
    3. get the ignored files from .gitignore OR other SCM ignore files
    4. scan the workspace to get the high-level project structure(e.g. source directories, test directories, etc.)
    5. scan all the files(not ignored) to get the file count by file type.
    6. read markdown files to understand the project business domain.
    7. chat with AI to analyze the framework/library used in the project(with the information above as the context).

    """

    def run(self, context: CommandContext, **kwargs: Any) -> int:
        output_path = kwargs.get("output") or (
            context.workspace / "docs" / "system-overview.md"
        )
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            build_system_overview(context.workspace), encoding="utf-8"
        )
        print(f"Wrote system overview to {output_path}")
        return 0
