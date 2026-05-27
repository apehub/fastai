"""Registry for discovered command classes."""

from __future__ import annotations

from fastai.commands.base import BaseCommand


class CommandRegistry:
    """Store command classes by their declared CLI name."""

    def __init__(self) -> None:
        self._commands: dict[str, type[BaseCommand]] = {}

    def register(self, command_cls: type[BaseCommand]) -> None:
        name = command_cls.name()
        if name in self._commands:
            raise ValueError(f"Command {name!r} is already registered")
        self._commands[name] = command_cls

    def list_commands(self) -> list[type[BaseCommand]]:
        return sorted(
            self._commands.values(),
            key=lambda command_cls: (command_cls.meta.order, command_cls.meta.name),
        )

    def clear(self) -> None:
        self._commands.clear()


_COMMAND_REGISTRY = CommandRegistry()


def get_command_registry() -> CommandRegistry:
    return _COMMAND_REGISTRY
