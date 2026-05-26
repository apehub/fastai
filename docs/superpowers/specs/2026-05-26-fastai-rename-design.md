## Goal

Rename the project from QuickAI to FastAI across product-facing copy and technical package
identifiers, so the repository, Python package, CLI command, and docs all use the same name.

## Scope

Update these assets:

- `QuickAI_Product_Overview.md` -> `FastAI_Product_Overview.md`
- `pyproject.toml`
- root `README.md`
- `docs/README.zh-CN.md`
- Python package directory `quickai/` -> `fastai/`
- tests that import or execute the package entrypoint

Update these technical identifiers:

- project name `quickai` -> `fastai`
- CLI command `quickai` -> `fastai`
- Python imports from `quickai` -> `fastai`
- class name `QuickAI` -> `FastAI`

## Recommended Approach

Apply a full rename instead of a partial branding update.

- Use `FastAI` as the display name in English and Chinese docs.
- Rename the product overview file so the documentation tree reflects the new name.
- Rename the Python package directory to `fastai` and update all imports and module
  entrypoints to match.
- Keep behavior unchanged apart from the new package and CLI names.

## Rationale

The repository directory has already been renamed to `fastai`. Leaving `quickai` in the
package name, CLI command, class name, and docs would create a split identity that gets more
expensive to fix later. Since the project is still at an early stage, a clean rename now is
lower risk than carrying compatibility shims.

## Validation

After editing:

- verify that `pyproject.toml` remains valid TOML
- verify that the entrypoint test still passes after import path changes
- verify that `python3 -m fastai --workspace .` runs successfully
- verify that docs reference `FastAI` / `fastai` consistently
