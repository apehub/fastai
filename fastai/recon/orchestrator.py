from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from collections.abc import Callable
from typing import TYPE_CHECKING

from fastai.recon.collectors import WorkspaceReconCollector
from fastai.recon.models import ReconRunResult
from fastai.recon.protocol import NullReconAnalyzer
from fastai.recon.renderer import OverviewRenderer

if TYPE_CHECKING:
    from fastai.agents.runtimes import AgentRuntime


logger = logging.getLogger(__name__)
ProgressReporter = Callable[[str], None]


@dataclass(slots=True, frozen=True)
class ReconBudget:
    """Execution limits for a single synchronous recon run."""

    max_rounds: int = 1
    max_requests_per_round: int = 5


class ReconOrchestrator:
    """Coordinate recon fact collection, agent analysis and rendering."""

    @staticmethod
    def run(
        workspace: Path,
        runtime: AgentRuntime | None = None,
        progress: ProgressReporter | None = None,
    ) -> ReconRunResult:
        """Run a single synchronous recon pass.

        Steps:
        1. collect deterministic base facts from the workspace
        2. analyze them with an agent runtime (the recon call flow)
        3. render the system overview

        When no agent runtime is supplied and none is installed on the system,
        the run degrades to a deterministic placeholder analysis so that
        ``fastai recon`` always produces an overview.
        """

        # Imported lazily to avoid an import cycle: the agents package depends
        # on fastai.recon.models, and fastai.recon.__init__ imports this module.
        from fastai.agents.flows.recon import ReconFlow
        from fastai.agents.runtimes import AgentRuntime

        logger.info("Starting recon run workspace=%s", workspace)
        _report_progress(progress, "Collecting workspace facts")
        facts = WorkspaceReconCollector().collect_base_facts(workspace)
        logger.info(
            "Collected recon facts total_files=%s markdown_files=%s python_modules=%s ecosystems=%s",
            facts.workspace.total_files,
            len(facts.documentation.markdown_files),
            len(facts.python_modules),
            len(facts.ecosystem_candidates),
        )

        if runtime is None:
            _report_progress(progress, "Detecting local agent runtime")
            available = AgentRuntime.detect()
            runtime = available[0] if available else None
            logger.info(
                "Detected agent runtimes count=%s selected=%s",
                len(available),
                runtime.__class__.__name__ if runtime is not None else None,
            )
        else:
            logger.info("Using supplied agent runtime runtime=%s", runtime.__class__.__name__)

        if runtime is not None:
            _report_progress(progress, f"Analyzing project context, agent runtime={runtime.__class__.__name__}")
            analysis = ReconFlow(runtime, workspace=workspace).run(facts)
        else:
            logger.info("No agent runtime available; using null recon analyzer")
            _report_progress(progress, "Analyzing project context")
            analysis = NullReconAnalyzer().analyze(facts)

        _report_progress(progress, "Rendering system overview")
        overview = OverviewRenderer().render(facts, analysis)
        logger.info("Rendered recon overview chars=%s", len(overview))
        return ReconRunResult(
            facts=facts,
            requests=[],
            analysis=analysis,
            overview_markdown=overview,
        )


def _report_progress(progress: ProgressReporter | None, message: str) -> None:
    if progress is not None:
        progress(message)
