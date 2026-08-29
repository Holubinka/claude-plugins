# Folder structure

Which folder a file goes in, and what it is named. Applies principles 1, 2 and 6 from [SKILL.md](SKILL.md).

## Contents

- [The four strategies, and how to tell which is in use](#the-four-strategies-and-which-one-this-repo-uses)
- [Colocation](#colocation)
- [The promotion rule](#the-promotion-rule)
- [Component folder anatomy](#component-folder-anatomy)
- [Constants](#constants)
- [Types and styles](#types-and-styles)
- [utils vs helpers vs lib](#utils-vs-helpers-vs-lib)
- [Barrels](#barrels)
- [Import paths](#import-paths)
- [Naming](#naming)
- [A tree that satisfies these rules](#a-tree-that-satisfies-these-rules)

---

## The four strategies, and which one is in use

| Strategy | Shape | Breaks when | Enforcement |
|---|---|---|---|
| **Flat** | everything in `src/` | ~20 files | none needed |
| **By type** | `components/ hooks/ utils/ contexts/` | one feature's code scatters across four folders; the global folders become dumping grounds | none possible |
| **By feature** | `features/<name>/{api,components,hooks,types,utils}` + `shared → features → app` | needs lint zones or cross-feature imports creep back | `import/no-restricted-paths`, `eslint-plugin-boundaries` |
| **FSD** | layers `app → pages → widgets → features → entities → shared`, segments `ui/api/model/lib/config`, public API per slice | high entry cost; needs a whole team on board | `steiger`, `dependency-cruiser` |

**In an App Router project, prefer route-colocation** — a fifth option the App Router makes possible and Next.js explicitly sanctions as "split project files by feature or route". Feature code lives under the route that owns it; only genuinely shared code moves up. Where a repository already committed to one of the four above, keep it: mixing two strategies is worse than either.

It also settles a real disagreement in the sources: A1, A4, A6 and A8 argue for feature folders, while A7 argues features blur over time and grouping by type stays predictable. Route-colocation satisfies both — files are grouped by the route that owns them, with type-named files (`constants.ts`, `helpers.ts`, `styles.ts`) *inside* the folder.

**When an alternative would win:** move to `features/` once the same domain code is consumed by many routes and cross-feature imports need policing. Move to FSD at multi-team scale. Either decays without enforcement — and none of the tools above is installed here, so do not cite a rule the build does not check.

## Colocation

Place code as close to where it is used as possible. Dodds's three benefits: maintainability (related files stay in sync), applicability (you find what exists), and ease of use (no context switch).

In the App Router this is safe by construction: a folder is **not routable** until it contains `page` or `route`, so project files sit inside route segments without becoming URLs.

Tests colocate too — `OrderCard.test.tsx` beside `OrderCard.tsx`, never a mirrored `__tests__/` tree. End-to-end tests are the standard exception: they exercise the app from outside, so they live at the project root rather than beside any one component.

## The promotion rule

**Code starts colocated and moves up only when a second consumer appears**.

- Never pre-place a file in a shared folder "because it might be reused".
- Promote in the same commit that adds the second consumer, and update both imports there.
- The inverse holds: a shared folder with one consumer is wrong — move it back down.

This is the only thing that stops `utils/` and `hooks/` becoming dumping grounds.

**Worked example.** A `StatusBadge` used only by the order detail page lives at `app/customers/[customerId]/orders/[orderId]/_components/StatusBadge/`. When the order list page needs it too, the folder moves to `src/components/status-badge/` and both routes import `@/components/status-badge`. It does **not** go to `orders/_components/` — that folder is the list route's own, not a shared parent.

**Bad:** creating `src/components/status-badge/` on day one. One consumer means one home.

## Component folder anatomy

One component per folder. The folder is the unit; the files inside are its segments.

```
OrderCard/
├── OrderCard.tsx        the component — JSX and wiring, nothing else
├── OrderCard.test.tsx   colocated
├── constants.ts           literals used only here
├── helpers.ts             pure functions — no hooks, no JSX
├── styles.ts              typed CSSProperties
└── index.ts               one re-export
```

Add a file only when it earns its place — a component with no constants has no `constants.ts`. Sub-components used only by this one nest as `_components/` inside it.

**Never in the component file:** a second exported component, a helper that takes no props, a magic value, an API call.

**Bad** — the same code as one file:

```tsx
// OrderCard.tsx — 400 lines
const STATUS_COLOR = { DELAYED: "var(--warn)", /* … */ };  // ✗ un-shareable, un-greppable
function etaLabel(o) { /* … */ }                           // ✗ can't be tested alone
export function OrderCard() { /* … */ }
export function OrderList() { /* … */ }                 // ✗ second component in the file
```

**Good** — `helpers.ts` holds a pure function, testable on its own:

```ts
/** Format a delivery window ("3" when exact, else "3-5"). */
export function etaLabel(o: Pick<OrderRecord, "eta_min" | "eta_max">): string {
  return o.eta_min === o.eta_max ? `${o.eta_min}` : `${o.eta_min}-${o.eta_max}`;
}
```

## Constants

**Check for an existing token first** (principle 6). A mature design-token module usually exports the whole set for a concept — colour, background, icon *and* label — in one record:

```ts
// the design-token module
export const STATUS: Record<OrderStatus, { c: string; bg: string; icon: IconName; label: string }> = {
  DELAYED: { c: "var(--warn)", bg: "var(--warn-bg)", icon: "AlertTriangle", label: "Delayed" },
  // …
};
```

The standard failure is a component restating one field of that record locally, then a second component copying the first. **When you find an existing local copy, that is drift, not precedent** — a third copy is the red flag, and the honest move is to say the drift exists rather than to add to it. Consume the token; and where the token module is a vendored copy, do not edit it to extend it — change the source of truth and re-vendor.

**Do not use a token's `label` field as display text.** Labels inside a token record are hardcoded in one language. User-facing strings go through the translation catalogue.

Otherwise: `constants.ts` beside the component, `SCREAMING_SNAKE`, `as const`; promote by the rule above. **No magic value in JSX** — an unnamed number or string in a template is a constant that has not been named yet.

```tsx
// ✗ Bad
{orders.slice(0, 50).map(/* … */)}
<div style={{ maxHeight: 420 }} />
```

```ts
// ✓ Good — constants.ts beside the component
/** Rows rendered before the list virtualises. */
export const ORDERS_PAGE_SIZE = 50;
/** Panel height cap, px — matches the timeline pane. */
export const PANEL_MAX_HEIGHT = 420;
```

`50` and `420` mean nothing at the call site, and the next person changing one has no way to find the other place it was pasted.

## Types and styles

**Types follow their consumer.** Component props stay in the component file. Types shared across the app go to the app's shared types module. Contract types shared with the server are **re-exported**, never redefined — the shared types module re-exports the inferred output types, not the schemas themselves.

**Styles stay in the component folder**. Here that is a typed `CSSProperties` object in `styles.ts`; Tailwind supplies the theme tokens and CSS variables. Follow whichever the surrounding component already uses rather than mixing both in one folder.

## utils vs helpers vs lib

A real distinction, worth holding:

| Kind | Test | Example | Home |
|---|---|---|---|
| **helper** | knows our domain | `etaLabel(order)` | beside its component, or the shared lib folder once shared |
| **helper** | knows our rules | `trackingUrl(carrier, code)` | the shared lib folder, e.g. `lib/tracking-urls.ts` |
| **util** | would drop into an unrelated project unchanged | `clamp(n, lo, hi)` | the shared lib folder |
| **lib** | a preconfigured integration, not a function | the API client, the query client | the shared lib folder |

If you cannot say which of the three a new file is, it is not ready to be extracted — leave it in the component that uses it.

## Barrels

**Allowed:** a leaf `index.ts` re-exporting one component's public surface.

```ts
export { OrderCard, OrderCard as default } from "./OrderCard";
```

```ts
/* order-timeline — event timeline with optional inline notes.
   Public surface: the OrderTimeline component + the TimelineEventApi contract. */
export { OrderTimeline } from "./OrderTimeline";
export type { TimelineEventApi } from "./comments";
```

**Not allowed:** new aggregating barrels. Importing one symbol from an `export *` barrel pulls the whole module graph — circular imports, slower dev builds (one measured case went 11k → 3.5k modules after removal), and `optimizePackageImports` cannot rescue a barrel containing any non-re-export line.

Where barrels already exist, leave them and do not add another. Removing one is a separate, deliberate change with its own verification — the import rewrite it forces touches every consumer, so it does not belong inside an unrelated task.

```ts
import { useOrderShipments } from "@/lib/hooks/orders";   // ✓ one module
import { useOrderShipments } from "@/lib/hooks";           // ✗ pulls every other domain in too
```

## Import paths

Use whatever path alias `tsconfig.json` already defines for anything outside the current folder; relative paths only for same-folder siblings (`./constants`, `./helpers`). `@/*` → `./src/*` is one common form, `~/*` and `#/*` are others — read the config rather than assuming the prefix. Where none is configured, adding one is its own change, not something to slip into an unrelated task.

```ts
// ✗ Bad
import { useTestConnection, useSecretsStatus } from "../../../../../../../lib/hooks";
import { ApiError } from "../../../../../../../lib/api";

// ✓ Good
import { useTestConnection, useSecretsStatus } from "@/lib/hooks/core";
import { ApiError } from "@/lib/api";
```

Seven levels of `../` break the moment a folder moves and hide which layer is being crossed. In a codebase where both forms are already present, do not add more — fix the ones you touch, and leave the rest to a deliberate pass.

## Naming

- Component file = component name, PascalCase: `OrderCard.tsx` exports `OrderCard`.
- Route-colocated component folders are PascalCase, matching the component.
- Shared component folders are kebab-case: `order-timeline/`.
- Non-component modules are kebab-case: `tracking-urls.ts`, `status-label.ts`.
- Hooks are `use` + capital letter — and only if they call a hook.

## A tree that satisfies these rules

An illustration of the shape, not a layout to impose on a repository that already has one:

```
src/
├── app/                                   # routes; pages stay thin
│   └── customers/[customerId]/orders/[orderId]/
│       ├── page.tsx
│       └── _components/                   # private folder — not routable
│           ├── OrderCard/               # the anatomy above
│           └── ShipmentDrawer/
│               └── _components/           # nested, single-parent sub-components
├── components/<kebab-name>/               # used by 2+ routes
│   └── app-shell/hooks/                   # non-data hooks, owned by their tree
├── lib/
│   ├── hooks/<domain>.ts                  # every TanStack Query hook
│   ├── api.ts · types.ts · <name>.ts      # client, re-exported types, helpers and utils
└── vendor/{shared,ui}/                    # vendored — do not edit here
```

Where a `vendor/` tree mirrors another package, that other package is the source of truth: change it first, then mirror deliberately. Type-checking cannot see the drift, because each package compiles against its own copy.
