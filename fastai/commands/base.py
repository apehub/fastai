"""Base abstractions for fastai commands."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import ClassVar
from typing import TypeVar

from fastai.commands.context import CommandContext

_CommandT = TypeVar("_CommandT", bound="BaseCommand")


@dataclass(frozen=True, slots=True)
class CommandMeta:
    """Static metadata describing a CLI command."""

    name: str
    description: str
    short_help: str = ""
    group: str = "project"
    aliases: tuple[str, ...] = ()
    hidden: bool = False
    deprecated: bool = False
    order: int = 100


class BaseCommand(ABC):
    """Base class for all fastai commands."""

    meta: ClassVar[CommandMeta]

    @classmethod
    def name(cls) -> str:
        """Return the registered command name."""

        return cls.meta.name

    def get_typer_callback(self) -> Callable[..., int] | None:
        """Return a custom Typer callback when the command needs its own options."""

        return None

    @abstractmethod
    def run(self, context: CommandContext, **kwargs: Any) -> int:
        """Execute the command."""


# @command decorator
def Command(
    *,
    name: str,
    description: str,
    short_help: str = "",
    group: str = "project",
    aliases: tuple[str, ...] = (),
    hidden: bool = False,
    deprecated: bool = False,
    order: int = 100,
) -> Callable[[type[_CommandT]], type[_CommandT]]:
    """Decorate and register a command class."""

    meta = CommandMeta(
        name=name,
        description=description,
        short_help=short_help,
        group=group,
        aliases=aliases,
        hidden=hidden,
        deprecated=deprecated,
        order=order,
    )

    def decorate(cls: type[_CommandT]) -> type[_CommandT]:
        """Decorate and register a command class."""

        cls.meta = meta

        from fastai.commands.registry import get_command_registry

        get_command_registry().register(cls)
        return cls

    return decorate
