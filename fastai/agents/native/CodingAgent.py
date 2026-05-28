"""Native coding agent CLI."""


# base/abstract class for all native coding agents
class CodingAgent:
    """Native coding agent."""

    cli: str = ""
    args: list[str] = []


# cursor agent
class CursorAgent(CodingAgent):
    """Cursor agent."""

    cli: str = "cursor-agent"
    args: list[str] = ["-p", "--output-format", "stream-json", "--yolo"]


# codex agent
class CodexAgent(CodingAgent):
    """Codex agent."""

    cli: str = "codex"
    args: list[str] = ["app-server", "--listen", "stdio://"]


# claude code agent
class ClaudeCodeAgent(CodingAgent):
    """Claude code agent."""

    cli: str = "claude"
    args: list[str] = [
        "-p",
        "--output-format",
        "stream-json",
        "--input-format",
        "stream-json",
        "--verbose",
        "--strict-mcp-config",
        "--permission-mode",
        "bypassPermissions",
    ]


# copilot agent
class CopilotAgent(CodingAgent):
    """Copilot agent."""

    cli: str = "copilot"
    args: list[str] = ["-p", "--output-format", "json", "--allow-all", "--no-ask-user"]

# opencode agent
class OpenCodeAgent(CodingAgent):
    """OpenCode agent."""

    cli: str = "opencode"
    args: list[str] = ["run", "--format", "json", "--dangerously-skip-permissions"]


# gemini agent
class GeminiAgent(CodingAgent):
    """Gemini agent."""

    cli: str = "gemini"
    args: list[str] = ["-p", "--yolo", "-o", "stream-json"]


# hermes agent
class HermesAgent(CodingAgent):
    """Hermes agent."""

    cli: str = "hermes"
    args: list[str] = ["acp"]
