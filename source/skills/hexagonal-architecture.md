---
id: hexagonal-architecture
kind: skill
title: Minimal Hexagonal Architecture
description: >
  Domain core surrounded by adapters. Domain depends on nothing.
  Adapters depend on domain ports. Describe responsibilities, not folder names.
applies_when:
  - new module
  - new service
  - integrating external system
  - refactor of tangled module
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Minimal Hexagonal Architecture

Core knows nothing. Adapters know core. Effects at the edge.

## Responsibilities (not folder names)

| Responsibility | What it does | Depends on |
|---|---|---|
| Domain | Pure rules + types | nothing |
| Ports | Interfaces the domain calls | domain types |
| Adapters | Concrete I/O (DB, HTTP, queue) | ports |
| Application | Orchestration use cases | domain + ports |
| Driving side | HTTP handlers, CLI, jobs | application |

Folder names per project. Responsibilities universal. See skill:functional-core-imperative-shell for the same idea zoomed-in.

## Dependency Direction

```text
driving (HTTP/CLI) → application → domain ← ports ← adapters (DB/HTTP/queue)
```

Arrows point inward. Domain has no outward arrows.

## Ports = Language-Native Interfaces

Python `Protocol`. TS `interface`. Rust `trait`. Go `interface`. Pick what is fluent for the language; LSP holds in all of them.

## GOOD

```python
class SessionStore(Protocol):
    def get(self, id: SessionId) -> Session | None: ...
    def save(self, s: Session) -> None: ...

@dataclass(frozen=True)
class CompleteSession:
    sessions: SessionStore
    clock: Clock

    def __call__(self, id: SessionId) -> Session:
        s = self.sessions.get(id) or raise_not_found(id)
        completed = s.complete(at=self.clock.now())
        self.sessions.save(completed)
        return completed
```

Domain (`Session.complete`) pure. Application (`CompleteSession`) orchestrates. `SessionStore` is the port. SQL adapter implements it elsewhere; nobody in domain imports SQL.

## BAD

```python
def complete_session(id):
    s = db.execute("SELECT * FROM sessions WHERE id = ?", id).fetchone()
    s["completed_at"] = datetime.utcnow()
    db.execute("UPDATE sessions SET completed_at = ? WHERE id = ?", ...)
    requests.post("https://billing/api/charge", json={"id": id})
    return s
```

Domain glued to SQL + HTTP. Untestable without standing up DB and webhook. Time hardcoded. Refactor cost: total rewrite.

## Testing Pays Off Here

Substitute adapters with in-memory fakes. Domain tests run in microseconds with no I/O. Integration tests cover the adapter contract once.

## Red Flags

- Domain module imports `requests`, `boto3`, `sqlalchemy`, `redis`.
- Adapter contains business rules.
- Use case touches three repositories AND publishes events AND sends emails.
- Port surfaces leak SQL syntax, HTTP status codes, or Kafka offsets.
- "Service" classes that are actually god objects.
