# ADR-0004: Managed-section markers for shared agent files

Date: 2026-05-07

## Context

Some agent files this harness writes into are owned by the agent or by the user, not by the harness alone. Examples:

- `~/.claude/CLAUDE.md` — the user's primary Claude memory file. They edit it by hand. I need to inject the managed rules without clobbering whatever else lives there.
- `<repo>/AGENTS.md` — Codex's per-project guidance file. The user (or other tools) may add their own sections.

Per-file outputs (Cursor `.mdc` files, Claude `SKILL.md` files inside `~/.claude/skills/<id>/`) are simpler — the harness owns each file end to end, so a fresh write is always correct. Shared files are the harder case.

## Decision

Shared files use BEGIN/END HTML-comment markers to delimit the managed region:

```text
<!-- BEGIN style-harness -->
... content this repo regenerates on every build ...
<!-- END style-harness -->
```

`scripts/adapters/base.py:replace_managed_section` replaces only the content between markers and leaves everything else untouched. On first run (no markers present), it appends the managed block at the end of the file.

Per-file outputs use a different convention: a single `<!-- style-harness:managed -->` HTML comment near the top of the file, purely as a tombstone so a future contributor knows the file is generated. Per-file writes are full overwrites; the marker is informational, not parsed.

## Consequences

**Positive.** Re-running the installer is idempotent for shared files. User-authored content above and below the markers survives indefinitely. The markers are HTML comments, so they render as nothing in any Markdown viewer and don't pollute the visible content. A grep for `style-harness` finds every file touched by this repo, simplifying uninstall.

**Negative.** Users who want to edit the managed block this harness writes will see their edits reverted on the next install. They have to copy the content out of the managed block to make it stick. The marker text becomes a load-bearing string; renaming it requires a migration.

**Mitigations.** The README documents the markers. The marker prefix `style-harness` is unique enough that conflicts with other tools are unlikely. An uninstall command (future work) can use the same markers to remove only what this repo added.
