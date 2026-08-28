---
name: frontend-architecture
description: "Decides where frontend code goes and how it is split. Use when adding a component and choosing between a colocated and a shared folder, splitting a component that grew too big, deciding between a hook / a pure function / a component body for logic, placing constants, types, styles, utils or helpers, choosing where state lives (local, URL, or server cache), or drawing the Next.js Server/Client boundary. Covers React and Next.js App Router file and folder structure."
metadata:
  version: "1.0.0"
  tags: react, nextjs, app-router, project-structure, folder-structure, colocation, component-splitting, state-placement, rsc
---

# Frontend Architecture — where code goes

Placement and decomposition for React + Next.js App Router.

**Give the answer, not an essay.** For a placement question the output is a path and one line of why. Agents reach the right answer without this skill but take 800–1500 words to get there — this skill exists to make the answer immediate and identical every time.

## Navigation

| Read | For |
|---|---|
| **This file** | The six principles, the five-step procedure, the boundary with sibling skills |
| [folder-structure.md](folder-structure.md) | Which folder. Strategies (flat / by-type / feature / FSD), colocation, naming, constants, types, styles, barrels, imports, **utils vs helpers** |
| [component-organization.md](component-organization.md) | Which file, and how many. Splitting, composition, business-logic layers, hook extraction, state placement |
| [nextjs-organization.md](nextjs-organization.md) | App Router specifics. `_private` folders, route groups, `src/`, the `'use client'` boundary, RSC data access, Server Actions |

## 0. Read the repository first

This skill names the decisions; **it does not know your folder names.** Before applying it, establish two things and say what you found:

1. **Which placement strategy is already in use** — flat, by-type, feature-first, or FSD. [folder-structure.md](folder-structure.md) §1 describes each. The existing one wins; a second strategy introduced beside the first is worse than either.
2. **Where the shared tier lives** — the design-token module, the shared UI package, the app's own `lib`/`utils` folder, the contract types shared with the backend. Principle 6 is unenforceable until you know where to look.

Where the repository has no discernible convention, say so and apply the principles below as a proposal rather than as a finding.

---

## The six principles

Everything in the topic files is an application of one of these. When a rule and a principle seem to disagree, the principle wins and the rule is wrong.

1. **Colocate by default.** Place code as close to where it is used as possible. Distance from the consumer is a cost you pay on every read.
2. **Promotion needs a second consumer.** Nothing moves to a shared folder before a real second caller exists — and nothing stays shared once it drops back to one.
3. **Symptoms split components, never counts.** A long component with no problem is fine. Name the symptom or leave it alone.
4. **The home follows the kind of code.** Pure calculation → a function. Stateful behaviour → a hook. Wiring props into JSX → the component body. A function that calls no hook is not a hook.
5. **State lives at its narrowest correct scope.** Server data → the query cache. Shareable → the URL. Otherwise local. Derivable from what you already have → nowhere.
6. **Reuse before you create.** Search the shared tier — tokens, shared UI, `lib` — before adding a token, a helper, a hook or an endpoint. Two definitions of one concept drift on the next change.

## The five-step procedure

Run these in order for any "where does this go" question. Stop as soon as the answer is determined.

**1 — Name what it is.** Component · hook · pure function · constant · type · style · user-facing text · server-only module. The kind decides the file; the consumers decide the folder. If you cannot name it, it is not ready to be extracted.

**2 — Check it already doesn't exist.** Principle 6, and this is the step most often skipped. Design tokens are the usual casualty: a severity or status colour map defined once in the token module and then restated locally in two components is the standard shape of this failure. Search before you add, and if you find two definitions already, say so — the third is not the problem.

**3 — Count the consumers.** One → colocate beside it. Two or more, in different routes → promote to the shared folder for that kind. Zero — you are speculating; go back to step 1.

**4 — Pick the folder.**

| It is… | It goes in |
|---|---|
| a component used by one route | `app/<route>/_components/<Name>/` |
| a component used by 2+ routes | the shared components folder, one directory per component |
| a hook that calls the API | the shared hooks folder, one file per domain |
| a hook with state but no API call | `<Owner>/hooks/use<Name>.ts` — never the shared hooks folder |
| a contract type shared with the server | the shared contract module — re-export, never redefine |
| user-facing text | the translation catalogue if the app has one — **not** `constants.ts` |
| a project-specific function | `helpers.ts` beside it, or the `lib` folder once shared |
| a portable function | the `lib` folder |
| a constant | `constants.ts` beside it |
| a style | `styles.ts` beside it |
| anything reading a secret, token or database | a `server-only` module |

Detail and rationale for each row: [folder-structure.md](folder-structure.md).

**5 — Check the boundaries you just crossed.** Does it need `'use client'`, and is the directive on a leaf rather than a layout or a barrel? Would it add an aggregating `export *` barrel? Does the import cross a layer, so it should use the path alias instead of `../../../../`? Is anything secret now reachable from the client graph?

## Boundary with the sibling skills

The split is by **question asked**, not by technology.

| Question | Owner |
|---|---|
| *Where does it go?* | **frontend-architecture** (this) — folders, splitting, placement, boundaries |
| *Is it written correctly?* | a React-specific skill, if the project has one — purity, hook misuse, keys, memoization, a11y |
| *What does the framework do?* | a Next.js-specific skill, if the project has one — file conventions, RSC mechanics, metadata, caching |
| *Which ring does the backend code sit in?* | `engineering-paved-path:onion-architecture` |

Two overlaps are worth stating, because they are where advice from different sources collides:

- **Line and prop limits.** Style guides commonly state "max 200 lines" and "max 5–7 props". Principle 3 overrides that: counts prompt a check for a symptom, never a split.
- **The Server/Client boundary.** Framework mechanics are not this skill's; the placement consequence is — which file gets the directive, and what that means for the folder.

Do not load this skill for "why is this re-rendering", "fix this hydration error", or "write a test for this".

## Red flags

Stop when you catch yourself writing any of these.

| Red flag | Principle broken |
|---|---|
| "I'll put it in `components/` since it might be reused" | 2 — one consumer, one home |
| "It's over 200 lines, so split it" | 3 — name the symptom or leave it |
| "`useSeverityLabel` reads better" | 4 — it calls no hook, so it is not a hook |
| "I'll copy the fetched row into `useState` so I can filter it" | 5 — derive during render |
| "The filter can just be `useState`" | 5 — it is shareable, so it is URL state |
| "I'll add a small colour map here" | 6 — the token module already has one |
| "One more `export *` in `index.ts` is tidier" | 1 — it drags five module graphs with it |
| "`'use client'` on the layout is simpler" | 1 — it drags the whole subtree client-side |

## Review checklist

- [ ] New file sits at the shallowest level with ≥1 consumer, and no shallower (1, 2)
- [ ] Nothing was created that already existed in the shared tier (6)
- [ ] Any split names a symptom, not a line count (3)
- [ ] Nothing named `use*` that calls no hook (4)
- [ ] No `fetch` outside the data-access layer; no query data copied into `useState` (5)
- [ ] Shareable state is in the URL (5)
- [ ] No magic value in JSX; no constant restating a shared token (6)
- [ ] No new aggregating barrel; no new `../../../../` import
- [ ] `'use client'` on the leaf, not the layout or a barrel
- [ ] Nothing secret is reachable from the client module graph
