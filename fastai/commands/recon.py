"""Project reconnaissance command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastai.commands.base import BaseCommand, Command, CommandOption
from fastai.commands.context import CommandContext
from fastai.recon import build_system_overview


@Command(
    name="recon",
    description="Project reconnaissance.",
    usage="Scan project docs and module structure",
    group="project",
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
    """Inspect the current project at a high level."""

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

