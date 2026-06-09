---
id: sql-antipatterns
kind: skill
title: SQL Antipatterns
description: >
  Relational traps: multi-valued scalars, naive trees, weak keys, missing FKs,
  EAV, polymorphic soup, shredded columns, and wide flag matrices. Practical fixes.
applies_when:
  - schema review
  - SQL smell
  - data model sketch
  - legacy DB cleanup
agents:
  claude: { kind: skill }
  cursor: { kind: skill, glob: "**/*.{sql,ddl,psql,pgsql},**/migrations/**/*,**/schema.prisma" }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# SQL Antipatterns

For loops that duplicate joins, see [skill:n-plus-one-prevention](source/skills/n-plus-one-prevention.md). This skill covers storage and model traps.

## Jaywalking (multi-valued scalar)

**Trap**: CSV / pipes / JSON string of ids in one column. **Why**: no FK; `FIND_IN_SET` / split-in-app; bad membership indexes; races corrupt string. **Fix**: junction `(parent_id, child_id)` PK or UNIQUE + FKs both sides; arrays only with team agreement + GIN. **Smell**: `LIKE '%,3,%'` or app splits before `WHERE`.

## Naive trees (adjacency only)

**Trap**: `parent_id` + app walks depth with repeated selects. **Why**: O(depth) round trips; subtree expensive without strategy ([skill:n-plus-one-prevention](source/skills/n-plus-one-prevention.md)). **Fix**: pick one — `WITH RECURSIVE` + index on `(parent_id)`; closure table `(ancestor, descendant, depth)`; materialized path + btree prefix; `ltree` if ops OK. **Smell**: tree loaded node-by-node in a loop.

## ID required (surrogate tyranny)

**Trap**: opaque `SERIAL` everywhere when stable natural/composite exists. **Why**: duplicates; hidden meaning; wide meaningless keys. **Fix**: natural/composite PK when invariant + stable; else surrogate — document. Always UNIQUE on business key if surrogate PK. **Smell**: UNIQUE missing on `(email)` but PK is arbitrary int.

## Keyless entry (constraints omitted)

**Trap**: logical FK without constraint; missing `NOT NULL`; skipped CHECK “for speed.” **Why**: orphans; silent corruption. **Fix**: FK every dependency; explicit `ON DELETE`/`ON UPDATE`; CHECK until real enum; deferrable only for bulk load. **Smell**: child rows reference deleted parents.

## Entity–attribute–value

**Trap**: `(entity_id, attr_name, value_text)` triple store. **Why**: untyped soup; reporting SQL awful; validation only in app. **Fix**: real columns for stable attrs; bounded fluid → `jsonb` + CHECK / generated / partial ([skill:jsonb-first-search](source/skills/jsonb-first-search.md)); true plugin EAV isolated, not in core queries.

## Polymorphic associations

**Trap**: `(commentable_type, commentable_id)` → many tables. **Why**: no FK; typo orphans; CASCADE undefined. **Fix**: per-target join tables with real FKs; or nullable `post_id`/`issue_id` + CHECK exactly-one; read union in view if needed. **Smell**: table name string beside id.

## Multicolumn attributes

**Trap**: phone/money/date split across ints/cols. **Why**: invariant explosion; intl formats; partial updates desync. **Fix**: single column (`e164`, `numeric`, `timestamptz` / `tstzrange`); validate at boundary; generated cols only for hot slices.

## Metadata tribbles

**Trap**: `is_foo`, `has_bar` nullable columns forever. **Why**: wide sparse rows; stats rot; merge pain. **Fix**: key/value or `jsonb` slice; flags outside hot row; extension table on revision.

## Identifiers (cross-cutting)

UUIDv4 as btree PK → insert scatter. Prefer UUIDv7 / ULID when UUID required; bigint surrogate OK internal-only.

## Other traps

- **Types**: money ≠ float; phone ≠ int; dates ≠ raw strings.
- **Query**: `= NULL` wrong; unbounded `OFFSET`; `%needle%` as only search; `SELECT *` in services.
- **Concurrency**: read-modify-write without lock/version.
- **App**: dynamic SQL concat; swallowed errors.

## GOOD

Junction tags; closure or recursive tree; FKs on every parent ref; polymorphism via typed tables or nullable FK + CHECK; `jsonb` for evolving v0 attrs; UUIDv7 PK on exposed insert-heavy facts.

## BAD

Comma-separated FKs; tree via app recursion; `(type, id)` polymorphism without FK; dozens of nullable feature columns; UUIDv4 PK on hot insert table.
