---
id: incident-response-and-postmortem
kind: skill
title: Incident Response and Postmortem
description: "Severity tiers, incident roles, mitigate-first discipline, and blameless postmortem template. Action items must produce a code artefact before closing."
applies_when:
  - production incident in flight
  - on-call paged or escalating an alert
  - writing a postmortem after an outage
  - defining severity tiers or on-call escalation policy
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

# Incident Response and Postmortem

Mitigate first. Root-cause second. Blameless retrospective. Every action item
produces a durable artefact before it closes.

## Severity Tiers

| Tier | Criteria | Response |
|---|---|---|
| SEV1 | Revenue impact, data loss, total outage, SLO burn > 5% in 1 h | Page on-call lead + comms; bridge open immediately |
| SEV2 | Degraded core feature, SLO burn elevated, no workaround | Page on-call; acknowledge within 15 min |
| SEV3 | Non-core degradation, workaround available | Ticket; fix in next sprint |

Burn-rate thresholds from skill:wide-events-and-cardinality error-budget math.
When in doubt, declare higher and downgrade — the cost of under-declaring is
always higher.

## Roles (One Human Each)

- **Commander** — owns the bridge, coordinates all actions, makes go/no-go
  calls on rollbacks.
- **Comms** — owns status page updates and customer-facing messaging.
- **Scribe** — timestamps every action and decision in a shared doc.

Roles are assigned at bridge open; no role = no action on that axis.

## Mitigate First

Before investing in root cause: can we rollback the deploy? Kill a feature
flag? Disable a noisy consumer? Use skill:rollout-and-feature-flags kill
switch. Mitigation reduces blast radius; root cause analysis can wait until
the customer is no longer impacted.

```python
def triage_priority(incident: Incident) -> list[str]:
    steps = ["check recent deploys", "check feature flags"]
    if incident.sev <= 2:
        steps.append("prepare rollback")
    steps.append("identify blast radius")
    return steps
```

## Timeline Capture

Scribe logs every event during the incident, not from memory after:

```python
@dataclass
class TimelineEvent:
    ts: datetime
    actor: str
    action: str
    outcome: str | None = None
```

Export to postmortem doc immediately after bridge closes.

## Blameless Postmortem Template

```
## Incident <ID> — <title>

**Severity:** SEV{1,2,3}  **Duration:** Xh Ym  **Date:** YYYY-MM-DD

### Timeline
| Time | Event |
|------|-------|
| ...  | ...   |

### Contributing Factors
(Not "who caused it" — what conditions made failure possible)
- ...

### What Went Well
- ...

### Action Items
| Item | Owner | Due | Artefact |
|------|-------|-----|----------|
| ...  | ...   | ... | PR / test / runbook |
```

"Contributing factors" not "root cause" — complex systems have multiple
conditions, not one guilty party.

## Action Items Must Produce Artefacts

| Action type | Required artefact |
|---|---|
| Bug fix | Failing test merged first (skill:bug-first-debugging) |
| Data repair | Idempotent CLI task merged (skill:operational-repair-tasks) |
| Detection gap | Alert or SLO threshold change in code (skill:wide-events-and-cardinality) |
| Process gap | Updated runbook committed to repo |

Action item without an artefact is not closed.

## GOOD

```
[14:03] Commander: recent deploy at 13:47 — initiating rollback
[14:08] Comms: status page updated — "degraded, investigating"
[14:11] Scribe: rollback deployed; error rate dropping
[14:18] Commander: service healthy; downgrading to SEV3 for root cause
```

Roles active. Timeline captured live. Mitigation before deep debug. Customer
informed within minutes.

## BAD

```
# Group chat, no roles declared
dev1: something's broken
dev2: yeah I see errors
dev1: anyone know what happened?
dev3: let me dig into logs
# 40 min pass, no status page update, no timeline
```

No roles, no timeline, no customer comms, no mitigation path.

## Red Flags

- No severity definition; every incident is "urgent".
- Commander and root-cause investigator are the same person.
- Status page not updated within 15 min of SEV1/2 declaration.
- Postmortem written from memory days later.
- Action items closed as "discussed" with no code or doc artefact.
- "Root cause: human error" — stops analysis before contributing factors found.
- Rollback not attempted before deep debug on a SEV1.
