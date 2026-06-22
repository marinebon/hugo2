# Plan: Papers Content Type with COinS & Tag Filtering

## Context

MBON has ~93 peer-reviewed publications catalogued in the legacy `www_marinebon2` Hugo-Academic site (individual `content/publication/*/index.md` files with structured YAML front matter). The goal is to surface these papers on the new `hugo2` site as a first-class content type — filterable by method/topic/year, each page exposing COinS metadata so Zotero can one-click import any citation directly from the browser.

---

## Approach: No external dependencies

Store papers as individual Hugo content files (`content/papers/slug.md`) with rich front matter. A custom `partials/coins.html` partial generates the COinS `<span class="Z3988">` from page params at build time. The existing JS facet-filter pattern (from tools) is copied with `data-paper-*` attributes. No npm, no Hugo modules, no external build step.

---

## Files to Create / Modify

### 1. Import script (run once, not committed to repo)
**`scripts/import_papers.py`** — reads every `../www_marinebon2/content/publication/*/index.md`, maps fields, auto-assigns ProperCase tags, writes `content/papers/{slug}.md`.

Field mapping:
| Source | Target front matter |
|---|---|
| `title` | `title` |
| `authors` (list) | `authors` |
| `date` (YYYY-MM-DD) | `date` + `year` (int extracted) |
| `publication` (strip `*`) | `journal` |
| `doi` | `doi` |
| `url_pdf` | `url` |
| body first paragraph | `abstract` (stripped of HTML) |

Auto-tag logic (keyword match on lowercased title + abstract):
- `edna / metabarcode / genomic` → `method.Genomics`
- `remote sens / satellite / seascape` → `method.Remote-Sensing`
- `acoustic / soundscape` → `method.Acoustics`
- `track / telemetry` → `method.Tracking`
- `indicator / eov / ebv / essential` → `method.Indicators`
- `trawl / visual survey / transect` → `method.Traditional`
- Always add `type.Paper`
- Always add `year.YYYY` (e.g. `year.2019`)

Old www_marinebon2 tags (messy strings like `"omics and edna"`) are **discarded** and replaced by the auto-assigned tags above.

### 2. Content files (~93)
**`content/papers/{slug}.md`** — front matter only, example:
```yaml
---
title: "Biomonitoring of marine vertebrates in Monterey Bay using eDNA metabarcoding"
authors:
  - Elizabeth A. Andruszkiewicz
  - Hilary A. Starks
  - Francisco P. Chavez
date: 2017-04-01
year: 2017
journal: PLOS ONE
doi: 10.1371/journal.pone.0176343
url: https://dx.plos.org/10.1371/journal.pone.0176343
tags:
  - type.Paper
  - method.Genomics
  - year.2017
abstract: >
  Water samples contain DNA shed by every organism that passed through...
---
```

### 3. `data/paper_filters.yaml` (new)
Two facets: `method` (same 6 values as tools) and `year` (one entry per year found in import, populated by the script).

### 4. `layouts/papers/list.html` (new)
Mirrors `layouts/tools/list.html` with paper-specific attributes. Uses a **list layout** (not image cards) — compact citation rows sorted by year descending:
```
[2019]  Canonico et al. — Global Observational Needs...  Frontiers in Marine Science  [tags]
```
Each row links to the single paper page. Scripts block loads `js/papers-filter.js`.

### 5. `layouts/papers/single.html` (new)
Full citation block + abstract + DOI link + tags + `{{ partial "coins.html" . }}`. Back-link to `/papers/`.

### 6. `layouts/partials/coins.html` (new)
Generates the invisible COinS span enabling Zotero import:
```html
{{ $rft := slice
    "ctx_ver=Z39.88-2004"
    "rft_val_fmt=info:ofi/fmt:kev:mtx:journal"
    "rft.genre=article"
    (printf "rft.atitle=%s" (.Title | urlquery))
    (printf "rft.jtitle=%s" (.Params.journal | default "" | urlquery))
    (printf "rft.date=%d" (.Params.year | default 0))
    (printf "rft.doi=%s" (.Params.doi | default "" | urlquery))
}}
{{ range .Params.authors }}
  {{ $rft = $rft | append (printf "rft.au=%s" (. | urlquery)) }}
{{ end }}
<span class="Z3988" title="{{ delimit $rft "&" }}"></span>
```

### 7. `static/js/papers-filter.js` (new)
Copy of `tools-filter.js` with `tool` → `paper` and `TOOLS` → `PAPERS`.

### 8. `static/css/components.css` (modify)
Add `.paper-row` list-item styles (year badge, "et al." author, italic journal, hover highlight) and `.tag--year { --_c: var(--ink-500); }`.

### 9. `hugo.yaml` menu (modify)
Insert Papers at weight 4, shift Tools→5, News→6, About→7.

### 10. `content/papers/_index.md` (new)
```yaml
---
title: Papers
summary: Peer-reviewed publications from MBON researchers. Click any title to view citation details — Zotero users can import directly from the page.
---
```

---

## Verification

1. Run import script → ~93 `.md` files in `content/papers/`
2. `hugo build` → zero errors; page count ≈ 290 + 93 papers + tag pages
3. `/papers/` — filter bar (Method + Year), list sorted by year desc
4. Click a paper → single page; inspect source for `<span class="Z3988">` with populated `title` attribute
5. Zotero browser connector on single paper page → article detected, import succeeds
6. Filter by method (e.g. Genomics) → only matching papers shown; Clear resets
7. `/tags/method.Genomics/` and `/tags/year.2019/` tag pages exist
