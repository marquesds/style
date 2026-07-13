---
id: context-gathering
kind: skill
title: Context Gathering
description: >
  Gather evidence before asking questions. Use before requirements work to
  collect repo, Linear, Datadog, Notion, Slack, and history context when
  available. If a source is unavailable, record that and continue.
applies_when:
  - starting requirements work and external context may exist
  - before asking questions that gathered evidence could answer
  - preparing a brief that should cite real evidence, not assumptions
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

# Context Gathering

Gather evidence before asking questions. Use only integrations available to the
current agent. If a source is unavailable, record that and continue.

Order:

1. Repo-local docs/code: `README.md`, `RUNBOOK.md`, `docs/`, tests,
   nearby feature packages, and recent diffs.
2. Linear if integrated: issue, parent, comments, labels, project, acceptance criteria.
3. Datadog if integrated: logs, monitors, incidents, dashboards, traces, error rates.
4. Notion if integrated: product docs, RFCs, specs, meeting notes.
5. Slack if integrated: relevant channels, threads, incident or decision context.
6. Git/GitHub if useful: recent commits, PRs, review comments.

Output concise evidence, contradictions, unknowns, and the questions that remain.
Do not ask questions already answered by gathered context.

## GOOD

Before drafting a brief for "add retry to the payment endpoint", the agent reads
the existing endpoint code, finds a related Linear issue with a linked incident,
checks Datadog for the error rate, and notes that Slack thread #payments already
decided on exponential backoff. The brief cites all of this and asks only the one
remaining question: target p99.

## BAD

The agent immediately asks "what is the retry policy?" without reading the code,
checking the issue, or looking at the incident — wasting the human's time on a
question the evidence already answers.

## Red Flags

- Asking a question that the repo, issue tracker, or telemetry already answers.
- Skipping a source because it "might not have anything" instead of checking.
- Listing every fact found instead of concise evidence, contradictions, and unknowns.
- Treating an unavailable integration as a blocker instead of recording the gap.
