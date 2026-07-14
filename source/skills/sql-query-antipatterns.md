---
id: sql-query-antipatterns
kind: skill
title: SQL Query Antipatterns
description: "Query smells: NULL handling, GROUP BY non-aggregates, RAND() sort, LIKE full-text, spaghetti queries, SELECT *. Fix each without rewriting the schema."
applies_when:
  - query review
  - slow query investigation
  - GROUP BY or aggregation logic
  - full-text search naively done
  - SELECT * in service code
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

# SQL Query Antipatterns

Query-level smells that produce wrong results or blow performance. Index shape →
[skill:sql-query-performance](source/skills/sql-query-performance.md). Storage/model
traps → [skill:sql-antipatterns](source/skills/sql-antipatterns.md).

## Fear of the Unknown

**Trap**: `WHERE col = NULL`, `WHERE col <> 'x'` silently excludes NULLs. **Why**:
NULL participates in three-valued logic (TRUE / FALSE / UNKNOWN); any comparison with
NULL yields UNKNOWN, which filters out the row. **Fix**: `IS NULL` / `IS NOT NULL`;
`COALESCE(col, default)` for default substitution; audit every `<>` predicate for
NULL leakage. **Smell**: `WHERE status <> 'deleted'` missing rows with `status IS NULL`.

```sql
-- BAD: misses rows where col IS NULL
SELECT * FROM items WHERE col <> 'archived';

-- GOOD
SELECT * FROM items WHERE col IS DISTINCT FROM 'archived';
-- or explicit:
SELECT * FROM items WHERE col <> 'archived' OR col IS NULL;
```

## Ambiguous Groups

**Trap**: `SELECT id, name, COUNT(*) FROM t GROUP BY name` — non-aggregated `id` in
SELECT without `GROUP BY`. **Why**: result is undefined (MySQL non-strict returns
arbitrary row; Postgres / ANSI error). **Fix**: aggregate every non-group column
explicitly (`MAX(id)`, `array_agg(id)`), or add to `GROUP BY`, or use window functions
(`ROW_NUMBER() OVER (...)`). Enable `ONLY_FULL_GROUP_BY` in MySQL. **Smell**:
`SELECT *` mixed with `GROUP BY` on a subset of columns.

```sql
-- BAD (MySQL non-strict silently picks arbitrary id)
SELECT id, status, COUNT(*) FROM orders GROUP BY status;

-- GOOD
SELECT status, COUNT(*), MAX(id) AS latest_id FROM orders GROUP BY status;
```

## Random Selection

**Trap**: `ORDER BY RAND() LIMIT n` or `ORDER BY RANDOM()`. **Why**: forces full-table
sort to assign a random key to every row — O(N log N) regardless of `n`. Kills
performance at scale. **Fix**: sample by id range (`WHERE id >= random_offset LIMIT n`
with a retry on empty); `TABLESAMPLE BERNOULLI(pct)` (Postgres) for approximate sample;
pre-shuffle in app for small sets already loaded. **Smell**: slow "random featured item"
query on a large table.

```sql
-- BAD
SELECT * FROM products ORDER BY RANDOM() LIMIT 5;

-- GOOD: id-range sample (approximate, fast)
SELECT * FROM products
WHERE id >= (SELECT FLOOR(RANDOM() * MAX(id)) FROM products)
ORDER BY id
LIMIT 5;
```

## Poor Man's Search Engine

**Trap**: `LIKE '%term%'` as the only full-text mechanism. **Why**: leading `%` prevents
any btree scan — sequential scan on every query (cross-ref
[skill:sql-query-performance](source/skills/sql-query-performance.md) sargability).
No ranking; no stemming; no stop words. **Fix**: `tsvector` + `tsquery` + GIN index
for Postgres full-text; `pg_trgm` GIN for substring / `ILIKE`; external engine
(Elasticsearch, Typesense) for relevance ranking, facets. **Smell**: `WHERE body LIKE
'%search_term%'` in a search endpoint with no index hint in `EXPLAIN`.

```sql
-- BAD
SELECT * FROM articles WHERE body LIKE '%postgres%';

-- GOOD: tsvector index + tsquery
CREATE INDEX articles_body_fts ON articles USING GIN (to_tsvector('english', body));
SELECT * FROM articles WHERE to_tsvector('english', body) @@ plainto_tsquery('postgres');
```

## Spaghetti Query

**Trap**: one giant query with cascading joins, subqueries, and cross-product
aggregations trying to produce a complex report in a single pass. **Why**: planner
loses ability to reason about selectivity; intermediate sets balloon; query becomes
unmaintainable; join fanout inflates aggregate counts. **Fix**: split into named CTEs
(`WITH`) for readability; split into two queries when result sets genuinely differ
(round trip cost < cost of correct planner estimate on joined mess). Verify counts
against smaller, simpler queries. **Smell**: query with 5+ joins, WHERE predicates on
aggregated values, and results that "seem off."

```sql
-- BAD: one query joining orders + line_items + promos inflating totals
SELECT u.id, SUM(li.price), COUNT(DISTINCT o.id), SUM(p.discount)
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN line_items li ON li.order_id = o.id
JOIN promos p ON p.order_id = o.id
GROUP BY u.id;

-- GOOD: separate aggregations, join results
WITH order_totals AS (
  SELECT o.user_id, COUNT(*) AS order_count FROM orders o GROUP BY o.user_id
),
item_totals AS (
  SELECT o.user_id, SUM(li.price) AS revenue
  FROM orders o JOIN line_items li ON li.order_id = o.id GROUP BY o.user_id
)
SELECT ot.user_id, ot.order_count, it.revenue
FROM order_totals ot JOIN item_totals it USING (user_id);
```

## Implicit Columns

**Trap**: `SELECT *` in service or application code. **Why**: schema drift (column
added, renamed, dropped) breaks callers silently or noisily; extra columns waste
network + deserialization; secrets/internal columns leak across layers; ORM mapping
becomes fragile. **Fix**: explicit column list at every service boundary; `SELECT *`
OK only for ad-hoc inspection or migrations with `INSERT INTO … SELECT *` where schema
is intentionally cloned. **Smell**: ORM model fetches `SELECT *` then serializes only
3 of 20 columns.

```sql
-- BAD
SELECT * FROM users WHERE id = $1;

-- GOOD
SELECT id, email, created_at FROM users WHERE id = $1;
```

## GOOD

`IS DISTINCT FROM` for NULL-safe comparisons; explicit `GROUP BY` all non-aggregated
cols; id-range or `TABLESAMPLE` for random picks; GIN full-text index instead of
`LIKE '%x%'`; CTEs to decompose multi-join reports; explicit column lists at service
boundaries.

## BAD

`= NULL`; `ORDER BY RANDOM()` on large tables; `LIKE '%term%'` as search; `SELECT *`
in API handlers; one 15-join query for a dashboard report that produces wrong totals.
