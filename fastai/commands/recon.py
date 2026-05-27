"""Project reconnaissance command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer

from fastai.commands.base import BaseCommand, Command
from fastai.commands.context import CommandContext
from fastai.recon import build_system_overview


@Command(
    name="recon",
    description="Project reconnaissance.",
    short_help="Scan project docs and module structure",
    group="project",
)
class ReconCommand(BaseCommand):
    """Inspect the current project at a high level."""

    def get_typer_callback(self):
        def callback(
            ctx: typer.Context,
            output: Annotated[
                Path | None,
                typer.Option(
                    "--output",
                    help="Write the generated system overview to this path.",
                    file_okay=True,
                    dir_okay=False,
                    writable=True,
                    resolve_path=False,
                ),
            ] = None,
        ) -> int:
            command_context = CommandContext(
                workspace=Path(ctx.obj["workspace"]).resolve()
            )
            return self.run(command_context, output=output)

        return callback

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

