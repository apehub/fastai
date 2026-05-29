from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from fastai.agents.flows.recon import ReconFlow
from fastai.agents.runtimes import AgentInvokeOptions, AgentResult, AgentRuntime
from fastai.recon.models import (
    DocumentationFacts,
    EcosystemCandidate,
    ReconFacts,
    WorkspaceSummary,
)
from fastai.recon.orchestrator import ReconOrchestrator


class StubRuntime(AgentRuntime):
    """An agent runtime that returns a canned result without any subprocess."""

    def __init__(self, result: AgentResult) -> None:
        self._result = result

    def available(self) -> bool:
        return True

    def invoke(self, prompt: str, *, options: AgentInvokeOptions | None = None) -> AgentResult:
        self.last_prompt = prompt
        return self._result


def _facts() -> ReconFacts:
    return ReconFacts(
        workspace=WorkspaceSummary(
            root=Path("/tmp/project"),
            top_level_directories=[Path("src"), Path("tests")],
            top_level_files=[Path("pyproject.toml")],
            total_files=42,
        ),
        documentation=DocumentationFacts(markdown_files=[Path("README.md")]),
        file_type_counts={".py": 30, ".md": 2},
        ecosystem_candidates=[EcosystemCandidate(name="python", evidence=[Path("pyproject.toml")])],
    )


def test_build_prompt_includes_key_facts() -> None:
    flow = ReconFlow(StubRuntime(AgentResult(ok=True, text="", raw="")))
    prompt = flow.build_prompt(_facts())

    assert "/tmp/project" in prompt
    assert "src" in prompt and "tests" in prompt
    assert "python" in prompt
    assert ".py:30" in prompt
    assert "JSON object" in prompt


def test_parse_good_json_populates_analysis() -> None:
    payload = {
        "project_type_hypotheses": ["python library"],
        "important_directories": ["src", "tests"],
        "important_files": ["pyproject.toml"],
        "framework_summary": "typer-based CLI",
        "domain_summary": "AI scaffolding tool",
        "open_questions": ["what is the release cadence?"],
    }
    # wrapped in prose + code fence to exercise tolerant extraction
    text = f"Here is the analysis:\n```json\n{json.dumps(payload)}\n```\nDone."
    flow = ReconFlow(StubRuntime(AgentResult(ok=True, text=text, raw=text)))

    analysis = flow.run(_facts())

    assert analysis.project_type_hypotheses == ["python library"]
    assert analysis.important_directories == [Path("src"), Path("tests")]
    assert analysis.important_files == [Path("pyproject.toml")]
    assert analysis.framework_summary == "typer-based CLI"
    assert analysis.domain_summary == "AI scaffolding tool"
    assert analysis.open_questions == ["what is the release cadence?"]


def test_parse_invalid_json_degrades_gracefully() -> None:
    flow = ReconFlow(StubRuntime(AgentResult(ok=True, text="not json at all", raw="")))

    analysis = flow.run(_facts())

    assert analysis.framework_summary == ""
    assert analysis.open_questions  # records the parse failure


def test_parse_failed_invocation_records_error() -> None:
    flow = ReconFlow(StubRuntime(AgentResult(ok=False, text="", raw="", error="cli missing")))

    analysis = flow.run(_facts())

    assert any("cli missing" in q for q in analysis.open_questions)


def test_orchestrator_uses_supplied_runtime() -> None:
    payload = {"framework_summary": "agent-authored", "domain_summary": "demo"}
    text = json.dumps(payload)
    runtime = StubRuntime(AgentResult(ok=True, text=text, raw=text))

    workspace = Path(tempfile.mkdtemp(prefix="fastai-recon-"))
    try:
        (workspace / "pyproject.toml").write_text("[project]\nname='x'\n")
        (workspace / "app.py").write_text("print('hi')\n")

        result = ReconOrchestrator.run(workspace, runtime=runtime)
    finally:
        shutil.rmtree(workspace)

    assert result.analysis.framework_summary == "agent-authored"
    assert "agent-authored" in result.overview_markdown


def test_orchestrator_degrades_without_runtime() -> None:
    workspace = Path(tempfile.mkdtemp(prefix="fastai-recon-"))
    try:
        (workspace / "app.py").write_text("print('hi')\n")
        # force "no agent installed"
        import fastai.agents.runtimes as runtimes

        original = runtimes.AgentRuntime.detect
        runtimes.AgentRuntime.detect = staticmethod(lambda: [])
        try:
            result = ReconOrchestrator.run(workspace)
        finally:
            runtimes.AgentRuntime.detect = original
    finally:
        shutil.rmtree(workspace)

    assert result.overview_markdown.startswith("# System Overview")
