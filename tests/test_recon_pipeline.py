"""Tests for the recon pipeline skeleton."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from fastai.recon.collectors import WorkspaceReconCollector
from fastai.recon.models import FactRequest, FactRequestKind, ReconFacts
from fastai.recon.orchestrator import ReconOrchestrator
from fastai.recon.protocol import (
    NullReconAnalyzer,
    NullReconPlanner,
    ReconAnalyzer,
    ReconPlanner,
)
from fastai.recon.renderer import OverviewRenderer

REPO_ROOT = Path(__file__).resolve().parents[1]


class ReconPipelineTests(unittest.TestCase):
    def test_recon_package_reexports_pipeline_modules(self):
        from fastai.recon.collectors import WorkspaceReconCollector as Collector
        from fastai.recon.models import ReconFacts as Facts
        from fastai.recon.orchestrator import ReconOrchestrator as Orchestrator
        from fastai.recon.protocol import ReconPlanner as Planner
        from fastai.recon.renderer import OverviewRenderer as Renderer

        self.assertIs(Collector, WorkspaceReconCollector)
        self.assertIs(Facts, ReconFacts)
        self.assertIs(Orchestrator, ReconOrchestrator)
        self.assertIsNotNone(Planner)
        self.assertIsNotNone(Renderer)

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fastai-recon-pipeline-"))
        self.workspace = self.temp_dir / "workspace"
        shutil.copytree(
            REPO_ROOT,
            self.workspace,
            ignore=shutil.ignore_patterns(".git", ".worktrees", "__pycache__"),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_base_collector_returns_recon_facts(self):
        collector = WorkspaceReconCollector()

        facts = collector.collect_base_facts(self.workspace)

        self.assertIsInstance(facts, ReconFacts)
        self.assertIn(Path("FastAI_Product_Overview.md"), facts.documentation.markdown_files)
        self.assertIn(Path("fastai/fastai.py"), facts.python_modules)
        self.assertGreater(facts.workspace.total_files, 0)
        self.assertIn(".py", facts.file_type_counts)

    def test_orchestrator_runs_pipeline_with_stub_components(self):
        orchestrator = ReconOrchestrator(
            collector=WorkspaceReconCollector(),
            planner=NullReconPlanner(),
            analyzer=NullReconAnalyzer(),
            renderer=OverviewRenderer(),
        )

        result = orchestrator.run(self.workspace)

        self.assertEqual([], result.requests)
        self.assertIn("# System Overview", result.overview_markdown)
        self.assertIn("## Documentation", result.overview_markdown)
        self.assertIn("## Python Modules", result.overview_markdown)

    def test_collector_accepts_structured_fact_requests(self):
        collector = WorkspaceReconCollector()
        facts = collector.collect_base_facts(self.workspace)
        requests = [
            FactRequest(
                kind=FactRequestKind.READ_FILE_SUMMARY,
                target="README.md",
                reason="Need a quick project summary.",
                budget=1,
            )
        ]

        updated = collector.collect_requested_facts(self.workspace, facts, requests)

        self.assertEqual(1, len(updated.sampled_files))
        self.assertEqual(Path("README.md"), updated.sampled_files[0].path)

    def test_provider_agnostic_protocol_exposes_planner_and_analyzer_interfaces(self):
        self.assertTrue(issubclass(NullReconPlanner, ReconPlanner))
        self.assertTrue(issubclass(NullReconAnalyzer, ReconAnalyzer))


if __name__ == "__main__":
    unittest.main()
