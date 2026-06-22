# Plan: Site Reorganization — Working Groups, Partners, Regional Split, Tools, Search

## Context

The MBON hugo2 site needs a structural reorganisation across five areas:
1. **Working Groups** separated from regional network nodes into their own content section
2. **Partners** gets a full detail page and appears in the Network hero
3. **Regional MBONs** split into USA vs International in nav + hero
4. **Tools** gets a nav dropdown pre-filtered by type; tag scheme cleaned up (`type.*` → `tool.*`)
5. **Search** gets an autocomplete tag selector with AND logic

Papers content type (previous task) is already complete and committed.

---

## A. Working Groups — new `working-groups` content section

**Move** 6 files: `content/network/{biosound,biotrack,data-mgmt,eco-indicators,edna,indicators}.md`
→ `content/working-groups/`

Each gets:
- `kind_node:` removed
- `leads:` list added (name + org, e.g. `- name: John Smith\n  org: MBARI`)
- `aliases: [/network/biosound]` added so old URLs redirect

**Create:**
- `content/working-groups/_index.md` — title: Working Groups, summary
- `layouts/working-groups/list.html` — card grid using `.feature-row` pattern
- `layouts/working-groups/single.html` — hero + leads panel + content body + related methods CTA

**Update:**
- `layouts/partials/methods-band.html` — add "View Working Groups →" `btn--outline` alongside "Explore all methods" button
- `layouts/network/list.html` — remove `<section id="thematic">` entirely; add short "Working Groups" band with CTA button to `/working-groups/`
- `layouts/partials/header.html` — Working Groups column queries `"Section" "working-groups"` instead of `"Params.kind_node" "thematic"`
- `layouts/partials/footer.html` — `"network/#thematic"` → `"working-groups"`, label "Working Groups"
- `hugo.yaml` — add Working Groups as weight 2.5 in nav (between Network and Methods), or keep only in Network dropdown (recommendation: dropdown only, no top-level entry)

---

## B. Partners page

**`data/partners.yaml`:** add `description:` to every entry (one sentence each).

**`layouts/network/partners.html`:** change from logo grid to detail cards — logo + `<h3>` name + description paragraph + "Visit →" link.

**`layouts/network/list.html`:** add partner strip band (`.partner-strip` / `.partner-chip` markup, same as footer) at bottom of the Network hero `<section class="page-header">`, with caption "Strategic collaborators" and a "View all partners →" link to `/network/partners/`.

**`layouts/partials/header.html`:** replace the current Partners column (10 external links) with a single `<a href="/network/partners/">All partners →</a>` link appended to the Working Groups column (or as a minimal 4th column labeled "Partners").

**`layouts/partials/footer.html`:** add `<a href="{{ "network/partners" | relURL }}">Partners</a>` to the Network footer column.

---

## C. Regional MBON split — International vs USA

**Add `geo:` field** to each of the 12 regional node front matters in `content/network/`:
- `geo: International` → asia-pacific-mbon.md, europe-mbon.md, pole-to-pole-americas.md
- `geo: USA` → arctic, central-california, coastal-new-england, great-lakes, gulf-of-maine, mid-atlantic, northern-california-current, south-florida, southern-california-bight

**`layouts/partials/header.html`:** split the single "Regional MBONs" column into two:
```go
{{ $usa  := where $regional "Params.geo" "USA" }}
{{ $intl := where $regional "Params.geo" "International" }}
<div class="nav-dropdown__col">
  <span class="nav-dropdown__label">USA</span>
  {{ range $usa.ByTitle }}<a href="{{ .RelPermalink }}">{{ .Title | strings.TrimSuffix " MBON" }}</a>{{ end }}
</div>
<div class="nav-dropdown__col">
  <span class="nav-dropdown__label">International</span>
  {{ range $intl.ByTitle }}<a href="{{ .RelPermalink }}">{{ .Title | strings.TrimSuffix " MBON" }}</a>{{ end }}
</div>
```

**`layouts/network/list.html`:** replace single `$regional` grid with two subsections — "USA Nodes" and "International Nodes" — each with eyebrow + grid.

---

## D. Tools navbar dropdown

**`hugo.yaml`:** add `identifier: tools` to the Tools menu entry.

**`layouts/partials/header.html`:** add `{{ else if eq .Identifier "tools" }}` dropdown case:
```html
<div class="nav-dropdown__panel nav-dropdown__panel--single">
  <div class="nav-dropdown__col">
    <a href="{{ "tools" | relURL }}">All Tools</a>
    <a href="{{ "tools" | relURL }}?tool=Portal">Portals</a>
    <a href="{{ "tools" | relURL }}?tool=App">Apps</a>
    <a href="{{ "tools" | relURL }}?tool=Infographic">Infographics</a>
    <a href="{{ "tools" | relURL }}?tool=Library">Libraries</a>
    <a href="{{ "tools" | relURL }}?tool=Protocol">Protocols</a>
  </div>
</div>
```

**`static/js/tools-filter.js`:** add URL-param pre-activation at start of `DOMContentLoaded`:
```js
var urlTool = new URLSearchParams(window.location.search).get('tool');
if (urlTool) {
  var preBtn = bar.querySelector('[data-facet="tool"][data-value="' + urlTool + '"]');
  if (preBtn) preBtn.click();
}
```

**`data/tool_filters.yaml`:** replace `type` facet with `tool` facet; keep place, org, method facets:
```yaml
- facet: tool
  label: Type
  values:
    - {value: Portal,      name: Portal}
    - {value: App,         name: App}
    - {value: Infographic, name: Infographic}
    - {value: Library,     name: Library}
    - {value: Protocol,    name: Protocol}
```

---

