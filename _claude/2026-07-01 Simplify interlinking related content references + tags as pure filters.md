# Simplify interlinking: `related:` content references + tags as pure filters

## Context

The tag system grew a confusing **"entity reference"** category — the `node.*` facet and
the `entity` role on `org`/`portal` — that tried to make *tags* act as links to *content
pages*. It doesn't hold up, and the user hit every seam:

- `/tags` "MBON nodes" showed **1 referenced node** while **13 nodes** exist.
- `org.*` can't link to a page — partners (GOOS, IOOS, …) are external-link cards in
  `data/partners.yaml`, not pages.
- **OBIS appears three times** (`/tools/obis` page, `org.OBIS`, `portal.OBIS`) with no
  single home.
- The `/tags` "Content types" row just duplicates the top nav / section index pages.
- Curated relationships don't surface: `methods/indicators` ↔ its 3 working groups only
  share the popular `method.Indicators` tag (on 15 items) and get out-ranked out of the
  top-6 Related.

**Goal (from the user):** link a page directly to *specific other pages* (e.g.
`/working-groups/indicators`, `/network/pole-to-pole-americas`) **without inventing
parallel tags**; keep tags for faceted **filter/search**; make each entity's own content
page its single home — while OBIS etc. stay filterable in `/tools/`, `/data/`, and search.

## Model — two clean mechanisms + structure

1. **Content type** = structural (the section, `.Type`). Not a tag; reachable via nav /
   section pages. (`type.*` already retired.)
2. **Tags** = faceted labels for **filter & search**: `tool`, `method`, `place`, `topic`,
   `year`, `org`, `portal`. One flat kind — no "entity/reference" subcategory. **`org` =
   who *built* a tool (the developer); `portal` = whose *data* it uses / where a dataset is
   served** (OBIS/GBIF/EDI/ERDDAP). `portal` now filters **both** `/data/` and `/tools/`.
   **OBIS is a portal, not an org** — tools tagged `org.OBIS` actually use OBIS data, so
   they move to `portal.OBIS`, and OBIS leaves the `org` facet. These keep OBIS/GBIF/GOOS
   filterable in `/tools/`, `/data/`, and Pagefind.
3. **`related:`** (NEW) = front-matter list of **content-page paths** for curated
   page-to-page links, rendered in the "Related" section and **bidirectional via
   backlinks** — so a referenced page (`/tools/obis`, `/network/*`, `/working-groups/*`,
   `/methods/*`) becomes the hub of everything pointing at it, with **no parallel term
   page**.

**Why keep `org`/`portal` as tags** (not fold into `related:`): most orgs have **no
content page** to point at (GOOS/IOOS/Sanctuaries/FWRI…), and org + portal power the
Tools/Data filters + search the user wants preserved. The page-backed portal
(`/tools/obis`) becomes OBIS's single hub via backlinks + its "datasets in this portal"
query, while `portal.OBIS` stays the filter/search handle.

## Decisions (from user Q&A)
- `/tags` "Content types" row → **remove**.
- methods ↔ working groups → **curate with `related:`**.
- Retire `node.*`; add `related:`; keep `org`/`portal` as filter facets; OBIS stays
  filterable + searchable.
- **OBIS is a portal, not an org:** drop OBIS from the `org` facet; convert existing
  `org.OBIS` → `portal.OBIS`; add a **Portals** section to the `/tools/` filter.

## Changes

### 1. `related:` rendering — `layouts/partials/related.html`
Build the "Related across the network" list from, in order (dedup by `.RelPermalink`, cap 6):
1. **Curated** — `site.GetPage` each `.Params.related` path (form `/section/slug`, confirmed working).
2. **Backlinks** — pages whose `.Params.related` resolves to the current page (loop
   `site.RegularPages`, `site.GetPage` each related value, compare `.RelPermalink`;
   GetPage is memoized — fine at ~450 pages). Compare via `.RelPermalink`, never `eq` on
   page objects.
3. **Tag-based fallback** — existing weighted shared-tag logic fills remaining slots.
Keep `excludeSection`/`heading`/`count`. Entity-weight list → `slice "org" "portal"` (drop `node`).

### 2. Make `related:` searchable — Pagefind
In the `.Kind "page"` pagefind block in `layouts/_default/baseof.html`, add one
`data-pagefind-meta="related"` span holding the comma-joined **titles** of the related
pages (resolved via GetPage), inside the existing `data-pagefind-ignore` hidden div.
(Searchable metadata, not per-page filter buttons — OBIS stays a filter *chip* via its
kept `org`/`portal` tags.)

### 3. Retire `node.*`
- `data/tags.yaml`: delete the `node` facet block; drop `role: entity` + `entity_section:`
  from `org`/`portal` (role → `attribute`); **add `tools` to `portal.filters` (→
  `[data, tools]`)** so the Tools filter shows a Portals section; **remove `OBIS` from the
  `org` values**.
