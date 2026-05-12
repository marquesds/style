# AGENTS.md — Contributor Rules for This Repo

This file tells any AI coding agent that opens the *style harness itself* what the
contributor rules are. Downstream projects get their own `AGENTS.md` via the harness;
this one governs work on the harness.

## Rules

### 1. Update the skills catalog when adding a new skill

Adding a file under `source/skills/` requires a matching row in
`source/rules/skills-catalog.md` in the same commit. The lint guard in
`scripts/lint_source.py` (`lint_skills_catalog`) will fail the build otherwise —
`python -m scripts.lint_source` must exit 0.

### 2. Update docs when behavior or surface changes

`README.md`, `docs/style-overview.md`, `docs/contributing.md`, and any relevant ADR
under `docs/adr/` must reflect the change. Stale docs are worse than absent docs
(rule:documentation).

### 3. Examples are Python by default

Use Python for `## GOOD` and `## BAD` blocks unless the skill's topic is intrinsically
another language or format — for example, `bindings-as-thin-wrappers` (Rust FFI),
`xss-and-csp` (HTML), `task-runner-conventions` (Makefiles),
`design-aesthetic-commitment` (CSS). See `source/rules/skills-catalog.md` for the
language translation note that agents should apply at runtime.

### 4. Prefer merging or upgrading existing rules/skills/commands over creating new ones

Before authoring `source/{rules,skills,commands}/<new-id>.md`, search the catalog
for an existing skill whose scope can absorb the change. Create a new file only when
the topic is genuinely distinct — `refactoring` is distinct from `code-simplification`
because it covers named transformations and Feathers' legacy-code seam techniques that
`code-simplification` deliberately excludes.

### 5. Prefer `.mdc` over `.md` for Cursor targets

Files emitted into `.cursor/rules/*.mdc` must use the `.mdc` extension so frontmatter
loads correctly. The canonical `source/*.md` files stay `.md`; the build pipeline
produces the `.mdc` outputs. When authoring directly under `.cursor/rules/`, pick
`.mdc`.

---

For everything else, follow the rules and skills installed by this harness — they apply
to this repo too.
