# ADR-0001: Single-source Markdown with frontmatter

Date: 2026-05-07

## Context

The same coding-style guidance has to land in multiple agents (Claude Code, Cursor, Codex, OpenClaw, OpenCode, Pi, Vibe), each of which has its own native file format and discovery rules. Duplicating the content per agent makes drift inevitable: a fix to the TDD skill in Claude lands days or weeks later in Cursor, and never lands in Codex. The other obvious option — writing in one agent's native format and converting from there — privileges whichever agent I pick as the source and leaves the others second-class.

I also need to keep these documents short, structured, and lintable. Free-form Markdown without conventions invites inconsistencies in heading levels, missing examples, and silent breakage.

## Decision

A single source of truth lives in `source/`, with three subdirectories (`rules/`, `skills/`, `commands/`). Every file is Markdown with YAML frontmatter that carries enough metadata for any per-agent generator to translate the file into that agent's native format:

- `id`, `kind`, `title`, `description` for identity and discovery.
- `applies_when` and `always_apply` for trigger semantics.
- `agents:` mapping selects which agents receive the file and lets each agent override per-agent specifics (Cursor `glob`, Codex section, Claude skill kind, etc.).

Per-agent adapters under `scripts/adapters/` consume this single source and emit the native layout for each agent. Adapters never read the others' outputs; the source file is the only contract.

A mechanical lint (`scripts/lint_source.py`) enforces frontmatter completeness, file size limits, the presence of GOOD and BAD example blocks, and cross-reference validity.

## Consequences

**Positive.** One file to edit per change. Drift between agents impossible by construction. Adding a new agent is "implement an adapter", not "rewrite all the rules". The lint catches structural problems before they reach the agents. Frontmatter doubles as machine-readable metadata for tooling.

**Negative.** Anyone editing `source/` learns a small frontmatter schema. Per-agent quirks (Cursor's globs, Claude's nested skill directories) are encoded in adapter logic, not in the source files; that complexity is now spread across `scripts/adapters/*.py`. PyYAML is a hard dependency; the installer pip-installs it on first run.

**Mitigations.** The shape preview in the plan and the README's "Authoring" section make the schema easy to copy. The adapters are small (under 100 lines each) and thoroughly snapshot-tested.
