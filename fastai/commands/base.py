"""Base abstractions for fastai commands."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any
from typing import ClassVar
from typing import TypeVar

import typer  # type: ignore[reportMissingImports]

import fastai.commands as commands_pkg

_CommandT = TypeVar("_CommandT", bound="BaseCommand")
_SKIP_MODULES = frozenset({"__init__", "base"})


# command context
@dataclass(slots=True)
class CommandContext:
    """Shared runtime context for command execution."""

    workspace: Path


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

# command registry
class CommandRegistry:
    """Store command classes by their declared CLI name."""

    REGISTRY: ClassVar[dict[str, type[BaseCommand]]] = {}

    @classmethod
    def register(cls, command_cls: type[BaseCommand]) -> None:
        name = command_cls.name()
        if name in cls.REGISTRY:
            raise ValueError(f"Command {name!r} is already registered")
        cls.REGISTRY[name] = command_cls

    @classmethod
    def list_commands(cls) -> list[type[BaseCommand]]:
        return sorted(
            cls.REGISTRY.values(),
            key=lambda command_cls: command_cls.meta.name,
        )

    @classmethod
    def clear(cls) -> None:
        cls.REGISTRY.clear()

# fastai command discovery
class CommandDiscovery:
    """Discover built-in command classes."""

    @classmethod
    def discover(cls) -> list[type[BaseCommand]]:
        """Return built-in command classes discovered in ``fastai.commands``."""

        CommandRegistry.clear()

        for _finder, module_name, _is_pkg in pkgutil.iter_modules(commands_pkg.__path__):
            if module_name.startswith("_") or module_name in _SKIP_MODULES:
                continue

            module_path = f"{commands_pkg.__name__}.{module_name}"
            if module_path in sys.modules:
                importlib.reload(sys.modules[module_path])
            else:
                importlib.import_module(module_path)

        return CommandRegistry.list_commands()


# @Command decorator
def Command(
    *, # force named arguments only
    name: str,
    description: str,
    usage: str = "",
    options: list[CommandOption] | tuple[CommandOption, ...] = (),
) -> Callable[[type[_CommandT]], type[_CommandT]]:
    """Decorate and register a command class."""

    meta = CommandMeta(
        name=name,
        description=description,
        usage=usage,
        options=tuple(options),
    )

    def decorate(cls: type[_CommandT]) -> type[_CommandT]:
        """Decorate and register a command class."""

        cls.meta = meta

        CommandRegistry.register(cls)
        return cls

    return decorate
