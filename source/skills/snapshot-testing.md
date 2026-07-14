---
id: snapshot-testing
kind: skill
title: Snapshot Testing
description: "Diff-reviewed output pinned to file. Use for complex rendered or serialized output. Review like code; never auto-accept. Pair with property and example tests, not as a replacement."
applies_when:
  - testing rendered templates, CLI output, or serialized formats
  - large complex output where field assertions are brittle
  - reviewing snapshot diffs before merge
  - deciding whether to accept a snapshot update
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

# Snapshot Testing

Diff-reviewed output pinned to file. Review like code; never auto-accept.

## When to Use

Large, complex outputs where field-by-field asserts are brittle or noisy: rendered
templates, serialized formats, CLI output, AST pretty-prints, API response shapes.

Pair with property tests and example-based tests (skill:tdd). Snapshots pin output
shape; they do not replace behavioral coverage.

## Review Like Code

Snapshot change = diff to read carefully. For each changed line:
1. Is this the intended new behavior?
2. Does the change indicate a regression elsewhere?
3. Would a narrower assertion catch this more precisely?

**Never bulk-accept.** One snapshot at a time. Accept intentional; investigate unexpected.

## Agent Constraint

Do not auto-accept or bulk-update snapshots in an agent run. Flag pending diffs for
human review. Use the `/snapshot-review` command.

## Keep Snapshots Focused

One snapshot per scenario, not one snapshot for the entire system output. Focused
snapshots produce focused diffs. A snapshot that changes on every feature is useless.

## Naming

Snapshot name = the scenario. `compress_empty_input` not `test_01_compress_variant_3`.

## Handle Non-Determinism

Timestamps, random IDs, and process IDs must be normalized before snapshotting:

```python
def normalize(output: str) -> str:
    return re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", "<timestamp>", output)
```

Tag non-deterministic snapshots with a comment. Fix the root cause; do not normalise
indefinitely.

## GOOD

```python
def test_render_invoice(snapshot):
    result = render_invoice(sample_order())
    snapshot.assert_match(result, "render_invoice_standard")
```

Reviewed on update. One scenario. Deterministic. Name explains the case.

## BAD

```python
def test_everything(snapshot):
    snapshot.assert_match(render_all(load_all_fixtures()), "full_output")
# accepted via --update-snapshots without reading the diff
```

One giant snapshot. Bulk-accepted. Any change anywhere passes silently.

## Red Flags

- `--update-snapshots` run in CI automatically without human review.
- Single snapshot file covers the entire system output.
- Snapshot diff accepted with "looks about right."
- Non-determinism fixed with a normalizer instead of removing the source.
- Snapshots committed as binary; diff is unreadable.
- Snapshot name encodes a number, not a scenario.
