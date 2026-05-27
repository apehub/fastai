"""Tests for command discovery and registration."""

import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastai.commands.base import BaseCommand, Command, CommandContext, CommandOption
import fastai.commands as commands_pkg
from fastai.commands import BaseCommand as ExportedBaseCommand
from fastai.commands import CommandDiscovery as ExportedCommandDiscovery
from fastai.commands import CommandRegistry as ExportedCommandRegistry
from fastai.fastai import app as exported_app
from fastai.fastai import main as exported_main
from fastai.commands.discovery import CommandDiscovery
from fastai.commands.registry import CommandRegistry


class CommandDiscoveryTests(unittest.TestCase):
    def test_commands_package_reexports_core_symbols(self):
        self.assertIs(ExportedBaseCommand, BaseCommand)
        self.assertIs(ExportedCommandDiscovery, CommandDiscovery)
        self.assertIs(ExportedCommandRegistry, CommandRegistry)

    def test_fastai_module_exports_cli_entrypoints(self):
        self.assertTrue(callable(exported_main))
        self.assertIsNotNone(exported_app)

    def test_discover_commands_includes_recon(self):
        command_names = [command_cls.meta.name for command_cls in CommandDiscovery.discover()]

        self.assertEqual(["recon"], command_names)

    def test_discovery_can_run_repeatedly(self):
        first = [command_cls.meta.name for command_cls in CommandDiscovery.discover()]
        second = [command_cls.meta.name for command_cls in CommandDiscovery.discover()]

        self.assertEqual(["recon"], first)
        self.assertEqual(["recon"], second)

    def test_registry_rejects_duplicate_command_names(self):
        previous_registry = CommandRegistry.REGISTRY

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

        CommandRegistry.REGISTRY = {}
        CommandRegistry.register(FirstCommand)

        try:
            with self.assertRaisesRegex(ValueError, "duplicate"):
                CommandRegistry.register(SecondCommand)
        finally:
            CommandRegistry.REGISTRY = previous_registry

    def test_command_decorator_attaches_metadata_and_registers_class(self):
        previous_registry = CommandRegistry.REGISTRY
        CommandRegistry.REGISTRY = {}

        try:
            @Command(
                name="sample",
                description="Sample command",
                usage="Run a sample command",
                options=[
                    CommandOption(
                        name="output",
                        flags=("--output",),
                        annotation=Path | None,
                        default=None,
                        help="Write output here.",
                    )
                ],
            )
            class SampleCommand(BaseCommand):
                def run(self, context: CommandContext) -> int:
                    return 0

            self.assertEqual("sample", SampleCommand.meta.name)
            self.assertEqual("Run a sample command", SampleCommand.meta.usage)
            self.assertEqual("output", SampleCommand.meta.options[0].name)
            self.assertEqual([SampleCommand], CommandRegistry.list_commands())
        finally:
            CommandRegistry.REGISTRY = previous_registry

    def test_command_can_build_typer_callback_signature(self):
        @Command(
            name="sample",
            description="Sample command",
            usage="Run a sample command",
            options=[
                CommandOption(
                    name="output",
                    flags=("--output",),
                    annotation=Path | None,
                    default=None,
                    help="Write output here.",
                )
            ],
        )
        class SampleCommand(BaseCommand):
            def run(self, context: CommandContext) -> int:
                return 0

        callback = SampleCommand().typer_callback()
        signature = inspect.signature(callback)

        self.assertIn("ctx", signature.parameters)
        self.assertIn("output", signature.parameters)
        self.assertEqual(inspect._ParameterKind.KEYWORD_ONLY, signature.parameters["output"].kind)

    def test_discovery_imports_modules_registered_by_decorator(self):
        with tempfile.TemporaryDirectory(prefix="fastai-commands-") as temp_dir:
            Path(temp_dir, "decorated.py").write_text(
                "\n".join(
                    [
                        "from fastai.commands.base import BaseCommand, Command",
                        "from fastai.commands.context import CommandContext",
                        "",
                        "@Command(name='decorated', description='Decorated command', usage='Decorated usage')",
                        "class DecoratedCommand(BaseCommand):",
                        "    def run(self, context: CommandContext) -> int:",
                        "        return 0",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            CommandRegistry.clear()

            with patch.object(commands_pkg, "__path__", [temp_dir]):
                command_names = [
                    command_cls.meta.name
                    for command_cls in CommandDiscovery.discover()
                ]

        self.assertEqual(["decorated"], command_names)
        CommandRegistry.clear()


if __name__ == "__main__":
    unittest.main()