## E. Tool tag cleanup — 16 content files

Drop entirely from all tool files: `type.Tool`, `type.Data`, `type.Instance`, `type.Dashboard`, `type.Portal`, `type.Infographic`
Rename everywhere: `org.NMS` → `org.NationalMarineSanctuaries`

| File | Action | New type tag(s) |
|---|---|---|
| biotrack-portal.md | update tags | `tool.Portal` |
| climate-dashboard-app.md | update tags | `tool.App`, `org.NationalMarineSanctuaries` |
| climate-dashboard.md | update tags | `tool.App`, `org.NationalMarineSanctuaries` |
| coastwatch-obis.md | update tags | `tool.App` |
| early-alert-dashboard.md | update tags | `tool.App`, `org.NationalMarineSanctuaries` |
| **edna-explorer.md → mbon-data-portal.md** | rename + update | `tool.Portal` + `aliases: [/tools/edna-explorer]` |
| infographic-cinms.md | update tags | `tool.Infographic`, `org.NationalMarineSanctuaries` |
| infographic-florida-keys-esr.md | update tags | `tool.Infographic` |
| infographic-iea-alaska.md | update tags | `tool.Infographic` |
| infographic-ocnms.md | update tags | `tool.Infographic`, `org.NationalMarineSanctuaries` |
| infographiq.md | update tags | `tool.Library` |
| pole-to-pole-atlas.md | update tags | `tool.Protocol` |
| **sanctuary-condition-reports.md → sanctuary-watch.md** | rename + update | `tool.Portal`, `tool.Infographic`, `org.NationalMarineSanctuaries` + alias |
| seascapes-viewer.md | update tags | `tool.App`, `org.NationalMarineSanctuaries` |
| seascapr.md | update tags | `tool.Library` |
| storymap-fk-fwri-water-quality.md | update tags | `tool.Infographic` |

Keep all `place.*`, `method.*`, `org.*` (non-NMS) tags unchanged.

**`layouts/partials/tag.html`:** extend the label-lookup loop to also search the `tool` facet values in `tool_filters.yaml`, and add a CSS class fallback for `tag--tool` prefix.

**`layouts/tools/single.html`:** update eyebrow from "Data & product" → "Tool".

---

## F. Tag / content consistency audit

| Location | Change |
|---|---|
| `layouts/partials/footer.html` | Tools col: `tools/edna-explorer` → `tools/mbon-data-portal`; label "Products" → "Tools" if still wrong |
| `layouts/network/single.html` | Aside: replace hardcoded `<span class="tag">Seascapes</span>` etc. with `{{ range .Params.tags }}{{ partial "tag.html" . }}{{ end }}` |
| `layouts/network/list.html` | Remove `id="thematic"` section; update any anchor links |
| `content/news/*.md` | Grep for `org.NMS` → rename; remove `type.Tool`/`type.Data`/`type.Instance` if present |
| `content/methods/*.md` | Same tag audit |
| `content/network/*.md` | Ensure `topic.Regional` (not `topic.regional`), `topic.Working-Group` removed (WGs moved) |
| `layouts/search.html` | Pagefind `filters` config: add `tool: "Tool type"` entry |

---

## G. Search — autocomplete tag selector with AND filtering

Replace `PagefindUI` in `layouts/search.html` with a custom widget using the programmatic Pagefind API (`/pagefind/pagefind.js`):

**UX flow:**
1. Text search input (keyword)
2. Tag input with dropdown autocomplete — user types, list shows matching `facet · Value` pairs from `pagefind.filters()`; click to add as chip
3. Active tag chips displayed inline, each with × to remove
4. AND logic: all selected tags must match — build filter object `{ method: ["Genomics"], type: ["Paper"] }` → `pagefind.search(query, { filters })`
5. Results rendered as title + excerpt + link items (custom HTML)

**Implementation sketch in `layouts/search.html` scripts block:**
```js
const pf = await import('/pagefind/pagefind.js');
await pf.options({ baseUrl: '/' });
const available = await pf.filters(); // { method: {Genomics: 42}, type: {Paper: 88} }
// Build flat autocomplete entries from available
// On change: call pf.search(textQ, { filters: chipFilters }) → render results
```

**CSS additions** to `static/css/components.css`: `.tag-chip` (dismissible chip in search bar), `.search-results` list styling. Keep `pagefind/pagefind-ui.css` for excerpt formatting if still linked, or remove it entirely.

---

## Verification

1. `hugo build` → 0 errors; page count grows by ~7 (6 WG pages + working-groups list)
2. `/network/` → hero has partner strip + "Strategic collaborators" + "View all partners →"; Regional split USA / International grids; "Working Groups" band with CTA
3. `/network/partners/` → cards with logo + name h3 + description + link
4. Network navbar → USA column (9 nodes), International (3), Working Groups (6), "All partners →" link
5. `/working-groups/` → list of 6 WG cards with leads shown
6. `/working-groups/biosound/` resolves; `/network/biosound/` 301-redirects via alias
7. Methods page → methods band shows "View Working Groups →" button
8. `/tools/` → filter bar has `tool` facet (Portal/App/Infographic/Library/Protocol); `type.*` buttons gone
9. Navbar Tools dropdown → 6 links; clicking "Portals" loads `/tools/?tool=Portal` with Portal pre-activated
10. `/tools/mbon-data-portal/` exists; `/tools/edna-explorer/` redirects via alias
11. `/tools/sanctuary-watch/` exists; `/tools/sanctuary-condition-reports/` redirects
12. `/search/` → type keyword, add tag chip "method · Genomics" → results narrow; add "type · Paper" → AND narrows further; remove chip → broadens
13. `hugo build` still 0 errors after all changes
