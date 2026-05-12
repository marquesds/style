---
id: reuse-and-idioms
kind: rule
title: Reuse and Idioms
description: >
  Search repo, stdlib, ecosystem before new implementation. Prefer maintained
  solution over bespoke reimplementation. Write idiomatic code per language;
  verify APIs from docs for installed version.
applies_when:
  - new helper or utility
  - nontrivial parsing, dates, paths, retries, serialization
  - adding dependency or choosing library
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

# Reuse and Idioms

Build last. Search first.

## Search First

Nontrivial behavior → pause. Grep / semantic search **this repo** for same problem. Then language **stdlib**. Then **one** well-maintained ecosystem package (official or de-facto standard for that stack).

Greenfield 50-line parser for CSV/JSON/dates/paths → stop. Almost always wrong vs stdlib + tests.

Outbound **retry / backoff / circuit breaker** → skill:resilience-retries — don’t hand-roll sleep loops.

New dep → justify: saves bugs/time vs tiny glue, maintenance OK, license compatible. See skill:minimal-dependency-budget.

## Idioms

Match language community style, not generic "C in X" patterns.

| Language | Bias |
|---|---|
| Python | PEP 8, stdlib first, comprehension/match where clearer, pathlib |
| Elixir | pipelines, pattern matching, OTP boundaries |
| Kotlin | null-safety, stdlib, coroutines where async |
| Other | official style guide + prevalent ecosystem patterns |

Training-data recall for API shape → insufficient. **skill:source-driven-development**: confirm against docs for **installed** version.

## GOOD

```python
from pathlib import Path

def read_local(name: str) -> str:
    return Path(name).read_text(encoding="utf-8")
```

```python
import csv
from io import StringIO

def rows_from_tsv(text: str) -> list[list[str]]:
    return list(csv.reader(StringIO(text), delimiter="\t"))
```

Stdlib + types. Behavior matches platform edge cases (encoding, delimiters).

## BAD

```python
import os

def read_under(base: str, name: str) -> str:
    full = base + os.sep + name
    with open(full, encoding="utf-8") as f:
        return f.read()
```

Manual join + string concat. `Path(base) / name` + `read_text` handles edge cases and reads idiomatic.

```python
def rows_from_tsv(text: str) -> list[list[str]]:
    out = []
    for line in text.splitlines():
        out.append(line.split("\t"))
    return out
```

No escaping, no quoting, breaks on real TSV. Reinvents `csv`.

## Red Flags

- "Quick" hand-rolled format parser for standard format.
- Duplicate helper elsewhere in repo — search missed.
- API usage from memory; docs differ for this version.
- Idiom from different language pasted verbatim (Java style in Ruby, etc.).
- Dependency added without comparing lighter stdlib-only path.
