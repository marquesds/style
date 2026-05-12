---
id: n-plus-one-prevention
kind: skill
title: N+1 Prevention
description: >
  Detect and eliminate N+1 query patterns. Eager-load, batch, or DataLoader.
  Perf budget enforced at review time.
applies_when:
  - listing endpoint
  - serializing nested objects
  - new query in a loop
  - perf regression suspicion
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

# N+1 Prevention

One query for the parents. One query for the children. Not `1 + N`.

## Detection

| Tool | Use |
|---|---|
| Query log | Count queries per request; assert in tests |
| `EXPLAIN ANALYZE` | Confirm index usage and join shape |
| ORM debug (`echo=True` / `query_log`) | Spot the loop |
| Tracing | Look for fan-out spans on one parent |

Add `assert_query_count(<n>)` style helpers to integration tests so regressions break the build.

## Prevention Patterns

| Pattern | When |
|---|---|
| Eager load (`joinedload`, `selectinload`, `with: { include }`) | Known parent → child shape |
| Batched IN | Independent fetch by ids |
| DataLoader | Request-scoped batching of repeated lookups |
| Materialized view / projection | Heavy read path, expensive joins |
| Pagination cap | Bounded N upfront |

## Perf Budget

Per endpoint: max query count, max latency budget. Tests enforce.

```python
def test_list_sessions_uses_at_most_two_queries(client, db_metrics):
    db_metrics.start()
    client.get("/v1/sessions?limit=50")
    assert db_metrics.queries() <= 2
```

## GOOD

```python
async def list_sessions_with_owners(limit: PositiveInt) -> list[SessionView]:
    rows = await db.fetch_all(
        """
        SELECT s.*, a.name AS agent_name
        FROM sessions s
        JOIN agents a ON a.id = s.agent_id
        ORDER BY s.created_at DESC
        LIMIT $1
        """,
        limit,
    )
    return [SessionView.from_row(r) for r in rows]
```

One query. View built in app code. Bounded by `limit`.

## BAD

```python
async def list_sessions_with_owners(limit):
    sessions = await db.fetch_all("SELECT * FROM sessions LIMIT $1", limit)
    out = []
    for s in sessions:
        agent = await db.fetch_one("SELECT * FROM agents WHERE id = $1", s["agent_id"])
        out.append({**s, "agent_name": agent["name"]})
    return out
```

Classic N+1. 1 + N round trips. Latency scales with `limit`.

## Refactor Recipe

1. Reproduce in a benchmark or test that asserts query count.
2. Identify the loop calling the DB.
3. Pull foreign keys out into a list; batch a single `WHERE id IN (...)`.
4. Stitch results in memory.
5. Test query count again. Should be O(1) or O(log N) at worst.

## Red Flags

- ORM relationship loaded inside a loop.
- Serializer accesses `obj.related.field` without prefetching.
- Test suite has no query-count assertion.
- "Slow page" report → root cause is N+1, not missing index.
- Code comment "TODO: optimize later" near a list view.
