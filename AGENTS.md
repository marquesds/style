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

The **"Load when"** column must describe the *situation* that fires the skill —
what the user is doing or requesting — not the skill's methodology, techniques, or
content. An agent pattern-matches the request against this text; if the text reads
like a technique list, the skill never fires.

| Good trigger (situational) | Bad trigger (technique list) |
|---|---|
| "adding rate limiting to an endpoint" | "token bucket vs sliding window; 429 + Retry-After" |
| "implementing user authentication" | "argon2id / bcrypt; salting; constant-time verify" |
| "writing any new code; adding behavior" | "RED → GREEN → REFACTOR; Testing Trophy" |

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

### 5. Prefer `.mdc` over `.md` for Cursor rule targets

Files emitted into `.cursor/rules/*.mdc` must use the `.mdc` extension so frontmatter
loads correctly. The canonical `source/*.md` files stay `.md`; the build pipeline
produces the `.mdc` outputs. When authoring directly under `.cursor/rules/`, pick
`.mdc`. Cursor skills use `.cursor/skills/<id>/SKILL.md` — see Rule 6 below.

---

## 6. Agent native conventions (cheat sheet)

Each adapter under `scripts/adapters/` must emit the agent's native format. When
adding or modifying an adapter, match the column for that agent below.

| Agent | Rules | Skills | Commands |
|-------|-------|--------|----------|
| claude | merged into `<root>/.claude/CLAUDE.md` (managed section) | `<root>/.claude/skills/<id>/SKILL.md` (frontmatter: `name`, `description`) | `<root>/.claude/commands/<id>.md` (plain markdown) |
| cursor | `<root>/.cursor/rules/<id>.mdc` (frontmatter: `description`, `globs`, `alwaysApply`) | `<root>/.cursor/skills/<id>/SKILL.md` (frontmatter: `name`, `description`) | `<root>/.cursor/commands/<id>.md` (plain markdown) |
| codex | merged into `<root>/.codex/AGENTS.md` `## Rules` | merged `## Skills` | merged `## Commands` |
| goose | merged into `<root>/.config/goose/AGENTS.md` | merged | merged |
| openclaw | merged into `<root>/.openclaw/workspace/AGENTS.md` | merged | merged |
| opencode | merged into `<root>/.config/opencode/AGENTS.md` | `<root>/.config/opencode/skills/<id>/SKILL.md` | `<root>/.config/opencode/commands/<id>.md` (frontmatter: `description`) |
| pi | merged into `<root>/.pi/agent/AGENTS.md` | merged | merged |
| vibe | `<root>/.vibe/rules/<id>.md` | `<root>/.vibe/skills/<id>.md` | `<root>/.vibe/commands/<id>.md` |

Native-skills agents (claude, cursor, opencode) get one frontmatter-bearing file per
skill in a dedicated directory. Merged-AGENTS.md agents (codex, goose, openclaw, pi)
collapse everything into a single managed block — no native skill split.

### Prune coverage

Every adapter must implement `prune_all(target_root, dry_run) -> AdapterReport`:

- **Per-file installs** (cursor skills/rules/commands, claude skills/commands, opencode
  skills/commands, vibe rules/skills/commands): delete files containing the
  `<!-- style-harness:managed -->` marker. Try to remove emptied parent dirs.
- **Merged AGENTS.md** (codex, goose, openclaw, pi, claude CLAUDE.md, opencode AGENTS.md):
  strip the `<!-- BEGIN style-harness --> … <!-- END style-harness -->` block. Delete the
  file only if nothing user-authored remains.

`prune_all` must be idempotent. `--dry-run` must list ops without writing.

---

For everything else, follow the rules and skills installed by this harness — they apply
to this repo too.
