# System Overview

## Project Summary

- Workspace: `/home/aceyin/Workspace/fastai`
- Total files: 50
- Markdown files: 9
- Python modules: 32

## Documentation

- `.pytest_cache/README.md`
- `FastAI_Product_Overview.md`
- `README.md`
- `docs/README.zh-CN.md`
- `docs/design/commands.md`
- `docs/superpowers/plans/2026-05-26-fastai-rename.md`
- `docs/superpowers/specs/2026-05-26-fastai-rename-design.md`
- `docs/superpowers/specs/2026-05-26-quikai-pyproject-metadata-design.md`
- `docs/system-overview.md`

## Python Modules

- `fastai/__init__.py`
- `fastai/__main__.py`
- `fastai/agents/__init__.py`
- `fastai/agents/flow.py`
- `fastai/agents/flows/__init__.py`
- `fastai/agents/flows/recon.py`
- `fastai/agents/runtimes.py`
- `fastai/commands/__init__.py`
- `fastai/commands/base.py`
- `fastai/commands/recon.py`
- `fastai/fastai.py`
- `fastai/recon/__init__.py`
- `fastai/recon/collectors.py`
- `fastai/recon/glance.py`
- `fastai/recon/models.py`
- `fastai/recon/orchestrator.py`
- `fastai/recon/protocol.py`
- `fastai/recon/renderer.py`
- `fastai/tools/SCM.py`
- `fastai/utils/__init__.py`
- `fastai/utils/strs.py`
- `tests/__init__.py`
- `tests/test_agent_runtime.py`
- `tests/test_cli_commands.py`
- `tests/test_cli_entrypoint.py`
- `tests/test_command_discovery.py`
- `tests/test_glance.py`
- `tests/test_recon_command.py`
- `tests/test_recon_flow.py`
- `tests/test_recon_pipeline.py`
- `tests/test_scm.py`
- `tests/test_strs_utils.py`

## Analysis

- Framework summary: Hatchling-built Python package (requires-python >=3.11) with a single runtime dependency on Typer. Entry point fastai maps to fastai.__main__:main, which builds a Typer app and auto-registers commands discovered from fastai.commands via BaseCommand and a @Command decorator registry. Test stack uses pytest (optional extra). The only shipped CLI command today is fastai recon: WorkspaceReconCollector and Glance gather deterministic workspace facts (tree, file types, ecosystem markers, markdown paths, SCM via SCM.py); ReconOrchestrator runs ReconFlow to invoke a local AgentRuntime subprocess (Cursor, Codex, Claude, Copilot, OpenCode, Gemini, Hermes) and parse structured JSON; OverviewRenderer writes docs/system-overview.md, with NullReconAnalyzer fallback when no agent CLI is on PATH.
- Domain summary: FastAI helps teams upgrade ordinary software repositories into AI-ready projects and keep AI collaboration infrastructure (rules, memory, workflows, spec/doc alignment) current over time. Product positioning is scaffolding and maintenance, not an AI IDE or an AI engineering team framework. Documented roadmap includes fastai init (AI-ready scaffold), serve/status/logs/stop (user-level daemon), and alignment checks; v0.1.0 alpha primarily implements project reconnaissance (fastai recon) as the executable capability.
