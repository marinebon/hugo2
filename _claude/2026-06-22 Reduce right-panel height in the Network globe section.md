# Plan: Reduce right-panel height in the Network globe section

## Context

The right column of the globe band (`.globe-band__inner` — a `1fr 1fr` grid) has grown taller than the globe itself (`min(56vh,520px)` ≈ 500px on a laptop). The accumulated height comes from four stacked elements: a 2-sentence lead paragraph, 12 node-chips (9 USA + 3 International) wrapping across rows, and a node card that appears on selection with coordinates + large heading + blurb + CTA button. The fix applies three targeted reductions.

---

## Changes

### 1 — Shorten the lead text (`layouts/index.html`)

Replace the 2-sentence `lead` parameter with a single short line (~25 words vs ~50 now). Saves ≈ 56 px.

```
Before: "Each node monitors its own waters and contributes biodiversity data to shared,
         open standards — connecting science across every ocean basin.
         Select a region to spin the globe."

After:  "Click on an MBON node — or drag to spin the globe."
```

---

### 2 — Two-column chip layout (`layouts/partials/globe.html` + `layout.css`)

Wrap the USA and International chip sets in separate `<div class="node-chips__col">` containers so they sit **side by side** rather than stacked. Chips within each column wrap normally inside their ≈ 300 px half-width, fitting ≈ 2 per row.

**HTML change** (globe.html lines 23-32):
```html
<div class="node-chips">
  <div class="node-chips__col">
    <span class="node-chip-label">USA</span>
    {{ range $usa.ByTitle }}
      <button class="node-chip" data-node-id="{{ .File.ContentBaseName }}">{{ replace .Title " MBON" "" }}</button>
    {{ end }}
  </div>
  <div class="node-chips__col">
    <span class="node-chip-label">International</span>
    {{ range $intl.ByTitle }}
      <button class="node-chip" data-node-id="{{ .File.ContentBaseName }}">{{ replace .Title " MBON" "" }}</button>
    {{ end }}
  </div>
</div>
```

**CSS change** (layout.css — `.node-chips` block):
```css
.node-chips {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3) var(--space-4);
  margin-bottom: var(--space-4);
}
.node-chips__col {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
/* node-chip-label no longer needs flex-basis:100% — it's a flex column item */
```

Effect: USA chips (9) and International chips (3) fill their own column. Height is `max(USA-col, Intl-col)` rather than USA+Intl summed. Chips per column at ≈ 300 px wrap ≈ 2 per row → USA ≈ 5 rows, net height ≈ 160 px vs ≈ 180 px currently. More visually organized.

---

### 3 — Compact node card (`layouts/partials/globe.html` + `layout.css`)

Remove the coordinate row (not essential on the homepage; `globe.js` already guards with `if (f('coord'))` so no JS change needed). Shrink heading size, blurb font, padding, and CTA. Saves ≈ 60–70 px.

**HTML change** (globe.html lines 33-38):
```html
<div class="node-card" data-node-card>
  <h4 data-node-field="name" style="font:var(--type-card);color:#fff;margin:0 0 var(--space-2);"></h4>
  <p data-node-field="blurb" style="color:var(--text-on-dark-muted);font-size:var(--text-sm);margin:0 0 var(--space-3);"></p>
  <a class="btn btn--action btn--sm" data-node-link href="#">Open this region <i class="fas fa-arrow-right" aria-hidden="true"></i></a>
</div>
```

Changes vs current:
- `data-node-field="coord"` div removed (saves ≈ 24 px)
- `h3` → `h4` with `var(--type-card)` (22 px vs 28 px, saves ≈ 10 px + tighter margin)
- blurb `font-size` → `var(--text-sm)` (14 px vs 16 px)
- `btn--sm` (saves ≈ 8 px height)

**CSS change** (layout.css — `.node-card`):
```css
.node-card { padding: var(--space-4); }  /* was var(--space-5) — saves 16 px */
```

---

## Files modified

| File | What changes |
|---|---|
| `layouts/index.html` | `lead` param text shortened (1 line) |
| `layouts/partials/globe.html` | chips wrapped in `.node-chips__col` divs; node card trimmed |
| `static/css/layout.css` | `.node-chips` → grid 2-col; add `.node-chips__col`; `.node-card` padding reduced |

`static/js/globe.js` — **no changes needed** (already guards all `data-node-field` lookups with `if (f('…'))`).

---

## Verification

1. `hugo server` — visit homepage, resize to laptop width (≈ 1100–1400 px)
2. Confirm right panel height ≤ globe height: no overflow/scrollbar
3. Click each chip → node card shows name + blurb + CTA (no coord display)
4. Drag globe → rotation still works
5. Mobile (< 860 px) — `.globe-band__inner` already switches to 1-col; confirm chips still readable
