---
id: ci-pipeline-design
kind: skill
title: CI Pipeline Design
description: "Fail-fast ordering: lint → types → unit → integration → smoke. Matrix discipline. Cache hygiene. Stage segregation by branch. Secrets via vault. One paved path per repo. Cross-refs: task-runner-conventions, definition-of-done, secrets-never-in-repo."
applies_when:
  - new CI workflow or pipeline change
  - adding a test stage or deployment step
  - slow CI investigation
  - secrets or credentials in pipeline
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

# CI Pipeline Design

Fail fast. Cache smart. One path. No secrets in logs.

## Fail-Fast Ordering

Cheapest, fastest signal first. Each stage gates the next.

```text
lint → types → unit → integration → smoke → publish
 ^fast^  ^fast^  ^fast^   ^medium^   ^slow^   ^rare^
```

- **Lint**: style + import sort. Milliseconds. Kill trivial errors immediately.
- **Types**: static type check. Seconds. Catches contract drift before runtime.
- **Unit**: pure logic, in-memory fakes. Seconds to low minutes.
- **Integration**: real DB / HTTP / adapters; fake only at system edge. Minutes.
- **Smoke**: minimal real flow against staging or ephemeral environment. Minutes.
- **Publish**: artifact signing + registry push. Runs only on tagged commits or main.

Do not reorder to "save time" by skipping cheap stages. A 5-second lint step that
catches an import error is cheaper than a 10-minute integration run that fails for
the same reason.

## Matrix Discipline

Test the floor and ceiling Python (or runtime) version. Skip intermediate minors
unless a dependency pins to them. YAGNI on permutation explosion.

```yaml
matrix:
  python-version: ["3.10", "3.12"]  # floor + ceiling; not every minor
  os: [ubuntu-latest]               # add macOS only if platform behavior differs
```

Cross-OS matrix only when platform differences are real (file paths, signals,
native extensions). Don't add it speculatively.

## Cache Hygiene

- Key on lockfile hash, not a date or branch name.
- Separate keys per OS when matrix includes multiple OS.
- Ratchet invalidation: change the key suffix when the cache shape changes rather
  than busting all keys globally.

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ runner.os }}-${{ hashFiles('**/uv.lock', '**/requirements*.txt') }}
    restore-keys: pip-${{ runner.os }}-
```

## Stage Segregation by Branch

| Stage | PR | main merge | Tagged release |
|-------|----|------------|----------------|
| lint + types + unit | ✓ | ✓ | ✓ |
| integration | ✓ | ✓ | ✓ |
| smoke (staging) | — | ✓ | ✓ |
| publish to registry | — | — | ✓ |

PRs should not publish artifacts or run slow smoke tests against shared infra.

## Required vs Informational Checks

- **Required** (block merge): lint, types, unit, integration.
- **Informational** (notify only): coverage trend, SBOM generation, perf benchmarks.

Mark checks explicitly in the VCS settings. Do not let informational checks
silently block merges.

## Secrets

- CI vault / OIDC only. No long-lived keys checked in (skill:secrets-never-in-repo).
- Never `echo` a secret — use masked variables.
- OIDC federation (GitHub → cloud) preferred over stored access keys.
- Rotate if a workflow accidentally prints a secret (treat as leaked).

## One Paved Path Per Repo

One canonical `ci.yml` (or equivalent). No per-developer YAML forks. Use
`workflow_call` or reusable actions to share logic across repos, not copy-paste.
Task verbs (`make test`, `just check`) decouple the CI file from the exact tool
(skill:task-runner-conventions).

## GOOD

```yaml
jobs:
  check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: pip install -e ".[dev]"
      - run: python -m ruff check .        # lint — fast
      - run: python -m pyright             # types — fast
      - run: python -m pytest -q           # unit + integration — medium
```

## BAD

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: pytest  # no lint, no types, no matrix, plain command (no venv)
      - run: echo "SECRET=${{ secrets.API_KEY }}"  # leaked in logs
```

No ordering. No matrix. Secret echoed. Single step = no fail-fast signal.

## Red Flags

- Integration runs before unit — slow feedback on trivial errors.
- Matrix covers every minor version (3.10, 3.11, 3.12) without reason.
- Cache key is a date or branch name — never hits on PR rebase.
- Secret printed via `echo` or embedded in a URL.
- CI YAML copy-pasted across five repos — diverges within a month.
- Informational check silently blocks merges because nobody configured required vs not.
