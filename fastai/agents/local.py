"""Local coding-agent runtimes.

An ``AgentRuntime`` drives a native coding-agent CLI (Cursor, Claude Code,
Codex, ...) as a subprocess to obtain LLM output. FastAI does not call any
model API itself; it reuses whatever coding agent the developer already has
installed on their machine.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AgentResult:
    """Normalized result of a single agent runtime invocation."""

    ok: bool
    text: str
    raw: str
    error: str | None = None


@dataclass(frozen=True, slots=True)
class AgentInvokeOptions:
    """Runtime options for one agent invocation."""

    workspace: Path | None = None
    timeout: float = 600.0
    model: str | None = None
    resume_session_id: str | None = None
    extra_args: tuple[str, ...] = ()


# base/abstract class for all local coding-agent runtimes
class AgentRuntime:
    """A local coding-agent CLI that FastAI drives to obtain LLM output."""

    cli: str = ""

    def available(self) -> bool:
        """Return True if this runtime's CLI is found on the system PATH."""
        return bool(self.cli) and shutil.which(self.cli) is not None

    def invoke(
        self,
        prompt: str,
        *,
        options: AgentInvokeOptions | None = None,
    ) -> AgentResult:
        """Run the agent CLI once with ``prompt`` and return a normalized result.

        Failures (missing CLI, timeout, non-zero exit, launch error) are
        captured into ``AgentResult.error`` rather than raised, so callers can
        degrade gracefully.
        """

        options = options or AgentInvokeOptions()

        if not self.available():
            return AgentResult(
                ok=False,
                text="",
                raw="",
                error=f"{self.cli or 'agent'} not found on PATH",
            )

        argv = self.build_argv(prompt, options)
        try:
            proc = subprocess.run(
                argv,
                cwd=str(options.workspace) if options.workspace is not None else None,
                capture_output=True,
                text=True,
                timeout=options.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return AgentResult(
                ok=False,
                text="",
                raw="",
                error=f"{self.cli} timed out after {options.timeout}s",
            )
        except OSError as exc:
            return AgentResult(
                ok=False,
                text="",
                raw="",
                error=f"failed to launch {self.cli}: {exc}",
            )

        raw = proc.stdout or ""
        text = self._parse_output(raw)
        if proc.returncode != 0:
            error = (proc.stderr or "").strip() or f"{self.cli} exited with code {proc.returncode}"
            return AgentResult(ok=False, text=text, raw=raw, error=error)
        return AgentResult(ok=True, text=text, raw=raw)

    def build_argv(self, prompt: str, options: AgentInvokeOptions) -> list[str]:
        """Build the process argv for a single prompt invocation."""
        return [self.cli, prompt, *options.extra_args]

    def _parse_output(self, stdout: str) -> str:
        """Extract assistant text from CLI output.

        The default handles newline-delimited stream-json (Cursor/Claude
        style): it concatenates assistant/text events and falls back to the
        final ``result`` event. Non-JSON output is returned stripped, as-is.
        Subclasses may override for other output conventions.
        """

        stripped = stdout.strip()
        if not stripped:
            return ""

        chunks: list[str] = []
        result_text = ""
        saw_json = False
        for line in stripped.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            saw_json = True
            if event.get("type") == "result" and isinstance(event.get("result"), str):
                result_text = event["result"]
                continue
            text = self._extract_event_text(event)
            if text:
                chunks.append(text)

        if not saw_json:
            return stripped
        joined = "".join(chunks).strip()
        return joined or result_text.strip()

    @staticmethod
    def _extract_event_text(event: dict) -> str:
        """Pull plain text from a single stream-json event."""

        etype = event.get("type")
        if etype == "text" and isinstance(event.get("text"), str):
            return event["text"]
        if etype == "assistant":
            message = event.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    parts = [
                        block["text"]
                        for block in content
                        if isinstance(block, dict)
                        and block.get("type") in ("text", "output_text")
                        and isinstance(block.get("text"), str)
                    ]
                    return "".join(parts)
        return ""

    @staticmethod
    def detect() -> list[AgentRuntime]:
        """Detect all local coding-agent runtimes installed on the system."""

        candidates = [
            CursorAgent(),
            CodexAgent(),
            ClaudeCodeAgent(),
            OpenCodeAgent(),
            CopilotAgent(),
        ]
        # keep only runtimes whose CLI is resolvable on the system PATH
        return [runtime for runtime in candidates if runtime.available()]


# cursor agent
class CursorAgent(AgentRuntime):
    """Cursor agent."""

    cli: str = "cursor-agent"

    def build_argv(self, prompt: str, options: AgentInvokeOptions) -> list[str]:
        argv = [
            self.cli,
            "-p",
            prompt,
            "--output-format",
            "stream-json",
            "--yolo",
        ]
        if options.workspace is not None:
            argv.extend(["--workspace", options.workspace.as_posix()])
        if options.model:
            argv.extend(["--model", options.model])
        if options.resume_session_id:
            argv.extend(["--resume", options.resume_session_id])
        argv.extend(options.extra_args)
        return argv


# codex agent
class CodexAgent(AgentRuntime):
    """Codex agent."""

    cli: str = "codex"

    def build_argv(self, prompt: str, options: AgentInvokeOptions) -> list[str]:
        return [self.cli, "app-server", "--listen", "stdio://", *options.extra_args]


# claude code agent
class ClaudeCodeAgent(AgentRuntime):
    """Claude code agent."""

    cli: str = "claude"

    def build_argv(self, prompt: str, options: AgentInvokeOptions) -> list[str]:
        argv = [
            self.cli,
            "-p",
            prompt,
            "--output-format",
            "stream-json",
            "--input-format",
            "stream-json",
            "--verbose",
            "--strict-mcp-config",
            "--permission-mode",
            "bypassPermissions",
        ]
        if options.model:
            argv.extend(["--model", options.model])
        if options.resume_session_id:
            argv.extend(["--resume", options.resume_session_id])
        argv.extend(options.extra_args)
        return argv


# copilot agent
class CopilotAgent(AgentRuntime):
    """Copilot agent."""

    cli: str = "copilot"

    def build_argv(self, prompt: str, options: AgentInvokeOptions) -> list[str]:
        argv = [
            self.cli,
            "-p",
            prompt,
            "--output-format",
            "json",
            "--allow-all",
            "--no-ask-user",
        ]
        if options.model:
            argv.extend(["--model", options.model])
        argv.extend(options.extra_args)
        return argv


# opencode agent
class OpenCodeAgent(AgentRuntime):
    """OpenCode agent."""

    cli: str = "opencode"

    def build_argv(self, prompt: str, options: AgentInvokeOptions) -> list[str]:
        argv = [
            self.cli,
            "run",
            prompt,
            "--format",
            "json",
            "--dangerously-skip-permissions",
        ]
        if options.model:
            argv.extend(["--model", options.model])
        argv.extend(options.extra_args)
        return argv


# gemini agent
class GeminiAgent(AgentRuntime):
    """Gemini agent."""

    cli: str = "gemini"

    def build_argv(self, prompt: str, options: AgentInvokeOptions) -> list[str]:
        argv = [self.cli, "-p", prompt, "--yolo", "-o", "stream-json"]
        if options.model:
            argv.extend(["--model", options.model])
        argv.extend(options.extra_args)
        return argv


# hermes agent
class HermesAgent(AgentRuntime):
    """Hermes agent."""

    cli: str = "hermes"

    def build_argv(self, prompt: str, options: AgentInvokeOptions) -> list[str]:
        return [self.cli, "acp", *options.extra_args]
