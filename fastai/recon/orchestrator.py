from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from fastai.recon.collectors import WorkspaceReconCollector
from fastai.recon.models import ReconRunResult
from fastai.recon.protocol import NullReconAnalyzer
from fastai.recon.renderer import OverviewRenderer

if TYPE_CHECKING:
    from fastai.agents.runtimes import AgentRuntime


@dataclass(slots=True, frozen=True)
class ReconBudget:
    """Execution limits for a single synchronous recon run."""

    max_rounds: int = 1
    max_requests_per_round: int = 5


class ReconOrchestrator:
    """Coordinate recon fact collection, agent analysis and rendering."""

    @staticmethod
    def run(workspace: Path, runtime: AgentRuntime | None = None) -> ReconRunResult:
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

        facts = WorkspaceReconCollector().collect_base_facts(workspace)

        if runtime is None:
            available = AgentRuntime.detect()
            runtime = available[0] if available else None

        if runtime is not None:
            analysis = ReconFlow(runtime, workspace=workspace).run(facts)
        else:
            analysis = NullReconAnalyzer().analyze(facts)

        overview = OverviewRenderer().render(facts, analysis)
        return ReconRunResult(
            facts=facts,
            requests=[],
            analysis=analysis,
            overview_markdown=overview,
        )
