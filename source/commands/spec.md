---
id: spec
kind: command
title: Start spec-driven development
description: >
  Kick off the SPECIFY phase: surface assumptions, define success criteria,
  fill the six-area template before any code.
agents:
  claude: { kind: command }
  cursor: { kind: command }
  codex:  { section: commands }
  goose:  { section: commands }
  openclaw: { section: commands }
  opencode: { kind: command }
  pi:       { section: commands }
  vibe:   { kind: command }
---

Use skill:spec-driven-development.

Phase: SPECIFY.

Steps:

1. State assumptions explicitly. Ask user to confirm or correct before continuing.
2. Reframe vague asks as measurable success criteria.
3. Fill the six-area template (Objective, Commands, Structure, Code Style, Testing Strategy, Boundaries).
4. Stop. Wait for human confirmation before moving to PLAN.

Output a `spec.md` block ready to paste into the project, plus a one-line summary of what remains open.
