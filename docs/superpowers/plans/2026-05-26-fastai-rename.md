# FastAI Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the project from QuickAI to FastAI across docs, package metadata, Python imports, class names, and CLI entrypoints without changing runtime behavior.

**Architecture:** This change is a coordinated rename across packaging, documentation, and a small Python CLI package. The safest sequence is to lock the package entrypoint behavior with a failing test first, then rename the Python package and symbols, then update docs and metadata to the new name, and finally run verification commands against the renamed module.

**Tech Stack:** Python 3.11, standard library `unittest`, TOML package metadata, Markdown docs

---

### Task 1: Rename the Python package and entrypoint symbols

**Files:**
- Create: `/home/aceyin/Workspace/fastai/fastai/__init__.py`
- Create: `/home/aceyin/Workspace/fastai/fastai/__main__.py`
- Create: `/home/aceyin/Workspace/fastai/fastai/cli.py`
- Create: `/home/aceyin/Workspace/fastai/fastai/fastai.py`
- Modify: `/home/aceyin/Workspace/fastai/tests/test_cli_entrypoint.py`
- Modify: `/home/aceyin/Workspace/fastai/fastai/__init__.py`
- Modify: `/home/aceyin/Workspace/fastai/fastai/__main__.py`
- Modify: `/home/aceyin/Workspace/fastai/fastai/cli.py`
- Create: `/home/aceyin/Workspace/fastai/fastai/fastai.py`
- Delete: `/home/aceyin/Workspace/fastai/fastai/quickai.py`
- Test: `/home/aceyin/Workspace/fastai/tests/test_cli_entrypoint.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for the package entrypoint."""

import unittest
from unittest.mock import patch


class ModuleEntrypointTests(unittest.TestCase):
    def test_module_entrypoint_delegates_to_cli_main(self):
        with patch("fastai.cli.main", return_value=7) as fake_main:
            from fastai.__main__ import main

            self.assertEqual(main(), 7)
            fake_main.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_cli_entrypoint -v`
Expected: FAIL because the `fastai` package still imports `quickai` modules internally.

- [ ] **Step 3: Write minimal implementation**

```python
# /home/aceyin/Workspace/fastai/fastai/__init__.py
"""Public package interface for fastai."""

from fastai.fastai import FastAI

__all__ = ["FastAI"]
```

```python
# /home/aceyin/Workspace/fastai/fastai/__main__.py
"""Module entry point for the fastai package."""

from fastai.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# /home/aceyin/Workspace/fastai/fastai/cli.py
"""Command-line interface for fastai."""

import argparse
from pathlib import Path

from fastai.fastai import FastAI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bot = FastAI(workspace=Path(args.workspace).resolve())
    bot.start()
    return 0
```

```python
# /home/aceyin/Workspace/fastai/fastai/fastai.py
"""
main entry point for the fastai application
"""

from pathlib import Path


class FastAI:
    """FastAI class"""

    def __init__(self, workspace: str | Path):
        """Initialize the FastAI class"""
        self.workspace = workspace

    def start(self):
        """Start the FastAI application"""
        print(f"Starting FastAI in workspace: {self.workspace}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_cli_entrypoint -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli_entrypoint.py fastai/__init__.py fastai/__main__.py fastai/cli.py fastai/fastai.py
git rm fastai/quickai.py
git commit -m "refactor: rename quickai package to fastai"
```

### Task 2: Update package metadata and product docs

**Files:**
- Modify: `/home/aceyin/Workspace/fastai/pyproject.toml`
- Modify: `/home/aceyin/Workspace/fastai/README.md`
- Modify: `/home/aceyin/Workspace/fastai/docs/README.zh-CN.md`
- Create: `/home/aceyin/Workspace/fastai/FastAI_Product_Overview.md`
- Delete: `/home/aceyin/Workspace/fastai/QuickAI_Product_Overview.md`
- Test: `/home/aceyin/Workspace/fastai/pyproject.toml`

