---
id: threat-modeling
kind: skill
title: Threat Modeling
description: >
  Map trust boundaries and walk STRIDE before code exists. Abuse cases alongside
  use cases. Mitigations recorded in ADRs. Lightweight DFD for the surface.
  Distinct from owasp-top-ten (post-hoc map) and defensive-programming (runtime).
applies_when:
  - new feature with external-facing surface
  - cross-service or cross-tenant boundary
  - authentication, authorization, or data handling change
  - pre-design review or security spike
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

# Threat Modeling

Design the attacker out. Decisions recorded before the diff exists.

## Trust Boundaries First

Identify every point where data crosses a privilege or process boundary:

- Network edge (public Internet → internal service)
- Service-to-service (internal API call, queue message)
- Tenant/account boundary (data from one tenant read by another)
- Privilege escalation (user-level → admin-level action)
- External process boundary (subprocess, OS call, third-party SDK)

Draw a data-flow diagram (DFD) — even a text sketch — for the surface under review.
Label each crossing with trust level on each side.

## STRIDE Per Boundary Element

Walk each element and each crossing with the STRIDE checklist:

| Letter | Threat | Question |
|--------|--------|----------|
| **S** | Spoofing | Can an attacker impersonate a legitimate principal? |
| **T** | Tampering | Can data be modified in transit or at rest without detection? |
| **R** | Repudiation | Can an actor deny an action without a verifiable audit trail? |
| **I** | Info Disclosure | Can sensitive data leak to an unauthorized party? |
| **D** | Denial of Service | Can an attacker exhaust resources or block legitimate use? |
| **E** | Elevation of Privilege | Can a lower-privilege actor gain higher-privilege access? |

One abuse case per applicable category per boundary element. Skip categories that
genuinely do not apply — but state why, not just skip silently.

## Mitigations

Pair each abuse case with a concrete mitigation decision:

- Reference the skill that owns the implementation: skill:injection-defense,
  skill:owasp-top-ten, skill:defensive-programming, skill:secrets-never-in-repo,
  skill:resilience-retries.
- Record irreversible or architectural mitigations in an ADR.
- If mitigation deferred: explicit acceptance note + owner + review date.

## Output Format

```text
Element: <component or data flow>
Boundary: <from> → <to>
S: <abuse case> → <mitigation / accepted>
T: <abuse case> → <mitigation / accepted>
I: <abuse case> → <mitigation / accepted>
D: <abuse case> → <mitigation / accepted>
(omit letters that do not apply with a one-line rationale)
```

## GOOD

```text
Element: POST /v1/payments handler
Boundary: public Internet → payment service (unauthenticated edge)

S: Attacker replays a valid payment token for a different amount
   → HMAC-signed payload; idempotency key stored + compared on replay
     (skill:resilience-retries + skill:restful-http-design)

T: Request body modified in transit
   → TLS 1.2+ enforced; no fallback to plain HTTP (ADR-0012)

I: Payment amount logged with full card digits
   → PAN masked at ingress; structured logs omit raw card data
     (skill:observability)

D: Attacker floods endpoint, exhausts DB connections
   → Rate limiting per IP + per account (skill:rate-limiting-and-throttling);
     DB pool cap + circuit breaker on downstream (skill:resilience-retries)

R: Dispute: "I never authorized this charge"
   → Audit row written in same UoW as charge (skill:unit-of-work-and-transactions);
     non-repudiation via signed event in outbox

E: Regular user calls admin refund path via IDOR
   → Role check at handler entry; object-level permission test
     (skill:owasp-top-ten A01)
```

## BAD

```text
"We use TLS so we're good."
```

TLS addresses T (in transit) only. S / R / I / D / E still open. No abuse cases,
no mitigations, no ADR. Security review cannot verify coverage.

## Decline: DREAD Scoring

Full DREAD (Damage / Reproducibility / Exploitability / Affected users / Discoverability)
calibration cost exceeds value at typical team/codebase size. STRIDE + concrete
mitigations per boundary element is sufficient signal.

## Red Flags

- Feature shipped with no trust-boundary diagram and no STRIDE walk.
- Security review checklist is "we use HTTPS and ORM" (covers 1 of 6 STRIDE categories).
- Mitigation decision "fix later" with no owner or date.
- Threat model written after the PR is merged — ADR backdated.
- All six STRIDE categories listed as "N/A" without rationale.
