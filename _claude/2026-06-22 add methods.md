# Plan: Methods Section with Interactive Illustration Hero

## Context

MBON wants to surface its observing methods as first-class content on the homepage — positioned between the photo-hero and the network globe. Each method maps to a working group (genomics, remote sensing, tracking, acoustics, indicators, data management) and the section should acknowledge that these modern approaches augment expensive traditional methods (trawl surveys, visual surveys). A scientific cross-section illustration (inspired by the MBARI "Observing Life in the Sea" artwork by Kelly Lance) serves as the background, with method hotspots overlaid in HTML so labels are always visible and hover shows a description card.

---

## 1. Image-Generation Prompt

Send this to an image-generating LLM (DALL·E 3, Midjourney, Stable Diffusion, etc.):

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

---

## 2. Method Hotspot Data — `data/methods.yaml`

Each entry drives one interactive hotspot overlaid on the illustration. Coordinates are expressed as percentage offsets from top-left corner of the image, tuned after the image is placed.

```yaml
- id: remote-sensing
  label: Remote Sensing
  icon: satellite
  x: 18    # satellite, upper-left quadrant
  y: 8
  summary: >
    Satellites and aerial sensors map ocean color, sea surface temperature, and
    habitat extent across millions of square kilometers — resolving patterns no
    ship survey could cover at that scale. Seascapes products blend multi-sensor
    imagery into dynamic biodiversity indicators.
  url: /methods/remote-sensing/

- id: genomics
  label: Genomics & eDNA
  icon: dna
  x: 54
  y: 58
  summary: >
    Water and sediment samples contain fragments of DNA shed by every organism
    that passed through. Metabarcoding and metagenomics decode this environmental
    DNA (eDNA) to produce species inventories from a single water bottle — faster
    and cheaper than traditional visual surveys for many taxa.
  url: /methods/genomics/

- id: acoustics
  label: Acoustics
  icon: wave-square
  x: 38
  y: 48
  summary: >
    Passive acoustic monitoring (PAM) listens for biological and anthropogenic
    sound to infer biodiversity and ecosystem health. Active acoustics (echosounders,
    ADCPs) enumerate fish and zooplankton biomass. Together they cover the water
    column continuously, day and night.
  url: /methods/acoustics/

- id: tracking
  label: Tracking
  icon: location-dot
  x: 62
  y: 38
  summary: >
    Electronic tags on fish, turtles, marine mammals, and seabirds record fine-scale
    movements, diving behavior, and physiology. Acoustic and satellite telemetry
    build 3-D pictures of how animals use ocean habitat — essential for understanding
    connectivity and response to climate change.
  url: /methods/tracking/

- id: indicators
  label: Indicators
  icon: chart-line
  x: 84
  y: 42
  summary: >
    Raw observations become decision-relevant information through synthesis into
    Essential Ocean Variables and Essential Biodiversity Variables. MBON's indicators
    working group designs reproducible pipelines that aggregate observations from
    multiple methods into comparable metrics for managers and policymakers.
  url: /methods/indicators/

- id: data-management
  label: Data Management
  icon: database
  x: 78
  y: 68
  summary: >
    FAIR data (Findable, Accessible, Interoperable, Reusable) is the connective
    tissue of the network. MBON's data management and community (DMAC) working
    group develops standards, pipelines, and tools so that observations from every
    node flow seamlessly into OBIS and the global biodiversity knowledge graph.
  url: /methods/data-management/

- id: traditional
  label: Traditional Surveys
  icon: ship
  x: 30
  y: 18
  summary: >
    Trawl surveys, visual transects, and ship-based acoustic surveys remain the
    calibration backbone for new methods. They are labor-intensive and expensive
    at large scale, which is exactly why MBON invests in genomic, acoustic, and
    remote-sensing approaches that can extend coverage between cruises.
  url: /methods/traditional/
```

---

## 3. Files to Create / Modify

### New partial — `layouts/partials/methods-band.html`

Dark full-width section. The illustration sits as a `position: relative` container; each method entry from `data/methods.yaml` becomes an absolutely-positioned `<button>` hotspot with:
- A pulsing ring indicator (CSS animation, `--teal-300`)
- A text label always visible below the ring
- On hover/focus: a floating card (above the ring) showing method name, summary, and "Learn more →" link

