from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastai.commands.recon.collectors import WorkspaceReconCollector
from fastai.commands.recon.models import FactRequest, ReconFacts, ReconRunResult
from fastai.commands.recon.protocol import (
    NullReconAnalyzer,
    NullReconPlanner,
    ReconAnalyzer,
    ReconPlanner,
)
from fastai.commands.recon.renderer import OverviewRenderer


@dataclass(slots=True, frozen=True)
class ReconBudget:
    """Execution limits for a single synchronous recon run."""

    max_rounds: int = 1
    max_requests_per_round: int = 5


class ReconOrchestrator:
    """Coordinate the recon collection, planning and rendering loop."""

    def __init__(
        self,
        *,
        collector: WorkspaceReconCollector | None = None,
        planner: ReconPlanner | None = None,
        analyzer: ReconAnalyzer | None = None,
        renderer: OverviewRenderer | None = None,
        budget: ReconBudget | None = None,
    ) -> None:
        self.collector = collector or WorkspaceReconCollector()
        self.planner = planner or NullReconPlanner()
        self.analyzer = analyzer or NullReconAnalyzer()
        self.renderer = renderer or OverviewRenderer()
        self.budget = budget or ReconBudget()

    def run(self, workspace: Path) -> ReconRunResult:
        """Run a single synchronous recon pass.

        This method intentionally wires the full phase structure now while
        keeping the inner intelligence minimal. Future versions can swap in a
        real planner/analyzer and allow multiple bounded collection rounds.

        Planned evolution of this loop:
        1. collect base facts
        2. ask the planner for bounded structured requests
        3. satisfy those requests and merge incremental facts
        4. repeat within ``ReconBudget.max_rounds``
        5. pass the final fact bundle to the analyzer

        The current version executes only one planning pass. This keeps the
        control flow visible without committing to a concrete AI runtime yet.
        """

        facts = self.collector.collect_base_facts(workspace)
        requests = self._plan_requests(facts)
        if requests:
            facts = self.collector.collect_requested_facts(workspace, facts, requests)
        analysis = self.analyzer.analyze(facts)
        overview_markdown = self.renderer.render(facts, analysis)
        return ReconRunResult(
            facts=facts,
            requests=requests,
            analysis=analysis,
            overview_markdown=overview_markdown,
        )

    def _plan_requests(self, facts: ReconFacts) -> list[FactRequest]:
        requests = self.planner.plan_requests(facts)
        if len(requests) > self.budget.max_requests_per_round:
            return requests[: self.budget.max_requests_per_round]
        return requests
