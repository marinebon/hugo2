# MBON website (Hugo)

The [Marine Biodiversity Observation Network](https://marinebon.github.io) site,
built with the [Hugo](https://gohugo.io) static-site generator. Content is plain
**Markdown** with **YAML** front matter; data is **YAML**; styling comes from a
small set of **CSS tokens**. It is rendered statically and hosted on **GitHub
Pages** at `marinebon/hugo2`.

Two ways to contribute:

- **No Git needed** — open an Issue from a template, or click **Suggest an edit**
  on any page. An automated workflow turns it into a Pull Request. See
  [Contributing content](#4-contributing-content).
- **Directly** — edit Markdown/YAML and open a PR (or use **Edit on GitHub**).

---

## 1. Run it locally

You need Hugo **extended**, v0.163+ ([install guide](https://gohugo.io/installation/)).
Run from the repository root:

```bash
hugo server          # live-reloading preview at http://localhost:1313
```

Build the production site (what CI publishes):

```bash
hugo --gc --minify   # output lands in ./public
npx pagefind --site public   # (optional) build the search index locally
```

## 2. Deploy

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds with Hugo
(pinned to the `HUGO_VERSION` in that file), indexes the site with **Pagefind**,
and publishes to GitHub Pages. A merged Pull Request is a push to `main`, so
**merging publishes automatically** within a couple of minutes.

---

## 3. Architecture

### Project layout

```
hugo.yaml                # site config: menu, hero text, params (incl. github_repo)
content/                 # ← all editable content (Markdown + YAML front matter)
  _index.md              #   home (hero text lives in hugo.yaml params)
  network/*.md           #   one file per regional node (geo: USA | International)
  working-groups/*.md    #   one file per working group (leads:)
  methods/*.md           #   observing methods (paired with data/methods.yaml hotspots)
  papers/*.md            #   one file per publication
  tools/*.md             #   one file per tool / data product
  news/*.md              #   one file per news post
  events/*.md            #   one file per event (date, location, presentations)
  about.md contact.md search.md
data/                    # ← structured data (YAML)
  stats.yaml             #   hero stat strip          social.yaml   # social links
  partners.yaml          #   partner logos + blurbs    methods.yaml  # methods hotspots
  tags.yaml              #   canonical tag registry: every facet, its filter
                         #   buttons, and display-name aliases (one source of truth)
layouts/                 # Hugo templates (HTML)
  _default/baseof.html   #   page shell (injects the on-page edit bar)
  partials/              #   header, footer, globe, cards, tag, edit-link, add-cta …
  <section>/{list,single}.html
static/
  css/styles.css         #   imports tokens/* then components.css + layout.css
  js/                    #   globe.js, methods.js, tools-filter.js, papers-filter.js
  img/<section>/         #   images referenced by front matter and Markdown
scripts/                 # Python helpers (import_papers.py, issue_to_content.py)
.github/
  ISSUE_TEMPLATE/*.yml   #   contribution issue forms
  workflows/             #   deploy.yml, content-from-issue.yml
```

### The tag system

Tags are **faceted**, written `facet.Value` where the value is `ProperCase`
(hyphenated for multi-word), e.g. `method.Remote-Sensing`, `tool.Portal`,
`place.US`, `org.OBIS`, `topic.Research`, `year.2021`, `type.Paper`. The facet
drives the tag color (`.tag--<facet>`) and the page filters.

| Facet | Used on | Allowed values |
|-------|---------|----------------|
| `method` | methods, tools, papers, news | Remote-Sensing, Genomics, Acoustics, Tracking, Indicators, Benthic, Traditional |
| `tool` | tools | Portal, App, Infographic, Package, Protocol, Training, Workflow |
| `place` | tools, news | Global, US, Americas, North-Atlantic, South-Florida, … |
| `org` | tools, news | OBIS, NOAA-IEA, NationalMarineSanctuaries, FWRI, … |
| `topic` | news, events | open-ended (Research, Partnership, Meeting, …) |
| `year` / `type` | papers | `year.<YYYY>`, `type.Paper` |

Every facet — its filter-bar buttons and the display-name **aliases** for open-set
values (so `org.GEOBON` renders "GEO BON", not "Geobon") — lives in one file,
`data/tags.yaml`. `layouts/partials/tag.html` renders a tag, resolving its label
there (case-insensitively, so it also works on the lowercased `/tags/` pages). The
Tools and Papers filter bars read the same file (the Papers **Year** buttons are
generated from the papers themselves).

### Contribution pipeline

```
Issue Form  ──►  content-from-issue.yml  ──►  scripts/issue_to_content.py  ──►  Pull Request  ──►  merge  ──►  deploy.yml
(dropdowns,      (resolve type, parse with     (build Markdown, map tags,        (maintainer        (push to       (Hugo + Pagefind
 image drag)      github-issue-parser)          import images, DOI→Crossref)      review)            main)          → GitHub Pages)
```

---

## 4. Contributing content

*No Git, YAML, or Markdown-file knowledge required.*

### Add something new

1. Go to the repo's **Issues → New issue** (or the **“+ Add …”** button on the
   News, Events, Tools, or Papers pages).
2. Pick a form — **Add a News post / Event / Paper / Tool**.
3. Fill in the fields. Choose **tags from the dropdowns** (no need to know the
   `facet.Value` codes) and **drag-and-drop images** into the image field.
   - **Papers:** paste a **DOI** and leave the rest blank — title, authors, year,
     journal, and abstract are fetched automatically.
4. Submit. A workflow drafts the page (importing your image) and opens a Pull
   Request, then links it back on your issue. A maintainer reviews and merges.

Basic Markdown for the body fields: `**bold**`, `*italic*`,
`[link](https://example.org)`, `## Subheading`, and `- ` for bullet lists.

### Edit an existing page

On any content page, use the bar at the bottom:

- **✏️ Suggest an edit** — opens an issue pre-filled with the page's location;
  describe the change in plain language (or paste a full replacement inside a
  ```` ```markdown ```` block to have it applied automatically).
- **Edit on GitHub** — opens the file in GitHub's web editor; saving creates the
  Pull Request for you (best for quick text fixes).

---

## 5. For maintainers

### Reviewing generated Pull Requests

Each contribution PR adds one file under `content/<section>/` (plus any image
under `static/img/<section>/`). Check the front matter, the mapped `tags`, and
the image, then **merge to publish**. Edit the PR branch directly if small tweaks
are needed. Editing the originating issue re-runs the workflow and updates the
same PR (the branch name is stable: `content/<type>-issue-<n>`).

### Running the scripts by hand

```bash
# Bulk-import publications from a Hugo-Academic source tree, regenerating
# content/papers/*.md:
python3 scripts/import_papers.py

# Build a single content file from issue-form JSON (what the workflow runs):
ISSUE_JSON='{"title":"…","summary":"…","body":"…","tags_topic":"Research"}' \
  CONTENT_TYPE=news ISSUE_NUMBER=0 python3 scripts/issue_to_content.py
```
Both use only `pyyaml` and the standard library.

### Adding a new tag value to the dropdowns

Two places must agree:

1. Add the value to the right facet in `data/tags.yaml` — under `values` to give it
   a filter button, or under `aliases` for a display-name-only label.
2. Add the matching human label to the dropdown `options:` in the corresponding
   `.github/ISSUE_TEMPLATE/add-*.yml` form.

If a label doesn't kebab-case cleanly to its `Value` (e.g. *GEO BON* → `GEOBON`,
*National Marine Sanctuaries* → `NationalMarineSanctuaries`), add it to
`TAG_ALIASES` in `scripts/issue_to_content.py`.

### Conventions & gotchas

- **`url:` is reserved** by Hugo as a permalink and rejects external URLs — papers
  use `paper_url:` and events use `event_url:`.
- **Upcoming events** rely on `buildFuture: true` in `hugo.yaml` (future-dated
  content is otherwise skipped). Events split into Upcoming vs Past by `date`.
- **Labels** `content:news|event|paper|tool|edit` are applied by the issue forms
  and key the workflow; GitHub creates them on first use.
- Front-matter images are paths relative to `static/`, e.g.
  `banner: img/news/my-post.jpg`.

---

## 6. Edit data & styling (no templates)

- **`data/stats.yaml`** — hero figures. **`data/partners.yaml`** — partner logos +
  descriptions (drop a logo in `static/img/partners/`). **`data/methods.yaml`** —
  the interactive methods illustration hotspots. **`data/social.yaml`** — social links.
- Top-nav, hero headline/lead, and `github_repo` live in **`hugo.yaml`**.
- All CSS is in `static/css/`, linked as `styles.css`, which imports the design
  tokens (`tokens/colors.css`, `typography.css`, `spacing.css`, `fonts.css`,
  `base.css`) then `components.css` (buttons, tags, cards) and `layout.css` (page
  chrome). Change a brand color or the `--facet-*` tag colors in one place.

---

## 7. The network globe

`static/js/globe.js` renders the rotating globe on the home and network pages from
the node data emitted by `layouts/partials/globe.html` — so **adding a
`content/network/*.md` file with `lat`/`lng` adds its globe node automatically**.
d3 + world-atlas load from a CDN at runtime; the globe degrades gracefully offline.

---

Markdown allows raw HTML (e.g. `<iframe>` embeds); `unsafe: true` is set in
`hugo.yaml`. Icons use **Font Awesome 6** (CDN, in `layouts/partials/head.html`).
