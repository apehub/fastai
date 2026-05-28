from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastai.recon.collectors import WorkspaceReconCollector
from fastai.recon.glance import Glance
from fastai.recon.models import FactRequest, ReconFacts, ReconRunResult
from fastai.recon.protocol import (
    NullReconAnalyzer,
    NullReconPlanner,
    ReconAnalyzer,
    ReconPlanner,
)
from fastai.recon.renderer import OverviewRenderer


@dataclass(slots=True, frozen=True)
class ReconBudget:
    """Execution limits for a single synchronous recon run."""

    max_rounds: int = 1
    max_requests_per_round: int = 5


class ReconOrchestrator:
    """Coordinate the recon collection, planning and rendering loop."""

    @staticmethod
    def run(workspace: Path) -> ReconRunResult:
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

        # get the glance facts
        glance = Glance.run(workspace)
        # TODO: request AI agent to analyze the workspace by glance facts

    def _plan_requests(self, facts: ReconFacts) -> list[FactRequest]:
        requests = self.planner.plan_requests(facts)
        if len(requests) > self.budget.max_requests_per_round:
            return requests[: self.budget.max_requests_per_round]
        return requests
