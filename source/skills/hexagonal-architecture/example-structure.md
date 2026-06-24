# Worked example: the `style` service

A real-shaped tree for a service named `style` with two features — `sessions` and
`transcriptions` — side by side. Copy this shape; rename the features to yours. The
top-level cut is the **feature**, never the technical layer. Each feature is a self
contained hexagon; the composition root is the only place imports cross a feature line.

## Full tree

```text
src/
├── main.py                         # entrypoint — starts the app, calls composition
├── composition.py                  # composition root — calls each create_*_api() once, wires them
├── config.py                       # Settings from env (shared shell)
├── errors.py                       # shared error base (shared shell)
│
├── infra/                          # SHARED SHELL — not a hexagon, no business rules
│   ├── __init__.py
│   ├── metrics.py                  # MetricsPort impl, injected into features
│   ├── redis.py                    # Redis client wrapper
│   ├── gcs.py                      # blob-storage client wrapper
│   └── clients/
│       ├── datalayer.py            # outbound GraphQL/HTTP client
│       └── retry.py                # ExponentialBackoffRetry (skill:resilience-retries)
│
└── features/
    ├── __init__.py                 # empty — namespace only
    │
    ├── sessions/                   # FEATURE: session lifecycle
    │   ├── __init__.py             # FACADE — __all__ exports API + VOs + errors + factory
    │   ├── api.py                  # SessionAPI — the driving port (Protocol)
    │   ├── _service.py             # SessionService — concrete API impl (private)
    │   ├── _helpers.py             # error translation, logging (private)
    │   ├── errors.py               # SessionError (public — re-exported by facade)
    │   ├── domain/                 # PURE — no I/O, no framework imports
    │   │   ├── __init__.py
    │   │   ├── session.py          # Session aggregate
    │   │   ├── session_status.py   # SessionStatus enum
    │   │   └── errors.py           # internal domain exceptions
    │   ├── ports/                  # driven ports the domain calls (Protocols, private)
    │   │   ├── __init__.py
    │   │   ├── session_repository.py   # SessionRepository
    │   │   └── recording_blob_store.py # RecordingBlobStore
    │   ├── adapters/               # concrete I/O behind the ports (private)
    │   │   ├── __init__.py
    │   │   ├── firestore_session_repo.py  # FirestoreSessionRepo → SessionRepository
    │   │   └── gcs_recording_store.py     # GcsRecordingStore → RecordingBlobStore
    │   ├── use_cases/              # application orchestration (one file per use case)
    │   │   ├── __init__.py
    │   │   ├── create_session.py
    │   │   └── complete_session.py
    │   └── presentation/           # driving adapter — HTTP (only if feature is HTTP-driven)
    │       ├── __init__.py
    │       ├── router.py           # FastAPI routes → use cases
    │       └── deps.py             # request-scoped dependency wiring
    │
    └── transcriptions/             # FEATURE: audio → text
        ├── __init__.py             # FACADE — exports TranscriptionAPI + VOs + factory
        ├── api.py                  # TranscriptionAPI — driving port (Protocol)
        ├── _service.py             # TranscriptionService — concrete impl (private)
        ├── errors.py               # TranscriptionError (public)
        ├── domain/
        │   ├── __init__.py
        │   ├── transcription_result.py # TranscriptionResult aggregate
        │   └── word.py             # Word value object (timing)
        ├── ports/
        │   ├── __init__.py
        │   ├── transcriber.py      # Transcriber — audio bytes → result
        │   └── corrector.py        # Corrector — raw text → corrected text
        ├── adapters/
        │   ├── __init__.py
        │   ├── openai_transcriber.py     # OpenaiTranscriber → Transcriber
        │   ├── gemini_corrector.py       # GeminiCorrector → Corrector
        │   └── retrying_transcriber.py   # decorator wrapping any Transcriber
        └── use_cases/
            ├── __init__.py
            └── transcribe.py
```

## How to read it

- **Top level is `features/`, not `domain/` / `services/` / `adapters/`.** One feature
  change touches one folder, not five. A layer-first tree (the BAD case in `SKILL.md`)
  scatters every change across the whole project.
- **`infra/` is the shared shell**, sibling to `features/`, not inside any feature. A
  feature *uses* a shared client through its own port; it never owns the client.
- **`composition.py` is the only cross-feature wiring point.** It calls
  `create_sessions_api()` and `create_transcriptions_api()` once at startup and hands
  the results to driving adapters. Nothing else imports across feature boundaries.
- **The `features/` namespace folder is optional.** This example nests features under
  it (common once a service has several); the `SKILL.md` skeleton places them directly
  at `src/<feature>/`. Same pattern either way — the feature is the top-level cut. Pick
  one per repo and keep imports consistent: `src.features.sessions` here, `src.sessions`
  in the skeleton.

## Naming conventions

| Thing | Pattern | Example |
|---|---|---|
| Facade | `__init__.py` + `__all__` | `from src.features.sessions import SessionAPI` |
| Driving port | `<Feature>API` in `api.py` | `SessionAPI`, `TranscriptionAPI` |
| Concrete service | `_service.py`, `<Feature>Service` | underscore = private |
| Driven port | behavior noun in `ports/` | `SessionRepository`, `Transcriber` |
| Adapter | `<Tech><Port>` in `adapters/` | `FirestoreSessionRepo`, `OpenaiTranscriber` |
| Use case | one verb-named file in `use_cases/` | `create_session.py`, `transcribe.py` |
| Factory | `create_<feature>_api()` | constructs adapters, injects into service |
| Private file | leading `_` | `_service.py`, `_helpers.py` |

Port name says **what it does** (`Transcriber`), not who implements it. Adapter name
says **what it adapts to** (`OpenaiTranscriber`). The facade re-exports the API, the
value objects callers must build or receive, the factory, and the feature's errors —
nothing from `domain/`, `ports/`, `adapters/`, or `_service`.

## The facade is the whole contract

```python
"""features/sessions/__init__.py — public surface for the sessions feature."""
from src.features.sessions.api import SessionAPI
from src.features.sessions.domain.session import Session
from src.features.sessions.domain.session_status import SessionStatus
from src.features.sessions.errors import SessionError


def create_sessions_api() -> SessionAPI:
    from src.features.sessions._service import SessionService
    from src.features.sessions.adapters.firestore_session_repo import FirestoreSessionRepo
    return SessionService(repo=FirestoreSessionRepo())


__all__ = ["Session", "SessionAPI", "SessionError", "SessionStatus", "create_sessions_api"]
```

A caller imports `SessionAPI` and `Session` — never `_service`, `ports`, or `adapters`.
That import line is the entire coupling between features. Swap Firestore for an in
memory repo inside the factory and no caller changes.

## Not shown here (add only when earned)

- **Nested sub-feature** — when a feature grows its own bounded sub-capability (e.g. a
  `transcriptions/audio_streams/` with its own domain/ports/adapters). Same rule recurses.
- **`presentation/` on every feature** — only HTTP/CLI-driven features need it. A pure
  compute feature exposes its API Protocol and stops there.
- **Workers / orchestrators** — background processing lives in its own shell module or
  feature, wired at the composition root like everything else.
