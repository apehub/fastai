from __future__ import annotations

import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from fastai.agents import local
from fastai.agents.local import (
    AgentInvokeOptions,
    AgentRuntime,
    ClaudeCodeAgent,
    CodexAgent,
    CopilotAgent,
    CursorAgent,
    GeminiAgent,
    HermesAgent,
    OpenCodeAgent,
)


def test_runtime_cli_defaults() -> None:
    assert CursorAgent.cli == "cursor-agent"

    assert CodexAgent.cli == "codex"

    assert ClaudeCodeAgent.cli == "claude"

    assert CopilotAgent.cli == "copilot"

    assert OpenCodeAgent.cli == "opencode"

    assert GeminiAgent.cli == "gemini"

    assert HermesAgent.cli == "hermes"


def test_only_mainstream_runtimes_are_exposed() -> None:
    agent_names = {name for name in vars(local) if name.endswith("Agent")}

    assert agent_names == {
        "ClaudeCodeAgent",
        "CodexAgent",
        "CopilotAgent",
        "CursorAgent",
        "GeminiAgent",
        "HermesAgent",
        "OpenCodeAgent",
    }


def test_available_resolves_cli_on_path() -> None:
    agent = CursorAgent()

    with patch.object(local.shutil, "which", return_value="/usr/bin/cursor-agent") as which:
        assert agent.available() is True
    which.assert_called_once_with("cursor-agent")

    with patch.object(local.shutil, "which", return_value=None):
        assert agent.available() is False


def test_available_is_false_for_empty_cli() -> None:
    with patch.object(local.shutil, "which") as which:
        assert AgentRuntime().available() is False
    which.assert_not_called()


def test_detect_keeps_only_agents_found_on_path() -> None:
    installed = {"cursor-agent", "claude"}

    with patch.object(
        local.shutil,
        "which",
        side_effect=lambda cli: f"/usr/bin/{cli}" if cli in installed else None,
    ):
        detected = AgentRuntime.detect()

    assert {runtime.cli for runtime in detected} == installed


def test_invoke_returns_error_when_cli_missing() -> None:
    agent = CursorAgent()
    with patch.object(local.shutil, "which", return_value=None):
        result = agent.invoke("hi")

    assert result.ok is False
    assert "not found" in (result.error or "")


def test_invoke_parses_stream_json_stdout() -> None:
    stdout = "\n".join(
        [
            '{"type": "system", "subtype": "init"}',
            '{"type": "assistant", "message": {"content": [{"type": "text", "text": "Hello "}]}}',
            '{"type": "text", "text": "world"}',
            '{"type": "result", "result": "Hello world"}',
        ]
    )
    agent = CursorAgent()
    completed = SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    with patch.object(local.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        local.subprocess, "run", return_value=completed
    ) as run:
        result = agent.invoke("analyze")

    assert result.ok is True
    assert result.text == "Hello world"
    assert run.call_args.args[0] == [
        "cursor-agent",
        "-p",
        "analyze",
        "--output-format",
        "stream-json",
        "--yolo",
    ]


def test_cursor_build_argv_includes_dynamic_options() -> None:
    options = AgentInvokeOptions(
        workspace=local.Path("/repo"),
        model="gpt-5",
        resume_session_id="session-1",
        extra_args=("--custom", "value"),
    )

    assert CursorAgent().build_argv("analyze", options) == [
        "cursor-agent",
        "-p",
        "analyze",
        "--output-format",
        "stream-json",
        "--yolo",
        "--workspace",
        "/repo",
        "--model",
        "gpt-5",
        "--resume",
        "session-1",
        "--custom",
        "value",
    ]


def test_claude_build_argv_places_prompt_after_print_flag() -> None:
    options = AgentInvokeOptions(model="opus", extra_args=("--dangerously-skip-permissions",))

    assert ClaudeCodeAgent().build_argv("inspect", options) == [
        "claude",
        "-p",
        "inspect",
        "--output-format",
        "stream-json",
        "--input-format",
        "stream-json",
        "--verbose",
        "--strict-mcp-config",
        "--permission-mode",
        "bypassPermissions",
        "--model",
        "opus",
        "--dangerously-skip-permissions",
    ]


def test_gemini_build_argv_places_prompt_after_prompt_flag() -> None:
    options = AgentInvokeOptions(model="gemini-pro")

    assert GeminiAgent().build_argv("summarize", options) == [
        "gemini",
        "-p",
        "summarize",
        "--yolo",
        "-o",
        "stream-json",
        "--model",
        "gemini-pro",
    ]


def test_invoke_uses_options_for_cwd_and_timeout() -> None:
    agent = CursorAgent()
    completed = SimpleNamespace(returncode=0, stdout="ok\n", stderr="")
    options = AgentInvokeOptions(workspace=local.Path("/tmp/project"), timeout=3.5)

    with patch.object(local.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        local.subprocess, "run", return_value=completed
    ) as run:
        result = agent.invoke("go", options=options)

    assert result.ok is True
    assert run.call_args.kwargs["cwd"] == "/tmp/project"
    assert run.call_args.kwargs["timeout"] == 3.5


def test_invoke_falls_back_to_result_when_no_streaming_text() -> None:
    stdout = '{"type": "result", "result": "final answer"}'
    agent = ClaudeCodeAgent()
    completed = SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    with patch.object(local.shutil, "which", return_value="/usr/bin/claude"), patch.object(
        local.subprocess, "run", return_value=completed
    ):
        result = agent.invoke("go")

    assert result.text == "final answer"


def test_invoke_returns_plain_stdout_when_not_json() -> None:
    agent = CursorAgent()
    completed = SimpleNamespace(returncode=0, stdout="just text\n", stderr="")

    with patch.object(local.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        local.subprocess, "run", return_value=completed
    ):
        result = agent.invoke("go")

    assert result.text == "just text"


def test_invoke_captures_nonzero_exit() -> None:
    agent = CursorAgent()
    completed = SimpleNamespace(returncode=1, stdout="", stderr="boom")

    with patch.object(local.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        local.subprocess, "run", return_value=completed
    ):
        result = agent.invoke("go")

    assert result.ok is False
    assert result.error == "boom"


def test_invoke_captures_timeout() -> None:
    agent = CursorAgent()

    with patch.object(local.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        local.subprocess,
        "run",
        side_effect=subprocess.TimeoutExpired(cmd="cursor-agent", timeout=1.0),
    ):
        result = agent.invoke("go", options=AgentInvokeOptions(timeout=1.0))

    assert result.ok is False
    assert "timed out" in (result.error or "")
