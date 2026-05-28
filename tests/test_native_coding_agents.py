import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "fastai" / "agents" / "native" / "CodingAgent.py"
SPEC = importlib.util.spec_from_file_location("native_coding_agent", MODULE_PATH)
assert SPEC is not None
native_coding_agent = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(native_coding_agent)


def test_native_coding_agent_cli_defaults() -> None:
    ClaudeCodeAgent = native_coding_agent.ClaudeCodeAgent
    CodexAgent = native_coding_agent.CodexAgent
    CopilotAgent = native_coding_agent.CopilotAgent
    CursorAgent = native_coding_agent.CursorAgent
    GeminiAgent = native_coding_agent.GeminiAgent
    HermesAgent = native_coding_agent.HermesAgent
    OpenCodeAgent = native_coding_agent.OpenCodeAgent

    assert CursorAgent.cli == "cursor-agent"
    assert CursorAgent.args == ["-p", "--output-format", "stream-json", "--yolo"]

    assert CodexAgent.cli == "codex"
    assert CodexAgent.args == ["app-server", "--listen", "stdio://"]

    assert ClaudeCodeAgent.cli == "claude"
    assert ClaudeCodeAgent.args == [
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

    assert CopilotAgent.cli == "copilot"
    assert CopilotAgent.args == ["-p", "--output-format", "json", "--allow-all", "--no-ask-user"]

    assert OpenCodeAgent.cli == "opencode"
    assert OpenCodeAgent.args == ["run", "--format", "json", "--dangerously-skip-permissions"]

    assert GeminiAgent.cli == "gemini"
    assert GeminiAgent.args == ["-p", "--yolo", "-o", "stream-json"]

    assert HermesAgent.cli == "hermes"
    assert HermesAgent.args == ["acp"]


def test_native_coding_agents_only_expose_mainstream_adapters() -> None:
    agent_names = {
        name
        for name in vars(native_coding_agent)
        if name.endswith("Agent") and name != "CodingAgent"
    }

    assert agent_names == {
        "ClaudeCodeAgent",
        "CodexAgent",
        "CopilotAgent",
        "CursorAgent",
        "GeminiAgent",
        "HermesAgent",
        "OpenCodeAgent",
    }
