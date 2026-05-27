"""Built-in command discovery."""

from __future__ import annotations

import importlib
import pkgutil
import sys

from fastai.commands.base import BaseCommand
from fastai.commands.registry import get_command_registry
import fastai.commands as commands_pkg

_SKIP_MODULES = frozenset({"__init__", "base", "context", "discovery", "registry"})


def discover_command_classes() -> list[type[BaseCommand]]:
    """Return built-in command classes discovered in ``fastai.commands``."""

    registry = get_command_registry()
    registry.clear()

    for _finder, module_name, _is_pkg in pkgutil.iter_modules(commands_pkg.__path__):
        if module_name.startswith("_") or module_name in _SKIP_MODULES:
            continue

        module_path = f"{commands_pkg.__name__}.{module_name}"
        if module_path in sys.modules:
            importlib.reload(sys.modules[module_path])
        else:
            importlib.import_module(module_path)

    return registry.list_commands()
