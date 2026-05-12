# ADR-0009 — Route codex and pi adapters to their native config directories

**Status:** Accepted  
**Date:** 2026-05-12

## Context

`./install.sh` (default `--target-root=$HOME`) was writing `~/AGENTS.md` (~260 KB)
because both the Codex and Pi adapters used `target_root / "AGENTS.md"` as their
output path.

Cursor discovers any `AGENTS.md` at `$HOME` and loads it as a global rule on every
request, duplicating the ~32 KB already delivered via `~/.cursor/rules/*.mdc`. The
net effect was roughly 65k tokens of redundant rule content injected per turn before
the user typed anything.

Goose (`.config/goose/`), OpenClaw (`.openclaw/workspace/`), and OpenCode
(`.config/opencode/`) already route into agent-owned subdirectories and were
unaffected.

## Decision

Route each agent to its documented native config directory:

| Agent | New path |
|-------|----------|
| Codex CLI | `<root>/.codex/AGENTS.md` (`CODEX_HOME`) |
| pi.dev | `<root>/.pi/agent/AGENTS.md` (`PI_CODING_AGENT_DIR`) |

Add a one-shot legacy-cleanup pass: on the next `write_all` or `prune_all` run, the
managed block is stripped from `<root>/AGENTS.md` via the existing
`strip_managed_section` helper. User-authored content outside the managed block is
preserved. The cleanup is idempotent.

## Consequences

- Cursor no longer double-loads the harness content from `~/AGENTS.md`.
- Existing users who ran a previous install get `~/AGENTS.md` cleaned automatically
  on their next install or uninstall — no manual intervention required.
- `prune_all` for both adapters now targets both the new path and the legacy
  `<root>/AGENTS.md`, making uninstall correct in either scenario.
- No CLI flag changes, no env-var support changes, no change to the merged block
  contents or structure.
