---
id: jsonb-first-search
kind: skill
title: JSONB-First Search (Postgres)
description: >
  Default jsonb + GIN for v0 search-heavy or schema-fluid features.
  Promote columns when schema stabilizes.
applies_when:
  - prototype ingest
  - unknown JSON shape
  - semi-structured search
  - avoid DDL churn early
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

# JSONB-First Search

Postgres `jsonb` + GIN for first cut. Migrate out when shape + integrity firm up ([skill:deprecation-and-migration](source/skills/deprecation-and-migration.md)).

## When

Prototypes, internal tools, webhook/event payloads, “we don’t know fields yet,” fast iteration before relational model is honest.

## Why

DDL + migrations expensive at v0. `jsonb` evolves without per-column migrations; GIN answers containment/existence queries.

## GIN flavors

| Opclass | Strength |
|---|---|
| `jsonb_ops` | `@>`, `?`, `?&`, `?|`, key paths — general |
| `jsonb_path_ops` | smaller/faster; containment `@>`-focused |
| `pg_trgm` on `::text` or extracted keys | `ILIKE` / substring — separate trade-off |

Pick opclass to match operators in hot queries.

## Operators (quick)

`@>` containment; `?` / `?&` / `?|` key existence; `->` / `->>` navigation; `jsonb_path_query` / path ops for complex extraction.

## Limits

No FK into nested keys. Weak DB-side validation vs typed cols. Uniqueness across dynamic paths is awkward. Observability harder when shape drifts silently.

## Migration trigger

Stable schema + frequent joins + integrity needed → promote hot keys to typed columns, constraints, FKs. Two-step: dual-write / backfill, then cut over (same playbook as deprecation skill).

## GOOD

`payload jsonb` + GIN(`jsonb_path_ops`) for `payload @> '{"status":"active"}'` on v0 webhook ingest.

## BAD

Five normalized tables before a single query works; schema churn blocks shipping the ingest path.