- [ ] **Step 1: Write the failing metadata expectations**

```python
import tomllib
from pathlib import Path


def test_pyproject_uses_fastai_identifiers():
    path = Path("/home/aceyin/Workspace/fastai/pyproject.toml")
    with path.open("rb") as f:
        data = tomllib.load(f)

    assert data["project"]["name"] == "fastai"
    assert data["project"]["scripts"]["fastai"] == "fastai.__main__:main"
```

- [ ] **Step 2: Run check to verify it fails**

Run:
```bash
python3 - <<'PY'
import tomllib
from pathlib import Path
path = Path('/home/aceyin/Workspace/fastai/pyproject.toml')
with path.open('rb') as f:
    data = tomllib.load(f)
assert data['project']['name'] == 'fastai'
assert data['project']['scripts']['fastai'] == 'fastai.__main__:main'
PY
```
Expected: FAIL because the project still uses `quickai`.

- [ ] **Step 3: Write minimal implementation**

```toml
[project]
name = "fastai"
version = "0.1.0"
description = "An AI scaffolding tool that upgrades software projects into AI-ready projects and keeps their AI infrastructure up to date."
readme = "README.md"
requires-python = ">=3.11"
keywords = ["ai", "scaffolding", "developer-tools", "documentation", "automation"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development",
    "Topic :: Software Development :: Build Tools",
    "Topic :: Software Development :: Documentation",
]
dependencies = []

[project.scripts]
fastai = "fastai.__main__:main"
```

```markdown
# FastAI

FastAI is an AI scaffolding tool for software projects.
```

```markdown
# Fast AI

Fast AI 是一个面向开发者团队的 AI 脚手架工具。
```

- [ ] **Step 4: Run check to verify it passes**

Run:
```bash
python3 - <<'PY'
import tomllib
from pathlib import Path
path = Path('/home/aceyin/Workspace/fastai/pyproject.toml')
with path.open('rb') as f:
    data = tomllib.load(f)
assert data['project']['name'] == 'fastai'
assert data['project']['scripts']['fastai'] == 'fastai.__main__:main'
print('metadata ok')
PY
```
Expected: PASS with `metadata ok`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml README.md docs/README.zh-CN.md FastAI_Product_Overview.md
git rm QuickAI_Product_Overview.md
git commit -m "docs: rename quickai product references to fastai"
```

### Task 3: Run final rename verification

**Files:**
- Modify: `/home/aceyin/Workspace/fastai/docs/superpowers/specs/2026-05-26-fastai-rename-design.md`
- Test: `/home/aceyin/Workspace/fastai/tests/test_cli_entrypoint.py`

- [ ] **Step 1: Update the design doc paths if needed**

```markdown
Update any stale file references in the rename spec so the documented paths match the final
repository state after the rename.
```

- [ ] **Step 2: Run unit test**

Run: `python3 -m unittest tests.test_cli_entrypoint -v`
Expected: PASS

- [ ] **Step 3: Run module entrypoint**

Run: `python3 -m fastai --workspace .`
Expected: PASS with output beginning `Starting FastAI in workspace:`

- [ ] **Step 4: Run metadata and doc consistency checks**

Run:
```bash
python3 - <<'PY'
import tomllib
from pathlib import Path

root = Path('/home/aceyin/Workspace/fastai')
with (root / 'pyproject.toml').open('rb') as f:
    data = tomllib.load(f)

assert data['project']['name'] == 'fastai'
assert data['project']['scripts']['fastai'] == 'fastai.__main__:main'
assert (root / 'FastAI_Product_Overview.md').exists()
assert (root / 'README.md').exists()
assert (root / 'docs' / 'README.zh-CN.md').exists()
print('rename verification ok')
PY
```
Expected: PASS with `rename verification ok`

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-05-26-fastai-rename-design.md docs/superpowers/plans/2026-05-26-fastai-rename.md
git commit -m "chore: document fastai rename plan"
```
