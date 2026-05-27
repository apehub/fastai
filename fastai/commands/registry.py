"""Registry for discovered command classes."""

from __future__ import annotations

from typing import ClassVar

from fastai.commands.base import BaseCommand


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
