---
id: task-runner-conventions
kind: skill
title: Task Runner Conventions
description: >
  Single canonical task file per repo. Short stable verbs (serve, test, check, fmt).
  AGENTS.md references task verbs, not raw commands. Task file is the entry point
  for agents and new developers alike.
applies_when:
  - setting up a new repo or project
  - writing AGENTS.md or CLAUDE.md instructions
  - onboarding a new developer or agent
  - the build commands are scattered across docs
agents:
  claude: { kind: skill }
  cursor: { kind: skill, glob: "**/{Makefile,makefile,justfile,Justfile,Taskfile.yml,Taskfile.yaml,package.json,pyproject.toml,*.mk}" }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Task Runner Conventions

One canonical surface for all project verbs. Agents and humans use the same commands.

## Single Task File

Pick one: `maskfile.md` (mask), `Makefile`, `justfile`. One file per repo. Document
the choice in `CONTRIBUTING.md` or `README.md`. Mixing task surfaces means agents
cannot rely on any one of them.

## Stable Short Verbs

| Verb            | Action                         |
|-----------------|--------------------------------|
| `serve` / `dev` | Start local dev server         |
| `test`          | Run full test suite            |
| `check`         | Lint + type check (no tests)   |
| `fmt`           | Format all code                |
| `build`         | Compile / package              |
| `release`       | Bump version, tag, publish     |
| `clean`         | Remove build artifacts         |

Verbs are stable. Underlying commands (`pytest`, `cargo test`, `mix test`) live behind
the verb. When the test framework changes, update the task file; nothing else changes.

## Reference Verbs in AGENTS.md

```markdown
## After any code change
1. `mask fmt`
2. `mask check`
3. `mask test`
```

Agents run task verbs, not raw compiler invocations. See skill:agents-md-checklists.

## Task File Is Executable Documentation

A new developer clones the repo and runs `mask serve`. It works, first time. No README
archaeology required. The task file is the canonical entry point.

## Composition

Complex tasks compose simple ones:

```makefile
ci: fmt check test
```

One verb for CI. The composition is the definition.

## GOOD

```makefile
.PHONY: test check fmt
test:
	pytest -q tests/
check:
	ruff check . && pyright
fmt:
	ruff format .
```

Short. Stable. `AGENTS.md` says `make check` and that never changes when pytest flags change.

## BAD

```markdown
# AGENTS.md
After a code change:
1. Run `python -m pytest -x --tb=short tests/ --ignore=tests/slow`
2. Run `ruff check --select E,W --ignore E501 .`
```

Raw commands in agent docs. Change the runner → edit every doc.

## Red Flags

- Two task files coexist (`Makefile` + `justfile`) with overlapping verbs.
- `AGENTS.md` references raw compiler commands instead of task verbs.
- `make test` on a fresh clone fails with a missing-dependency error.
- No `fmt` target; formatting is manual or ad hoc.
- Task verbs differ between repos on the same team; agents cannot generalise.
