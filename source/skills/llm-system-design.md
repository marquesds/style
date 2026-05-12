---
id: llm-system-design
kind: skill
title: LLM System Design
description: >
  LLM as product-layer planner and synthesizer over retrieved evidence, never
  sole oracle. Explicit confidence scoring, structured outputs, fake client for
  tests, conservative fallback, token-cost accounting.
applies_when:
  - shipping an LLM-powered product feature
  - multi-source evidence synthesis
  - structured extraction or classification pipeline
  - LLM output drives downstream business logic
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

# LLM System Design

LLM is a collaborator that synthesizes evidence. It is not the source of truth.
For security boundaries and prompt injection, see skill:llm-prompt-injection.

## LLM as Synthesizer, Not Oracle

Feed the model **retrieved, cited evidence**. Model answers over that corpus;
it does not reach into its training weights as the only basis. Caller can always
trace a claim back to a source record.

## Explicit Confidence Scoring

Don't rely on opaque model probability. Compute confidence from sub-scores that
reflect real epistemic properties:

| Sub-score | What it measures |
|---|---|
| Authority | Source is primary, citable, recognized |
| Independence | Sources are independent, not echoes |
| Timeliness | Evidence is recent enough for the domain |
| Consensus | Multiple independent sources agree |

Combine into a single score; expose it to callers. Never inflate.

## Structured Outputs

Define a schema before writing the prompt. Model output is validated against it.
Downstream logic depends only on the typed schema, not on prose parsing.

```python
class AnalysisResult(BaseModel):
    summary: str
    confidence: float  # [0.0, 1.0]
    sources: list[SourceRef]
    flags: list[str]
```

## Test with a Fake Client

Real model calls are slow, expensive, and non-deterministic. Inject a fake client
in tests. Stub responses modeled on at least one real live call first.

```python
class FakeLLMClient:
    def __init__(self, responses: dict[str, AnalysisResult]) -> None:
        self._responses = responses

    def analyze(self, prompt_key: str) -> AnalysisResult:
        return self._responses[prompt_key]
```

## Conservative Fallback

When the model is degraded or confidence is below threshold, return a
deterministic heuristic result — never inflate low-confidence output to look
like a high-confidence one.

```python
def with_fallback(result: AnalysisResult, threshold: float) -> AnalysisResult:
    if result.confidence >= threshold:
        return result
    return CONSERVATIVE_DEFAULT
```

## Token-Cost Accounting

Track tokens consumed per call; surface as a metric. Budget per pipeline run.
Fail loudly when a single call exceeds the budget — it usually signals a prompt
or context-assembly bug, not a model issue.

## GOOD

Retrieve evidence → score sub-dimensions → call model with structured schema →
validate output → apply confidence threshold → return typed result or fallback.
Fake client in unit tests; real client integration-tested once per schema change.

## BAD

```python
def analyze(text: str) -> str:
    return llm.complete(f"analyze this: {text}")
```

Prose in, prose out. No schema. No confidence. No fallback. Untestable.
Downstream parses free text — breaks on any model version update.

## Red Flags

- Model output parsed with `split()` or regex instead of a declared schema.
- Confidence reported as "high/medium/low" from model prose, not computed score.
- No fake client; every test calls the real API.
- Pipeline continues on low-confidence output instead of falling back.
- Token spend unmetered; no budget ceiling per run.
- LLM prompt built by concatenating user-submitted content (skill:llm-prompt-injection).
