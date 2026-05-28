---
id: hexagonal-architecture
kind: skill
title: Package by Feature with Lightweight Hexagon
description: >
  Slice top-level packages by feature, not by technical layer. Each
  feature is a small hexagon (domain, ports, adapters, application) and
  exposes only its behavior through a facade — not its internals.
applies_when:
  - new module
  - new service
  - integrating external system
  - refactor of tangled module
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

# Package by Feature with Lightweight Hexagon

Top-level cut is the **feature** (a capability you ship as a unit). Inside each feature, a small hexagon: pure domain, ports, adapters, application. Each feature exposes **behavior** — a single facade — and hides everything else.

## Behavior, not content

A feature's public surface is its **API** plus the data shapes callers must construct or receive. Internals — services, ports, adapters, helpers — stay private. External code depends on the facade only.

| Public (re-exported by facade) | Private (no external import) |
|---|---|
| `<Feature>API` class / protocol | `_service.py`, `_helpers.py` |
| Domain value objects callers need | `ports/` (driven ports + protocols) |
| Feature-specific errors | `adapters/` (concrete I/O) |
| `create_<feature>_api()` factory | the `domain/` package itself |

Language-native facade: Python `__init__.py` + `__all__`; TS `index.ts` barrel export; Rust `pub use` in `mod.rs`; Go internal packages; Elixir module boundary.

## Feature layout

```text
src/
├── main.py                        # composition root — wires APIs
├── start.py                       # entrypoint
├── config.py, errors.py           # shared shell
├── clients/                       # shared outbound clients (auth, datastore)
├── infrastructure/                # shared infra (queues, metrics, shutdown)
└── <feature>/
    ├── __init__.py                # facade: __all__ exports API + VOs + factory
    ├── api.py                     # <Feature>API — the driving port
    ├── _service.py                # internal orchestration (underscore = private)
    ├── _helpers.py                # internal helpers
    ├── errors.py                  # feature-specific errors (public)
    ├── domain/                    # pure domain types and rules
    ├── ports/                     # driven port Protocols (internal)
    └── adapters/                  # concrete adapter impls (internal)
```

## Responsibilities (per feature)

| Responsibility | What it does | Depends on |
|---|---|---|
| Domain | Pure rules + types | nothing |
| Ports | Interfaces the domain calls | domain types |
| Adapters | Concrete I/O (DB, HTTP, queue) | ports |
| Application | Use-case orchestration | domain + ports |
| Driving side | API class, HTTP handlers, CLI | application |

Folder names per project. Responsibilities universal. Inner pure/shell split: skill:functional-core-imperative-shell.

## Dependency direction (per feature)

```text
driving (API/HTTP/CLI) → application → domain ← ports ← adapters (DB/HTTP/queue)
```

Arrows point inward. Domain has no outward arrows. Each feature is its own hex.

## Composition root

`main.py` calls each feature's `create_<feature>_api()` factory once at startup, wires the resulting APIs together, and hands them to driving adapters. Adapters are constructed inside the factory; outside code never sees them.

## Shared shell

`clients/` and `infrastructure/` hold cross-feature primitives (auth clients, queues, metrics, GCS, Redis). They live at the root, not inside any feature. A feature **uses** shared clients via its own port; it does not own them.

## Between features

A feature may import **only** another feature's facade — `from src.sessions import SessionAPI`. Reaching into `src.sessions._service`, `src.sessions.ports`, or `src.sessions.adapters` is forbidden. Richer seams (anticorruption layer, published events, translators, shared kernel when genuinely shared): skill:bounded-context-mapping.

## Ports = language-native interfaces

Python `Protocol`. TS `interface`. Rust `trait`. Go `interface`. LSP holds in all.

## GOOD

Facade exports behavior + the value objects callers need; everything else stays private.

```python
"""sessions/__init__.py — public surface for the sessions feature."""
from src.sessions.api import SessionAPI
from src.sessions.domain.session import Session
from src.sessions.domain.session_status import SessionStatus
from src.sessions.errors import SessionError


def create_session_api() -> SessionAPI:
    from src.sessions._service import SessionService
    from src.sessions.adapters.firestore_repo import FirestoreSessionRepo
    return SessionService(repo=FirestoreSessionRepo())


__all__ = [
    "Session", "SessionAPI", "SessionError",
    "SessionStatus", "create_session_api",
]
```

Driving adapter depends on the facade, not internals:

```python
from src.sessions import SessionAPI, SessionError

async def complete_endpoint(api: SessionAPI, id: str) -> dict:
    try:
        return api.complete(id).to_payload()
    except SessionError as e:
        return {"error": str(e)}
```

## BAD

Cross-feature leak + layer dumping ground:

```python
from src.sessions._service import SessionService          # private
from src.sessions.adapters.firestore_repo import FirestoreSessionRepo  # private
from src.transcription.domain.word import Word            # ok (VO) — but...

def hand_rolled_pipeline(id: str) -> list[Word]:
    svc = SessionService(repo=FirestoreSessionRepo())     # rewires adapters
    return svc.transcribe(id)                              # reaches across features
```

```text
src/
├── domain/{sessions.py, transcription.py, billing.py, ...}   # one bag
├── services/{everything.py}                                  # dumping ground
└── adapters/{db.py, http.py, ...}                            # shared per-tech
```

Layer-first tree forces edits in every folder for one feature change; nothing hides behind a facade.

## When not to apply

Hexagonal earns its overhead when a domain has invariants worth defending across multiple I/O backends and the system has more than one feature. Skip the strict partition when:

- **Single-shot scripts** (<200 lines, one collaborator).
- **Pure libraries** (parsers, math, codecs) — no I/O boundary.
- **Prototypes pre-product-fit** — model unstable; premature ports churn.
- **Single-feature service** — project *is* the feature; don't invent a wrapper folder.
- **Infra glue** wiring two frameworks with no business logic.

Heuristic: if you can anticipate ≥2 features that will ship from this codebase, or ≥2 adapter implementations behind one port (SQL + in-memory, real queue + fake), apply the pattern. Otherwise keep types + small functions.

## Red flags

- `from feature_a.adapters.x import ...` or `from feature_a._service import ...` outside `feature_a`.
- Feature `__init__.py` missing `__all__` — star-import leaks internals.
- Facade re-exports `_service`, `ports`, or `adapters` modules.
- Top-level `domain/`, `services/`, `adapters/` folders mixing unrelated features.
- Shared "service" class that knows about three features.
- Adapter contains business rules; domain imports `requests`, `boto3`, `sqlalchemy`.
- Port surfaces leak SQL syntax, HTTP status codes, or Kafka offsets.
- Use case touches three repositories AND publishes events AND sends emails.
- Single-feature project with an empty `<feature>/` folder built "for symmetry".
