"""Project reconnaissance helpers."""

from __future__ import annotations

from pathlib import Path


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
        if ".git" not in path.parts and ".worktrees" not in path.parts and "__pycache__" not in path.parts
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
