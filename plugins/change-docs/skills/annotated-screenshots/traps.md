# Four ways a capture comes out wrong

Reference for `annotated-screenshots`. Each of these produces an image that looks plausible and is
wrong, which is the only kind worth writing down.

## 1 — A virtualised table does not render the rows you cannot see

Grid libraries that virtualise — most of the popular ones do — keep only the visible window in the
DOM. Querying for a row that is scrolled out returns nothing, and `__annotate` warns and draws
nothing, which is easy to miss in a batch.

**Scroll the grid's own inner container**, not the window, until the row is in view; then query, then
annotate. Confirm the element exists before you call, rather than after you look at the file.

The same applies to anything lazily mounted: a collapsed accordion section, an inactive tab panel, a
list behind "show more".

## 2 — A native `<dialog>` sits above every z-index you can set

An element opened with `showModal()` lives in the browser's **top layer**, which is above the entire
stacking context. The overlay uses `z-index: 2147483647` — the maximum — and is still painted
underneath it.

Two workable options:

- Annotate what is *inside* the dialog only, and accept that a callout cannot point at it from
  outside.
- Capture the dialog and the page beneath it as two images.

Do not try to raise the overlay. There is no value that wins, and an hour disappears into finding
that out.

## 3 — The viewport is the frame, and the frame is a decision

A screenshot at 1280 wide and one at 1920 are different images of the same feature, and a layout
that reflows will look like a different implementation. **Set the viewport explicitly** and mention
the size when the layout depends on it.

Capture the viewport, never the full page, whenever the overlay is on — see the skill body. Where a
subject genuinely does not fit, two viewport captures beat one stitched image with duplicated boxes.

## 4 — The page is still moving when you capture

A capture taken during a transition catches the element mid-flight, and the box lands where it was
rather than where it settles. Skeleton loaders, toasts on a timer, an entrance animation, a chart
that draws in — all of them produce an image that is technically of the right screen and shows the
wrong thing.

Wait for the state you are photographing to be *settled*, not merely present. Where the interface has
a loading indicator, wait for its absence rather than for a fixed delay.

A related case: a tooltip or a hover state opened by the pointer being where the automation left it.
Move the pointer somewhere neutral before capturing, unless the hover state is the subject.
