# Contributing

This repo is my single source of truth that compiles into per-agent native files. Editing anything other than `source/`, `scripts/`, or `docs/` is rarely the right move.

## Adding or editing a rule, skill, or command

1. Drop a Markdown file under the appropriate directory: `source/rules/<id>.md`, `source/skills/<id>.md`, or `source/commands/<id>.md`.
2. Use the same frontmatter shape as any neighboring file. Required fields: `id`, `kind`, `title`, `description`, `agents`. Optional: `applies_when`, `always_apply`, `globs`.
3. Write the body in caveman style (drop articles and filler, keep technical terms verbatim, fragments are fine). Code examples stay in normal style — caveman never applies inside code fences.
4. Include a `## GOOD` and a `## BAD` example block. The lint script enforces this for rules and skills.
5. Keep the file under 200 lines and any code example function under 10 body lines.
6. When adding a new skill, also add a row to `source/rules/skills-catalog.md` in the same commit. The lint guard (`lint_skills_catalog`) will fail the build if the catalog drifts.

See `AGENTS.md` at the repository root for the full set of contributor rules that apply to AI agents working on this repo.

## Validating

```bash
.venv/bin/python -m scripts.lint_source           # mechanical lint
.venv/bin/python -m scripts.build --dry-run       # preview generated outputs
.venv/bin/python -m pytest tests/ -q              # snapshot tests
.venv/bin/python -m ruff check scripts tests      # Python style
```

The lint script checks file size, frontmatter, the presence of GOOD/BAD blocks, code-example function length, and cross-skill references.

## Adding a new agent target

Implement `scripts/adapters/<agent>.py` with a class exposing `name: str` and `write_all(sources, target_root, dry_run) -> AdapterReport`. Register the adapter in `scripts/adapters/__init__.py`. Add the agent name to `ALLOWED_AGENTS` in `scripts/source.py`. Cover the new layout with a parametrized case in `tests/test_build.py`.

## Voice

Source files use caveman voice. README, this file, `docs/style-overview.md`, and ADRs use normal prose. Newcomers read the docs; agents read the source files. Don't mix the two.

## ADRs

Architectural decisions about this repo itself live under `docs/adr/`, numbered sequentially. Format: title, context, decision, consequences. Keep each ADR under 200 lines.
