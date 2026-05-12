# ADR 0007 — Prune / uninstall path via `prune_all` + `uninstall.sh`

**Date:** 2026-05-12
**Status:** Accepted

## Context

Users who try the harness and later remove it had no supported way to reverse the
install without manually deleting files. The harness already marks ownership two ways:

- `<!-- style-harness:managed -->` at the top of per-file installs.
- `<!-- BEGIN style-harness --> … <!-- END style-harness -->` blocks in merged files.

Both markers are machine-readable, making automated removal straightforward.

## Decision

Add `prune_all(target_root, dry_run) -> AdapterReport` to the `Adapter` protocol and
implement it on every adapter:

- **Per-file adapters** (cursor, claude skills/commands, opencode skills/commands,
  vibe): `walk_managed_files` yields files whose first 10 lines contain the file
  marker; each yields a `WriteOp(action="delete")`. Empty parent dirs are removed
  after file deletion.
- **Merged-file adapters** (codex, goose, openclaw, pi, claude CLAUDE.md,
  opencode AGENTS.md): `strip_managed_section` excises the `BEGIN…END` block.
  The file is deleted only when nothing user-authored remains.

`scripts/build.py` gains a `--prune` flag that calls `adapter.prune_all` instead of
`adapter.write_all`; lint is skipped when pruning.

`uninstall.sh` wraps `python -m scripts.build --prune "$@"`, symmetric with
`install.sh`.

## Safety invariants

1. Prune touches only files containing one of the two harness markers.
2. Adjacent user files in the same directory are never deleted.
3. Merged AGENTS.md user content outside the managed block is preserved.
4. Prune is idempotent — running twice is a no-op on the second run.
5. `--dry-run` lists every deletion without performing it.

## Consequences

- Users can fully reverse the install: `./uninstall.sh` or
  `./uninstall.sh --agent cursor`.
- `--dry-run` gives a safe preview before destructive ops.
- Each adapter must maintain `prune_all` coverage when new emission targets are added.
