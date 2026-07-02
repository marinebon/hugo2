# Harmonize the tag system around content interlinking

## Context

Tags on this site are a flat `facet.Value` namespace, but the facets serve
**four different jobs** that have gotten conflated, which is what's causing the
confusion:

1. **Content type** — `type.Paper`, `type.Dataset` (what a page *is*).
2. **Content subtype** — `tool.App`, `tool.Portal`, … (a finer type *within* one
   section; drives the Tools index filter).
3. **Descriptive attributes** — `method.*`, `place.*`, `topic.*`, `year.*`
   (cross-cutting axes shared by many content types).
4. **Entity references** — `org.OBIS`, `portal.OBIS` (point at a named
   organization/portal that has, or should have, its own content page).

The stated goal is **inter-linking content**: from any page, surface other pages
sharing its tags, and make its tags clickable to their own collections. Today
that barely works — tag chips on content pages are dead `<span>`s (only the
`/tags/` index links them), and "Related stories" on news just shows the 3
newest posts, not tag-related content. The `portal.*` situation is the sharpest
symptom: a dataset carries `portal.OBIS` tags **and** `sources[]`/`portal_primary`
fields, while `tools/obis.md` exists separately as `tool.Portal` — three parallel
"OBIS" structures that never link to each other.

**Outcome:** one documented mental model (facets have a `role`), every tag chip
clickable, a real "related by shared tag" section on every content page, and the
OBIS/GBIF/EDI/ERDDAP tool pages acting as hubs that aggregate their datasets and
related content. All interlinking is **derived at build time from tags** — never
baked into content — so adding a node or dataset needs no script re-run.

## Decisions (from user)

- **Portals:** keep `portal.*` as a facet (filters + `?portal=` deep-links stay
  working) **and** add two-way links between datasets and the portal tool pages.
- **/tags index:** group by facet, alphabetical within (years descending).
- **Org/place:** re-tag network nodes with their `place.*`/`org.*`, and let node
  pages aggregate related content by those tags — computed at build time.

## The model (documented, minimal enforcement)

Add a `role:` key to each facet in `data/tags.yaml`. Roles are semantic/display
only — they don't change the contribution pipeline:

| role | facets | behavior |
|------|--------|----------|
| `type` | `type` | the content type (Paper/Dataset) |
| `subtype` | `tool` | refines one section; section filter buttons |
| `attribute` | `method`, `place`, `topic`, `year` | cross-cutting browse/filter axes |
| `entity` | `org`, `portal` | term page features the matching content page (portal→`tools/<slug>`, org→partner/node) |

