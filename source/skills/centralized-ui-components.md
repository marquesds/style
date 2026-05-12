---
id: centralized-ui-components
kind: skill
title: Centralized UI Components
description: >
  Build UI components into a catalog before any page imports them. One source
  of truth per element; story file collocated; no hand-rolled duplicates on pages.
applies_when:
  - building or reviewing a frontend UI
  - adding a new reusable element (button, badge, modal, form field)
  - reviewing a page that inlines raw markup also found elsewhere
  - setting up or extending a component library or Storybook
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Centralized UI Components

One component, one catalog entry, zero hand-rolled duplicates.

## Why

Duplicated markup drifts: radius on one copy, padding on another, focus ring missing
on a third. Pairs with skill:design-aesthetic-commitment (the token layer that keeps
every component on-brand) and skill:code-simplification (duplicated snippet → shared
helper before the third copy lands).

## Workflow

1. **Check the catalog first.** Does a component for this element already exist?
   If yes, import it. If not, proceed.
2. **Create component + story before any page import.** The story is the spec and the
   smoke test. A component that has no story has no verified contract.
3. **Import only after the catalog renders.** Page code imports from the catalog;
   pages never define their own primitives.

## Naming and location

Collocate the story next to the component:

```text
src/components/
  Button/
    Button.tsx
    Button.stories.tsx   ← story ID mirrors component path
```

Story variations map 1-to-1 to real props (not invented states).
Phoenix Storybook equivalent: `core_components/<name>.story.exs` next to the
component module — same colocation rule, different extension.

## GOOD

```tsx
// Button.tsx
export type ButtonProps = {
  label: string;
  variant: "primary" | "ghost";
  onClick: () => void;
};

export function Button({ label, variant, onClick }: ButtonProps) {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {label}
    </button>
  );
}
```

```tsx
// Button.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta: Meta<typeof Button> = { component: Button };
export default meta;

export const Primary: StoryObj<typeof Button> = {
  args: { label: "Save", variant: "primary", onClick: () => {} },
};

export const Ghost: StoryObj<typeof Button> = {
  args: { label: "Cancel", variant: "ghost", onClick: () => {} },
};
```

```tsx
// CheckoutPage.tsx
import { Button } from "@/components/Button/Button";

export function CheckoutPage() {
  return <Button label="Pay now" variant="primary" onClick={handlePay} />;
}
```

Single source of truth. Story covers both variants. Page imports, never redefines.

## BAD

```tsx
// CartPage.tsx — hand-rolled inline button
<button
  className="rounded-md px-4 py-2 bg-blue-600 text-white"
  onClick={handleCheckout}
>
  Go to checkout
</button>

// CheckoutPage.tsx — drifted copy: different radius, missing focus ring
<button
  className="rounded px-4 py-2 bg-blue-600 text-white"
  onClick={handlePay}
>
  Pay now
</button>
```

Two pages, two slightly different primitives. Next page makes it three.
No story means no verified contract. Radius drifts silently.

## Red Flags

- Page imports raw HTML/JSX markup that mirrors markup on another page.
- Component shipped without a collocated story file.
- Story props diverge from the component's actual prop types.
- Catalog used as a marketing screenshot dump rather than the import source of truth.
- New page lands with inline primitives (`<button class="...">`) instead of catalog imports.
- Story added after multiple pages already import the component — contract written last.
