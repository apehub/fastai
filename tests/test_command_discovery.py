"""Tests for command discovery and registration."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastai.commands.base import BaseCommand, Command, CommandContext
import fastai.commands as commands_pkg
from fastai.commands.discovery import discover_command_classes
from fastai.commands.registry import CommandRegistry, get_command_registry


class CommandDiscoveryTests(unittest.TestCase):
    def test_discover_commands_includes_recon(self):
        command_names = [command_cls.meta.name for command_cls in discover_command_classes()]

        self.assertEqual(["recon"], command_names)

    def test_discovery_can_run_repeatedly(self):
        first = [command_cls.meta.name for command_cls in discover_command_classes()]
        second = [command_cls.meta.name for command_cls in discover_command_classes()]

        self.assertEqual(["recon"], first)
        self.assertEqual(["recon"], second)

    def test_registry_rejects_duplicate_command_names(self):
        class FirstCommand(BaseCommand):
            @classmethod
            def name(cls) -> str:
                return "duplicate"

            def run(self, context: CommandContext) -> int:
                return 0

        class SecondCommand(BaseCommand):
            @classmethod
            def name(cls) -> str:
                return "duplicate"

            def run(self, context: CommandContext) -> int:
                return 0

        registry = CommandRegistry()
        registry.register(FirstCommand)

        with self.assertRaisesRegex(ValueError, "duplicate"):
            registry.register(SecondCommand)

    def test_command_decorator_attaches_metadata_and_registers_class(self):
        registry = CommandRegistry()

        with patch("fastai.commands.registry.get_command_registry", return_value=registry):
            @Command(name="sample", description="Sample command", order=42)
            class SampleCommand(BaseCommand):
                def run(self, context: CommandContext) -> int:
                    return 0

        self.assertEqual("sample", SampleCommand.meta.name)
        self.assertEqual([SampleCommand], registry.list_commands())

    def test_discovery_imports_modules_registered_by_decorator(self):
        with tempfile.TemporaryDirectory(prefix="fastai-commands-") as temp_dir:
            Path(temp_dir, "decorated.py").write_text(
                "\n".join(
                    [
                        "from fastai.commands.base import BaseCommand, Command",
                        "from fastai.commands.context import CommandContext",
                        "",
                        "@Command(name='decorated', description='Decorated command')",
                        "class DecoratedCommand(BaseCommand):",
                        "    def run(self, context: CommandContext) -> int:",
                        "        return 0",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            get_command_registry().clear()

            with patch.object(commands_pkg, "__path__", [temp_dir]):
                command_names = [command_cls.meta.name for command_cls in discover_command_classes()]

        self.assertEqual(["decorated"], command_names)
        get_command_registry().clear()


if __name__ == "__main__":
    unittest.main()
