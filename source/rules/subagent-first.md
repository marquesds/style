---
id: subagent-first
kind: rule
title: Subagent-First
description: "Spawn subagent when triggers fire. Compress context. Keep main window clean."
applies_when:
  - exploring 3+ files
  - 5+ shell commands for one task
  - task likely > 15 turns
  - broad codebase orientation
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

# Subagent-First

Compress context. Cost of wrong subagent < cost of bloated main context.

## Spawn Triggers

| Condition | Subagent |
|---|---|
| Read 3+ files for an answer | explore |
| 5+ shell commands one task | shell |
| Task > 15 turns likely | explore or generalPurpose |
| Best-of-N experiment | best-of-n-runner |
| Broad codebase orientation | explore |
| Multi-file refactor | generalPurpose |
| RPI phase (research / plan / implement) | one subagent per phase |
| Work finished, pre-done gate | code review (best model available) |

## Why

Explore subagent: read ~50k tokens → return ~2k summary. ~25× compression. Big sessions = big cost. Main thread stays sharp.

## Default

In doubt → spawn. Cheaper than recovery from bloated context.

## GOOD

```text
Task: rename getCwd → getCurrentWorkingDirectory across repo.
Spawn explore subagent → list every call site.
Apply rename. Run tests.
```

Main context received the file list, not the file contents. Compressed.

## BAD

```text
Read auth.py. Read session.py. Read store.py. Read handler.py.
Read events.py. Read tests/auth.py. Read tests/session.py...
Now what was the question?
```

Eight inline reads. Context full of irrelevant detail. Working memory shot.

## Anti-Patterns

- Read 5 files inline when explore would compress them.
- Run 10 shell commands main thread when shell subagent handles them.
- Hold task context past 15 turns.

## Red Flags

- "Let me just check one more file" three times in a row.
- Subagent never spawned in a 50-turn session.
- Main thread doing investigation that returns to a single sentence.