Guidance (docs, not code): **don't** mint a `topic.*` that duplicates a
`method`/`place`/`type` value (e.g. use `method.Genomics`, not `topic.eDNA`); if
both truly apply, tag both. Keep `topic` flat and open-set — no hierarchical tags
(Hugo's flat taxonomy makes them brittle).

## Changes

### 1. Canonical registry — `data/tags.yaml`
- Add `role:` to every facet (table above).
- Move the **used-but-undeclared `place` values** out of `aliases` into `values`
  so the filter bars and browse are complete: `Pole-to-Pole`, `Europe`, `Arctic`,
  `Antarctic`, `Monterey-Bay`, `Bering-Sea`, `Coastal` (keep genuinely one-off
  places like `Azores`, `Uruguay`, `Lisbon` as aliases — still labeled, still
  shown in the browse).
- For `org`/`portal`, add `entity_section:` (e.g. `portal → tools`) so templates
  can resolve the canonical page by slug.

### 2. Clickable tags everywhere — `layouts/partials/tag.html`
Make it backward-compatible so cards (which may sit inside a card link) stay safe:
- Called with a **string** (current) → render the `<span>` exactly as now.
- Called with a **dict** `(dict "value" . "link" true)` → render an `<a>` to the
  term page: `href = relURL (printf "tags/%s/" (lower $raw))` (Hugo lowercases
  taxonomy terms, so `lower` + `relURL` matches the real term URL and keeps the
  `/hugo2/` base path). Label resolution is unchanged.

Switch the tag lists on **single** templates to the linked variant (tools, data,
news, papers, events, methods, network, working-groups). Leave card partials
passing the bare string.

### 3. Related-by-tag — new `layouts/partials/related.html` + `hugo.yaml`
- Add Hugo Related Content config to `hugo.yaml`:
  ```yaml
  related:
    threshold: 20
    includeNewer: true
    toLower: false
    indices:
      - {name: tags, weight: 100}
  ```
- `related.html`: `{{ $rel := first 6 (site.RegularPages.Related .) }}`, render
  each through the existing type-aware `partial "card.html"` in a `grid-3`. Renders
  nothing if empty. This is the core interlinking piece and is fully build-time.
- Add a `{{ partial "related.html" . }}` "Related across the network" section to
  every single template. In `news/single.html` this **replaces** the naive
  "Related stories" block (which currently just lists newest news).

### 4. Portal ⇄ dataset ⇄ tool hub (the "everything OBIS" answer)
- **`layouts/data/single.html`:** in the existing "Available in" block, besides the
  external `sources[].url`, add an internal link to the portal's tool page when it
  exists: `{{ with site.GetPage (printf "/tools/%s" (lower .portal)) }}…{{ end }}`.
- **`layouts/tools/single.html`:** when the tool is a portal (has `tool.Portal`),
  add a "Datasets in this portal" stat linking to `/data/?portal=<Name>` with the
  count = number of datasets whose tags include `portal.<Name>`. Combined with the
  `related.html` section (shared `org.OBIS`/`place.*` tags), the OBIS tool page
  becomes the hub the user asked for.

### 5. /tags index — rewrite `layouts/tags/terms.html`
Group by facet, in `data/tags.yaml` order, headings from each facet's `label`:
- Iterate `.Data.Terms.Alphabetical` (already alphabetical; each has `.Name`,
  `.Count`, `.Page`), bucket by facet parsed as `index (split .Name ".") 0`.
- Render one section per facet with the human `label` heading, then the linked
  chips (reuse `tag.html`) with a small `.Count` badge. Years section sorted
  descending. Facets with no used terms are skipped.

### 6. Entity term pages — `layouts/_default/taxonomy.html`
Already groups a term's pages by content type. Add: when the term's facet is an
`entity` (`portal`/`org`), feature the matching content page at the top — for
`portal.OBIS` link `tools/obis`; for `org.*` link the partner (`data/partners.yaml`)
or a network node if one matches. Purely additive to the existing grouping.

### 7. Re-tag network nodes — `content/network/*.md` (14 files)
Add each node's `place.*` (and `org.*` where it hosts/partners an org) alongside
the existing `topic.Regional`, e.g. `south-florida-mbon` → `place.South-Florida`.
Assign per node by reading its `geo`/title; **flag the mapping for user review**
in the PR. The node page's `related.html` then aggregates datasets/tools/news
sharing that place/org — no harvest re-run required. `harvest_datasets.py` is
unchanged (it already stamps a dataset's own `place` from `NODE_PLACE`).

### 8. Contribution pipeline stays in sync
- Add the newly-promoted `place` labels to the `tags_place` dropdowns in
  `.github/ISSUE_TEMPLATE/add-news.yml` and `add-tool.yml`; add any non-trivial
  label→Value mapping to `TAG_ALIASES` in `scripts/issue_to_content.py`
  (e.g. `"Pole to Pole" → "Pole-to-Pole"`). Field→facet mapping is otherwise
  unchanged.

### 9. Styling + docs
- `static/css/components.css`: `a.tag` — remove underline, add hover state;
  small `.tag__count` for the /tags index. Reuse existing grid/card CSS otherwise.
- `CLAUDE.md` + `README.md`: document the facet `role` model, the build-time
  interlinking principle, the portal hub behavior, and the topic-vs-method
  guidance.

## Files to touch

- `data/tags.yaml` — roles, promoted place values, entity hints
- `hugo.yaml` — `related:` config
- `layouts/partials/tag.html` — linked variant
- `layouts/partials/related.html` — **new**
- `layouts/tags/terms.html` — group-by-facet rewrite
- `layouts/_default/taxonomy.html` — entity feature block
- `layouts/{news,tools,data,papers,events,methods,network,working-groups}/single.html`
  — related section + linked tags (+ portal specifics in data/tools)
- `content/network/*.md` — node place/org tags (14 files)
- `.github/ISSUE_TEMPLATE/add-{news,tool}.yml`, `scripts/issue_to_content.py` — dropdown sync
- `static/css/components.css` — `a.tag`, `.tag__count`
- `CLAUDE.md`, `README.md` — model + guidance

## Verification

1. `hugo --gc --minify --baseURL "https://marinebon.org/hugo2/"` exits 0, no
   stray files in `public/`.
2. `npx --yes pagefind --site public` then `python3 scripts/check_links.py public`
   exits 0 — confirms every new tag-chip link and portal/entity link resolves
   under `/hugo2/` (this is the real check that `lower`+`relURL` term URLs match).
3. Serve `public/` (`python3 -m http.server`) and spot-check in the browser:
   - `/tags/` shows one alphabetical section per facet with counts.
   - A dataset page links its portals to both the external record **and** the
     internal `tools/<portal>` page; the OBIS/GBIF/EDI/ERDDAP tool pages show a
     "Datasets in this portal" count linking to `/data/?portal=…`, plus a Related
     section.
   - `/data/?portal=OBIS` still filters (facet + deep-link intact).
   - A network node page (e.g. South Florida) shows related datasets/tools/news by
     its new place tag; its tag chips are clickable.
   - Tag chips on tool/paper/news/dataset pages navigate to their `/tags/…` term
     pages.
