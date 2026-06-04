"""Main CLI entrypoints for the fastai application."""

from __future__ import annotations

import typer  # type: ignore[reportMissingImports]

from fastai.commands import CommandDiscovery

app = typer.Typer(
    name="fastai",
    help="FastAI command-line interface.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _register_commands() -> None:
    for cls in CommandDiscovery.discover():
        cmd = cls()
        meta = cmd.meta

        app.command(
            name=meta.name,
            help=meta.description,
            short_help=meta.usage or meta.description,
        )(cmd.typer_callback())


@app.callback()
def _callback() -> None:
    return None


def main(argv: list[str] | None = None) -> int:
    try:
        _register_commands()
        return app(args=argv, standalone_mode=False) or 0
    except Exception as exc:
        if type(exc).__name__ == "NoArgsIsHelpError":
            return 0
        raise
