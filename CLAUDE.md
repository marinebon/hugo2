# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is the Marine Biodiversity Observation Network (MBON) website: a **Hugo**
static site. Content is Markdown with YAML front matter, data is YAML, styling is
plain CSS tokens. Published to GitHub Pages at `marinebon/hugo2` on every push to
`main`. `README.md` is the contributor-facing guide and is the source of truth for
the contribution flow — read it for anything user-facing.

## Commands

```bash
hugo server                  # live-reloading preview at http://localhost:1313
hugo --gc --minify           # production build into ./public (what CI runs)
npx --yes pagefind --site public   # build the search index over the built site
python3 scripts/check_links.py public   # fail on any broken internal link (CI runs this)
```

Requires Hugo **extended** ≥ 0.163 (CI pins `HUGO_VERSION: 0.163.3` in
`.github/workflows/deploy.yml`). There is no test suite; the build is the check —
`hugo --gc --minify` must exit 0 and not leak unintended files into `public/`,
and `check_links.py` must exit 0.

To reproduce the deployed subpath locally (CI serves under `/hugo2/`), build with
`hugo --gc --minify --baseURL "https://marinebon.org/hugo2/"` before checking —
the default local `baseURL` has no path, so base-path bugs only surface that way.

Python helper scripts use only `pyyaml` + stdlib:

```bash
python3 scripts/import_papers.py     # regenerate content/papers/*.md + data/paper_filters.yaml
                                     # from a Hugo-Academic source tree
# build one content file from issue-form JSON (what the workflow runs):
ISSUE_JSON='{"title":"…","tags_topic":"Research"}' CONTENT_TYPE=news ISSUE_NUMBER=0 \
  python3 scripts/issue_to_content.py
```

## Architecture

Standard Hugo layout: `content/<section>/*.md` (one file per item) → rendered by
`layouts/<section>/{list,single}.html` → styled by `static/css/styles.css`.
Structured data lives in `data/*.yaml`; client behavior in `static/js/` (globe,
methods hotspots, tools/papers filters). `hugo.yaml` holds the menu, hero text,
and `params.github_repo` (which backs the contribution links).

Two things require reading multiple files to understand:

### The faceted tag system

Tags are written `facet.Value` with `ProperCase` (hyphenated) values, e.g.
`method.Remote-Sensing`, `tool.Portal`, `tool.Training`, `place.US`, `org.OBIS`,
`topic.Research`, `year.2021`, `type.Paper`. The facet drives the tag color
(`.tag--<facet>` in CSS) and the on-page JS filters.

**`data/tags.yaml` is the single source of truth** for every facet: its filter-bar
`values` (buttons) and an `aliases` map giving open-set values proper labels (so
`org.GEOBON` → "GEO BON", not the humanized "Geobon"). `layouts/partials/tag.html`
resolves a label there **case-insensitively** — important because Hugo lowercases
taxonomy terms, so the same lookup must work on `/tags/` term pages and on
original-case front-matter tags. `tools/list.html` and `papers/list.html` build
their filter bars from the facets whose `filters:` list names that section (the
Papers **Year** buttons are generated from the papers themselves, not the file).

**Adding a new tag value requires two places to agree:** add it to `data/tags.yaml`
(under `values` for a filter button, or `aliases` for a label only) AND add the
human label to the dropdown `options:` in the matching
`.github/ISSUE_TEMPLATE/add-*.yml`. If a label doesn't kebab-case cleanly to its
`Value`, also add it to `TAG_ALIASES` in `scripts/issue_to_content.py`.

### The contribution pipeline (no-Git path)

```
Issue Form → content-from-issue.yml → scripts/issue_to_content.py → Pull Request → merge → deploy.yml
```

A contributor opens an issue from a template (or the "+ Add …" buttons / "Suggest
an edit" bar that `layouts/_default/baseof.html` injects). The workflow runs
`issue_to_content.py`, which builds one `content/<section>/*.md` (+ any image under
`static/img/<section>/`), maps dropdown labels to `facet.Value` tags, and for
papers resolves a DOI via Crossref. It opens a PR on a stable branch
`content/<type>-issue-<n>` — editing the issue re-runs and updates the same PR.

### Type-aware cards

`layouts/partials/card.html` is a dispatcher that renders the right card for a
Page by `.Type`: news (`card-news`, month/year badge over banner), events
(`card-event`, date), papers (`card-paper`, year badge over a placeholder),
everything else (`card-tool`, generic image card). Any mixed-content list should
call `card.html` so each result keeps its section's treatment. The tag term page
`layouts/_default/taxonomy.html` uses it, grouping a tag's results by type.

Search (`layouts/search.html`, Pagefind) renders the same type-aware cards in JS.
`baseof.html` emits per-page Pagefind meta (`type`, `badge`, `image`) as **one
non-empty element per key** wrapped in `data-pagefind-ignore`: empty elements get
dropped by the minifier, a single comma-joined attribute isn't split into keys by
Pagefind, and without `-ignore` the hidden values leak into result excerpts.

## Conventions & gotchas

- **`url:` is reserved** by Hugo (permalink); papers use `paper_url:`, events use
  `event_url:` for external links.
- **Upcoming events** depend on `buildFuture: true` in `hugo.yaml` — future-dated
  content is otherwise skipped. Events split Upcoming/Past by `date`.
- Front-matter image paths are relative to `static/`, e.g. `banner: img/news/x.jpg`.
- Adding a `content/network/*.md` with `lat`/`lng` auto-adds a globe node
  (`globe.js` reads nodes emitted by `layouts/partials/globe.html`).
- Markdown allows raw HTML (`unsafe: true` in `hugo.yaml`); icons are Font Awesome 6.
- **Internal links must carry the base path** (`/hugo2/` in prod). The trap:
  `relURL` *drops* the base path on a leading-slash string — `relURL "/methods/x/"`
  → `/methods/x/` (404s under `/hugo2/`), while `relURL "methods/x/"` →
  `/hugo2/methods/x/`. So write `relURL` args **without** a leading slash, prefer
  `.RelPermalink` for pages, and keep `data/*.yaml` link values slash-free. Markdown
  links/images are safe automatically: `layouts/_default/_markup/render-{link,image}.html`
  trim a leading slash and run every internal destination through `relURL`.
  `scripts/check_links.py` enforces all of this against the built site (see Commands).
- All CSS is in `static/css/`: `styles.css` imports `tokens/*` then
  `components.css` + `layout.css`. Brand and `--facet-*` colors are single-source.

## Repo-only directories (not part of the Hugo build)

- `_claude/` — working notes from prior Claude sessions (`notes.md` plus dated
  session logs). Useful background on past changes; not published.
- `tools-review/` — a one-off audit of `marinebon`/`noaa-onms`/`noaa-iea` repos for
  Tools-catalog candidates (`README.md`, `inventory.csv`, screenshots). Ignored by
  Hugo; kept as repo documentation.

## Style (R/Python helpers)

The parent `/Users/bbest/Github/CLAUDE.md` applies: 2-space indent, snake_case,
align `=` across multi-line assignments, lowercase comments.
