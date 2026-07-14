---
id: accessibility-and-inclusive-ui
kind: skill
title: Accessibility and Inclusive UI
description: "WCAG AA compliance, keyboard parity, and screen-reader contract for every interactive surface. Semantic HTML first. axe-core in CI enforces zero regressions."
applies_when:
  - building or reviewing a frontend UI
  - adding a form, modal, or interactive widget
  - shipping a user-facing screen
  - auditing keyboard or screen-reader support
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

# Accessibility and Inclusive UI

Semantic HTML first. Keyboard parity mandatory. Screen-reader contract explicit.
CI fails on new violations. Zero regressions is the only acceptable budget.

## Semantic HTML

Use the element whose semantics match the behavior. Never use `<div>` or
`<span>` where a native element exists:

- `<button>` for actions, `<a href>` for navigation.
- Landmark regions: `<header>`, `<main>`, `<nav>`, `<footer>`.
- Heading hierarchy (`<h1>`…`<h6>`) reflects document outline, not visual size.

Cross-ref skill:centralized-ui-components — enforce semantics once in the
catalog primitive, not per page.

## Keyboard Parity

Every action reachable by pointer must be reachable by keyboard:

- Tab order follows DOM order; never use `tabindex > 0`.
- Modal dialogs trap focus while open; return focus to the trigger on close.
- Custom widgets (combobox, date-picker) implement the ARIA Authoring Practices
  Guide pattern for that role.

## Visible Focus Ring

Never `outline: none` without a visible replacement. Provide `:focus-visible`
ring that meets 3:1 contrast vs adjacent background. Cross-ref
skill:design-aesthetic-commitment — the design token layer must include a
`--focus-ring` variable applied consistently.

## Screen-Reader Contract

- Accessible name comes from visible text first; `aria-label` only when label
  text is genuinely invisible.
- Dynamic state changes use `aria-live="polite"` (non-urgent) or `"assertive"`
  (errors only).
- Icons without adjacent text get `aria-hidden="true"` on the SVG plus a
  visually-hidden label on the parent button.

## Forms

```html
<!-- GOOD: label linked, error linked, autocomplete declared -->
<label for="email">Email</label>
<input id="email" type="email" autocomplete="email"
       aria-describedby="email-err" />
<span id="email-err" role="alert">Enter a valid email.</span>
```

Every input has `<label for>`. Errors linked via `aria-describedby`. Declare
`autocomplete` tokens per HTML spec section 4.10.18.7 (cross-ref
skill:i18n-discipline for `lang` attribute on `<html>`).

## States: Empty, Loading, Error, Partial

Each state requires a text affordance — not only color or spinner:

```html
<!-- GOOD -->
<button aria-busy="true" disabled>
  <span aria-hidden="true">⏳</span> Saving…
</button>

<!-- BAD: spinner with no text; screen reader announces nothing useful -->
<button><Spinner /></button>
```

## Color Contrast

- Body text: 4.5:1 contrast ratio vs background (WCAG AA).
- Large text (≥18pt / 14pt bold) and UI components: 3:1.
- Never use color as the sole signal (error border needs icon or text too).

## Motion

Wrap animations in `@media (prefers-reduced-motion: reduce)` or check the
`useReducedMotion` hook. Cross-ref skill:design-aesthetic-commitment.

## CI Enforcement

Add axe-core to Playwright or jest-axe. Failure budget = zero new violations:

```js
// jest-axe example
const { axe, toHaveNoViolations } = require("jest-axe");
expect.extend(toHaveNoViolations);

it("has no a11y violations", async () => {
  const { container } = render(<LoginForm />);
  expect(await axe(container)).toHaveNoViolations();
});
```

## GOOD

```html
<button type="button" aria-expanded="false" aria-controls="menu">
  Options
</button>
<ul id="menu" role="menu" hidden>
  <li role="menuitem">Edit</li>
  <li role="menuitem">Delete</li>
</ul>
```

Native button, ARIA expanded state, menu role, keyboard pattern correct.

## BAD

```html
<div class="btn" onclick="openMenu()">Options</div>
<div class="menu">
  <div onclick="edit()">Edit</div>
  <div onclick="del()">Delete</div>
</div>
```

No role, no keyboard access, no expanded state, no focus management.

## Red Flags

- `<div onClick>` or `<span onClick>` for interactive elements.
- `outline: none` or `outline: 0` without `:focus-visible` replacement.
- Modal that does not trap focus or loses focus on close.
- Async result announced only by color change with no live region.
- `aria-label` on every element regardless of visible text.
- CI skips a11y checks or violations are suppressed rather than fixed.
- New page ships with no axe-core coverage.
