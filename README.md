# MBON Website (Hugo)

The Marine Biodiversity Observation Network site, built with the
[Hugo](https://gohugo.io) static-site generator and the MBON design system.
Statically rendered, hosted on **GitHub Pages**. Content is plain **Markdown**,
data is **YAML**, and the look comes from a small set of **CSS tokens** — so
editing is approachable without touching templates.

---

## 1. Run it locally

You need Hugo **extended**, v0.128+ ([install guide](https://gohugo.io/installation/)).

```bash
cd site
hugo server          # live-reloading preview at http://localhost:1313
```

Build the production site (what CI publishes):

```bash
hugo --gc --minify   # output lands in ./public
```

## 2. Deploy to GitHub Pages

A workflow is included at `.github/workflows/deploy.yml`. One-time setup:

1. Push this `site/` directory to a repo (or make it the repo root).
2. In the repo: **Settings → Pages → Build and deployment → Source = GitHub Actions**.
3. Push to `main`. The action builds with Hugo and publishes automatically;
   every later push redeploys within a couple of minutes.

> If you host the site in a sub-path, the workflow already passes the correct
> `--baseURL`. For a custom domain, add a `CNAME` file in `static/`.

---

## 3. Project layout

```
site/
  hugo.toml              # site config: title, menu, hero text, social links
  archetypes/            # templates used by `hugo new` (default front matter)
  content/               # ← all editable content (Markdown)
    _index.md            #   home (text lives in hugo.toml params)
    regions/*.md         #   one file per network node (regional + thematic)
    products/*.md        #   one file per data product
    news/*.md            #   one file per news post
  data/                  # ← structured data (YAML)
    stats.yaml           #   hero stat strip
    partners.yaml        #   footer collaborator logos
    product_filters.yaml #   the facet filter taxonomy (Region/Tool/Org/Type)
  layouts/               # Hugo templates (HTML) — edit for structure
    _default/            #   baseof, single, list fallbacks
    partials/            #   header, footer, globe, cards, tag
    index.html           #   home
    regions/ products/ news/  # per-section list + single templates
  static/
    css/                 # ← styling (see §6)
    js/                  #   globe.js, products-filter.js
    img/                 #   logos/, partners/, photos/
```

---

## 4. Add or edit content

Everything below is a Markdown file with a `+++` TOML front-matter block. Use
`hugo new <section>/<slug>.md` to scaffold one with the right fields, or copy an
existing file.

### A news post
```bash
hugo new news/my-post.md
```
Edit the front matter (`title`, `date`, `author`, `banner`, `summary`, `tags`),
write the body in Markdown, and drop any images in `static/img/photos/`,
referencing them as `/img/photos/your-image.jpg`. It appears automatically on
**/news** and in the "Latest news" home strip (newest first).

### A data product
```bash
hugo new products/my-product.md
```
Set `weight` (sort order), `image`, `summary`, `links`, and **`tags`** as
`"facet:value"` tokens (e.g. `"region:south-fl"`, `"tool:dashboard"`). The tags
color-code the card and drive the filter on **/products**. To introduce a new
filter value, add it to `data/product_filters.yaml` first (see §5).

### A network node (regional or thematic) — *also a point on the globe*
```bash
hugo new regions/my-node.md
```
Set `kind_node` (`regional`/`thematic`), `lat`, `lng` (decimal degrees), and
`footprint` (the faint area radius on the globe, in degrees). Optionally
`fcenter = [lng, lat]` to center a large basin footprint away from the node
marker (used for Pole-to-Pole, Europe, Asia-Pacific). The page **and** its globe
node/chip are generated from this one file — no other edits needed.

---

## 5. Edit data (no templates)

- **`data/stats.yaml`** — the four hero figures.
- **`data/partners.yaml`** — footer logos. Drop a file in `static/img/partners/`
  and add a `{ name, logo, url }` entry.
- **`data/product_filters.yaml`** — the four facets and their allowed values.
  Add a `{ value, name }` under a facet, then use `facet:value` in a product's
  `tags`. Colors come from the facet name (region/tool/org/type).

Top-nav links, the hero headline/lead, and social URLs all live in
**`hugo.toml`** under `[menu]` and `[params]`.

---

## 6. Tweak the styling

All CSS is in `static/css/`, linked as one file (`styles.css`) that imports:

- **`tokens/colors.css`** — the ocean palette. Change a brand color in one place:
  e.g. `--brand` (cobalt), `--accent` (teal), `--action` (coral), or the
  `--facet-*` tag colors. Everything downstream updates.
- **`tokens/typography.css`** — font families and the type scale.
- **`tokens/fonts.css`** — the webfont `@import` (Space Grotesk / IBM Plex
  Sans / IBM Plex Mono). Self-host for production if desired.
- **`tokens/spacing.css`** — spacing, radii, shadows, motion.
- **`components.css`** — buttons, tags, badges, cards, stats (class-based).
- **`layout.css`** — page chrome: header, hero, globe band, footer, grids.

These mirror the **MBON Design System** this site was built from — see that
project's `README.md` for the full design guidance, voice, and component API.

---

## 7. The network globe

`static/js/globe.js` renders the rotating globe on the home and network pages.
It reads node data emitted by `layouts/partials/globe.html` from your
`content/regions/*.md` files, so **adding a region automatically adds its globe
node**. Continent outlines and the d3 projection load from a CDN at runtime
(cached); the globe degrades to a "Loading…" state if offline. To vendor those
for full offline use, download `d3`, `topojson-client`, and `world-atlas`
`land-110m.json` into `static/js/` and update the URLs in `globe.js`.

---

## Notes

- Markdown allows raw HTML (e.g. `<iframe>` embeds for live maps/video) —
  `unsafe = true` is set in `hugo.toml`.
- Icons use **Font Awesome 6** (loaded from CDN in `layouts/partials/head.html`).
- This is a fresh, redesigned theme (not the old Bootstrap `hugo-universal-theme`).
