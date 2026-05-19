---
id: review
kind: command
title: Six-axis review of current diff
description: >
  Review the working diff (or PR) against correctness, readability, architecture,
  security, performance, operability. Label findings by severity.
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

Use skill:code-review-and-quality.

Steps:

1. Read the spec or task summary. Hold it next to the diff.
2. Read the **tests first**. They tell intent.
3. Walk the diff against the six axes:
   - Correctness: edge cases, error paths, spec match.
   - Readability: names, control flow, abstraction cost.
   - Architecture: dependency direction, LSP, port boundaries (skill:hexagonal-architecture, skill:liskov-and-design-by-contract).
   - Security: input validation at boundaries, secrets, auth.
   - Performance: N+1 (skill:n-plus-one-prevention), unbounded loops, blocking in async.
   - Operability: correlation id propagated, structured logs at state changes, span at every boundary, RED counter present, alert path defined, runbook current (rule:observability, skill:wide-events-and-cardinality).
4. Label each finding: `Critical:`, `(none)` for required, `Optional:`, `Nit:`, `FYI:`.
5. Confirm tests + lint + types pass.

Output a flat list of findings with file:line, severity, and proposed fix.
