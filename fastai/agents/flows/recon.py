"""Recon call flow.

Builds a reconnaissance prompt from collected ``ReconFacts``, asks an
``AgentRuntime`` to analyze the project, and parses the JSON response into a
``ReconAnalysis``. Parsing failures degrade into a ``ReconAnalysis`` that
records the problem in ``open_questions`` instead of raising.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastai.agents.flow import AgentFlow
from fastai.agents.local import AgentResult
from fastai.recon.models import ReconAnalysis, ReconFacts

_SCHEMA_HINT = (
    '{"project_type_hypotheses": [string], "important_directories": [string], '
    '"important_files": [string], "framework_summary": string, '
    '"domain_summary": string, "open_questions": [string]}'
)


class ReconFlow(AgentFlow[ReconFacts, ReconAnalysis]):
    """Agent-backed project reconnaissance analysis."""

    def build_prompt(self, inputs: ReconFacts) -> str:
        workspace = inputs.workspace
        directories = _join(p.as_posix() for p in workspace.top_level_directories)
        files = _join(p.as_posix() for p in workspace.top_level_files)
        types = _join(f"{ext}:{count}" for ext, count in inputs.file_type_counts.items())
        ecosystems = _join(candidate.name for candidate in inputs.ecosystem_candidates)
        markdown = _join(p.as_posix() for p in inputs.documentation.markdown_files[:20])

        return (
            "You are analyzing a software project to produce a high-level "
            "reconnaissance summary for an engineering team.\n\n"
            f"Workspace root: {workspace.root.as_posix()}\n"
            f"Total files: {workspace.total_files}\n"
            f"Top-level directories: {directories}\n"
            f"Top-level files: {files}\n"
            f"File type counts: {types}\n"
            f"Ecosystem hints: {ecosystems}\n"
            f"Markdown docs: {markdown}\n\n"
            "Respond with ONLY a single JSON object (no prose, no markdown code "
            "fence) using exactly these keys:\n"
            f"{_SCHEMA_HINT}\n"
        )

    def parse(self, result: AgentResult, inputs: ReconFacts) -> ReconAnalysis:
        if not result.text:
            reason = result.error or "agent returned an empty response"
            return ReconAnalysis(open_questions=[f"Agent invocation failed: {reason}"])

        payload = _extract_json_object(result.text)
        if payload is None:
            return ReconAnalysis(
                open_questions=["Agent response was not a parseable JSON object."],
            )

        return ReconAnalysis(
            project_type_hypotheses=_as_str_list(payload.get("project_type_hypotheses")),
            important_directories=_as_path_list(payload.get("important_directories")),
            important_files=_as_path_list(payload.get("important_files")),
            framework_summary=_as_str(payload.get("framework_summary")),
            domain_summary=_as_str(payload.get("domain_summary")),
            open_questions=_as_str_list(payload.get("open_questions")),
        )


def _join(values: Any) -> str:
    joined = ", ".join(values)
    return joined or "(none)"


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Extract the first JSON object from ``text`` (tolerates code fences/prose)."""

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _as_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _as_path_list(value: Any) -> list[Path]:
    if not isinstance(value, list):
        return []
    return [Path(item) for item in value if isinstance(item, str)]