- `layouts/_default/taxonomy.html`: delete the entity-feature ("Its page") block.
- `static/css/tokens/colors.css`: remove `--facet-node`/`--facet-node-deep`;
  `static/css/components.css`: remove `.tag--node`.
- Migrate the 5 `node.*` files → drop the node tag, add `related: [/network/pole-to-pole-americas]`:
  `content/news/{sea-of-cortez-fieldwork,mbon-pole-to-pole-progress,uruguay-rocky-shore-workshop}.md`,
  `content/tools/pole-to-pole-atlas.md`; and remove the **self**-tag from
  `content/network/pole-to-pole-americas.md` (backlinks now surface its content).

### 4. Collapse `/tags` — `layouts/tags/terms.html`
Remove the "Content types" section and the "References" block; render one flat set of tag
facets: **Tool types, Methods, Regions, Topics, Years, Organizations, Portals**. Trim the
intro (drop the two-systems / references framing).

### 5. methods ↔ working groups — `related:` refs
Add `related:` to method pages that have working groups (per audit; backlinks show the
reverse on each WG page automatically):
- `content/methods/indicators.md` → `/working-groups/indicators`, `/working-groups/eco-indicators`, `/working-groups/data-mgmt`
- `content/methods/acoustics.md` → `/working-groups/biosound`
- `content/methods/genomics.md` → `/working-groups/edna`
- `content/methods/tracking.md` → `/working-groups/biotrack`

### 6. OBIS: org → portal
Convert every `org.OBIS` tag → `portal.OBIS` (skip if the file already has `portal.OBIS`):
chiefly `content/tools/*.md` (tools that use OBIS data, incl. `content/tools/obis.md`
itself), plus any `news`/`events` carrying `org.OBIS` — if such a post is *about the OBIS
organization* rather than its data, prefer `related: /tools/obis` instead (I'll flag those
for review). The `/tools/` Portals filter section appears automatically from the tags.yaml
`filters` change; `/tools/?portal=OBIS` deep-links pre-activate (tools-filter.js already
handles any facet param).

### 7. Contribution + docs
- `.github/ISSUE_TEMPLATE/add-*.yml`: replace the `node.Pole-to-Pole-Americas` example
  with `related:` guidance (advanced field: list content paths); keep org/place dropdowns.
- `archetypes/default.md` (if present): commented `related:` example.
- `CLAUDE.md` + `README.md`: document the two mechanisms (tags = filter/search;
  `related:` = page-to-page links with backlinks), content type as structural, and
  `org`/`portal` as plain filter facets with the **`org` = developer / `portal` = data
  source** distinction (OBIS is a portal); remove node/entity/References/Content-types text.

## Files to touch
- `layouts/partials/related.html` — curated + backlinks + fallback
- `layouts/_default/baseof.html` — pagefind `related` meta
- `data/tags.yaml` — drop node; org/portal → attribute, drop entity_section
- `layouts/_default/taxonomy.html` — drop entity-feature block
- `layouts/tags/terms.html` — flat facet list
- `static/css/tokens/colors.css`, `static/css/components.css` — drop facet-node
- `content/{news,tools,network}/…` (5) — node → related
- `content/tools/*.md` (+ any `news`/`events`) — `org.OBIS` → `portal.OBIS`
- `content/methods/{indicators,acoustics,genomics,tracking}.md` — related refs
- `.github/ISSUE_TEMPLATE/add-*.yml`, `archetypes/default.md` — related guidance
- `CLAUDE.md`, `README.md` — model docs

## Verification
1. `hugo --gc --minify --baseURL "https://marinebon.org/hugo2/"` exits 0.
2. `npx --yes pagefind --site public` then `python3 scripts/check_links.py public` exits 0
   (validates every `related:` path resolves and carries the `/hugo2/` base).
3. Browser (`python3 -m http.server` with a `/hugo2` symlink):
   - `/methods/indicators/` Related shows the 3 Indicators working groups (curated);
     `/working-groups/indicators/` shows `methods/indicators` (backlink).
   - `/news/sea-of-cortez-fieldwork/` Related shows the Pole-to-Pole node;
     `/network/pole-to-pole-americas/` shows the referencing news + atlas (backlinks); no
     `node.*` chip anywhere.
   - `/tags/` shows one flat set of tag facets (no Content types / References); no `org.OBIS`.
   - `/tools/` shows a **Portals** filter section; `/tools/?portal=OBIS` filters tools by
     OBIS-data use; the `org` filter now lists only developers (NOAA-IEA, Sanctuaries,
     FWRI). `/data/?portal=OBIS` still filters. Search finds OBIS via `portal.*` tags +
     related-title text.
