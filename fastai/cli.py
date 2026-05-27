"""Command-line interface for fastai."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from fastai.commands.context import CommandContext
from fastai.commands.discovery import discover_command_classes

app = typer.Typer(
    name="fastai",
    help="FastAI command-line interface.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _build_context(workspace: Path) -> CommandContext:
    return CommandContext(workspace=workspace.resolve())


def _register_commands() -> None:
    def make_callback(command_instance):
        def callback(ctx: typer.Context) -> int:
            command_context = _build_context(ctx.obj["workspace"])
            return command_instance.run(command_context)

        return callback

    for command_cls in discover_command_classes():
        command = command_cls()
        meta = command.meta

        callback = command.get_typer_callback() or make_callback(command)

        app.command(
            name=meta.name,
            help=meta.description,
            short_help=meta.short_help or meta.description,
            hidden=meta.hidden,
            deprecated=meta.deprecated,
        )(callback)


_register_commands()


@app.callback()
def _callback(
    ctx: typer.Context,
    workspace: Annotated[
        Path,
        typer.Option(
            "--workspace",
            help="Workspace path used by commands.",
            exists=False,
            file_okay=False,
            dir_okay=True,
            resolve_path=False,
        ),
    ] = Path("."),
) -> None:
    ctx.obj = {"workspace": workspace}


def main(argv: list[str] | None = None) -> int:
    return app(args=argv, standalone_mode=False) or 0
