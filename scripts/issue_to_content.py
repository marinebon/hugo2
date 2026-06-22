#!/usr/bin/env python3
"""
Turn a parsed GitHub Issue Form into a Hugo content file (+ imported images),
and emit outputs for the calling workflow.

Reads (env):
  ISSUE_JSON    JSON string of issue-form fields keyed by field id
                (from stefanbuck/github-issue-parser, with template-path set)
  CONTENT_TYPE  one of: news | event | paper | tool | edit
  ISSUE_NUMBER  the originating issue number
  GITHUB_OUTPUT (optional) path to append key=value workflow outputs

Writes the content file under content/<section>/ and any dragged-in images
under static/img/<section>/, then prints/emits: made_change, file, branch,
pr_title, section, slug, content_path.

Run locally for a dry test:
  ISSUE_JSON='{"title":"Test","summary":"x","body":"hi","tags_topic":"Research"}' \
  CONTENT_TYPE=news ISSUE_NUMBER=0 python3 scripts/issue_to_content.py

Shares the ProperCase tag + METHOD_RULES conventions with import_papers.py.
"""
import os, re, sys, json, datetime
import urllib.request, urllib.parse
import yaml

NO_RESPONSE = "_No response_"

# ── field helpers ─────────────────────────────────────────────────────────────
def clean(v) -> str:
    if v is None:
        return ""
    v = str(v).strip()
    return "" if v == NO_RESPONSE else v

def multi(v) -> list:
    """A multi-select dropdown value -> list of selected labels."""
    v = clean(v)
    return [x.strip() for x in v.split(",") if x.strip()] if v else []

# ── tag mapping (friendly label -> facet.Value, ProperCase) ───────────────────
# Aliases for labels that don't kebab-case trivially to their canonical value.
TAG_ALIASES = {
    "United States": "US",
    "GEO BON": "GEOBON",
    "National Marine Sanctuaries": "NationalMarineSanctuaries",
    "NOAA IEA": "NOAA-IEA",
    "AIR Centre": "AIR-Centre",
}

def to_value(label: str) -> str:
    label = label.strip()
    if label in TAG_ALIASES:
        return TAG_ALIASES[label]
    v = label.replace(" ", "-")
    v = re.sub(r"[.'’]", "", v)   # drop periods and apostrophes
    return v

def tag(facet: str, label: str) -> str:
    return f"{facet}.{to_value(label)}"

def collect_tags(data: dict, facets: list) -> list:
    """facets: [(field_id, facet_name), ...]; also folds in free-text tags_other."""
    tags = []
    for fid, facet in facets:
        for label in multi(data.get(fid)):
            tags.append(tag(facet, label))
    other = clean(data.get("tags_other"))
    if other:
        for t in re.split(r"[,\n]", other):
            t = t.strip()
            if t and "." in t:
                tags.append(t)
    seen, out = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t); out.append(t)
    return out

# ── method auto-tagging (mirrors scripts/import_papers.py) ─────────────────────
METHOD_RULES = [
    ("method.Genomics",       r"edna|e\.dna|metabarcode|metagenom|genomic|\bDNA\b"),
    ("method.Remote-Sensing", r"remote.sens|satellite|seascape|imagery|spectral|ocean.color"),
    ("method.Acoustics",      r"acoustic|soundscape|passive.acoustic|bioacous"),
    ("method.Tracking",       r"\btrack|telemetry|\btag\b|tagging|biotrack"),
    ("method.Indicators",     r"\bindicator|\beov\b|\bebv\b|essential.ocean|essential.biodiv"),
    ("method.Benthic",        r"benthic|intertidal|rocky.shore|sandy.beach|photo.?quadrat|quadrat"),
    ("method.Traditional",    r"trawl|visual.survey|transect|traditional.survey"),
]

def auto_method_tags(text: str) -> list:
    out = []
    for tagname, pat in METHOD_RULES:
        if re.search(pat, text, re.I):
            out.append(tagname)
    return out

# ── slug + serialization ──────────────────────────────────────────────────────
def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:80] or "untitled"

def dedup(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x); out.append(x)
    return out

def dump_md(fm: dict, body: str) -> str:
    front = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    body = (body or "").strip()
    return "---\n" + front + "---\n" + (f"\n{body}\n" if body else "")

