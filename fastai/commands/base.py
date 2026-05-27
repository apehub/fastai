"""Base abstractions for fastai commands."""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import ClassVar
from typing import TypeVar

from fastai.commands.context import CommandContext
import typer  # type: ignore[reportMissingImports]

_CommandT = TypeVar("_CommandT", bound="BaseCommand")


# command option
@dataclass(frozen=True, slots=True)
class CommandOption:
    """Static metadata describing a CLI option."""

    name: str
    flags: tuple[str, ...]
    annotation: Any = str
    default: Any = None
    help: str = ""


# command meta for command decorator
@dataclass(frozen=True, slots=True)
class CommandMeta:
    """Static metadata describing a CLI command."""

    name: str
    description: str
    usage: str = ""
    group: str = "project"
    options: tuple[CommandOption, ...] = ()


# super class for all commands
class BaseCommand(ABC):
    """Base class for all fastai commands."""

    meta: ClassVar[CommandMeta]

    @classmethod
    def name(cls) -> str:
        """Return the registered command name."""

        return cls.meta.name

    def build_context(self) -> CommandContext:
        """Build runtime context for the current command invocation."""

        return CommandContext(workspace=Path.cwd().resolve())

    def build_option_parameter(self, option: CommandOption) -> inspect.Parameter:
        """Convert command option metadata into a Typer-compatible parameter."""

        return inspect.Parameter(
            option.name,
            inspect.Parameter.KEYWORD_ONLY,
            default=typer.Option(option.default, *option.flags, help=option.help),
            annotation=option.annotation,
        )

    def typer_callback(self) -> Callable[..., int]:
        """Build the callback object Typer inspects to define CLI parameters.

        Typer reads the callback signature to discover options like ``--output``.
        We synthesize that signature from ``CommandOption`` metadata so command
        classes can declare options declaratively via ``@Command(..., options=...)``.
        """

        def callback(ctx: typer.Context, **kwargs) -> int:
            command_context = self.build_context()
            return self.run(command_context, **kwargs)

        callback.__signature__ = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    "ctx",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=typer.Context,
                ),
                *[
                    self.build_option_parameter(option)
                    for option in self.meta.options
                ],
            ],
            return_annotation=int,
        )
        return callback

    @abstractmethod
    def run(self, context: CommandContext, **kwargs: Any) -> int:
        """Execute the command."""


# @Command decorator
def Command(
    *, # force named arguments only
    name: str,
    description: str,
    usage: str = "",
    group: str = "project",
    options: list[CommandOption] | tuple[CommandOption, ...] = (),
) -> Callable[[type[_CommandT]], type[_CommandT]]:
    """Decorate and register a command class."""

    meta = CommandMeta(
        name=name,
        description=description,
        usage=usage,
        group=group,
        options=tuple(options),
    )

    def decorate(cls: type[_CommandT]) -> type[_CommandT]:
        """Decorate and register a command class."""

        cls.meta = meta

        from fastai.commands.registry import CommandRegistry

        CommandRegistry.register(cls)
        return cls

    return decorate
