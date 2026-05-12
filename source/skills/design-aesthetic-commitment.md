---
id: design-aesthetic-commitment
kind: skill
title: Design Aesthetic Commitment
description: >
  Pick one aesthetic direction and hold it. Reject generic AI defaults. CSS tokens
  for all design decisions. Honor prefers-reduced-motion. Consistency beats
  imperfect-but-inconsistent.
applies_when:
  - building or reviewing a frontend UI
  - setting up a design system or token file
  - reviewing visual consistency across screens
  - starting a new web product from scratch
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

# Design Aesthetic Commitment

Pick one direction. Reject defaults. Commit fully.

## Pick and Hold

Aesthetic = a consistent set of decisions: typography, spacing, color tokens, motion.
Choose once, document in a token file, apply everywhere. Inconsistency across screens
is worse than an imperfect but consistent choice.

## Reject Generic Defaults

Generic AI-generated design is recognisable and signals no intentionality:

- Inter or system-ui as the only font choice
- Purple-to-pink gradient hero
- Three-card "what we offer" section
- Rounded corners on every element
- Animated counting numbers

Avoid these unless they are genuinely right for the product. If your first draft looks
like every other AI-generated landing page, that is a red flag.

## CSS Design Tokens

All aesthetic decisions live in variables. Changing the look = changing the token file,
not hunting through components.

```css
:root {
  --font-display: "Instrument Serif", Georgia, serif;
  --font-body: "Inter", system-ui, sans-serif;
  --color-ink: #1a1a1a;
  --color-paper: #f9f6ee;
  --space-unit: 8px;
  --radius: 2px;
}
```

## Honor `prefers-reduced-motion`

Every animation must be gated. Motion that cannot be disabled is an accessibility
failure.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Commit at Component Boundaries

Apply the full aesthetic to each component before moving on. "We'll polish later"
produces inconsistency. Consistent incomplete beats inconsistently polished.

## GOOD

Single `tokens.css`. Every component references tokens. All animations gated on
`prefers-reduced-motion`. Reading across screens, the UI is one thing, not a committee.

## BAD

Hero uses the project's display font; a different screen uses system-ui. Button radius
is 4px in one component, `rounded-full` in another. Two color palettes coexist with no
documented reason.

## Red Flags

- Multiple conflicting font families with no documented intent.
- Animations hard-coded with no `prefers-reduced-motion` gate.
- Magic numbers in CSS instead of token references.
- "Polish pass" deferred indefinitely after launch.
- UI looks identical to a default AI-generated template; no directional choice made.
