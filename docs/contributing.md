# Contributing

This repo is my single source of truth that compiles into per-agent native files. Editing anything other than `source/`, `scripts/`, or `docs/` is rarely the right move.

## Adding or editing a rule, skill, or command

1. Drop a Markdown file under the appropriate directory: `source/rules/<id>.md`, `source/skills/<id>.md`, or `source/commands/<id>.md`.
2. Use the same frontmatter shape as any neighboring file. Required fields: `id`, `kind`, `title`, `description`, `agents`. Skills also require `applies_when`; the adapter folds it into the emitted native skill `description` as `Use when: ...` so Claude, Codex, and Cursor can discover the skill. Optional: `always_apply`, `globs`. Skills may also declare `do_not_use_when` (negative routing hints), `related_skills` (ids to load alongside), `conflicts_with` (ids that should not load together), and `verification_prompts` (offline routing assertions: list of `{prompt, should_load}`).
3. Write the body in concise technical prose: brief, direct, and low-filler, but use normal grammar whenever it improves clarity. Code examples stay in normal style.
4. Include a `## GOOD` and a `## BAD` example block. The lint script enforces this for rules and skills.
5. Keep the file under 200 lines and any code example function under 10 body lines.
6. When adding a new skill, also add a row to `source/rules/skills-catalog.md` in the same commit. The lint guard (`lint_skills_catalog`) will fail the build if the catalog drifts.
7. When changing routing wording (catalog entries, descriptions, `applies_when`, `do_not_use_when`), add or update cases in `source/evals/skill-routing.yml`. Each case lists a prompt with `load` and `do_not_load` skill ids. The linter validates that referenced ids exist; the file is a static fixture (no LLM is executed).

## Multi-file skill bundles

A skill that needs reference material beyond one file is a bundle: a directory
`source/skills/<id>/` holding `SKILL.md` (the router, normal skill frontmatter and
GOOD/BAD blocks) plus auxiliary `*.md` reference files alongside it. The skill `id`
must match the directory name. Auxiliary files are plain markdown: no frontmatter,
at most 200 lines each, python example defs at most 10 body lines, and lowercase
hyphenated file stems. Cross-references (`skill:<id>`) inside auxiliary files are
linted like any body.

Native-skill agents (Claude, Cursor, Codex, OpenCode, Vibe) install the whole
bundle directory. Merged-AGENTS agents (Goose, OpenClaw, Pi) only inline the
`SKILL.md` body and append a note that reference files are not installed — keep the
router body self-sufficient as an index. Renaming or deleting an auxiliary file
leaves the old copy installed; run uninstall/prune and reinstall to clear stale
files.

## Editing skills

Prefer small bounded edits — add, delete, or replace a discrete block — over full rewrites. Skills are versioned artifacts; bounded patches make review and rollback cheap and keep cross-agent rendering predictable. Full rewrites are fine when a skill is genuinely off-spec, but they should be justified in the PR description.

When a proposed skill edit is rejected during review, record the rationale in `docs/skill-review-notes.md` so the same change is not re-attempted. That file is for review knowledge only — it is not installed into downstream agents.

See `AGENTS.md` at the repository root for the full set of contributor rules that apply to AI agents working on this repo.

## Validating

```bash
.venv/bin/python -m scripts.lint_source           # mechanical lint
.venv/bin/python -m scripts.build --dry-run       # preview generated outputs
.venv/bin/python -m pytest tests/ -q              # snapshot tests
.venv/bin/python -m ruff check scripts tests      # Python style
```

The lint script checks file size, frontmatter, native skill metadata (`id` shape, required `applies_when`, discovery description length/XML), the presence of GOOD/BAD blocks, code-example function length, cross-skill references, optional skill metadata (`related_skills`, `conflicts_with`, `verification_prompts`), and `source/evals/skill-routing.yml` integrity.

Before marking a harness change done, manually exercise the changed surface and record
the exact steps plus observed result. For source-content changes, a targeted
`scripts.build --dry-run --agent <agent>` preview is usually the right smoke test.

## Adding a new agent target

Implement `scripts/adapters/<agent>.py` with a class exposing `name: str` and `write_all(sources, target_root, dry_run) -> AdapterReport`. Register the adapter in `scripts/adapters/__init__.py`. Add the agent name to `ALLOWED_AGENTS` in `scripts/source.py`. Cover the new layout with a parametrized case in `tests/test_build.py`.

## Voice

Source files use concise technical prose. Keep them short, but do not force caveman grammar. README, this file, `docs/style-overview.md`, and ADRs also use normal prose so contributors have one writing style across the repo.

## ADRs

Architectural decisions about this repo itself live under `docs/adr/`, numbered sequentially. Format: title, context, decision, consequences. Keep each ADR under 200 lines.
