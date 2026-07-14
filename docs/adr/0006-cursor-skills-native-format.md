# ADR 0006 — Cursor skills use native `.cursor/skills/<id>/SKILL.md` layout

**Date:** 2026-05-12
**Status:** Accepted

## Context

Cursor's native layout distinguishes rules from skills:

- Rules: `~/.cursor/rules/<id>.mdc` with frontmatter (`description`, `globs`, `alwaysApply`).
- Skills: `~/.cursor/skills/<id>/SKILL.md` with frontmatter (`name`, `description`).

The `CursorAdapter` previously funnelled both kinds through `_mdc_op`, writing every
skill as `.cursor/rules/<id>.mdc` with `alwaysApply: false`. This violated Cursor's
convention and meant skills could not be loaded via the skills panel.

## Decision

Split `CursorAdapter.write_all` into three branches:

1. `kind == "rule"` → `_mdc_op` (unchanged, emits `.cursor/rules/<id>.mdc`).
2. `kind == "skill"` → new `_skill_op` (emits `.cursor/skills/<id>/SKILL.md` with
   `name` + double-quoted `description` frontmatter, matching Claude's skill format).
3. `kind == "command"` → `_command_op` (unchanged).

All 57 `source/skills/*.md` files have their `cursor:` agent block updated from
`{ kind: rule }` to `{ kind: skill }` to reflect the new intent.

## Consequences

- Skills appear in Cursor's native skill panel and are loaded on demand by description.
- Current adapter behavior folds `applies_when` into the emitted `description` and
  emits Cursor `paths` when a skill declares `agents.cursor.glob`.
- Existing installs retain stale `.cursor/rules/<id>.mdc` skill files until
  `./uninstall.sh --agent cursor` (or a manual sweep) cleans them up.
- The `CursorAdapter` test fixture is updated; `test_cursor_writes_skill_dir` asserts
  the new layout.
