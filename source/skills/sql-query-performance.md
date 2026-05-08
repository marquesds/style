---
id: sql-query-performance
kind: skill
title: SQL Query Performance
description: >
  Index shape, sargable predicates, join/order strategies, pagination,
  and write cost. Vendor-agnostic mental model. Pair with ORM fan-out skill.
applies_when:
  - slow queries
  - new indexes
  - EXPLAIN review
  - pagination at scale
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  vibe:   { kind: skill }
---

# SQL Query Performance

Complements [skill:n-plus-one-prevention](source/skills/n-plus-one-prevention.md) (ORM fan-out). This is plan/shape on the database side.

## Mental model

B-tree index = sorted key → row locator. Not magic. Planner matches predicates + sort order to that structure.

## Composite / concatenated keys

Leftmost prefix rule: leading columns must match equality (or range on last used column) for the rest to help. Put equality columns first, range/inequality last. Column not in `WHERE` rarely helps unless it carries sort for `ORDER BY`.

## Sargable predicates

`WHERE LOWER(email) = $1` breaks a plain btree on `email`. Use expression index, normalize on write, or generated column. Prefer bind variables for plan reuse (vendor-specific literals still hurt).

## LIKE

Leading `%` kills btree prefix scan; trailing `%` can use index. Substring search needs trigram / full-text indexes (`pg_trgm`, GIN full-text), not default btree.

## Joins

Nested loop wants index on inner probe key. Hash join often scans both sides — index less critical. Merge join needs ordered inputs; indexes that deliver order help.

## ORDER BY / GROUP BY

If index order matches `ORDER BY`, planner may pipeline. Else sort/hash materializes — watch memory + latency.

## Pagination

Prefer keyset: `WHERE (created_at, id) < ($1, $2) ORDER BY created_at DESC, id DESC LIMIT n`. `OFFSET` grows cost linearly. Composite index aligned with sort + filter.

## Covering / index-only

`INCLUDE` cols (or narrow composite) avoid heap fetch when all needed cols live in index. Check “index-only” / “covering” in your vendor’s plans.

## Partial indexes

`WHERE deleted_at IS NULL` (or hot slice) shrinks index + improves selectivity when queries always filter that way.

## DML cost

Each index = extra write path. Budget count. Drop unused after measurement.

## Insert key shape

Random PK (e.g. UUIDv4) scatters inserts → page splits, fragmentation, WAL churn. Monotonic PK (sequence, UUIDv7, ULID) appends at leaf edge. Prefer time-ordered UUID when IDs must be UUID.

## GOOD

Composite `(agent_id, created_at DESC)` for `WHERE agent_id = ? ORDER BY created_at DESC LIMIT n`; PK UUIDv7 so inserts stay at leaf edge.

## BAD

Only `(agent_id)` index + UUIDv4 PK: scan/sort for the listing; PK index fragments on insert-heavy facts.
