---
id: i18n-discipline
kind: skill
title: i18n Discipline
description: >
  No hardcoded user-facing strings at the boundary. Locale files as single
  source of truth. Locale-aware date/number formatting. ICU pluralization.
  LLM prose follows configured locale; machine fields stay in the system language.
applies_when:
  - adding any user-facing string
  - date or number rendering
  - pluralization logic
  - LLM feature producing prose shown to users
  - multi-locale deployment
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

# i18n Discipline

Hardcoded strings are coupling. Locale files are the contract.

## No Hardcoded Strings at the Boundary

User-facing text — labels, errors, notifications, email subjects — belongs in a
locale file, not in handler or template code.

```python
# GOOD
return t("errors.payment.declined", locale=user.locale)

# BAD
return "Your payment was declined."
```

## Locale Files as Single Source of Truth

One namespace per feature module. Key names encode context, not phrasing.
`errors.payment.declined` is stable; the English phrase behind it can change
without touching code.

Flat key hierarchy preferred over deeply nested. Avoid re-deriving the same
string under multiple keys — divergence is a bug.

## Locale-Aware Date and Number Formatting

Pass the locale to the formatter; do not call `strftime` with a hardcoded
format string in user-facing output.

```python
def format_date(dt: datetime, locale: Locale) -> str:
    return babel.dates.format_date(dt, format="medium", locale=locale)
```

Monetary amounts: use a locale-aware money formatter that handles decimal
separator, grouping, and currency symbol placement.

## Pluralization via ICU-Style Rules

Don't branch on `count == 1`. Use the locale's plural rules.

```python
# GOOD
t("items.count", count=n, locale=user.locale)  # locale file handles plural forms

# BAD
label = "item" if n == 1 else "items"
```

Many languages have more than two plural forms. Hard-coding English duality is
wrong for most locales.

## LLM Output

- **Machine fields** (IDs, statuses, tags, keys): always in the system language.
  These cross service boundaries and must not vary by user locale.
- **Prose shown to users** (summaries, explanations, notifications): pass the
  target locale to the model and validate that output matches the requested
  language before rendering.

Mixing is a bug: don't let a locale-specific prose field sneak into a
machine-readable status enum.

## Translation Hygiene

- Production strings: reviewed by a human translator, not auto-translated.
- Accents and diacritics matter; `résumé ≠ resume`.
- Missing translation key → raise in development, fall back to default locale
  in production with a structured log (not silently blank).

## GOOD

```python
class PaymentView(BaseModel):
    status: PaymentStatus          # machine field; always English enum
    message: str                   # populated via t("payment.status.declined")
    processed_at: str              # via format_date(dt, user.locale)
```

Status crosses API boundaries unchanged; message and date are locale-aware.

## BAD

```python
class PaymentView(BaseModel):
    status: str = "Declined"        # hardcoded English prose in a typed field
    message: str = f"{n} items"     # plural broken for non-English locales
```

## Red Flags

- String literals in HTTP handlers or templates instead of locale keys.
- `strftime("%B %d, %Y")` in user-facing output (US-only format).
- `if count == 1: ... else: ...` pluralization in code.
- LLM summary stored as English text regardless of user locale.
- Missing translation key renders as blank or raises 500 in production.
- Same concept under two different locale keys that drift apart over time.
