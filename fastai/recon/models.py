from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class FactRequestKind(StrEnum):
    """Structured request kinds the planner may ask the collector to satisfy."""

    LIST_DIRECTORY = "listDirectory"
    READ_FILE_SUMMARY = "readFileSummary"
    SAMPLE_FILES_BY_GLOB = "sampleFilesByGlob"
    SUMMARIZE_MANIFEST = "summarizeManifest"
    READ_MARKDOWN_SUMMARY = "readMarkdownSummary"


@dataclass(slots=True, frozen=True)
class WorkspaceSummary:
    """High-level workspace facts gathered without AI assistance."""

    root: Path
    top_level_directories: list[Path] = field(default_factory=list)
    top_level_files: list[Path] = field(default_factory=list)
    total_files: int = 0


@dataclass(slots=True, frozen=True)
class ScmFacts:
    """Repository-level facts collected from SCM-aware tools."""

    kind: str | None = None
    repo_url: str | None = None
    ignore_sources: list[Path] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class DocumentationFacts:
    """Facts about documentation assets that may guide later analysis."""

    markdown_files: list[Path] = field(default_factory=list)
    summary_candidates: list[Path] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class StructureFacts:
    """Candidates for source, test, resource and script directories."""

    source_directories: list[Path] = field(default_factory=list)
    test_directories: list[Path] = field(default_factory=list)
    resource_directories: list[Path] = field(default_factory=list)
    script_directories: list[Path] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class EcosystemCandidate:
    """A possible ecosystem hint inferred from high-signal manifest files."""

    name: str
    evidence: list[Path] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class SampledFile:
    """A file snippet or summary requested by the planner."""

    path: Path
    summary: str


@dataclass(slots=True, frozen=True)
class FactRequest:
    """A structured request for additional facts made by the planner."""

    kind: FactRequestKind
    target: str
    reason: str
    budget: int = 1


@dataclass(slots=True, frozen=True)
class ReconAnalysis:
    """The analyzer's structured view of the project after fact collection."""

    project_type_hypotheses: list[str] = field(default_factory=list)
    important_directories: list[Path] = field(default_factory=list)
    important_files: list[Path] = field(default_factory=list)
    framework_summary: str = ""
    domain_summary: str = ""
    open_questions: list[str] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class ReconFacts:
    """The full fact container passed between collectors, planner and analyzer."""

    workspace: WorkspaceSummary
    scm: ScmFacts = field(default_factory=ScmFacts)
    documentation: DocumentationFacts = field(default_factory=DocumentationFacts)
    structure: StructureFacts = field(default_factory=StructureFacts)
    file_type_counts: dict[str, int] = field(default_factory=dict)
    ecosystem_candidates: list[EcosystemCandidate] = field(default_factory=list)
    sampled_files: list[SampledFile] = field(default_factory=list)
    python_modules: list[Path] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class ReconRunResult:
    """The result returned by the orchestrator to the command layer."""

    facts: ReconFacts
    requests: list[FactRequest]
    analysis: ReconAnalysis
    overview_markdown: str
