---
id: deprecation-and-migration
kind: skill
title: Deprecation + Migration
description: "Code is liability. Less code = less to maintain. Two-step removal. Reversible migrations. Schema vs data migrations separate."
applies_when:
  - removing or replacing existing system
  - schema change
  - sunsetting a feature
  - cleaning up dead code
agents:
  claude: { kind: skill }
  cursor: { kind: skill }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Deprecation + Migration

Code is liability. Each line costs to maintain, test, debug. Remove when possible.

## Mindset

Before adding: can existing code solve it? Can we remove instead?

## Two-Step Column / Field Removal

```text
Step 1: Stop writing + reading the column in code. Deploy. Soak.
Step 2: Drop the column in a migration. Deploy.
```

Never drop a column code still references. Never deploy code referencing a column that's already gone.

## Reversible Migrations

`up` + `down`. Or single `change` only when truly reversible. Backfills get their own data migration, separate from schema.

```python
def up():
    op.add_column("messages", sa.Column("edited_at", sa.DateTime, nullable=True))
    op.create_index("ix_messages_edited_at", "messages", ["edited_at"])

def down():
    op.drop_index("ix_messages_edited_at")
    op.drop_column("messages", "edited_at")
```

## Data Migration ≠ Schema Migration

Different files. Different review focus. Different risk profile.

```python
def up():
    op.execute(
        "UPDATE users SET display_name = first || ' ' || last "
        "WHERE display_name IS NULL"
    )
```

Idempotent. Safe to retry. Backfill in batches if table is large.

## Deprecation Markers

```python
import warnings

def send_message(room: Room, content: str) -> Message:
    warnings.warn(
        "send_message is deprecated; use create_message(room, author, attrs). "
        "Removed in v2.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return create_message(room, current_user(), MessageAttrs(content=content))
```

Pin removal version in the warning. Open a tracking issue with the cutoff date.

## Zombie Code Removal

Audit periodically:

- Unused functions (`vulture`, `pyflakes`, `cargo-udeps`, `tsc --noUnusedLocals`).
- Commented-out blocks (delete; git remembers).
- Feature-flagged code where the flag is permanent.
- Modules with no callers.

## GOOD

```text
DEAD CODE FOUND:
- legacy.format_date in src/helpers.py — replaced 3 months ago.
- src/dashboards/old_dashboard.py — no route reference.
→ Safe to remove? (proposed PR #421)
```

## BAD

```python
# OLD VERSION — keep for reference
# def calculate(...):
#     ...
def calculate(...):
    ...
```

Two versions, one commented. Reader confused. Git already remembers.

## Red Flags

- Column dropped while code still reads / writes it.
- Schema change + data backfill in the same migration.
- Migration with no `down()` and no justification.
- Deprecated call without a removal version pinned.
- Dead code accumulating with no removal cadence.
