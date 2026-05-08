---
id: restful-http-design
kind: skill
title: RESTful HTTP Design
description: >
  Nouns not verbs. URL versioning. RFC 7807 errors. Cursor pagination.
  ETags + conditional requests. Idempotency keys for non-idempotent POSTs.
applies_when:
  - new HTTP endpoint
  - new HTTP API
  - reviewing HTTP design
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# RESTful HTTP Design

Resources, status codes, idempotency. Predictable shape. No surprises.

## Resource Modeling

Nouns plural. Verbs hidden in HTTP method.

| Path | Method | Action |
|---|---|---|
| `/v1/sessions` | GET | list |
| `/v1/sessions` | POST | create |
| `/v1/sessions/{id}` | GET | read |
| `/v1/sessions/{id}` | PATCH | partial update |
| `/v1/sessions/{id}` | DELETE | remove (idempotent) |
| `/v1/sessions/{id}/complete` | POST | named action when not CRUD |

## Versioning

URL versioning: `/v1/...`. Bump on breaking change. Run multiple versions side by side until clients migrate. Deprecate with `Sunset` header + ADR.

## Status Codes

| Code | Use |
|---|---|
| 200 | OK with body |
| 201 | Created (Location header) |
| 202 | Accepted, async |
| 204 | OK, no body |
| 400 | Validation error |
| 401 | Not authenticated |
| 403 | Authenticated, not authorized |
| 404 | Resource missing |
| 409 | Conflict (concurrent edit, idempotency replay mismatch) |
| 412 | Precondition failed (ETag mismatch) |
| 422 | Semantic validation error |
| 429 | Rate limited (Retry-After) |
| 5xx | Server problems only |

## Errors: RFC 7807 problem+json

```json
{
  "type": "https://api.example.com/problems/invalid-input",
  "title": "Invalid input",
  "status": 422,
  "detail": "field 'email' must be a valid address",
  "instance": "/v1/users",
  "errors": [{"field": "email", "code": "invalid_format"}]
}
```

`Content-Type: application/problem+json`. Stable `type` URI. Detail human-readable.

## Pagination: Cursor

Cursor-based, not offset. Stable across inserts.

```text
GET /v1/sessions?limit=50&cursor=eyJpZCI6ICJhYmMiLCAidHMiOiAiMjAyNS0wMS0wMVQwMDowMDowMFoifQ
→ {"data": [...], "next_cursor": "..."}
```

## Conditional Requests

ETags on GET. `If-Match` on PATCH/PUT/DELETE → 412 on mismatch. Optimistic concurrency for free.

## Idempotency

Non-idempotent POST (e.g. payment) → require `Idempotency-Key` header. Replay returns the original response. Mismatch on replay → 409.

## GOOD

```http
POST /v1/payments HTTP/1.1
Idempotency-Key: 7f5e3b1a-...
Content-Type: application/json

{"amount": 1000, "currency": "USD", "source_id": "src_abc"}
```

```http
HTTP/1.1 201 Created
Location: /v1/payments/pay_xyz
ETag: "v1"
Content-Type: application/json
```

## BAD

```http
POST /api/getOrCreatePayment?amount=1000&id=src_abc
```

Verb in path. Mixed query + body. No version. No idempotency key. Returns 200 even on validation failure.

## Red Flags

- Verbs in URLs (`/getUser`, `/processOrder`).
- 200 with `{"error": "..."}` body.
- Offset pagination on a write-heavy collection.
- `PATCH` without `If-Match` on shared resources.
- Same endpoint returns different shapes based on a query flag.
