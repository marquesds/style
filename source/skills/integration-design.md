---
id: integration-design
kind: skill
title: Integration Design (Syntactic / Semantic / Domain)
description: >
  Build integrations that split API shape from business meaning and behavior.
  Syntactic layer normalizes external contracts; semantic layer translates
  meaning; domain layer runs rules, invariants, workflows, domain events.
applies_when:
  - external API or webhook integration
  - partner feeds, streams, file ingest
  - CRM, ERP, payments, healthcare, legacy SaaS
  - anticorruption or external enum mapping
  - point-to-point integration rework
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

# Integration Design

Mature integration ≠ single HTTP call. Push partner churn to edge; keep core honest.

Ask **which layer owns this?** — not only **how do we call API?**

| Layer | Question | Examples |
|---|---|---|
| Syntactic | Communicate + normalize payload? | HTTP/SDK, auth, pagination, retries, raw DTOs, schema |
| Semantic | What means **here**? | Provider `APPROVED` → pre-qualified ≠ booked |
| Domain | What transition / invariant / event? | Eligible for offer; aggregate method; domain event |

Ports + ACL direction: skill:hexagonal-architecture, skill:bounded-context-mapping.

## Syntactic layer

Transport + mechanical shape: auth, rate limits, timeouts, parsing, webhook signatures, idempotency keys, external IDs, validation vs schema. **No business meaning.**

Good names: `PartnerWebhookEnvelope`, `VendorStatusCode`, `RawLoanPayload`.

## Semantic layer

Maps external concepts → **our** vocabulary. Concept table (external → internal → notes); list ambiguities + unsupported values. Lives at anticorruption seam — not scattered `if vendor ==` inside domain rules.

## Domain layer

Aggregates, domain methods, invariants, workflows, domain events. Consumes **internal** types after semantic map.

## Integration Design brief

Paste into ticket / ADR; fill per provider.

1. **Context** — external system, internal domain, capability, trigger, direction, sync/async, criticality.
2. **Syntactic** — transport, auth, payload, delivery guarantee, rate limits, versioning; DTOs; validation; failure modes.
3. **Semantic** — mapping table; ambiguities; unsupported values.
4. **Domain** — aggregates; domain methods; domain events; invariants.
5. **Application flow** — receive → syntactic validate → semantic translate → load aggregate → domain behavior → persist → publish events → integration audit.
6. **Testing** — syntactic, semantic, domain, contract.
7. **Observability** — logs, metrics, traces, alerts, replay, DLQ.
8. **Open questions**

Outbound retries / idempotency: skill:resilience-retries.

## Final rule

Partner **must not** define your domain. APIs → **syntax**. Business → **semantics**. Domain model guards meaning, invariants, behavior.

## Red flags

- Partner DTO types imported under `domain/`.
- One module parses HTTP, decides workflow, mutates aggregate.
- Raw external enums in use case with no mapping table.

## GOOD

```python
def to_offer_signal(raw: PartnerWebhookEnvelope) -> OfferEligibilitySignal:
    parsed = raw.verify_and_parse()
    return map_partner_semantics(parsed)
```

Syntactic envelope in; semantic `OfferEligibilitySignal` out for domain.

```python
class LoanApplication:
    def record_prequalified(self, at: datetime) -> None:
        ...
```

Domain speaks internal vocabulary only.

## BAD

```python
class LoanApplication:
    def apply_partner_body(self, body: dict) -> None:
        self.status = body["loan_status"]
```

External dict drives aggregate — syntax + semantics leaked into domain.

## Datasets and Analytics Extension

For analytical workloads, the three-layer model extends with two additional
layers below the domain:

| Layer | Question | Examples |
|---|---|---|
| Datasets | What cohort / slice? | Filter, join, aggregate domain events |
| Analytics | What insight? | KPIs, trends, ML feature vectors |

These layers consume **domain events and snapshots** — never raw syntactic or
semantic objects. Analytical queries read; they do not write back to the domain.
Keep dataset assembly and aggregation logic out of domain aggregates.

Cross-context analytical reads use published events or read-only projections —
never direct joins across bounded context tables
(skill:bounded-context-mapping).
