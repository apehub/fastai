from __future__ import annotations

from collections import Counter
from pathlib import Path

from fastai.commands.recon.models import (
    DocumentationFacts,
    EcosystemCandidate,
    FactRequest,
    FactRequestKind,
    ReconFacts,
    SampledFile,
    ScmFacts,
    StructureFacts,
    WorkspaceSummary,
)
from fastai.tools.SCM import SCM, SCMError

_IGNORED_PARTS = {".git", ".worktrees", "__pycache__", ".venv"}
_ECOSYSTEM_MARKERS = {
    "python": ["pyproject.toml", "requirements.txt"],
    "node": ["package.json", "pnpm-lock.yaml", "yarn.lock"],
    "java": ["pom.xml", "build.gradle", "settings.gradle"],
    "dotnet": ["Directory.Build.props"],
    "cpp": ["CMakeLists.txt", "meson.build", "Makefile"],
    "unity": ["Packages/manifest.json"],
    "lua": [".rockspec", "init.lua"],
}


class WorkspaceReconCollector:
    """Collect recon facts from the local workspace.

    The first iteration intentionally keeps collection logic simple and
    deterministic. Future versions can deepen each collection stage with richer
    language-specific scanning, ignore resolution, manifest parsing and richer
    file summaries.
    """

    def collect_base_facts(self, workspace: Path) -> ReconFacts:
        """Collect the first pass of high-signal workspace facts."""

        files = [path for path in workspace.rglob("*") if path.is_file() and not self._is_ignored(path)]
        top_level_directories = sorted(
            path.relative_to(workspace)
            for path in workspace.iterdir()
            if path.is_dir() and path.name not in _IGNORED_PARTS
        )
        top_level_files = sorted(
            path.relative_to(workspace)
            for path in workspace.iterdir()
            if path.is_file()
        )
        markdown_files = self.iter_markdown_files(workspace)
        python_modules = self.iter_python_modules(workspace)
        file_type_counts = dict(sorted(Counter(path.suffix or "<no-ext>" for path in files).items()))

        return ReconFacts(
            workspace=WorkspaceSummary(
                root=workspace,
                top_level_directories=top_level_directories,
                top_level_files=top_level_files,
                total_files=len(files),
            ),
            scm=self.collect_scm_facts(workspace),
            documentation=DocumentationFacts(
                markdown_files=markdown_files,
                summary_candidates=markdown_files[:5],
            ),
            structure=self.collect_structure_facts(workspace),
            file_type_counts=file_type_counts,
            ecosystem_candidates=self.detect_ecosystem_candidates(workspace),
            python_modules=python_modules,
        )

    def collect_requested_facts(
        self,
        workspace: Path,
        facts: ReconFacts,
        requests: list[FactRequest],
    ) -> ReconFacts:
        """Satisfy structured follow-up requests.

        The first iteration only demonstrates the protocol shape. Each supported
        request kind is handled conservatively and returns tiny summaries. Future
        versions can add budget-aware readers, directory expansion, manifest
        parsing and richer summarization.
        """

        sampled_files = list(facts.sampled_files)
        for request in requests:
            if request.kind is FactRequestKind.READ_FILE_SUMMARY:
                target = workspace / request.target
                if target.is_file():
                    sampled_files.append(
                        SampledFile(
                            path=target.relative_to(workspace),
                            summary=self._summarize_file(target, request.budget),
                        )
                    )

        return ReconFacts(
            workspace=facts.workspace,
            scm=facts.scm,
            documentation=facts.documentation,
            structure=facts.structure,
            file_type_counts=facts.file_type_counts,
            ecosystem_candidates=facts.ecosystem_candidates,
            sampled_files=sampled_files,
            python_modules=facts.python_modules,
        )

    def iter_markdown_files(self, workspace: Path) -> list[Path]:
        """Return markdown files relative to the workspace."""

        return sorted(
            path.relative_to(workspace)
            for path in workspace.rglob("*.md")
            if not self._is_ignored(path)
        )

    def iter_python_modules(self, workspace: Path) -> list[Path]:
        """Return Python source files relative to the workspace."""

        return sorted(
            path.relative_to(workspace)
            for path in workspace.rglob("*.py")
            if not self._is_ignored(path)
        )

    def collect_scm_facts(self, workspace: Path) -> ScmFacts:
        """Collect repository facts from the SCM adapter layer.

        This currently captures only the repository type, remote URL and common
        ignore-file candidates. Future implementations can enrich it with tracked
        file sets, ignore rule parsing and branch/head metadata.
        """

        scm = SCM.detect(workspace)
        if scm is None:
            return ScmFacts(ignore_sources=self._discover_ignore_sources(workspace))

        try:
            repo_url = scm.repo()
        except SCMError:
            repo_url = None

        return ScmFacts(
            kind=scm.__class__.__name__.lower(),
            repo_url=repo_url,
            ignore_sources=self._discover_ignore_sources(workspace),
        )

    def collect_structure_facts(self, workspace: Path) -> StructureFacts:
        """Infer likely source/test/resource/script directories."""

        source_directories: list[Path] = []
        test_directories: list[Path] = []
        resource_directories: list[Path] = []
        script_directories: list[Path] = []

        for path in workspace.iterdir():
            if not path.is_dir() or path.name in _IGNORED_PARTS:
                continue

            rel = path.relative_to(workspace)
            lowered = path.name.lower()
            if lowered in {"src", "source", "app", "lib"}:
                source_directories.append(rel)
            if "test" in lowered:
                test_directories.append(rel)
            if lowered in {"assets", "resources", "resource", "static"}:
                resource_directories.append(rel)
            if lowered in {"scripts", "script", "tools", "bin"}:
                script_directories.append(rel)

        return StructureFacts(
            source_directories=sorted(source_directories),
            test_directories=sorted(test_directories),
            resource_directories=sorted(resource_directories),
            script_directories=sorted(script_directories),
        )

    def detect_ecosystem_candidates(self, workspace: Path) -> list[EcosystemCandidate]:
        """Detect ecosystem candidates from high-signal manifest files."""

        candidates: list[EcosystemCandidate] = []
        for name, markers in _ECOSYSTEM_MARKERS.items():
            evidence = [
                path.relative_to(workspace)
                for marker in markers
                for path in workspace.rglob(marker)
                if path.is_file() and not self._is_ignored(path)
            ]
            if evidence:
                candidates.append(EcosystemCandidate(name=name, evidence=sorted(set(evidence))))
        return candidates

    def _discover_ignore_sources(self, workspace: Path) -> list[Path]:
        candidates = [
            workspace / ".gitignore",
            workspace / ".hgignore",
            workspace / ".svnignore",
        ]
        return [
            path.relative_to(workspace)
            for path in candidates
            if path.exists()
        ]

    def _summarize_file(self, path: Path, budget: int) -> str:
        """Return a tiny deterministic summary for the requested file.

        This placeholder does not attempt semantic understanding. A future
        version can add syntax-aware summarization, token budgeting and content
        truncation policies tailored to each request kind.
        """

        line_budget = max(1, budget) * 5
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        snippet = lines[:line_budget]
        return "\n".join(snippet).strip()

    def _is_ignored(self, path: Path) -> bool:
        return any(part in _IGNORED_PARTS for part in path.parts)
