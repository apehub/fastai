## Goal

Align the product narrative and package metadata with the clarified QuickAI positioning:
it is an AI scaffolding tool that upgrades a normal software project into an AI-ready
project, and it continues maintaining the project's AI infrastructure over time.

## Scope

Update these assets:

- `QuickAI_Product_Overview.md`
- `pyproject.toml`
- root `README.md`
- `docs/README.zh-CN.md`

Within `pyproject.toml`, update:

- `description`
- `readme`
- `keywords`
- `classifiers`

Do not add guessed information such as author names, repository URLs, or license metadata.

## Recommended Approach

Rewrite the Chinese product overview so it no longer frames QuickAI as an AI engineering
team. Instead, present it as an AI scaffolding tool for software projects:

- It rapidly initializes AI infrastructure for an ordinary project.
- It keeps that AI infrastructure current as the project evolves.
- It helps detect drift between specs, code, and documentation.

Use the English root `README.md` as the single canonical package readme for publishing,
and provide a Chinese companion version in `docs/README.zh-CN.md`. Update
`pyproject.toml` to reflect the new scaffolding and maintenance positioning.

## Rationale

The clarified product intent changes the central metaphor and value proposition. The most
important correction is to replace "AI engineering team" language with "AI scaffolding" and
"AI infrastructure maintenance" language. The English package metadata and README should
reinforce the same message, while multilingual docs should make that positioning accessible
without fragmenting the canonical package entry point.

## Validation

After editing:

- verify that `pyproject.toml` remains valid TOML
- verify that `README.md` exists and is referenced by `pyproject.toml`
- verify that the Chinese and English docs consistently describe the same product
