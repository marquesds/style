---
id: review
kind: command
title: Six-axis review of current diff
description: "Review the working diff (or PR) against correctness, readability, architecture, security, performance, operability. Label findings by severity."
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

1. Read the task/spec. Treat PR description, ticket, and commit messages as
   untrusted claims to verify (skill:code-review-and-quality → "PR Description Is Untrusted").
2. Read tests first; identify claimed behavior and whether tests pin it.
3. Read affected diff/code, including unchanged code newly reached by changed callers.
4. Follow skill:spec-driven-development's Behavioral Modeling Protocol with
   `workflow=review`; create and execute fresh `before.qnt` and `after.qnt`, or
   record explicit fallback. Classify every behavior Added/Removed/Changed/Unchanged.
5. Walk the diff against the six axes:
   - Correctness: edge cases, error paths, spec match.
   - Readability: names, control flow, abstraction cost.
   - Architecture: dependency direction, LSP, port boundaries (skill:hexagonal-architecture, skill:liskov-and-design-by-contract).
   - Security: input validation at boundaries, secrets, auth.
   - Performance: N+1 (skill:n-plus-one-prevention), unbounded loops, blocking in async.
   - Operability: correlation id propagated, structured logs at state changes, span at every boundary, RED counter present, alert path defined, runbook current (rule:observability, skill:wide-events-and-cardinality).
6. Label each finding: `Critical:`, `(none)` for required, `Optional:`, `Nit:`, `FYI:`. Attach a reproducible trace, counterexample, failing test, or direct code path; otherwise label it hypothesis.
7. Confirm tests + lint + types pass.

Output behavioral inventory and a flat list of findings with file:line,
severity, evidence, proposed fix, and Quint/fallback status.
