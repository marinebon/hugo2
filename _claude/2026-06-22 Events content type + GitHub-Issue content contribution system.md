# Plan: Events content type + GitHub-Issue content contribution system

## Context

Two connected goals:

1. **Events should be a real content type.** Today `content/events.md` is a single hand-maintained page (rendered by the default single template, linked only from the footer). It groups events as `## [Title](url)` + `#### date · location` + a list of presentation links. We want `content/events/` as a first-class section with per-event pages and a listing, surfaced under a **News** navbar dropdown. This also makes Events a clean target for the contribution system below.

2. **Lower the barrier to contributing content.** Non-technical collaborators (scientists, node leads) should be able to *add* or *edit* News, Events, Papers, and Tools without touching Git, YAML, or Markdown directly. We do this with **GitHub Issue Forms** (structured fields + tag dropdowns + image drag-and-drop) consumed by a **GitHub Action** that builds the Markdown file, imports any attached images into `static/img/...`, and opens a Pull Request for maintainer review. Every content page also gets an on-page link to propose an edit, pre-filled with that page's path.

Repo facts that shape the design:
- GitHub repo `marinebon/hugo2`; deploys to GitHub Pages via `.github/workflows/deploy.yml` on push to `main` (Hugo 0.163.3 + Pagefind). A merged PR = a push to main = auto-deploy. No PR checks exist today.
- Existing Python tooling `scripts/import_papers.py` already parses/writes Hugo front matter with `pyyaml` (`yaml.dump(..., sort_keys=False)`), generates slugs, and **auto-assigns method tags** from title/abstract via `METHOD_RULES` — directly reusable by the Action.
- Faceted tag convention `lowercase.ProperCase` (`tool.Portal`, `method.Genomics`, `place.US`, `org.OBIS`, `topic.Research`). Allowed values live in `data/tool_filters.yaml` and `data/paper_filters.yaml`; `layouts/partials/tag.html` renders them.
- Content sections & their front matter (representative):
  - **news**: `title`, `date`, `summary`(optional), `banner`(optional img), `tags` (topic/place/method/org), body.
  - **papers**: `title`, `authors[]`, `date`, `year`, `journal`, `doi`, `paper_url`, `abstract`, `tags` (method/year).
  - **tools**: `title`, `summary`, `image`, `links[]`(label/url/primary), `tags` (tool/place/org/method), `weight`, body.
  - **events** (new): see Part 1.
- Images live under `static/img/{news,products,photos,working-groups,...}` and are referenced by `banner:`/`image:` front matter or `![](img/...)` in body.
- Single templates per section in `layouts/<section>/single.html`; shared chrome in `layouts/_default/baseof.html`. Navbar dropdowns dispatched in `layouts/partials/header.html` by `.Identifier` (network, tools) or `.Name` (Methods).

---

## Part 1 — Events content type (do this first)

**New content section `content/events/`:**
- `content/events/_index.md` — `title: Events`, `summary:` (move text from current `content/events.md`).
- One file per event: `content/events/<slug>.md` with front matter:
  ```yaml
  ---
  title: National MBON Meeting
  date: '2022-11-01'
  end_date: '2022-11-04'        # optional; multi-day events
  location: Monterey, CA
  url: https://www.iode.org/conf2022   # event website (optional)
  summary: One-line description.
  tags:
  - topic.Meeting
  ---
  Presentation / resource links preserved as the markdown body
  (e.g. "[Talk title](url) — Authors").
  ```
- **Migrate**: split the existing `content/events.md` (each `## [..]` block delimited by `---`) into individual event files, parsing title, URL, date range, and location from the `####` line; keep the presentation list as the body. Then delete `content/events.md`.

**New templates:**
- `layouts/events/list.html` — listing that splits **Upcoming** (`date >= now`) vs **Past** (descending), using event cards. Mirror the structure of `layouts/news/list.html`.
- `layouts/events/single.html` — event detail: title, date range, location, event-site button, then body (presentations). Mirror `layouts/news/single.html` minus the banner-required bits.
- `layouts/partials/card-event.html` — compact card: date chip + title + location + tags (reuse `.node-link`/`card` styling already in `components.css`).

**Navbar — make News a dropdown containing News + Events:**
- `hugo.yaml`: add `identifier: news` to the News menu entry.
- `layouts/partials/header.html`: add `{{ else if eq .Identifier "news" }}` branch — a single-column dropdown linking **All News** (`/news/`) and **Events** (`/events/`), following the existing Tools-dropdown markup.
- `layouts/partials/footer.html`: keep the Events link (already present), ensure it points to `/events/`.

**Verify Part 1**: `hugo` builds 0 errors; `/events/` lists each migrated event; each event has its own page; News navbar shows a dropdown with News + Events; old `/events/` URL still resolves (section list now serves it).

---

## Part 2 — GitHub Issue Forms (structured contribution)

**Confirmed scope:** dedicated "Add" forms for **News, Events, Papers, Tools** (Network nodes & Working Groups use the generic edit form). Plus one **edit** form.

`.github/ISSUE_TEMPLATE/` issue **forms** (`.yml`, not legacy markdown) — each auto-applies a label the Action keys on:
- `add-news.yml` (label `content:news`), `add-event.yml` (`content:event`), `add-paper.yml` (`content:paper`), `add-tool.yml` (`content:tool`), and `edit-content.yml` (`content:edit`).
- Forms use **`dropdown`** fields for every tag facet (multi-select where the section allows), so contributors pick human-readable values (“Remote Sensing”, “National Marine Sanctuaries”) and never type the `facet.Value` convention. The Action maps selections → tags.
- Image fields are `textarea`s instructing the user to drag-drop an image (GitHub uploads it and inserts `![](https://github.com/user-attachments/...)`); the Action extracts + downloads it.
- Each form embeds inline **help**: how to pick tags, Markdown formatting basics, and an example — so the “instructions” live right in the form.
- `.github/ISSUE_TEMPLATE/config.yml` can link out to the contributing guide.