# ── image import ──────────────────────────────────────────────────────────────
def download_images(field: str, dest_dir: str, slug: str) -> list:
    """Extract GitHub attachment URLs from a textarea value, download them,
       return the saved filenames (first = primary)."""
    field = field or ""
    urls = re.findall(r"!\[[^\]]*\]\((https?://[^)\s]+)\)", field)
    urls += re.findall(
        r"(?<!\()\bhttps?://(?:user-images\.githubusercontent\.com|github\.com/user-attachments)/[^\s)]+",
        field,
    )
    urls = dedup(urls)
    saved = []
    if not urls:
        return saved
    os.makedirs(dest_dir, exist_ok=True)
    for i, url in enumerate(urls):
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or ".png"
        if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
            ext = ".png"
        name = f"{slug}{ext}" if i == 0 else f"{slug}-{i+1}{ext}"
        path = os.path.join(dest_dir, name)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mbon-content-bot"})
            with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
                f.write(r.read())
            saved.append(name)
        except Exception as e:  # noqa: BLE001 — best-effort; missing image isn't fatal
            print(f"warn: image download failed for {url}: {e}", file=sys.stderr)
    return saved

# ── Crossref (DOI auto-fill for papers) ───────────────────────────────────────
def crossref(doi: str) -> dict:
    doi = doi.strip().removeprefix("https://doi.org/").removeprefix("doi:").strip()
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(
        url, headers={"User-Agent": "mbon-content-bot (mailto:info@marinebon.org)"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["message"]

# ── builders (return: section, slug, front-matter dict, body) ─────────────────
def build_news(d):
    title = clean(d.get("title"))
    date = clean(d.get("date")) or datetime.date.today().isoformat()
    slug = slugify(title)
    fm = {"title": title, "date": date}
    imgs = download_images(d.get("image"), "static/img/news", slug)
    if imgs:
        fm["banner"] = f"img/news/{imgs[0]}"
    fm["summary"] = clean(d.get("summary"))
    fm["tags"] = collect_tags(d, [
        ("tags_topic", "topic"), ("tags_method", "method"),
        ("tags_place", "place"), ("tags_org", "org"),
    ])
    return "news", slug, fm, clean(d.get("body"))

def build_event(d):
    title = clean(d.get("title"))
    date = clean(d.get("date")) or datetime.date.today().isoformat()
    slug = slugify(f"{title}-{date[:4]}")
    fm = {"title": title, "date": date}
    for key in ("end_date", "location", "event_url"):
        if clean(d.get(key)):
            fm[key] = clean(d.get(key))
    fm["summary"] = clean(d.get("summary"))
    fm["tags"] = collect_tags(d, [("tags_topic", "topic"), ("tags_method", "method")])
    return "events", slug, fm, clean(d.get("body"))

def build_paper(d):
    doi = clean(d.get("doi"))
    title = clean(d.get("title"))
    authors = [a.strip() for a in clean(d.get("authors")).split(",") if a.strip()]
    year = clean(d.get("year"))
    journal = clean(d.get("journal"))
    abstract = clean(d.get("abstract"))
    paper_url = clean(d.get("paper_url"))
    if doi:
        try:
            m = crossref(doi)
            if not title:
                title = " ".join(m.get("title", []) or []).strip()
            if not authors:
                authors = [
                    " ".join(p for p in [a.get("family", ""), a.get("given", "")] if p).strip()
                    for a in m.get("author", [])
                ]
                authors = [a for a in authors if a]
            if not year:
                parts = (m.get("issued", {}) or {}).get("date-parts", [[None]])
                if parts and parts[0] and parts[0][0]:
                    year = str(parts[0][0])
            if not journal:
                ct = m.get("container-title", []) or []
                journal = ct[0] if ct else ""
            if not abstract and m.get("abstract"):
                abstract = re.sub(r"<[^>]+>", "", m["abstract"]).strip()
            if not paper_url:
                paper_url = f"https://doi.org/{doi}"
        except Exception as e:  # noqa: BLE001
            print(f"warn: Crossref lookup failed for {doi}: {e}", file=sys.stderr)

    fm = {"title": title}
    if authors:
        fm["authors"] = authors
    if year:
        fm["date"] = f"{year}-01-01"
        fm["year"] = int(year) if year.isdigit() else year
    if journal:
        fm["journal"] = journal
    if doi:
        fm["doi"] = doi.removeprefix("https://doi.org/").removeprefix("doi:").strip()
    if paper_url:
        fm["paper_url"] = paper_url
    if abstract:
        fm["abstract"] = abstract
    tags = ["type.Paper"]
    tags += [tag("method", l) for l in multi(d.get("tags_method"))]
    tags += auto_method_tags(f"{title} {abstract}")
    if year:
        tags.append(f"year.{year}")
    fm["tags"] = dedup(tags)

    base = ""
    if authors:
        base = authors[0].split()[0] if authors[0] else ""
    slug = slugify(f"{base}-{year}" if base and year else title)
    return "papers", slug, fm, ""

def build_tool(d):
    title = clean(d.get("title"))
    slug = slugify(title)
    fm = {"title": title}
    imgs = download_images(d.get("image"), "static/img/products", slug)
    if imgs:
        fm["image"] = f"img/products/{imgs[0]}"
    fm["summary"] = clean(d.get("summary"))
    links = []
    for i, line in enumerate(clean(d.get("links")).splitlines()):
        line = line.strip()
        if "|" in line:
            label, url = line.split("|", 1)
            link = {"label": label.strip(), "url": url.strip()}
            if not links:
                link["primary"] = True
            links.append(link)
    if links:
        fm["links"] = links
    fm["tags"] = collect_tags(d, [
        ("tags_tool", "tool"), ("tags_place", "place"),
        ("tags_org", "org"), ("tags_method", "method"),
    ])
    fm["weight"] = 99  # new tools sort last until a maintainer assigns a weight
    return "tools", slug, fm, clean(d.get("body"))

# ── edit path ─────────────────────────────────────────────────────────────────
def apply_edit(d):
    """Apply a full-content replacement when the contributor pasted a fenced
       ```markdown block```. Returns (made_change, content_path)."""
    content_path = clean(d.get("content_path"))
    changes = clean(d.get("changes"))
    blocks = re.findall(r"```(?:markdown|md)?\s*\n(.*?)```", changes, re.S)
    if content_path and blocks:
        target = os.path.join("content", content_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(blocks[-1].strip() + "\n")
        return True, content_path
    return False, content_path

# ── main ──────────────────────────────────────────────────────────────────────
def emit(out: dict):
    for k, v in out.items():
        print(f"{k}={v}")
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a", encoding="utf-8") as f:
            for k, v in out.items():
                f.write(f"{k}={v}\n")

def main():
    data = json.loads(os.environ.get("ISSUE_JSON") or "{}")
    ctype = os.environ.get("CONTENT_TYPE", "").strip()
    issue = os.environ.get("ISSUE_NUMBER", "0").strip()
    out = {}

    if ctype == "edit":
        made, path = apply_edit(data)
        out["made_change"] = "true" if made else "false"
        out["content_path"] = path
        out["file"] = os.path.join("content", path) if (made and path) else ""
        out["branch"] = f"content/edit-issue-{issue}"
        out["pr_title"] = f"Edit: {path or 'content'} (#{issue})"
        emit(out)
        return

    builders = {"news": build_news, "event": build_event,
                "paper": build_paper, "tool": build_tool}
    if ctype not in builders:
        out["made_change"] = "false"
        emit(out)
        print(f"error: unknown CONTENT_TYPE {ctype!r}", file=sys.stderr)
        sys.exit(1)

    section, slug, fm, body = builders[ctype](data)
    if not fm.get("title"):
        out["made_change"] = "false"
        emit(out)
        print("error: missing title", file=sys.stderr)
        sys.exit(1)

    path = f"content/{section}/{slug}.md"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(dump_md(fm, body))

    out["made_change"] = "true"
    out["section"] = section
    out["slug"] = slug
    out["file"] = path
    out["branch"] = f"content/{ctype}-issue-{issue}"
    out["pr_title"] = f"Add {ctype}: {fm['title']} (#{issue})"
    emit(out)

if __name__ == "__main__":
    main()
