---
id: data-privacy-and-retention
kind: skill
title: Data Privacy + Retention
description: >
  Data classification, retention windows and automated purge,
  right-to-erasure workflows, pseudonymization, access audit logs, residency.
applies_when:
  - storing personal or sensitive data
  - designing a retention policy
  - handling deletion requests (GDPR / CCPA)
  - building a data pipeline or export feature
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

# Data Privacy + Retention

Collect less. Keep shorter. Delete on schedule. Audit access.

## Classification

Label every data element before storing it.

| Tier | Examples | Default access |
|---|---|---|
| Public | marketing copy, public product names | anyone |
| Internal | employee ids, internal metrics | authenticated principals |
| Sensitive | emails, names, IP addresses | owning service only |
| Regulated | PII under GDPR/CCPA, payment data, health data | explicit + audited |

Classification drives encryption at rest, log redaction, cross-region restrictions,
and retention window. Misclassifying "regulated" as "internal" is the most common gap.

## Retention Windows

Every table with personal data needs a documented retention policy:

```python
RETENTION = {
    "user_events":  timedelta(days=90),
    "audit_log":    timedelta(days=365 * 7),  # legal hold
    "session_data": timedelta(days=30),
}
```

An automated purge job (cron or scheduled task) runs the window daily.
"Delete when we get around to it" is not a policy — it doesn't execute.

## Right to Erasure (DSR)

When a user requests deletion (GDPR Art. 17, CCPA):

1. Mark record `erasure_requested_at = now()`.
2. Purge job finds rows where `erasure_requested_at IS NOT NULL`.
3. Hard-delete PII columns; retain anonymous statistical residue if needed.
4. Write a `DataErased` event to audit log — `user_hash` + timestamp, no PII.
5. Propagate to downstream systems via event; no direct cross-service DB write.

Erasure is a state machine, not a synchronous delete. It must complete reliably even
after partial failure — outbox pattern applies. See skill:unit-of-work-and-transactions.

## Pseudonymization vs Anonymization

**Pseudonymization**: replace PII with a reversible token (keyed HMAC or lookup table).
Re-identification possible with the key. Still personal data under GDPR.

**Anonymization**: irreversible removal or aggregation. No longer personal data.
Hard to achieve — k-anonymity and l-diversity are starting points, not guarantees.

Default: pseudonymize for analytics pipelines, anonymize for public exports.

## Access Audit Log

Every read or write of regulated data generates a structured audit event:

```python
audit_log.info(
    "data.access",
    actor=request.user_id,
    resource="user_profile",
    resource_id=sha256(user_id),  # hash, not raw id
    action="read",
    purpose="support_ticket",
)
```

No PII in log fields. Hash the identifier. Log the purpose.
See rule:observability (no-PII requirement). See skill:secrets-never-in-repo.

## Residency

Regulated data may not cross certain jurisdictions without consent or SCCs.
Tag tables with `residency: ["EU"]`. Deploy per-region DB if required.
Never store EU personal data in a US-only DB without a documented transfer mechanism.

## GOOD

Retention column + automated purge job + pseudonymized analytics table + audit row
on every access to regulated data.

## BAD

PII in log messages. No retention policy beyond a code comment. Synchronous hard-delete
that fails halfway and leaves partial records. Cross-border replication of regulated
data with no residency check.

## See Also

- `rule:privacy-by-design` — always-on principles, opt-out ADR, regime list.

## Red Flags

- `SELECT *` on PII table with no purpose logged.
- Log line contains `email=` or `name=` in plaintext.
- Retention "policy" is a comment in source code, not a running job.
- Erasure = `DELETE WHERE id = ?` — no audit trail, no downstream propagation.
- Analytics table is a live copy of the production users table.
- Data classified "internal" but accessible without authentication.
- No documented legal basis for cross-region personal data transfer.
