// Page overlay annotator for screenshots. Paste once per page load — the functions
// live on `window`, so any navigation or reload wipes them and you paste again.
//
// __annotate(el, label, side)  el = a DOM element (not a selector). Draws a box around
//                              it, a label chip `gap` px to one side, and an arrow between.
//                              side: "auto" | "left" | "right" — where the LABEL sits.
//                              "auto" puts the chip right if it fits, otherwise left, so
//                              you only pass it explicitly to override.
// __clearAnno()                Removes the layer. Call before handing the browser back.
//
// ANNO.color must be a 6-digit hex — the box shadow appends an alpha suffix (`${C}40`),
// which only works on hex. Pick a colour that does not occur in the UI being shot.

const ANNO = { color: "#e5342a", chipW: 260, gap: 70 };

window.__annotate = (el, label, side = "auto") => {
  if (!el) return console.warn("__annotate: no element");
  if (!window.__annoLayer) {
    const l = document.createElement("div");
    l.id = "__annoLayer";
    l.style.cssText = "position:fixed;inset:0;z-index:2147483647;pointer-events:none";
    document.body.appendChild(l);
    window.__annoLayer = l;
  }
  const { color: C, chipW: W, gap: G } = ANNO;
  const r = el.getBoundingClientRect();
  const right = side === "auto" ? r.right + G + W <= innerWidth : side === "right";
  const box = document.createElement("div");
  box.style.cssText = `position:fixed;box-sizing:border-box;left:${r.left - 4}px;top:${r.top - 4}px;width:${r.width + 8}px;height:${r.height + 8}px;border:3px solid ${C};border-radius:6px;box-shadow:0 0 0 3px ${C}40`;
  const chip = document.createElement("div");
  chip.textContent = label;
  chip.style.cssText = `position:fixed;box-sizing:border-box;visibility:hidden;max-width:${W}px;background:${C};color:#fff;font:600 15px/1.35 system-ui,sans-serif;padding:8px 12px;border-radius:6px`;
  window.__annoLayer.append(box, chip);
  const c = chip.getBoundingClientRect();             // shrink-to-fit — measure, never assume chipW
  const chipL = right ? r.right + G : Math.max(8, r.left - G - c.width);
  const y = r.top + r.height / 2;
  chip.style.left = `${chipL}px`;
  chip.style.top = `${Math.max(8, y - c.height / 2)}px`;
  chip.style.visibility = "visible";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.style.cssText = "position:fixed;inset:0;width:100%;height:100%";
  const id = "ah" + Math.random().toString(36).slice(2);
  const x1 = right ? r.right + G - 4 : Math.min(chipL + c.width + 4, r.left - 8);
  const x2 = right ? r.right + 8 : r.left - 8;
  svg.innerHTML =
    `<defs><marker id="${id}" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="${C}"/></marker></defs>` +
    `<line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke="${C}" stroke-width="3" marker-end="url(#${id})"/>`;
  window.__annoLayer.append(svg);
};

window.__clearAnno = () => { window.__annoLayer?.remove(); window.__annoLayer = null; };
