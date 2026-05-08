---
id: source-driven-development
kind: skill
title: Source-Driven Development
description: >
  Cite official docs before writing framework code. Detect versions first.
  Don't implement from training-data memory.
applies_when:
  - using unfamiliar framework API
  - is-this-the-right-way question about a third-party API
  - upgrading library version
  - any code calling third-party SDK
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  vibe:   { kind: skill }
---

# Source-Driven Development

Don't write framework code from memory. Verify, cite, flag unverified.

## Process

```text
DETECT versions → FETCH docs → IMPLEMENT → CITE
```

## Detect Versions

Read the lockfile / manifest first.

| Stack | File |
|---|---|
| Python | `pyproject.toml`, `uv.lock`, `requirements.txt` |
| Node / TS | `package.json`, `pnpm-lock.yaml` |
| Rust | `Cargo.toml`, `Cargo.lock` |
| Elixir | `mix.exs`, `mix.lock` |
| Go | `go.mod`, `go.sum` |

```text
DETECTED:
- FastAPI 0.115.x
- SQLAlchemy 2.0.x (async)
- Pydantic 2.x
→ fetching docs for these versions.
```

## Source Hierarchy

| Priority | Source |
|---|---|
| 1 | Official docs at the version installed |
| 2 | Official guides + cookbook |
| 3 | Standard library docs |
| 4 | Changelog / release notes |

Not authoritative: blogs, Stack Overflow, training data.

## Cite Inline

```python
# SQLAlchemy 2.0 async session — see docs.sqlalchemy.org/en/20/orm/session_basics.html
async with AsyncSession(engine) as session:
    async with session.begin():
        ...
```

In conversation:

```text
Using `select().options(selectinload(...))` per SQLAlchemy 2.0 async docs.
Source: docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#selectin-loading
```

## Conflicts With Existing Code

```text
CONFLICT:
existing code uses `Session()` directly; SQLAlchemy 2.0 docs prefer
`async_sessionmaker` with `expire_on_commit=False`.

Options:
A) Modernize to async_sessionmaker (matches docs, breaks calling code)
B) Keep current shape (consistency, drifts from docs)
→ Which?
```

Don't silently pick one.

## Unverified Flag

```text
UNVERIFIED: Could not find official docs for `pydantic.dataclasses` + SQLAlchemy hybrid.
Implementation based on training data; verify before merging.
```

## GOOD

```python
# FastAPI 0.115: dependencies-with-yield require try/finally for cleanup.
# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
async def get_session():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
```

Documented pattern. Cited. Matches installed version.

## BAD

```python
# I think FastAPI does this somehow
@app.get("/")
def root():
    db = Session()  # Pydantic 1.x style, plus 1.0 FastAPI shape
    return db.exec("...").all()
```

Mixed versions. Guessed API. No citation. Likely wrong against installed deps.

## Red Flags

- "I'm pretty sure this is how X works" without docs link.
- Code mixes API shapes from multiple versions of the same library.
- No version detection step performed.
- Deprecated function used because "training data preferred it".
- Pull request lacks links to the docs that justify the patterns chosen.
