---
id: ai-contribution-disclosure
kind: skill
title: AI Contribution Disclosure
description: >
  Disclose AI assistance in PR descriptions. One-time .ai-ack gate per contributor.
  Security-sensitive code must be human-authored or explicitly re-reviewed.
applies_when:
  - opening a PR that contains AI-generated code
  - reviewing a PR of unknown authorship mix
  - setting up AI policy in CONTRIBUTING.md
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# AI Contribution Disclosure

Disclose AI assistance on PRs. One-time acknowledgment gate per contributor.

## Why

Review rigor differs for AI-generated vs human-authored code (skill:ai-collaboration-hygiene).
Undisclosed AI output reviewed at human-author confidence creates false assurance.
Teams need to know what got independent human judgment and what got AI-assisted generation.

## Gate: `.ai-ack`

One-time contributor acknowledgment. Commit `.ai-ack` to the repo the first time you
use AI assistance on a contribution. The file may contain a brief statement or be
empty. Purpose: signal that the contributor has read and agreed to the project's
AI disclosure policy.

## Per-PR Disclosure

In the PR description, state how AI was used:

```markdown
## AI Assistance
- Boilerplate and test scaffolding generated with AI; reviewed and verified.
- Domain logic and security-sensitive code written by hand.
```

Present = disclosure. Absent = no AI used. Never omit the section silently if AI was used.

## CONTRIBUTING.md Statement

Projects that accept external contributions must state the rule:

```markdown
## AI Assistance Policy
If you used an AI tool to write or substantially modify code in this PR,
note it under "AI Assistance" in the PR description. Auth, crypto, and
injection-guard code must be human-authored or explicitly re-reviewed.
```

## In Commit Messages

When a commit is substantially AI-generated (>50% generated without significant rework),
note it in the commit body:

```text
feat(api): add cursor pagination to /sessions

Pagination logic AI-assisted; verified against RFC and integration-tested.
Reviewed: yes. Tests: independent.
```

## GOOD

PR description includes "AI Assistance" section. Security code written by human.
`.ai-ack` present in repo. Reviewer applies stricter scrutiny (skill:ai-collaboration-hygiene).

## BAD

AI-generated auth middleware merged with no disclosure. Reviewer evaluates as if
fully human-authored. Hallucinated API call not caught because the review did not
apply the extra skepticism AI output warrants.

## Red Flags

- AI-generated security or crypto code merged without explicit disclosure.
- `.ai-ack` absent; contributor never acknowledged the policy.
- PR reviewed at human-author confidence when AI-generated.
- Bulk-generated test suite committed; fabricated tests pass while behavior is wrong.
- "The model suggested it" treated as a rationale in an ADR.
