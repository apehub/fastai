"""Runtime context passed to commands."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CommandContext:
    """Shared runtime context for command execution."""

    workspace: Path
