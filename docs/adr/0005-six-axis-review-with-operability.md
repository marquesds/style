# ADR-0005: Six-axis code review — adding operability as a peer axis

Date: 2026-05-12

## Context

`source/skills/code-review-and-quality.md` is a public surface: the `/review`
command, agent descriptions, and downstream agent configs (Cursor `.mdc`, Claude
`SKILL.md`, AGENTS.md managed section) all derive their review checklist from it.
Adding an axis is a breaking change for any agent that caches the five-axis framing.

The original five axes (correctness, readability, architecture, security, performance)
left operability as an implicit concern. In practice, PRs that are "correct" by the
five-axis checklist routinely ship without correlation-id propagation, missing spans,
or undefined alert paths — faults only visible under production load.

The rule:observability already mandates structured logs, traces, and metrics. The gap
is that the review skill did not surface operability as a first-class merge gate,
so reviewers would miss operability regressions unless they happened to remember the
rule.

## Decision

Promote operability to a sixth review axis, peer to security and performance.

The axis checks:

- Correlation id propagated through every new async boundary.
- Structured log at every state change (persist, publish, auth change, retry).
- Span on every new external call (DB, HTTP, queue).
- RED counter (rate, errors, duration) for any new endpoint or background job.
- Alert path defined — SLO burn-rate threshold set or existing threshold still valid.
- Runbook updated if on-call behavior changes.
- On-call can diagnose and recover without the author present.

The `/review` command (`source/commands/review.md`) gains an Operability bullet in
step 3, pointing at rule:observability and skill:wide-events-and-cardinality.

The skill title changes from `Code Review (Five-Axis)` to `Code Review (Six-Axis)`.
The description is updated in the frontmatter so agent-side description-driven loading
picks up the change without requiring code changes in adapters.

## Consequences

**Positive.** Every PR that touches a service boundary is now checked for
observability completeness at review time. The gap between the observability rule
and review practice closes. The `/review` command output includes operability findings
automatically.

**Negative.** Any downstream agent configuration or prompt that caches the phrase
"five axes" or the exact axis list must be updated. This is a one-time update on next
install or `./install.sh` run.

**Mitigations.** The frontmatter `description` field is updated so agents that load
skills by description will pick up "six-axis" without a manual config edit. Agents
with hardcoded text (human-written prompts referencing "five axes") are notified via
this ADR. No ADR is needed for the five new skills added in the same batch — they are
purely additive and introduce no public surface changes.
