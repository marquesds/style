---
id: privacy-by-design
kind: rule
title: Privacy by Design
description: "Privacy and data protection baked in before code. Minimize, declare purpose, enforce retention, honor subject rights. Opt-out only via dated ADR."
applies_when:
  - any feature touching user or personal data
  - schema change adding a column that could hold PII
  - logging, analytics, export, sharing, replication
  - third-party processor or sub-processor change
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

# Privacy by Design

Privacy is a design property, not a feature added later. Default to least
data, declared purpose, enforced retention, honored rights. Silent skip not
allowed — opt out via ADR.

## Principles

| Principle | What it means |
|---|---|
| Minimization | Collect only fields the declared purpose needs. No "might be useful later" columns |
| Purpose limitation | Each PII field has a recorded purpose at schema time |
| Lawful basis | Consent / contract / legitimate interest declared **before** the write path lands |
| Storage limitation | Every PII column has a retention window enforced by an automated purge job |
| Integrity | Encrypt at rest + in transit. Least-privilege access. Audit reads of regulated data |
| Subject rights | Access, rectify, erase, port, object — wired before launch, not after first request |
| Default privacy | Defaults deny sharing, PII logging, cross-region replication |
| Accountability | DPIA when triggered (below). Records of processing maintained |

Mechanics (classification table, retention enum, DSR state machine, audit event
shape, residency tags) live in `skill:data-privacy-and-retention`. Load it when
implementing.

## Regimes Covered

This rule is the **common spine** across:

- GDPR (EU)
- UK GDPR
- LGPD (Brazil)
- CCPA / CPRA (California)
- PIPEDA (Canada)
- POPIA (South Africa)
- APPI (Japan)
- PDPA (Singapore / Thailand)

Per-regime specifics (e.g. LGPD ANPD reports, CCPA "do not sell" link, GDPR Art.
30 records, POPIA Information Officer) are **not** duplicated here. When a
regime-specific question arises:

1. Fetch official source: eur-lex.europa.eu, planalto.gov.br, oag.ca.gov,
   priv.gc.ca, justice.gov.za, ppc.go.jp, pdpc.gov.sg, ico.org.uk.
2. Cache under `.style-cache/privacy/<regime>.md`. Header: source URL,
   retrieved-on date, snippet scope.
3. Reuse cache before re-fetching. Treat cache stale after 180 days.
4. Cite the cached file + URL in the code or ADR that depends on it.

Pairs with `skill:source-driven-development` (verify against installed-version
docs, never memory) and `skill:canonical-reference-in-docstrings` (cite RFC /
statute number at the relevant point).

## DPIA Trigger

Run a Data Protection Impact Assessment when **any** of:

- Large-scale processing of regulated data (health, financial, biometric,
  children, location).
- Automated decisions producing legal or similarly significant effect on a
  person (credit scoring, hiring filter, content moderation ban).

DPIA scope and template = consult counsel. This rule does not replace legal
review.

## Opt-Out

Feature, repo, or scope demonstrably free of personal data (internal sandbox,
synthetic-only data set, contributor tooling) may opt out. Opt-out is **never
silent** — author an ADR:

```
docs/adr/NNNN-privacy-opt-out-<scope>.md
```

Required fields:

| Field | Example |
|---|---|
| Scope | `feature: prototype-x`, or `repo: style-harness` |
| Reason | No personal data collected, internal-only, synthetic data |
| Owner | Engineer + manager + DPO (or equivalent) |
| `review_by:` | Date ≤ 12 months out. Stale ADR = invalid opt-out |
| Reversal trigger | What would re-engage the rule (e.g. real users onboard) |

No ADR → rule applies. Expired ADR → rule applies. Scope creep beyond ADR text
→ rule applies.

## Cross-Links

- `skill:data-privacy-and-retention` — classification, retention, DSR, audit,
  residency mechanics
- `skill:threat-modeling` — trust boundaries around regulated data
- `rule:observability` — no PII in logs
- `skill:secrets-never-in-repo` — keys, tokens, credential hygiene
- `skill:wide-events-and-cardinality` — event field design without PII leakage
- `skill:data-quality-and-analytics` — pseudonymized analytics tables

## GOOD

```python
@dataclass(frozen=True)
class UserEmail:
    """Regulated PII. Purpose: account auth + transactional mail.
    Retention: 90d after account deletion. Lawful basis: contract."""
    value: str
    classification: ClassTag = ClassTag.REGULATED
    retention: timedelta = timedelta(days=90)
```

```python
async def request_erasure(user_id: UserId, uow: UnitOfWork) -> None:
    user = await uow.users.get(user_id)
    user.mark_erasure_requested(at=now())
    await uow.audit.record("erasure.requested", actor_hash=sha256(user_id))
    await uow.commit()
```

Field declares purpose + retention + lawful basis. Erasure is a state
transition, not a synchronous delete. Audit row written. Hashed actor.

## BAD

```python
def create_user(payload):
    db.execute(
        "INSERT INTO users(email, name, dob, ip, locale, marketing_opt_in) "
        "VALUES (?,?,?,?,?,?)",
        payload.values(),
    )
    log.info(f"created user {payload['email']}")
```

Five PII fields, no purpose recorded. No retention. No lawful basis declared.
Email plaintext in log. No audit. No erasure path. Inserting first, asking
permission never.

## Red Flags

- New table holding personal data with no retention window in the migration.
- New analytics event whose fields include `email`, `name`, raw `ip`, or
  reversible user id.
- Cross-region replication added without residency tag or transfer mechanism.
- DSR ("delete my data") request handled by ad-hoc SQL, no audit row, no
  downstream propagation.
- Third-party processor added without contract review or sub-processor list.
- Feature shipped, ADR opt-out written **after** launch to justify it.
- ADR opt-out with no `review_by:` date, or date already passed.
- Regime-specific behavior implemented from memory, no cached source citation.
