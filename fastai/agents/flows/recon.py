"""Recon call flow.

Builds a reconnaissance prompt from collected ``ReconFacts``, asks an
``AgentRuntime`` to analyze the project, and parses the JSON response into a
``ReconAnalysis``. Parsing failures degrade into a ``ReconAnalysis`` that
records the problem in ``open_questions`` instead of raising.
"""

from __future__ import annotations

import logging
from typing import Any

from fastai.agents.flow import AgentFlow
from fastai.agents.runtimes import AgentResult
from fastai.recon.models import ReconAnalysis, ReconFacts
from fastai.utils.strs import as_path_list, as_str, as_str_list, extract_json_object

_SCHEMA_HINT = (
    '{"project_type_hypotheses": [string], "important_directories": [string], '
    '"important_files": [string], "framework_summary": string, '
    '"domain_summary": string, "open_questions": [string]}'
)
logger = logging.getLogger(__name__)


class ReconFlow(AgentFlow[ReconFacts, ReconAnalysis]):
    """Agent-backed project reconnaissance analysis."""

    def build_prompt(self, inputs: ReconFacts) -> str:
        workspace = inputs.workspace
        logger.info(
            "Building recon prompt for workspace=%s total_files=%s markdown_files=%s python_modules=%s",
            workspace.root,
            workspace.total_files,
            len(inputs.documentation.markdown_files),
            len(inputs.python_modules),
        )
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
            logger.warning("Recon agent returned no parseable text: %s", reason)
            return ReconAnalysis(open_questions=[f"Agent invocation failed: {reason}"])

        payload = extract_json_object(result.text)
        if payload is None:
            logger.warning(
                "Recon agent response was not parseable JSON: response_chars=%s",
                len(result.text),
            )
            return ReconAnalysis(
                open_questions=["Agent response was not a parseable JSON object."],
            )

        analysis = ReconAnalysis(
            project_type_hypotheses=as_str_list(payload.get("project_type_hypotheses")),
            important_directories=as_path_list(payload.get("important_directories")),
            important_files=as_path_list(payload.get("important_files")),
            framework_summary=as_str(payload.get("framework_summary")),
            domain_summary=as_str(payload.get("domain_summary")),
            open_questions=as_str_list(payload.get("open_questions")),
        )
        logger.info(
            "Parsed recon analysis hypotheses=%s important_directories=%s important_files=%s open_questions=%s",
            len(analysis.project_type_hypotheses),
            len(analysis.important_directories),
            len(analysis.important_files),
            len(analysis.open_questions),
        )
        return analysis


def _join(values: Any) -> str:
    joined = ", ".join(values)
    return joined or "(none)"
