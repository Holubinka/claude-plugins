---
name: annotated-screenshots
description: "Produces screenshots with boxes, labels and arrows pointing at real elements on a running page, including before/after pairs. Use when a UI change has to be shown rather than described — for a ticket, a pull request, a release note or documentation — or when asked to point at a specific control in an image. It injects an overlay into the live page so the callouts land on actual element coordinates instead of being guessed at afterwards."
metadata:
  version: "1.0.0"
keywords: [screenshots, ui, annotation, documentation, browser]
---

# Annotated screenshots

A screenshot with an arrow on it answers "which button" in one glance. This produces them by
**injecting an overlay into the running page**, so a box lands on the element's real coordinates
rather than on a guess about where it was.

Works with any browser automation that can evaluate a script in the page and save a screenshot to a
file — a DevTools MCP server, Playwright, Puppeteer. Nothing here is specific to one of them.

## Procedure

**1 — Decide what to capture.** One image per claim. A change that alters three things is three
images, not one crowded one. Before/after pairs only where the *difference* is the point; otherwise
the after is enough and the before is noise.

**2 — Name the files in reading order** — `1-`, `2-`, `3-` prefixes with a short slug:
`1-orders-list-before.png`, `2-orders-list-after.png`. Whoever pastes them into a document will do it
in filename order, and the prefix is the only thing keeping that order.

**3 — Get the page into the state you want, and note what you changed.** A filter set, a row
selected, a dialog opened. You will need to put it back.

**4 — Inject the annotator.** Read `assets/annotator.js` and evaluate its contents in the page. It
defines two functions on `window`:

```
__annotate(el, label, side)   el is a DOM element, not a selector. Draws a box around it,
                              a label chip to one side, and an arrow between them.
                              side: "auto" | "left" | "right" — where the LABEL sits.
__clearAnno()                 Removes the overlay layer entirely.
```

**They live on `window`, so any navigation or reload wipes them.** Re-inject after each one.

**5 — Annotate.** **At most two or three callouts per image.** Past that the reader is decoding a
diagram instead of seeing a screen, and each extra arrow costs the others their weight.

**6 — Capture the viewport, not the full page.** A fixed-position overlay does not survive
full-page stitching: the browser scrolls, the overlay stays put, and the boxes appear repeatedly at
the wrong offsets. If the subject does not fit in the viewport, take two images rather than one
stitched one.

**7 — Read the image back.** Open the file you just wrote and look at it. This is the step that is
easiest to skip and the one that catches everything — a box on the wrong row, a chip off-screen, a
tooltip that opened over the subject, a label covering the value it points at.

**8 — Clear the overlay and restore the UI state** you changed in step 3. Then say where the files
are, by absolute path.

`traps.md` carries the four cases where a naive capture produces a wrong image.

## The colour

`ANNO.color` at the top of `assets/annotator.js` must be a **six-digit hex**. The box shadow appends
an alpha suffix (`${C}40`), which is only valid on hex — a named colour or `rgb()` silently produces
no shadow.

Pick one that does not occur in the interface being photographed. A red arrow on a screen full of
red error states points at nothing.

## Rules

- **Never annotate a screenshot after the fact** by drawing boxes at estimated coordinates. That is
  the failure this exists to prevent: it looks right at authoring time and is wrong by a row.
- **Never seed data to make a screen look fuller.** A screenshot is evidence. Three real rows are
  worth more than thirty invented ones, and the invented ones will be quoted back at you.
- **Do not photograph something that is not working yet.** An annotated screenshot reads as proof.
- **Redact before you capture, not after.** Real names, tokens and account numbers in a screenshot
  are in the ticket forever. If the page shows them, change the data or crop the region before the
  capture, not by editing the file afterwards.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Full-page capture with the overlay on | Capture the viewport. The overlay is fixed-position and does not stitch |
| Passing a selector to `__annotate` | It takes an element. Query it first |
| Five callouts on one image | Two or three. Split it |
| Not reading the image back | Open it. Half of all bad callouts are visible immediately and invisible in the code |
| Leaving the overlay in place | `__clearAnno()` before handing the browser back, or the next screenshot has your boxes on it |
| Re-annotating after a reload without re-injecting | Navigation wipes `window`. The call silently does nothing |
