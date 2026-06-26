
## TODO

### Update README with style

Pull relevant bits from the Claude.ai/design design system at `/Users/bbest/Downloads/MBON Design System (1)` for 

### refine **tags**

Expand and refine the use of [tags](https://marinebon.org/hugo2/tags/), so they could be prefixed by type, eg method.Tracking. 

### add **people**

And add **People** as its own content type under About to similarly enable connecting with Papers and Projects / Working Groups (ie Network). We want to be able to see related content throughout website.


## 2026-06-26.d + Data #1

Take on issue #1 + Data

  I now have a clear picture of the architecture. Issue #1 has a firm ask (Data nav item + landing page explaining data access via Tools) and a larger "Consider" (a new filterable dataset content type harvested from OBIS/GBIF/EDI/ERDDAP). Those are very different sizes of work, so let me confirm scope before building.

  ☐ Scope

  Issue #1 firmly asks for a Data nav item + landing page (routing to Portals/Apps/Packages), and separately says to *consider* a new filterable `dataset` content type harvested from OBIS/GBIF/EDI/ERDDAP. How far should I take it now?

    1. Landing page only            ┌───────────────────────────────────────────────────┐
    2. Landing page + dataset scaffold                      │                                                   │
  > 3. Full build incl. harvester    │ scripts/harvest_datasets.py                       │
                                    │   → queries OBIS / GBIF / EDI / ERDDAP            │
                                    │   → writes content/datasets/*.md                  │
                                    │   → n_records, cross-portal linking               │
                                    │                                                   │
                                    │ Needs: API exploration, network calls,            │
                                    │ de-dup logic. Multi-hour, iterative.              │
                                    └───────────────────────────────────────────────────┘

Let's prefer OBIS datasets over GBIF duplicates, since OBIS has more extended schemas and QA/QC

## 2026-06-26.c fix navbar, website on phone

I notice on a smartphone that the navbar is not navigable [image]. The whole website needs to be reviewed for use on smartphone devices.

## 2026-06-26.b fix 404s on Methods illustration

I notice that the Methods illustration links are not properly formed, eg goes to https://marinebon.org/methods/acoustics/ which 404s. It is missing `hugo2`:  https://marinebon.org/hugo2/methods/acoustics/. Fix all these links now and into future (for when the website gets staged from https://marinebon.org/hugo2/ to https://marinebon.org/). 

Can we also check for these 404s throughout the website, possibly on render and fail if any are found to flag for fixing? We could also have an exceptions list to allow publishing the site anyways, until some known culprits are fixed later.

Done. Everything is fixed and verified against both the production subpath build (/hugo2/) and the future root build (/).

Root cause

The methods illustration "Learn more" links came from data/methods.yaml (url: /methods/acoustics/) rendered via relURL. The trap: relURL drops the base path when given a leading-slash string — relURL "/methods/acoustics/" → /methods/acoustics/ (404s under /hugo2/), whereas relURL "methods/acoustics/" → /hugo2/methods/acoustics/. It "worked" locally only because the default local baseURL has no path.

What I fixed

The link checker I wrote surfaced 20 broken links across the site, not just the methods band — all now fixed (zero content edits needed for the markdown ones):

- data/methods.yaml — removed leading slashes from the 7 hotspot url: values (the reported bug).
- layouts/_default/_markup/render-link.html (new) — there was already a render-image.html hook but no link hook, which is exactly why markdown images resolved correctly but markdown links didn't. This new hook runs every internal markdown link through relURL (base-path-correct), fixing the tool/news/method cross-links and the relative docs/*.pdf links automatically — now and for future content.
- layouts/partials/social-links.html — the footer "Contact" link (/contact/ from data/social.yaml, on all 327 pages) now resolves through relURL.
- layouts/404.html — hardcoded href="/" and href="/search" now use relURL.

404 detection (your second ask)

- scripts/check_links.py (new, stdlib-only) — walks the built site, extracts every href/src/srcset, and fails (exit 1) if any internal link either drops the base path (catches the exact relURL class of bug) or points to a missing file. Auto-detects the base path from sitemap.xml, so it's correct whether the site is served at /hugo2/ or root.
- scripts/linkcheck_allow.txt (new) — your exceptions list: glob patterns for known-broken links to allow publishing anyway. Currently empty — every real link was fixable, so nothing needed an exception.
- .github/workflows/deploy.yml — runs the checker after the Hugo build (against the real /hugo2/ baseURL), so a regression fails the deploy.
- CLAUDE.md — documented the command, the leading-slash gotcha, the render hooks, and how to reproduce the subpath locally.

Verification: pre-fix build → 20 broken (exit 1); fixed subpath build → 0 broken (exit 0); fixed root build → 0 broken (exit 0); allow-file correctly demotes matches to warnings.

To check locally the way CI does:
hugo --gc --minify --baseURL "https://marinebon.org/hugo2/"
python3 scripts/check_links.py public

One thing worth your awareness: the build I tested includes your in-progress data/tags.yaml refactor (the deleted *_filters.yaml files) — it builds clean and passes the link check, so nothing there is blocked.

Committed on a new branch fix/base-path-internal-links (commit 3674e3e).

What's in the commit — only the 7 task files:
- data/methods.yaml, layouts/_default/_markup/render-link.html, layouts/partials/social-links.html, layouts/404.html — the link fixes
- scripts/check_links.py, scripts/linkcheck_allow.txt, .github/workflows/deploy.yml — the checker + CI wiring

Deliberately left out of this commit (still in your working tree, uncommitted):
- Your in-progress tags refactor — data/tags.yaml, the deleted *_filters.yaml, the card-*/taxonomy.html/baseof.html/etc. changes — not mine to commit.
- CLAUDE.md — my doc additions (link-checker command + the relURL gotcha) are entangled with your refactor's documentation in that same new file, so I left it for you to commit alongside the refactor.
- _claude/notes.md — was already modified before this session.

Two notes:
- I branched (rather than committing to main) per the default for the default branch. To fold it into your trunk-based flow: git checkout main && git merge fix/base-path-internal-links (fast-forward). Nothing has been pushed, so no deploy was triggered.
- Your other uncommitted changes carried over to this branch and will follow you back when you git checkout main.


## 2026-06-26.a create CLAUDE.md, harmonize tags

  All references check out. I've created /Users/bbest/Github/marinebon/hugo2/CLAUDE.md.

  It deliberately doesn't restate the contributor-facing README (which is already excellent). Instead it captures what a future Claude instance needs to be productive fast:

  - Commands — hugo server / hugo --gc --minify / pagefind, the pinned extended-Hugo version, and the fact that the build is the test (no test suite).
  - Architecture — the two non-obvious systems that require reading several files: the faceted facet.Value tag system (color + filter wiring, and the two-places-must-agree rule for new values) and the issue → PR → deploy contribution pipeline.
  - Conventions & gotchas — the reserved url:, buildFuture for events, image path roots, auto-globe nodes, unsafe: true, CSS token structure.
  - Repo-only dirs — _claude/ (session notes) and tools-review/ (the repo audit), both ignored by Hugo so an agent doesn't mistake them for site content.
  - A pointer to the parent /Users/bbest/Github/CLAUDE.md for R/Python style rules.

  One thing I noticed but left out (flag for you): data/product_filters.yaml uses a different, lowercase facet:value schema (region/tool with dashboard, infographic) that doesn't match the live tool_filters.yaml ProperCase convention — it looks like a legacy/orphaned file. Worth confirming whether it's still used or should be deleted.
  One thing I noticed but left out (flag for you): data/product_filters.yaml uses a different, lowercase facet:value schema (region/tool with dashboard, infographic) that doesn't match the live tool_filters.yaml ProperCase convention — it looks like a legacy/orphaned file. Worth confirming whether it's still used or should be deleted.

Yes, proceed with harmonizing all the tags and their usage. The data/product_filters.yaml is I
  believe vestigial and should be removed (after confirming it is not used), since products was
  renamed to tools (or maybe the tools/ index needs to properly point to the working
  tool_filters.yaml). This should be confirmed by looking at the /tags page, which ideally would
  also describe results here and in the search with different cards  based on content type (like a
  header tag similar to the news card with "month year" over news image).

  All verified — year buttons render descending (2021→2016); minify had just dropped the attribute quotes from my grep. Everything builds clean and works in the browser.

  Summary

  Done. Here's what changed, grouped by your three asks.

  1. Removed the vestigial files
  - data/product_filters.yaml was confirmed unused (referenced nowhere in templates — only tool_filters/paper_filters were). Deleted it, along with tool_filters.yaml and paper_filters.yaml, now superseded by a single source.

  2. Harmonized all tags into one canonical source — data/tags.yaml
  - Every facet (method/tool/place/org/topic/type/year) lives in one file with curated filter-button values plus an aliases map for proper labels of open-set values.
  - Fixed the /tags inconsistency you spotted: Hugo lowercases taxonomy terms, so the old case-sensitive lookup fell back to humanize — the index showed "Geobon", "Noaa iea", "Nationalmarinesanctuaries". tag.html now resolves labels case-insensitively from tags.yaml, so the index reads "GEO BON", "NOAA IEA", "Nat'l Marine Sanctuaries", "AIR Centre", "Seabed 2030" everywhere consistently.
  - tools/list.html and papers/list.html filter bars now read tags.yaml (via each facet's filters: list); the Papers Year buttons are generated from the papers themselves, so import_papers.py no longer writes a filter file.
  - Fixed the stray undefined method.Data-Mgmt → aliased to "Data Management".

  3. Type-aware cards on /tags term pages and search
  - New card.html dispatcher routes by content type: news = month/year badge over banner, events = date, papers = year badge over a placeholder (the news-card motif you described, applied to papers), everything else = generic image card.
  - New layouts/_default/taxonomy.html renders a tag's results grouped by type (verified in-browser: "Genomics" → Working groups, Methods, Tools, Papers with year badges, News, Events).
  - Search (search.html + Pagefind) renders the same type-aware cards with thumbnail + badge. This required emitting per-page Pagefind meta (type/badge/image) in baseof.html — verified in-browser that news shows "JAN 2022", tools "TOOLS", etc., images load, and excerpts are clean (data-pagefind-ignore keeps the hidden meta out of result text).

  Also renamed the vestigially-named card-product.html → card-tool.html, and updated README.md and CLAUDE.md to document the single tags.yaml registry and the card/search architecture.

  Verified throughout: hugo --gc --minify builds clean (442 pages, exit 0), pagefind indexes 329 pages + 5 filters, and I drove the actual rendered /tags/ and /search/ pages in Chrome to confirm.

  Two notes:
  - I did not commit anything (you didn't ask). When you're ready, the relevant changes are the data/, layouts/, scripts/import_papers.py, static/css/components.css, README.md, and new CLAUDE.md/data/tags.yaml files.
  - Your working tree also has unrelated uncommitted edits I didn't touch (data/methods.yaml, layouts/404.html, scripts/check_links.py, scripts/linkcheck_allow.txt) — left them as-is.

## 2026-06-23.b + Tools, incl Trainings, from `marinebon/*`, `noaa-onms/*`, `noaa-iea/*`

Now comb all repositories under github.com/marinebon github.com/noaa-onms and develop a table for considering new additions to the Tools. See also the Glossary and Repository listing of latest paper on MBON indicators with repository references at `/Users/bbest/Library/CloudStorage/GoogleDrive-ben@ecoquants.com/.shortcut-targets-by-id/1sppUmlMtZ-sXaBm72M1-8PnjVudXO91v/US MBON Public Folder/Working Groups/BioIndicators/manuscripts/indicators/ocean_indicators_manuscript_DRAFT_v2.docx`. Try to classify each according to the existing tags (especially tool.*) and record date_last_commit, website if listed, screenshot of website (using webshot2 a la existing tools), status of website, description. Provide a recommendation for inclusion, exclusion, include if updated, etc with any notes. Place the table and images in a safe place within this repository for pushing to the Github repo without interrupting the regular hugo website.

⏺ Done — the review is committed and pushed to `tools-review/` (viewable at github.com/marinebon/hugo2/tree/main/tools-review).

  **What I built**

  **Scope**: Combed all **108 repos** — 90 under `marinebon` + 18 under `noaa-onms` — via the GitHub API, and cross-referenced the indicators manuscript's **Supplement S3 (Source Code Repositories)** and software section to
  prioritize indicator-relevant tools and borrow its descriptions. (The unpublished draft is not reproduced — I deleted the converted text before committing.)

  Disposition: 11 already on-site · **17 candidates** · 80 excluded (websites, workshops, backend infra, superseded demos, analyses).

  **Deliverable in `tools-review/`**:
  - `README.md` — a recommendation table + per-candidate detail cards with embedded screenshots, classified by `tool.*`/method/org tags, each with date_last_commit, website + 🟢/🔴 HTTP status, and a
  recommendation. 
  - `inventory.csv` — all 108 repos with disposition + reason.
  - `img/` — 13 webshot2/chromote screenshots (mirroring your screenshots.R pattern).

  **Top recommendations (Include)**: `obisindicators`, `extractr`, `onmsR` (R packages); `sanctsound` (Portal); `map-of-activities` (App); `eco-indicators` (App — though the screenshot showed it's still an early landing
  page).

  Safe placement: `tools-review/` is a top-level dir Hugo doesn't process — verified the build is clean (exit 0) and nothing leaks into public/.

  Two notes

  - 3 sites are down (404): `obis-hex-map`, `sdm-explore`, `sdg14-shiny` — flagged "include if live/updated."
  - `MarineSDMs` screenshot failed (page render timeout, even via chromote) — noted as unavailable in the doc; the row is otherwise complete.

  Also FYI: inventory.csv includes ~9 manuscript-cited repos in other orgs (CalCOFI, MarineSensitivity, noaa-iea/ecoidx, GEO-BON, iobis) that I listed for context but didn't recommend, since they're outside
  the two orgs you asked me to comb — easy to fold in if you want them considered too.

Excellent! I fixed MarineSDMs website so should now be able to screenshot, and lets include. Also noaa-onms/sanctsound should be tool.Infographic. proceed with including all recs, and promote workshop /    
  course / training materials with new tool.Training (and Trainings into navbar of Tools)   

⏺ The screenshot job is already running in the background and will notify me when it completes — no need for a separate monitor. The filter facet, navbar, and all 19 content pages are done and the build is
  clean. I'll verify the images and commit once the renders finish.

  Interim status:
  - 19 tool pages created (14 software/data + 5 training workshops), build passes.
  - tool.Training facet added + Trainings in the Tools navbar (alphabetical).
  - sanctsound reclassified to tool.Infographic. 
  - MarineSDMs included (site confirmed live again).
  - Held back only obis-hex-map and sdm-explore (still 404).
  - Screenshots rendering into static/img/tools/ (6/19 done so far).

  I'll pick up automatically when the screenshot render finishes to confirm all 19 images landed (re-shooting any failures) and commit everything.

⏺ Committed and pushed. The Tools catalog grew from 16 to 35 entries.

  What was added

  19 new Tools (all with live sites + webshot2 card screenshots in static/img/tools/):

  Software / data (14) — sanctsound (reclassified tool.Infographic per your note), map-of-activities, extractr, obisindicators, onmsR, eco-indicators, edna-vis, aquamaps-downscaled, MarineSDMs
  (re-screenshotted now that you fixed its site), py-dwc-viz, gmbi, extract-app, intertidal-temps, data-reports.

  Training workshops (5) under the new tool.Training facet — USF Moore taxa mobilization (2026), MBON AIR mobilization, and Pole to Pole Mexico / Brazil / Colombia.

  Navbar + filter — added a tool.Training value to data/tool_filters.yaml and a Trainings entry to the Tools dropdown (alphabetical: Apps · Infographics · Packages · Portals · Protocols · Trainings).

  Disposition note added to tools-review/README.md.

  Two things to flag

  - Held back 2 of the 17 recs — obis-hex-map and sdm-explore still return 404 (no live GitHub Pages site). They're ready to add the moment their sites publish; everything else is curated.
  - One adjacent training resource left out of scope: ioos/bio_mobilization_workshop — the canonical IOOS/MBON biological-data-mobilization curriculum (cited by the manuscript), live and directly relevant,
  but it lives in the ioos org rather than the two you asked me to comb. Say the word and I'll add it as a tool.Training too.

  The newer/stronger tools were given lower weights so they sort ahead of the older ones (gmbi, extract-app, intertidal-temps) within the catalog. The site build is clean and the page is live-deployable.


Yes, add `ioos/bio_mobilization_workshop` as a `tool.Training`. Similarly add `tbep-tech/shiny-workshop`, and `noaa-iea/r3-train`. Comb through all repos in https://github.com/noaa-iea and update all relevant files in `@./tools-review`.

Let's move these from `tool.App` to new `tool.Workflow` and add **Worfklows** to Tools navbar:
- [Sanctuary Eco-Indicators · MBON](http://localhost:1313/tools/eco-indicators/)
- [AquaMaps Downscaled · MBON](http://localhost:1313/tools/aquamaps-downscaled/)
- [Intertidal Temperatures · MBON](http://localhost:1313/tools/intertidal-temps/)
And a few more changes:
- [MarineSDMs · MBON](http://localhost:1313/tools/marine-sdms/): tool.Package -> tool.Protocol
- [onmsR · MBON](http://localhost:1313/tools/onmsr/): for image use https://noaa-onms.github.io/onmsR/reference/figures/onmsR.svg with white background padding.
- [seascapeR · MBON](http://localhost:1313/tools/seascapr/): similarly to onmsR, use white backgrounded https://marinebon.org/seascapeR/logo.svg.


⏺ All done and pushed. Summary of this pass:

  Tools site changes
  
  - New tool.Workflow facet + Workflows in the Tools navbar (alphabetical, after Trainings). Moved eco-indicators, aquamaps-downscaled, intertidal-temps from tool.App → tool.Workflow.
  - MarineSDMs: tool.Package → tool.Protocol.
  - 3 new tool.Training tools with screenshots — ioos/bio_mobilization_workshop, tbep-tech/shiny-workshop, noaa-iea/r3-train (Tools catalog now 38, with 8 trainings).
  - onmsR and seascapeR card images replaced with their white-padded SVG hex logos (rsvg-convert → PIL composite on a 16:10 white canvas).

  noaa-iea sweep → tools-review/

  Combed all 20 noaa-iea repos: 2 already on-site (fk-esr-info, ak-info), 6 candidates, 12 excluded. Added to:
  - inventory.csv (now 128 repos across the three orgs)
  - README.md — a new "noaa-iea sweep" section with a recommendation table + screenshots, plus an updated change-log banner.

  Candidates surfaced (in the review, not auto-added to the site): ecoidx (manuscript-cited IEA indicator package — include if updated), ca-esr-info (California Current ESR infographic — include, sibling of
  the on-site FK/AK infographics), and three demo/borderline ones (ecoidx-report, ecoidx-dashboard, fl-wq — maybe). r3-train is both a noaa-iea candidate and one of the three I added to the site this pass.

  Build is clean (0 errors), tools-review/ stays out of the Hugo output.

  One small note for next time: those two review candidates — ecoidx and ca-esr-info — are the strongest noaa-iea additions (ecoidx is manuscript-cited; ca-esr-info matches infographics you already publish).
  Say the word and I'll promote them onto the site like the others.

✻ Baked for 9m 19s

Yes, add ecoidx, ca-esr-info, fl-wq. Fix the missing basemap in `@~/Github/noaa-iea/fl-wq`

⏺ Both parts done and pushed.

  **fl-wq basemap fix** (`noaa-iea/fl-wq`, pushed to master)

  Root cause: Esri retired the Ocean_Basemap MapServer — its tile URL now returns HTTP 500, so the Leaflet map showed only the marker + attribution with blank tiles. The fix switches to the live
  Ocean/World_Ocean_Base service (verified 200):
  - date_template.Rmd — replaced addProviderTiles(Esri.OceanBasemap) with explicit addTiles() URLs (durable — no longer depends on the leaflet-providers alias), plus the ocean reference/labels layer.
  - docs/site_libs/.../leaflet-providers_1.9.0.js — updated the bundled provider variant so the already-deployed dashboards render tiles immediately (shared site_libs, so all date pages fixed at once).

  I confirmed the redeploy went live and the screenshot now shows the SW-Florida coastline behind the marker.

  **3 tools added** to the site (hugo2, pushed to main)

  - **ecoidx** — tool.Package · method.Indicators · org.NOAA-IEA (manuscript-cited IEA indicator package)
  - **California Current ESR Infographic** — tool.Infographic · org.NOAA-IEA (sibling of the Florida Keys ESR and Alaska IEA infographics)
  - **Fisher Water Quality Monitoring** (fl-wq) — tool.App · place.South-Florida · org.NOAA-IEA, screenshotted after the basemap fix

  The tools-review/README.md now marks all three as included (with a change-log banner noting the fl-wq basemap fix), and tools-review/img/fl-wq.png was refreshed to the fixed version. The Tools catalog is now 41 entries; build is clean.

  One note: I left three of your in-progress edits untouched and uncommitted in the working tree — extract-app.md (draft: true), and gmbi.md / py-dwc-viz.md (tool.App → tool.Package). They're yours to commit when ready; say the word if you'd like me to fold them into a commit instead.


Add these two:
- ioos/bio_data_guide: tool.Protocol, tool.Training
- bbest/dismapr: tool.Package

⏺ Both added and pushed. Tools catalog is now 43 entries.

  - Bio Data Guide (ioos/bio_data_guide) — tool.Protocol + tool.Training, plus org.OBIS and place.Global. IOOS Standardizing Marine Biological Data Working Group's guide for mobilizing biological data to
  Darwin Core/OBIS.
  - dismapr (bbest/dismapr) — tool.Package, plus method.Traditional and place.US. R access to NOAA's DisMAP species-distribution/range-shift APIs (derived from bottom-trawl surveys).

  Both sites are live (200), screenshotted as card images, build is clean. Since bio-data-guide carries both tool.Protocol and tool.Training, it'll surface under both the Protocols and Trainings filters/nav.

## 2026-06-23 tag tool.Library -> Package

Let's change tag `tool.Library` to `tool.Package` and update the navbar Tools accordingly to **Packages** (keeping alphabetical order).

### pad seascapeR hex logo
Can you pad the `seascapeR` **hex logo** https://marinebon.org/seascapeR/reference/figures/logo.png so the entirety of it (with subtle margin) appears in the card [Image #1]

### fix funk cards: grafana dashboard, fk storymap

Come up with a standardized fix for these 2 tools: 1) https://marinebon.org/hugo2/img/products/early-alert-dashboard.png needed more time to render. 2) https://marinebon.org/hugo2/img/products/storymap-fk-fwri-water-quality.png is crazy long full page without any of the images loaded (probably more time needed to render). The point is to make the cards look nice. Also noticing the vestigial "products" name in img url that should be swapped for updated "tools"

## 2026-06-22 **methods** content and hero

Let's brainstorm on adding another content type **methods** that has its own hero section below the first hero and above the network globe. Each page should hightlight the different methods for observing, synthesizing and disseminating that MBON seeks to advance. These are also reflective of the working groups: genomics (DNA, eDNA), remote sensing (seascapes, imagery), tracking (telemetry), sound (passive & active acoustics), indicators (synthesis, dissemination), data management (DMAC, data sharing). It should also give some mention of supporting and augmenting traditional methods (trawl, visual & acoustic survey), which can be expensive at scale. Come up with a prompt for an image-generating LLM to make a graphic that can be converted to an interactive display in the hero section highlighting each method, so method labels live seperatly on top and when icon hovered shows a description.

We're looking for a simplified scientific illustration, but let this graphic be an inspiration [Image #2] 

**PLAN**: `@./_claude/2026-06-22 add methods.md`

Excellent, proceed with Gemini Pro image generated to `~/Downloads/gemini_pro.png`

Make the description show on hover. Resolve the z-index problems with the underlying point markers showing throught the description per [image screenshot]

⏺ Two root causes fixed:

  1. Hover now works — removed hidden attribute from the tip <div> in the template. The attribute's browser-level display:none was overriding the CSS :hover rule regardless of specificity. Tips are now hidden
  purely by display:none in CSS, which :hover / :focus-within / .is-active can freely override.
  2. Z-index bleed-through fixed — added z-index:30 to the entire .method-spot wrapper on hover/focus/active. Previously each spot sat at z-index:2 and the tip had z-index:20 within that stacking context,
  meaning sibling spots (also at z-index:2) could paint over it. Elevating the whole hovered wrapper to z-index:30 puts it above all idle sibling spots and their pins.


Add Methods to navbar. Rename Products to Tools (and associated content and content types), which will be software and data portals. Clean up the tags (http://localhost:1313/tags/) and filters (eg in old Products / new Tools) to consistently refer to tags from recently added "Method. remote sensing" to "method.remote sensing" but then consistently drop the prefixes (eg "method.") and color code for given category. Rename Regions to "place." Resolve a prefix for all tags, creating new ones if need be. Can we update the Search page to filter across content types for any given tag (along with free text search)?

⏺ This is a wide-ranging refactor. Let me survey the full picture before touching anything.

Move "Genomics & eDNA" (not EDNA) to above the double helix, and the Indicators & Data to above the dashboards (over land) per screenshot with pink arrows [image]

Now the descriptions for Methods hover/click are cutoff by border [Image #6] [Image #7]

⏺ Pushed. Here's what landed in this commit:

  - Products → Tools: all 17 content files, both layout templates, and products-filter.js renamed via git mv; every template reference (/products/ hrefs, button text, section headers, footer links) updated
  - Tag normalization: all content across methods, network, news, and tools normalized to prefix.value dot notation (e.g., place.global, method.genomics, org.noaa)
  - New CSS token variables: --facet-place, --facet-method, --facet-topic with matching .tag--place, .tag--method, .tag--topic classes
  - JS filter: tools-filter.js now matches facet + '.' + val and uses data-tool-* attributes
  - Methods hotspot positions: genomics moved to x=73,y=42 (above DNA helix); indicators moved to x=93,y=22 (dashboard strip)
  - Search: Pagefind filter facets wired up (method, place, org, type, topic) with data-pagefind-filter spans injected into all single-page templates — the search page will show facet checkboxes once you
  rebuild the pagefind index with npx pagefind --site public


⏺ Two changes landed:

  1. overflow:hidden removed from .methods-scene — tooltip cards can now escape the image boundary. border-radius moved onto the <img> tag so the image corners still look rounded.
  2. Edge-anchor modifiers — the template automatically assigns:
    - .method-spot--right when x > 75 (Indicators at 93, Genomics at 73) — tooltip aligns its right edge to the pin instead of centering, preventing rightward overflow
    - .method-spot--left when x < 25 (Tracking at 14) — tooltip aligns its left edge to the pin

  Refresh the dev server and the cards for Genomics and Indicators should now be fully visible.

The tag caps scheme is inverted: category.TagProper should be the way. Also let's add partners (revisit @../marinebon.github.io/) to the Network nav and convert Thematic BONs to Working Groups, adding eDNA, indicators, eco-indicators and data as working groups. Expand the Methods menu to a simple drop-down.

⏺ Pushed. Here's what landed:

  Tags — All 202 tag instances across 80 files renamed to prefix.ProperCase. topic.thematic became topic.Working-Group. tool_filters.yaml values updated to match.

  Network dropdown now has three columns:
  - Regional MBONs (unchanged)
  - Working Groups — BioSound, BioTrack + 4 new: eDNA, Indicators, Eco-Indicators, Data Management
  - Partners — 10 orgs with external links (IOOS, GEOBON, GOOS, GEO, OBIS, AIR Centre, GCRMN, MarineGEO, SCAR, LifeWatch)

  Methods — now a single-column dropdown listing all 6 method pages with a chevron caret, consistent with the Network dropdown style.

### methods hero image

The image needs to be redone. Google Gemini Pro NanoBanana is much better at one shot images -- tweaks become fraught with complications. Provide a fresh prompt borrowing with old:

```
A wide-format (16:9) scientific illustration in a simplified, flat-diagram style showing a cross-section of the ocean environment from outer space to the seafloor. Style: clean vector-like scientific illustration with a limited palette of deep navy, ocean teal, steel blue, and warm coral accents on a near-black navy background. No text or labels anywhere in the image.

Composition, top to bottom:
— Space / upper atmosphere: a satellite in low Earth orbit, downward-looking sensors implied by subtle scan-line fans toward the ocean surface.
— Open ocean surface: a research vessel on the water, with a trawl net implied below the hull; seabirds in flight; faint sonar cone radiating downward from the hull.
— The ocean surface itself as a crisp, luminous boundary layer with gentle waves.
— Shallow coastal zone (right side): kelp forest and coral reef visible near the seafloor edge; a diver with a camera and slate floating mid-column.
— Mid water column (center): a streamlined underwater glider/AUV emitting acoustic fan beams in multiple directions; a hydrophone mooring rising from the seafloor with signal rings; two or three fish with small tag devices on them, signal arcs radiating outward; a faint double-helix DNA strand spiraling upward from a water-sampling bottle, indicating environmental DNA capture.
— Deep seafloor (bottom): benthic lander instrument package with sensor arms; soft coral and sparse invertebrates for ecological context.
— Far right edge: a translucent data-visualization overlay — a thin vertical strip showing abstract time-series lines and a world-map heat-map fragment — suggesting the synthesis and dissemination pipeline.

Atmosphere: deep, luminous, scientifically authoritative. The underwater lighting should suggest sunlight refracting through the surface. The overall tone is dark ocean blue with teal bioluminescence accents. The illustration should feel like a premium magazine centrepiece — detailed enough to reward close inspection but clean enough to work as a UI background. Aspect ratio 16:9, no letterboxing.
```

Running this in Gemini 3.5 Thinking produced: `@~/Downloads/gemini_thinking.png`

Then upgrading to  Gemini 3.1 Pro produced: `@~/Downloads/gemini_pro.png`

But then here are my complaints for Pro:

```
I like that there is a fish and coral. Add a whale and turtle. Remove the seafloor robot, but add cables extending from traditional ship a drone and bottle collector with eDNA above. Remove the robotoic arm holding the DNA attached to the rock

I like that there is a fish and coral. Add a whale and turtle. Remove the seafloor robot, but add cables extending from traditional ship a drone and bottle collector with eDNA above. Remove the robotoic arm holding the DNA attached to the rock
```

And it produced: `@~/Downloads/gemini_pro_v2.png`

The rosette should not be on the floor. Probably a good idea to include a buoy in the scene and emphasize instruments/vessels maybe a shore-based rocky/sandy beach quadrat with person above like human in loop with scuba already.

  ---
  Key changes from the v2 prompt:
  - Rosette moved to mid-water on a ship cable, not the seafloor
  - Shore scene added far-left: person doing quadrat survey on rocky intertidal
  - Buoy added at surface with mooring cable 
  - Drone added above the ocean near the satellite
  - No seafloor robot or robotic arm — explicitly removed
  - Whale and turtle kept from v2
  - Data strip stays far right 

Ok, use the latest `@~/Downloads/gemini_thinking_v3.png`. This image is ~6 MB (like the previous), so should get downsampled for use on the web.

### **papers**

Let's add **papers** as a new content type and navbar item with allowance for any of the tags. The papers should be filterable by tags and absorbable via Coins -- maybe a Hugo helper out there.  Hugo websites handle academic citations and publications using plugins like [Hugo-Bibliography](https://dh-tech.adho.org/blog/2025/07/11/hugo-bibliography/) or tools like [Hugo Simple Cite](https://github.com/joksas/hugo-simplecite) or [Lucid Manager Bibliography](https://lucidmanager.org/productivity/hugo-bibliography/). These tools expose bibliography entries via COinS (OpenURL-based metadata), enabling reference managers like Zotero to automatically detect and import publication citations directly from the webpage.

I'm seeing some publications on the old websit here:
https://web.archive.org/web/20231213233358/https://marinebon.org/publications/. Perhaps extractable in @../marinebon.github.io.

⏺ Pushed. Here's what's live:
  
  - /papers/ — filterable list of 88 publications, sorted newest first, with Method and Year facets using the same JS filter pattern as Tools
  - /papers/{slug}/ — single paper page with full author list, journal, DOI link, abstract, and an invisible <span class="Z3988"> COinS element — the Zotero browser connector will detect it and offer
  one-click import
  - Papers in the navbar at weight 4 (between Methods and Tools)
  - scripts/import_papers.py left in the repo so you can re-run it if the source library is updated

  The COinS title attribute on the andruszkiewicz paper encodes all 6 authors, title, journal, year, and DOI correctly. Install the Zotero browser connector and visit any single paper page to test the import.

### re-org: network -> node, working-group

We need to reorganize the content:

- There are not actually thematic nodes to MBON in its current form -- they are simply **Working Groups** (WG) that are tightly connected to Methods. WGs should be a seperate content type `working-group` with `Lead(s)` pointing to individuals in the content type YAML. 
  * biosound.md
  * biotrack.md
  * data-mgmt.md
  * eco-indicators.md
  * edna.md
  * indicators.md
A button to all the Working Groups could link out from the Methods hero as well as the Network hero. 

The "Strategic collaborators" (which is really the subtitle to Partners) should show up at the bottom of Network hero and a link out to the **Partners** page, which should have each listed with a header and description (to be fetched from a new yaml `partners` content type). The Partners link should also be added to the Network navbar.

- The Regional MBONs should be split in the hero and navbar into:
  * International
    - asia-pacific-mbon.md
    - europe-mbon.md
    - pole-to-pole-americas.md
  * USA
    - arctic-mbon.md
    - central-california-mbon.md
    - coastal-new-england-mbon.md    
    - great-lakes-mbon.md
    - gulf-of-maine-mbon.md    
    - mid-atlantic-mbon.md
    - northern-california-current-mbon.md
    - south-florida-mbon.md
    - southern-california-bight-mbon.md

The **Tools** should become better organized with a new drop-down navbar pointing directly to the tools page filtered by one of: "Portals" (Type.Portal -> tool.Portal), "Apps" (tool.App), "Infographics" (Type.Infographic  -> tool.Infographic), "Libraries" (tool.Library), "Protocols" (tool.Protocol).

- biotrack-portal.md: tool.Portal
- climate-dashboard-app.md: tool.App
- climate-dashboard.md: tool.App
- coastwatch-obis.md: tool.App
- early-alert-dashboard.md: tool.App
- edna-explorer.md -> mbon-data-portal: tool.Portal
- infographic-cinms.md: tool.Infographic
- infographic-florida-keys-esr.md: tool.Infographic
- infographic-iea-alaska.md: tool.Infographic
- infographic-ocnms.md: tool.Infographic
- infographiq.md: tool.Library
- pole-to-pole-atlas.md: tool.Protocol
- sanctuary-condition-reports.md -> sanctuary-watch.md: tool.Portal, tool.Infographic
- seascapes-viewer.md: tool.App
- seascapr.md: tool.Library
- storymap-fk-fwri-water-quality.md: tool.Infographic

Tags that should get dropped: Type.Tool, Type.Data, Type.Instance
Tags that should get renamed: Org.NMS -> org.NationalMarineSanctuaries

Comb throughout the website for any inconsistencies, including navbar, footers, related / cross-linked content. For instance, all tags should have a lower prefix before "." and use capitals after.

Can you add tags to the Search interface, perhaps selectable from auto-complete list with AND (vs OR) to filter?

⏺ Everything pushed. Here's a summary of what was done across all 5 areas:

  A. **Working Groups** — 6 files moved from `content/network/` → `content/working-groups/` with `leads:` field added. New `layouts/working-groups/list.html` + `single.html`. Old `/network/biosound/` etc. redirect via
  aliases. "View working groups" CTA added to both the methods band and the network hero.

  B. **Partners** — 10 partner entries in `data/partners.yaml` now have descriptions. `/network/partners/` shows logo + name + description cards. The Network hero shows the partner logo strip with a "View all
  partners →" link. Nav dropdown replaced the 10 individual partner links with a single "All partners →" link.

  C. **Regional split** — 12 nodes tagged with `geo: USA` or `geo: International`. Nav now has USA (9 nodes) + International (3 nodes) columns. Network list page has separate USA and International grid sections.

  D. **Tools dropdown** — Nav Tools item now has a dropdown: All / Portals / Apps / Infographics / Libraries / Protocols. `/tools?tool=Portal` pre-activates the Portal filter. `type.*` tags replaced with `tool.*`
  across all 16 tools. Two files renamed (`edna-explorer` → `mbon-data-portal`, `sanctuary-condition-reports` → `sanctuary-watch`) with aliases. `org.NMS` → `org.NationalMarineSanctuaries` everywhere.

  E. **Search** — Custom autocomplete widget using the programmatic Pagefind API. Type-ahead tag suggestions from `pagefind.filters()`, dismissible chips, AND logic across selected facets. The `?q=` URL param still
  pre-fills the text search.

  Note: the WG `leads` for data-mgmt, eco-indicators, edna, and indicators are placeholder "TBD" — you'll want to fill those in with actual names.

The Tools filter doesn't seem to actually filter anything, eg http://localhost:1313/tools/?tool=Portal shows All and I am not seeing the Portal tag selected 

⏺ Pushed. The two root causes were:
  
  1. Timing race — defer scripts run just before DOMContentLoaded fires, but Hugo's dev server sometimes delivers the script after that event has already fired. Wrapping in
  addEventListener('DOMContentLoaded', ...) then silently does nothing. The fix is the readyState === 'loading' guard: if the DOM is still loading, wait for the event; if it's already ready, call init()
  immediately.
  2. preBtn.click() bypassed — simulating a DOM click event to pre-activate a filter is fragile. The fix directly writes into sel and adds the is-active class, then calls apply() unconditionally at the end of
  init().

  Hard-refresh the page (Cmd+Shift+R) to clear the cached old JS, then try /tools/?tool=Portal — you should see the Portal button highlighted and only the 3 portal tools showing.

Add leads:
- Data Management: Matt Biddle (NOAA Integrated Ocean Observing System)
- Indicators: Ben Best (Ocean Metrics LLC)
- eDNA: Luke Thompson (NOAA Atlantic Oceanographic and Meteorological Laboratory)
- Eco-Indicators: Joshua Kilborn (University of South Florida)

⏺ Done. All four working groups now have named leads — Matt Biddle, Ben Best, Luke Thompson, and Joshua Kilborn. BioSound and BioTrack already had leads (Liz Ferguson/Neil Hammerschlag and Neil Hammerschlag respectively), so all six working groups are now fully populated.

Consider revising the Network hero with spinning globe to seperate the many USA nodes from the few International MBON nodes. Update text since no longer showcasing "thematic" nodes -- these are simply the Working Groups (mentioned above in Methods hero). And the Partners did not get migrated from below into the Network hero. Reconsider all titles, subtitles and text in the home page for consistency. Also, consider alternating light and dark between sections which presently are not (viewing from top to bottom): white navbar, blue overview, dark blue Methods, lighter blue Network, white News, white Tools, dark Strategic Collaborators (Partners which should be moved up to Network hero), and dark footer. 

⏺ Good. Now I have the full picture. Here's my plan:

  Color fix: swap News (white → currently tint) and Tools (tint → currently white), move partner strip from footer into the globe section. This produces: dark(hero) → dark(methods) → dark(globe+partners) →
  white(news) → tint(tools) → dark(footer) — proper alternation.

  Globe: split chips into USA / International labeled groups, remove "thematic" text, add partner strip at bottom.

  Network page: remove partner strip from page-header (it'll be in the globe section below).


⏺ Done. Here's what changed and why:
  
  Section color rhythm (homepage, top to bottom):

  ┌──────────────────┬───────────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
  │     Section      │                Before                 │                                 After                                  │
  ├──────────────────┼───────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
  │ Hero             │ dark photo                            │ dark photo ✓                                                           │
  ├──────────────────┼───────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
  │ Methods          │ dark                                  │ dark ✓                                                                 │
  ├──────────────────┼───────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
  │ Globe + Partners │ dark / separate dark stripe at bottom │ dark (partners now live inside the globe section)                      │
  ├──────────────────┼───────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
  │ News             │ foam tint                             │ white — stronger contrast after dark                                   │
  ├──────────────────┼───────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
  │ Tools            │ white                                 │ foam tint — alternates with white news                                 │
  ├──────────────────┼───────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
  │ Footer           │ dark                                  │ dark ✓ (now arrives cleanly without the orphaned partner stripe above) │
  └──────────────────┴───────────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘

  Globe changes:
  - Node chips split into a "USA" group (9 nodes) and an "International" group (3 nodes), each with a faint monospaced label above
  - Heading updated to "Regional nodes from Arctic to Antarctic" (no more "thematic")
  - Partners logo strip now lives at the bottom of the globe section on both the homepage and the /network/ page — one consistent location

  Network page: Partner strip removed from the page-header (where it used the wrong CSS class). It now appears in the globe section immediately below, using the correct .globe-partners styling on the dark
  gradient background.

Drop the duplicative orange dot in the label of the globe (already orange dot on map and only one label showing at a time).

Change Network hero title from "Regional nodes from Arctic to Antarctic" "Regional nodes from the US and Internationally"


⏺ Done. Two changes:
  
  1. Globe canvas labels — the small 3px dot that was drawn inside the text callout box (both the orange active dot and yellow hover dot) is removed. The label now starts flush after the stem line, with the
  box sized to fit just the text. The node's main dot on the globe surface still shows the orange/yellow indicator.
  2. Globe heading — changed from "Regional nodes from Arctic to Antarctic" to "Regional nodes from the US and internationally".

### 404 not found

Populate a lovely 404 page that automatically shows search results                                                                                                                                            
⏺ All good. Here's what was built:

  layouts/404.html — A "Lost at Depth" page with:
  - Eyebrow label — Signal lost · depth unknown in teal mono
  - "404" numeral — enormous (clamp(6rem, 22vw, 14rem)), gradient from aqua-100 → teal-300 → cobalt-300 → navy-500, with a pulsing bioluminescent glow animation
  - Volumetric light rays — conic-gradient shafts that slowly drift
  - 32 bioluminescent bubble particles — generated by JS, float upward with random size/speed/phase/opacity
  - Wave SVG — organic break between the dark abyss hero and the light search surface
  - Auto-search — extracts terms from the 404 URL path (strips stop words, numbers, short fragments), pre-fills Pagefind and fires the search automatically; hint text shows Showing results for <em>term</em>
  - Action buttons — "↑ Return to surface" and "Browse all"

Looks good, but the suffix to the website was not populated into the Search

⏺ Three fixes applied:

  1. .replace(/\.html?$/i, '') — strips .html/.htm from the path before splitting, so accessing /404.html directly → path becomes /404 → 404 is all digits → filtered → terms = "" → shows "Explore MBON content
  below" instead of searching for the useless word "html".
  2. Split regex changed from /[\/\-_\.]+/ to /[\/\-_]+/ — no longer splits on dots, so paths like /tools/my.tool stay coherent.
  3. Particles moved before PagefindUI and PagefindUI wrapped in try/catch — particles always render even if pagefind isn't built yet.

  In production (Netlify/GitHub Pages), the real 404'd URL is preserved in the address bar, so /papers/lafferty-at-2021 correctly yields search terms papers lafferty.

### add **benthic survey**

Add benthic surveys to Methods and hero (quadrat person on coast already in image), at sea and on coast (especially rocky tidal and sandy beach; photo quadrat). Differentiate from surveys at sea (∆ "Traditional Surveys" to "Traditional At-Sea Surveys" for label on hero image). 

Link to tools/pole-to-pole-atlas

⏺ Done. What changed:
  
  - New "Benthic Surveys" hotspot placed at the rocky coast on the left side of the illustration (x=14, y=46) — exactly where the quadrat figure already is in the image. Tooltip appears to the right of the
  pin via the method-spot--left class. Covers rocky intertidal transects, sandy-beach surveys, and photo quadrats.
  - New /methods/benthic/ page with kelp.jpg banner, full description of all three coastal survey types, and a direct link to the Pole to Pole Data Atlas in the final section.
  - "Traditional Surveys" → "Traditional At-Sea Surveys" in both data/methods.yaml (hotspot label) and content/methods/traditional.md (page title), making the ship vs. shore distinction explicit.
  - Pole to Pole Atlas now tagged method.Benthic so it surfaces when users filter tools by benthic method.
  - tool_filters.yaml has Benthic added to the method facet for the tools filter bar.

Alphabetically order the Methods navbar elements

⏺ Done. The Methods dropdown now reads: Acoustics → Benthic Surveys → Genomics & eDNA → Indicators & Data Management → Remote Sensing → Tracking → Traditional At-Sea Surveys.

Alphabetically order the Tools navbar elements

⏺ Done. Tools dropdown now reads: All Tools → Apps → Infographics → Libraries → Portals → Protocols.

### Github Issue templates (+ events content type)

Design Github Issue templates to enable issue creation to add or edit content. Pre-populate with all necessary YAML and instructions with help on finding tags and formatting basics. Make these consumable via a Github Action that imports images and injects content into the website. Consider a link directly on the pages enabling issue creation for edits of existing content. I think this is all doable, but be creative with the most efficient system that minimizes the technical burden for end users contributing.

In reality events should be its own content type too, and added under the News navbar, with a listing. Please do that first, then the rest. 

←  ☒ Edit flow  ☒ Add forms  ☐ Papers  ✔ Submit  →

For editing existing pages, how should the on-page link behave?

 1. Issue form + GitHub      ✔    ┌───────────────────────────────────────────┐
   editor                         │ Page footer:                              │
  2. Issue form only              │   ✏️  Suggest an edit   ·   Edit on GitHub │
  3. GitHub editor only           │    └ issue form          └ raw web editor │
                                  │      → Action → PR          → instant PR  │
                                  └───────────────────────────────────────────┘

←  ☒ Edit flow  ☒ Add forms  ☐ Papers  ✔ Submit  →

Which content types should get dedicated 'Add new…' issue forms?

 1. News, Events, Papers,    ✔    ┌───────────────────────────────────────────┐
   Tools                          │ Add forms:                                │
  2. All content types            │ - Add News                                │
  3. News & Events only           │ - Add Event                               │
                                  │ - Add Paper                               │
                                  │ - Add Tool                                │
                                  │ (Network/WG → generic edit)               │
                                  └───────────────────────────────────────────┘

←  ☒ Edit flow  ☒ Add forms  ☒ Papers  ✔ Submit  →

How should adding a Paper work?

  1. DOI auto-fill                ┌───────────────────────────────────────────┐
  2. Full manual form             │ Form:                                     │
❯ 3. Both (DOI or manual) ✔       │   DOI (optional, auto-fills)              │
                                  │   — or —                                  │
                                  │   Title/Authors/Year/...                  │
                                  │   (manual fallback)                       │
                                  └───────────────────────────────────────────┘


⏺ Done — all five parts are implemented, verified with clean Hugo builds, committed, and pushed to main.

  **What shipped**

  **Part 1 — Events content type**. content/events.md split into 13 per-event files under a new content/events/ section, with layouts/events/{list,single}.html, a range-aware event-date.html formatter, and
  card-event.html. News is now a navbar dropdown (All News + Events). All dates display faithfully (Nov 1–4, 2022, October 2021, 2016–2018).

  **Part 2 — Issue Forms**. .github/ISSUE_TEMPLATE/ forms for News, Event, Paper, Tool, plus an Edit form and chooser config. Contributors pick tags from dropdowns (no facet.Value typing), drag-drop images, and
  get inline formatting help. Each auto-labels content:<type>.

  **Part 3 — Action + builder**. scripts/issue_to_content.py (tested for all five types) builds the Markdown file, maps friendly labels → facet.Value tags, imports dragged-in images, auto-tags methods, and
  fetches Crossref metadata for papers given a DOI. .github/workflows/content-from-issue.yml parses the form, runs the script, and opens a PR. buildFuture: true so upcoming events publish.

  **Part 4 — On-page links**. Every content page gets a ✏️  Suggest an edit (pre-filled issue) + Edit on GitHub bar (wired once in baseof.html), and the News/Events/Tools/Papers list pages get + Add buttons.

  **Part 5 — README**. Rewritten to correct the stale architecture and document the full contributor and maintainer procedures.

  **One manual setup step for the maintainer**

  For the workflow to open PRs with the default token, enable in repo Settings → Actions → General → Workflow permissions:
  - "Read and write permissions", and
  - "Allow GitHub Actions to create and approve pull requests"

  Without that toggle, create-pull-request fails with a permissions error. (The forms, on-page links, and Events type all work regardless.)

  **Note on your in-progress edits**

  I left your staged globe/hero/layout.css/_claude changes (the "reduce right-panel height" work) untouched and uncommitted — none of my commits include them, so they're still yours to finish.

  One thing worth deciding when you can test it live: the edit form's auto-apply only triggers when someone pastes a full ```markdown block; plain-language edit requests are left for a maintainer. If you'd prefer the on-page "Suggest an edit" to always prefill the current page content for editing, that's a worthwhile follow-up — but it runs into GitHub's URL-length limit on long pages, which is why I didn't default to it.


### tag fix

Why are all the news tags of incorrect format, eg "Place. pole to pole" vs "place.Pole-to-Pole" and not synchronized the tags page? Clean this up. Why also are the tags in the tags page not sorted alphabetically? [Image #3] [Image #4]

⏺ All fixes applied. Here's the full summary:

  Root causes:
  1. card-news.html called humanize (index . 0) on the raw full string "place.Pole-to-Pole" → the dot becomes a period with a space, giving "Place. pole to pole". Fixed to partial "tag.html" (index . 0).
  2. news/single.html had the same bug — humanize . on full tag strings in the banner. Fixed to partial "tag.html" ..
  3. tag.html emitted tag--Place (uppercase) when given a title-cased input; CSS only defines tag--place. Fixed with $facet | lower.
  4. Tags page had no dedicated template, falling back to _default/list.html with unsorted .Pages. Created layouts/tags/terms.html using .Pages.ByTitle for alphabetical order and rendering each tag via the
  tag.html partial (colored chips linking to their tag page).
  5. Bonus: humanize was ordinalizing years ("2016th"). Fixed with a numeric check — pure digit values skip humanize and display as-is.