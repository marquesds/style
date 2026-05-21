---
id: documentation
kind: rule
title: Documentation
description: >
  Document only user-facing surfaces (HTTP, CLI, public libs) and ADRs.
  Never narrate obvious code. Stale docs worse than no docs.
applies_when:
  - any public API change
  - any architectural decision
always_apply: true
globs: "**/*"
agents:
  claude: { kind: rule }
  cursor: { kind: rule, glob: "**/*" }
  codex:  { section: rules }
  goose:  { section: rules }
  openclaw: { section: rules }
  opencode: { kind: rule }
  pi:       { section: rules }
  vibe:   { kind: rule }
---

# Documentation

Document the surfaces users read. Do not narrate what the code already says.

## Scope

| Surface | Document |
|---|---|
| HTTP endpoint | yes (OpenAPI / docstrings) |
| CLI command | yes (help text + example) |
| Public library API | yes (preconditions, postconditions, errors) |
| ADR-worthy choice | yes (`docs/adr/NNNN-*.md`) |
| Internal helper | no — name + types speak |

## Non-Obvious Only

Docs explain intent, preconditions, invariants, postconditions, error cases, trade-offs. Never narrate the code line by line. State known limits and constraints up front (skill:honest-limits-disclosure). Cite canonical sources (RFCs, math, papers) where correctness depends on a spec (skill:canonical-reference-in-docstrings).

## ADRs

An architectural decision needs an ADR with a title, context, decision, and consequences. Keep it short, dated, and numbered.

### ADR Lifecycle

Each ADR moves through a defined lifecycle. Obsolete ADRs stay in the repo —
history matters. Index them in a `docs/adr/README.md` table so readers can
navigate without reading every file.

| Status | Meaning |
|---|---|
| `Proposed` | Under discussion; not yet binding |
| `Accepted` | Binding; code should reflect this decision |
| `Superseded` | Replaced by a newer ADR (link to it) |
| `Obsolete` | No longer relevant; context has gone away |

When a decision changes: write a new ADR, mark the old one `Superseded`, and
link both. Do not edit the original text — it is a historical record.

For system-level context across many decisions, see skill:architecture-haiku.

## Keep Current

When docs drift from code, delete the doc or fix it immediately. Stale docs are worse than absent docs because readers trust them.

| Change | Update |
|---|---|
| New env var | `docs/config.md` |
| New module / crate | `docs/architecture.md` |
| New entity | `docs/datamodel.md` |
| Layout shift | `docs/structure.md` |
| New pattern | `docs/patterns.md` |

## GOOD

```python
def broadcast(session_id: SessionId, event: SessionEvent) -> None:
    """Broadcast event to all subscribers on the session topic.

    Preconditions:
        session_id must be registered.

    Postconditions:
        Every connected subscriber receives `event`.

    Raises:
        BroadcastError: channel closed.
    """
```

## BAD

```python
def create_message(attrs):
    """Insert message into database."""
    return db.insert(attrs)
```

Narration of obvious code. Wastes reader time. Adds zero info beyond signature.

## Red Flags

- Docstring that re-states the function name in English.
- Public endpoint without an OpenAPI / schema description.
- ADR missing for "why we picked X over Y".
- Doc referencing function/file that no longer exists.