```html
{{/* Methods band. Reads data/methods.yaml for hotspot configuration. */}}
<section class="methods-band">
  <div class="methods-band__intro">
    <span class="eyebrow eyebrow--rule eyebrow--ondark">How we observe</span>
    <h2>Methods for a connected ocean record</h2>
    <p>MBON advances modern observing approaches that extend the reach of
    traditional surveys — from satellite pixels to single molecules of DNA.</p>
    <a class="btn btn--action" href="/methods/">Explore all methods →</a>
  </div>
  <div class="methods-scene" aria-label="Interactive methods diagram">
    <img class="methods-scene__img" src="/img/methods/methods-illustration.png" alt="">
    {{ range site.Data.methods }}
    <div class="method-spot" style="left:{{ .x }}%;top:{{ .y }}%;"
         data-method="{{ .id }}">
      <button class="method-spot__pin" aria-describedby="tip-{{ .id }}">
        <span class="sr-only">{{ .label }}</span>
      </button>
      <span class="method-spot__label">{{ .label }}</span>
      <div class="method-spot__tip" id="tip-{{ .id }}" role="tooltip">
        <strong>{{ .label }}</strong>
        <p>{{ .summary }}</p>
        <a href="{{ .url }}">Learn more <i class="fas fa-arrow-right"></i></a>
      </div>
    </div>
    {{ end }}
  </div>
</section>
```

### Homepage template — `layouts/index.html`

Insert `{{ partial "methods-band.html" . }}` between the hero section and the globe:

```html
{{/* ===== HERO ===== */}}   …existing…
{{/* ===== METHODS ===== */}}
{{ partial "methods-band.html" . }}
{{/* ===== NETWORK GLOBE ===== */}}
{{ partial "globe.html" … }}
```

### New CSS — append to `static/css/components.css`

```css
/* ---- Methods band ----------------------------------------------------- */
.methods-band { … dark background, layout grid … }
.methods-scene { position:relative; }
.methods-scene__img { width:100%; display:block; }
.method-spot { position:absolute; transform:translate(-50%,-50%); }
.method-spot__pin { … pulsing ring … }
.method-spot__label { … always-visible text below pin … }
.method-spot__tip { … hidden by default, shown on :focus-within / hover … }
```

### New JS — `static/js/methods.js`

Minimal: toggle `.is-active` on pin click for mobile (hover not available), close on outside click, keyboard navigation (Tab to focus pin, Enter/Space to open card, Escape to close). Load via `<script src="/js/methods.js" defer></script>` in `baseof.html`.

### Content type — `content/methods/`

```
content/methods/
  _index.md              (section index)
  genomics.md
  remote-sensing.md
  acoustics.md
  tracking.md
  indicators.md
  data-management.md
  traditional.md
```

Front matter schema mirrors `network/` pages: `title`, `summary`, `banner`, `icon`, `weight`. Body content is a detailed method write-up.

### Layouts — `layouts/methods/`

```
layouts/methods/
  list.html    — grid of method cards (similar to network/list.html)
  single.html  — full method page (similar to network/single.html)
```

---

## 4. Hotspot Interaction Design (CSS/JS pattern)

```
Default state:   pin ring visible + label text always shown
Hover/focus:     tooltip card floats above (CSS :focus-within + :hover)
Mobile:          JS toggles .is-active class on click; Escape closes
Accessibility:   role="tooltip", aria-describedby, keyboard-navigable
```

Tip card appears **above** the pin so it doesn't obscure the illustration region being pointed at. Cards flip to appear below when the hotspot is in the top 25% of the image (check via JS or static CSS class `method-spot--top`).

---

## 5. Verification

1. `hugo server` — homepage renders without errors; methods band appears between hero and globe
2. Hover each of the 7 hotspots — tooltip card appears with correct label, summary, and working link
3. Tab through all pins with keyboard — focus ring visible, Enter opens card, Escape closes
4. Mobile viewport (375 px) — tap pin opens card; tap outside closes; labels don't overflow
5. `/methods/` list page renders all 7 method cards
6. Individual method pages (e.g. `/methods/genomics/`) render with correct title and content
7. `hugo build` — no warnings about missing data or template errors
