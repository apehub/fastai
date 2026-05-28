from __future__ import annotations

from abc import ABC, abstractmethod

from fastai.recon.models import FactRequest, ReconAnalysis, ReconFacts


class ReconPlanner(ABC):
    """Plan which additional facts should be collected next.

    Real implementations will later translate ``ReconFacts`` into a structured
    prompt for an LLM/provider and parse the provider response into
    ``FactRequest`` objects. The first iteration keeps this interface abstract
    and provider-agnostic so the orchestration loop can be designed and tested
    before a concrete model SDK is introduced.
    """

    @abstractmethod
    def plan_requests(self, facts: ReconFacts) -> list[FactRequest]:
        """Return structured follow-up requests for additional facts."""


class ReconAnalyzer(ABC):
    """Turn collected facts into a structured project analysis.

    A real implementation will eventually call an AI provider with the final
    fact bundle. For now, the interface exists so the command and orchestrator
    can be wired without committing to any provider/runtime design.
    """

    @abstractmethod
    def analyze(self, facts: ReconFacts) -> ReconAnalysis:
        """Return the structured analysis for a recon run."""


class NullReconPlanner(ReconPlanner):
    """A placeholder planner that asks for nothing.

    This is intentionally minimal. Later versions will inspect the initial facts
    and emit bounded, schema-constrained requests such as manifest summaries or
    markdown summaries.
    """

    def plan_requests(self, facts: ReconFacts) -> list[FactRequest]:
        return []


class NullReconAnalyzer(ReconAnalyzer):
    """A placeholder analyzer that emits a tiny deterministic analysis."""

    def analyze(self, facts: ReconFacts) -> ReconAnalysis:
        framework_summary = (
            "Initial skeleton analyzer. A future AI-backed analyzer will infer "
            "frameworks and architecture from collected facts."
        )
        domain_summary = (
            "Initial skeleton analyzer. A future AI-backed analyzer will infer "
            "the project domain from documentation and source structure."
        )
        return ReconAnalysis(
            framework_summary=framework_summary,
            domain_summary=domain_summary,
        )
