from __future__ import annotations

from pathlib import Path
from typing import Any

from fastai.commands.base import BaseCommand, Command, CommandContext, CommandOption
from fastai.commands.recon.collectors import WorkspaceReconCollector
from fastai.commands.recon.orchestrator import ReconOrchestrator


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
        result = ReconOrchestrator().run(context.workspace)
        output_path.write_text(result.overview_markdown, encoding="utf-8")
        print(f"Wrote system overview to {output_path}")
        return 0


def iter_markdown_files(workspace: Path) -> list[Path]:
    """Facade helper retained for tests and future command-local usage."""

    return WorkspaceReconCollector().iter_markdown_files(workspace)


def iter_python_modules(workspace: Path) -> list[Path]:
    """Facade helper retained for tests and future command-local usage."""

    return WorkspaceReconCollector().iter_python_modules(workspace)


def build_system_overview(workspace: Path) -> str:
    """Build the current overview markdown for a workspace."""

    return ReconOrchestrator().run(workspace).overview_markdown
