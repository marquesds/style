---
id: sql-physical-design
kind: skill
title: SQL Physical Design
description: >
  Physical design traps: money types, ENUM lookups, file storage in DB.
  Rounding errors, rigid enums, phantom files.
applies_when:
  - schema design
  - money or decimal columns
  - enum / lookup tables
  - file attachment storage
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

# SQL Physical Design

Physical column and storage decisions that cause silent data loss or schema pain.
Query smells → [skill:sql-query-antipatterns](source/skills/sql-query-antipatterns.md).
Storage/model traps → [skill:sql-antipatterns](source/skills/sql-antipatterns.md).

## Rounding Errors

**Trap**: `FLOAT` / `DOUBLE` for money or any exact decimal. **Why**: IEEE 754 binary
representation cannot express most decimal fractions exactly — `0.1 + 0.2 ≠ 0.3`;
accumulated rounding errors surface in totals, tax, and financial reports. **Fix**:
`NUMERIC(p, s)` / `DECIMAL(p, s)` for exact arithmetic; or store as minor-unit integer
(`cents`); at app boundary use `Decimal` / `BigDecimal`, never float. **Smell**:
`FLOAT` column named `price`, `amount`, `rate`, `tax`.

```sql
-- BAD
CREATE TABLE orders (total FLOAT);

-- GOOD
CREATE TABLE orders (total NUMERIC(12, 2));
```

## 31 Flavors

**Trap**: native `ENUM('active','inactive','pending')` for fluid lookup sets. **Why**:
adding a value requires `ALTER TABLE` (lock on MySQL < 8; schema change everywhere);
values invisible without `SHOW COLUMNS`; no FK to attach metadata; impossible to query
"all valid statuses" without DDL inspection. **Fix**: lookup table with FK — values are
rows, not DDL; add without `ALTER`; attach label, display order, deprecation flag.
Reserve `CHECK` constraint for truly fixed sets that never grow (e.g. `('M','F','X')`).

```sql
-- BAD
CREATE TABLE users (status ENUM('active','inactive','pending'));

-- GOOD
CREATE TABLE user_statuses (code TEXT PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE users (
  status TEXT NOT NULL REFERENCES user_statuses(code)
);
```

## Phantom Files

**Trap**: storing file system paths in a `VARCHAR` column without atomicity. **Why**:
DB row and file can diverge — row deleted, file stays (orphan); file deleted, row
references missing path (broken ref); no transactional guarantee between FS and DB.
**Fix**: pick one strategy and commit:

- **Bytes in DB** (`BYTEA` / `BLOB`): atomic with row; backup covers files; OK for
  small blobs (< a few MB). Backup and WAL bloat for large files.
- **Object store** (S3, GCS, etc.) with content-addressed key + DB row in same UoW:
  write key to object store first (idempotent PUT by content hash); persist row with
  that key in the same transaction (cross-ref [skill:unit-of-work-and-transactions](source/skills/unit-of-work-and-transactions.md)).
  Orphan cleanup: periodic reconcile; async delete after row deleted.

**Smell**: `profile_photo VARCHAR(255)` containing `/uploads/user/42/avatar.png`.

```sql
-- BAD: path with no atomicity guarantee
ALTER TABLE users ADD COLUMN avatar_path VARCHAR(255);

-- GOOD: content-addressed key; row + storage write share UoW
ALTER TABLE users ADD COLUMN avatar_key TEXT;  -- e.g. sha256 hex or UUID
```

## GOOD

`NUMERIC(12,2)` for money; lookup table for statuses with FK; content-addressed object
store key written in same UoW as the parent row; small blobs in `BYTEA` when backup
story covers it.

## BAD

`FLOAT` for currency accumulation; `ENUM` that needs an `ALTER` every quarter; file
paths in DB with no orphan-cleanup strategy and no atomic write.
