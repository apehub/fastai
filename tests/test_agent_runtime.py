from __future__ import annotations

import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from fastai.agents import runtimes
from fastai.agents.runtimes import (
    AgentInvokeOptions,
    AgentRuntime,
    ClaudeRuntime,
    CodexRuntime,
    CopilotRuntime,
    CursorRuntime,
    GeminiRuntime,
    HermesRuntime,
    OpenCodeRuntime,
)


def test_runtime_cli_defaults() -> None:
    assert CursorRuntime.cli == "cursor-agent"

    assert CodexRuntime.cli == "codex"

    assert ClaudeRuntime.cli == "claude"

    assert CopilotRuntime.cli == "copilot"

    assert OpenCodeRuntime.cli == "opencode"

    assert GeminiRuntime.cli == "gemini"

    assert HermesRuntime.cli == "hermes"


def test_only_mainstream_runtimes_are_exposed() -> None:
    runtime_names = {name for name in vars(runtimes) if name.endswith("Runtime")}

    assert runtime_names == {
        "AgentRuntime",
        "ClaudeRuntime",
        "CodexRuntime",
        "CopilotRuntime",
        "CursorRuntime",
        "GeminiRuntime",
        "HermesRuntime",
        "OpenCodeRuntime",
    }


def test_available_resolves_cli_on_path() -> None:
    runtime = CursorRuntime()

    with patch.object(runtimes.shutil, "which", return_value="/usr/bin/cursor-agent") as which:
        assert runtime.available() is True
    which.assert_called_once_with("cursor-agent")

    with patch.object(runtimes.shutil, "which", return_value=None):
        assert runtime.available() is False


def test_available_is_false_for_empty_cli() -> None:
    with patch.object(runtimes.shutil, "which") as which:
        assert AgentRuntime().available() is False
    which.assert_not_called()


def test_detect_keeps_only_agents_found_on_path() -> None:
    installed = {"cursor-agent", "claude"}

    with patch.object(
        runtimes.shutil,
        "which",
        side_effect=lambda cli: f"/usr/bin/{cli}" if cli in installed else None,
    ):
        detected = AgentRuntime.detect()

    assert {runtime.cli for runtime in detected} == installed


def test_invoke_returns_error_when_cli_missing() -> None:
    runtime = CursorRuntime()
    with patch.object(runtimes.shutil, "which", return_value=None):
        result = runtime.invoke("hi")

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
    runtime = CursorRuntime()
    completed = SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    with patch.object(runtimes.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        runtimes.subprocess, "run", return_value=completed
    ) as run:
        result = runtime.invoke("analyze")

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


def test_base_runtime_parse_output_strips_stdout() -> None:
    assert AgentRuntime().parse_output("  plain output\n") == "plain output"


def test_cursor_parse_output_reads_stream_json() -> None:
    stdout = "\n".join(
        [
            '{"type": "assistant", "message": {"content": [{"type": "text", "text": "Hello "}]}}',
            '{"type": "text", "text": "world"}',
        ]
    )

    assert CursorRuntime().parse_output(stdout) == "Hello world"


def test_claude_parse_output_reads_stream_json_result_fallback() -> None:
    stdout = '{"type": "result", "result": "final answer"}'

    assert ClaudeRuntime().parse_output(stdout) == "final answer"


def test_copilot_parse_output_uses_base_stdout_behavior() -> None:
    assert CopilotRuntime().parse_output('{"answer": "kept raw"}\n') == '{"answer": "kept raw"}'


def test_cursor_build_args_includes_dynamic_options() -> None:
    options = AgentInvokeOptions(
        workspace=runtimes.Path("/repo"),
        model="gpt-5",
        resume_session_id="session-1",
        extra_args=("--custom", "value"),
    )

    assert CursorRuntime().build_args("analyze", options) == [
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


def test_claude_build_args_places_prompt_after_print_flag() -> None:
    options = AgentInvokeOptions(model="opus", extra_args=("--dangerously-skip-permissions",))

    assert ClaudeRuntime().build_args("inspect", options) == [
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


def test_gemini_build_args_places_prompt_after_prompt_flag() -> None:
    options = AgentInvokeOptions(model="gemini-pro")

    assert GeminiRuntime().build_args("summarize", options) == [
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
    runtime = CursorRuntime()
    completed = SimpleNamespace(returncode=0, stdout="ok\n", stderr="")
    options = AgentInvokeOptions(workspace=runtimes.Path("/tmp/project"), timeout=3.5)

    with patch.object(runtimes.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        runtimes.subprocess, "run", return_value=completed
    ) as run:
        result = runtime.invoke("go", options=options)

    assert result.ok is True
    assert run.call_args.kwargs["cwd"] == "/tmp/project"
    assert run.call_args.kwargs["timeout"] == 3.5


def test_invoke_falls_back_to_result_when_no_streaming_text() -> None:
    stdout = '{"type": "result", "result": "final answer"}'
    runtime = ClaudeRuntime()
    completed = SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    with patch.object(runtimes.shutil, "which", return_value="/usr/bin/claude"), patch.object(
        runtimes.subprocess, "run", return_value=completed
    ):
        result = runtime.invoke("go")

    assert result.text == "final answer"


def test_invoke_returns_plain_stdout_when_not_json() -> None:
    runtime = CursorRuntime()
    completed = SimpleNamespace(returncode=0, stdout="just text\n", stderr="")

    with patch.object(runtimes.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        runtimes.subprocess, "run", return_value=completed
    ):
        result = runtime.invoke("go")

    assert result.text == "just text"


def test_invoke_captures_nonzero_exit() -> None:
    runtime = CursorRuntime()
    completed = SimpleNamespace(returncode=1, stdout="", stderr="boom")

    with patch.object(runtimes.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        runtimes.subprocess, "run", return_value=completed
    ):
        result = runtime.invoke("go")

    assert result.ok is False
    assert result.error == "boom"


def test_invoke_captures_timeout() -> None:
    runtime = CursorRuntime()

    with patch.object(runtimes.shutil, "which", return_value="/usr/bin/cursor-agent"), patch.object(
        runtimes.subprocess,
        "run",
        side_effect=subprocess.TimeoutExpired(cmd="cursor-agent", timeout=1.0),
    ):
        result = runtime.invoke("go", options=AgentInvokeOptions(timeout=1.0))

    assert result.ok is False
    assert "timed out" in (result.error or "")