---

## Part 3 — GitHub Action: issue → content file + images → PR

`.github/workflows/content-from-issue.yml`, triggered on `issues: [opened, edited]`, filtered to the `content:*` labels:
1. **Parse** the issue form with `stefanbuck/github-issue-parser@v3` → JSON keyed by field id.
2. **Build** the content file with a new `scripts/issue_to_content.py` (reuses `import_papers.py` patterns: `yaml.dump(sort_keys=False)`, slugging, `METHOD_RULES` auto-tagging). Maps dropdown labels → `facet.Value` tags via the `data/*_filters.yaml` tables.
3. **Import images**: regex the attachment URLs from the image field, download to `static/img/<section>/<slug>.<ext>`, set `banner:`/`image:` accordingly.
4. **Open a PR** with `peter-evans/create-pull-request@v6` (branch `content/issue-<n>`), and comment back on the issue with the PR link. Maintainer review/merge is the quality gate; merge → existing deploy workflow publishes.
- Needs `permissions: contents: write, pull-requests: write` (default `GITHUB_TOKEN`).
- **Papers (confirmed: DOI *or* manual):** the paper form has an optional `doi` field plus the manual fields. If a DOI is provided, the Action fetches Crossref metadata (`https://api.crossref.org/works/<doi>`) to fill title/authors/year/journal/abstract and only falls back to the manual fields for anything missing; method tags auto-assigned via `METHOD_RULES`. If no DOI, the manual fields are used directly.

---

## Part 4 — On-page contribution links  *(confirmed: both links)*

- New `layouts/partials/edit-link.html` included by each section `single.html` (and list pages), rendering **two** links side by side:
  1. **“✏️ Suggest an edit”** (primary, non-technical) → pre-filled edit issue form:
     `https://github.com/marinebon/hugo2/issues/new?template=edit-content.yml&title=Edit:%20{{ .Title }}&page_url={{ .Permalink }}&content_path={{ .File.Path }}` (issue-form query params pre-fill fields by id).
  2. **“Edit on GitHub”** (secondary, power users) → native web editor `https://github.com/marinebon/hugo2/edit/main/content/{{ .File.Path }}` (instant fork+PR; zero infra).
- Section list pages (`/news/`, `/events/`, `/tools/`, `/papers/`) get an **“+ Add …”** button linking to the matching add form.

---

## Part 5 — Rewrite `README.md` (architecture + procedures)

The current `README.md` is **stale** — it predates the reorganization and must be corrected *and* extended. Stale facts to fix: `site/` subdir (now repo root), `hugo.toml` → `hugo.yaml`, TOML `+++` → YAML `---` front matter, `regions/` → `network/` + `working-groups/`, `products/` → `tools/`, `product_filters.yaml` → `tool_filters.yaml`, colon tags `region:value` → dot tags `facet.Value` (ProperCase), `kind_node` thematic → `geo: USA|International`, plus missing sections (`papers/`, new `events/`, custom Pagefind `search`).

Rewrite into three audiences:

1. **Architecture** — accurate project layout (current `content/`, `data/`, `layouts/`, `static/` tree), build/deploy flow (`hugo` + Pagefind → GitHub Pages on push to `main`), the faceted **`facet.Value`** tag system with the canonical facets and where allowed values live (`data/*_filters.yaml`), and a short diagram of the **contribution pipeline**: *issue form → Action (`stefanbuck/github-issue-parser` → `scripts/issue_to_content.py` → image import → `peter-evans/create-pull-request`) → PR review → merge → deploy*.

2. **For contributors (no Git/Markdown needed)** — “Add content”: open an Issue → pick the right form (News / Event / Paper / Tool) → fill fields, choose tags from dropdowns, drag-drop images → submit; a maintainer reviews the auto-generated PR. “Edit content”: on any page use **✏️ Suggest an edit** (issue form) or **Edit on GitHub** (web editor). Note the DOI shortcut for papers.

3. **For admins/maintainers (ingest & update)** — how the Action turns issues into PRs and what to check when reviewing; how to run the scripts manually (`python3 scripts/issue_to_content.py`, `python3 scripts/import_papers.py` for bulk paper import); how to **add a new tag value** (edit `data/<section>_filters.yaml` *and* the matching dropdown options in the issue form); how images are placed under `static/img/<section>/`; local preview (`hugo server`) and the deploy workflow; the `content:*` label convention.

---

## Verification (whole plan)

1. `hugo` builds with 0 errors after Part 1; page count grows by (#events + events list).
2. Submit each issue form in the GitHub UI → Action opens a PR with a correctly-formed `.md` (front matter valid, tags mapped, image committed under `static/img/...`).
3. Merge a generated PR → `deploy.yml` runs → page appears live.
4. From a live page, “Suggest an edit” opens an issue pre-filled with that page’s path; submitting → Action opens an edit PR.
5. DOI paper form: paste a DOI → PR contains a fully-populated paper file.
6. `README.md` reflects the current tree/tags (no `site/`, `hugo.toml`, `products/`, colon-tags) and documents the contributor and admin procedures end-to-end.
