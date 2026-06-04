from __future__ import annotations

from pathlib import Path
from typing import Any

import typer  # type: ignore[reportMissingImports]

from fastai.commands.base import BaseCommand, Command, CommandContext, CommandOption
from fastai.recon.orchestrator import ReconOrchestrator


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
    """

    def run(self, context: CommandContext, **kwargs: Any) -> int:
        outfile = kwargs.get("output") or (
            context.workspace / "docs" / "system-overview.md"
        )
        outfile = Path(outfile)
        outfile.parent.mkdir(parents=True, exist_ok=True)

        def report_progress(message: str) -> None:
            typer.echo(f"[recon] {message}...", err=True)

        result = ReconOrchestrator().run(context.workspace, progress=report_progress)
        typer.echo(f"[recon] Writing overview to {outfile}...", err=True)
        outfile.write_text(result.overview_markdown, encoding="utf-8")
        typer.echo(f"Wrote system overview to {outfile}")
        return 0
