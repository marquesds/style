---
id: api-and-interface-design
kind: skill
title: API + Interface Design
description: >
  Stable, hard-to-misuse interfaces. Contract first. Validate at boundaries.
  Addition over modification. Hyrum's Law respected.
applies_when:
  - new public function or module
  - new port / Protocol / interface / trait
  - public API change
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# API + Interface Design

Hard to misuse. Honest. Stable. Tells the truth.

## Principles

### Hyrum's Law

Every observable behavior becomes contract. Be intentional about what's exposed. Don't leak internals — file paths, ORM types, transport quirks.

### Contract First

Define the shape before implementing.

```python
class SessionStore(Protocol):
    def create(self, s: Session) -> None:
        """Raise StoreError if id exists."""
    def get(self, id: SessionId) -> Session | None:
        """None if not found."""
    def list_for_agent(self, agent_id: AgentId) -> list[Session]:
        """Newest first."""
    def delete(self, id: SessionId) -> None:
        """Idempotent. Already-deleted = success."""
```

### Consistent Error Semantics

Pick one pattern, use everywhere:

```python
Ok(value)              # success
Err(NotFound)          # missing resource
Err(Invalid(reason))   # validation
Err(Denied)            # permission
```

Or exceptions, or `Result` — choose, then enforce.

### Validate at Boundaries

External input → validate. HTTP handler, CLI parser, env load, queue consumer. Internal callers trust types.

```python
async def handle_ingest(payload: IngestPayload) -> IngestResponse:
    event = payload.validate()
    return await ingest(event)
```

### Addition Over Modification

Add optional parameters via builders or new methods. Don't change existing signatures — that breaks callers.

## Deep Modules

Simple interface, hidden complexity.

```python
def list_sessions(agent_id: AgentId, opts: ListOpts | None = None) -> list[Session]: ...
```

Hides query building, filtering, auth, paging.

## GOOD

```python
@dataclass(frozen=True)
class ListOpts:
    limit: PositiveInt = PositiveInt(50)
    since: datetime | None = None

def list_sessions(agent_id: AgentId, opts: ListOpts | None = None) -> list[Session]:
    """Newest first. Limit defaults to 50."""
```

Honest signature. Easy to evolve via `ListOpts`.

## BAD

```python
def list_sessions(agent_id, qb, filters, limit=None, since=None,
                  auth_check=None, include_deleted=False):
    ...
```

Leaks query builder. Boolean param flips semantics. Five optional args; callers guess.

## Red Flags

- `unwrap()` / `assert` on values from external input.
- Boolean flags that toggle "two modes" — split the function.
- Public function returns different shapes by argument.
- Internal types (`SqlAlchemyRow`, `_PrivateThing`) cross the module boundary.
- Same error condition raised three different ways across the module.
- `# TODO: change signature later` — Hyrum says you can't.
