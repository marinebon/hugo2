#!/usr/bin/env python3
"""
Import MBON publications from www_marinebon2 Hugo-Academic format
into hugo2 content/papers/*.md files with ProperCase tags + COinS-ready front matter.
Run from the hugo2 root: python3 scripts/import_papers.py
"""
import os, re, yaml
from pathlib import Path
from html.parser import HTMLParser

SRC  = Path("../www_marinebon2/content/publication")
DEST = Path("content/papers")

# ── tag auto-assignment ───────────────────────────────────────────────────────
METHOD_RULES = [
    ("method.Genomics",       r"edna|e\.dna|metabarcode|metagenom|genomic|\bDNA\b"),
    ("method.Remote-Sensing", r"remote.sens|satellite|seascape|imagery|spectral|ocean.color"),
    ("method.Acoustics",      r"acoustic|soundscape|passive.acoustic|bioacous"),
    ("method.Tracking",       r"\btrack|telemetry|\btag\b|tagging|biotrack"),
    ("method.Indicators",     r"\bindicator|\beov\b|\bebv\b|essential.ocean|essential.biodiv"),
    ("method.Traditional",    r"trawl|visual.survey|transect|traditional.survey"),
]

def auto_tags(title: str, abstract: str, year: int) -> list[str]:
    text = (title + " " + abstract).lower()
    tags = []  # content type is structural (the papers section), not a tag
    for tag, pattern in METHOD_RULES:
        if re.search(pattern, text, re.I):
            tags.append(tag)
    if year:
        tags.append(f"year.{year}")
    return tags

# ── HTML stripper ─────────────────────────────────────────────────────────────
class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, d): self.parts.append(d)

def strip_html(html: str) -> str:
    p = _Stripper(); p.feed(html); return "".join(p.parts).strip()

def first_paragraph(text: str) -> str:
    """Return first non-empty paragraph, stripped of HTML/markdown."""
    for para in re.split(r"\n{2,}", text.strip()):
        s = strip_html(para).strip()
        s = re.sub(r"[*_`#>]", "", s).strip()
        if len(s) > 40:
            return s
    return ""

# ── journal name cleanup ──────────────────────────────────────────────────────
def clean_journal(pub: str) -> str:
    if not pub:
        return ""
    return re.sub(r"[*_]", "", pub).strip()

# ── author list cleanup ───────────────────────────────────────────────────────
def clean_authors(raw: list) -> list[str]:
    out = []
    for a in (raw or []):
        a = str(a)
        # strip affiliation pipes from bib-sourced entries
        a = a.split("|")[0].strip()
        a = re.sub(r"\s+", " ", a).strip()
        if a:
            out.append(a)
    return out

# ── slug from folder name ─────────────────────────────────────────────────────
def make_slug(folder: str) -> str:
    return folder.strip("/").rstrip("/")

# ── main ──────────────────────────────────────────────────────────────────────
years_seen = set()
written = 0
skipped = 0

for pub_dir in sorted(SRC.iterdir()):
    if not pub_dir.is_dir():
        continue
    index = pub_dir / "index.md"
    if not index.exists():
        continue

    raw = index.read_text(encoding="utf-8")
    # split front matter
    parts = raw.split("---", 2)
    if len(parts) < 3:
        skipped += 1; continue
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        skipped += 1; continue
    body = parts[2] if len(parts) > 2 else ""

    title = (fm.get("title") or "").strip()
    if not title:
        skipped += 1; continue

    # date / year
    date_val = fm.get("date") or ""
    date_str = str(date_val).split("T")[0] if date_val else ""
    year = int(date_str[:4]) if date_str and date_str[:4].isdigit() else None

    authors  = clean_authors(fm.get("authors") or [])
    journal  = clean_journal(fm.get("publication") or fm.get("journal") or "")
    doi      = (fm.get("doi") or "").strip()
    url      = (fm.get("url_pdf") or fm.get("url") or "").strip()
    abstract = first_paragraph(body)

    tags = auto_tags(title, abstract, year)
    if year:
        years_seen.add(year)

    slug = make_slug(pub_dir.name)
    out_path = DEST / f"{slug}.md"

    # build front matter dict (ordered)
    out_fm: dict = {"title": title}
    if authors:
        out_fm["authors"] = authors
    if date_str:
        out_fm["date"] = date_str
    if year:
        out_fm["year"] = year
    if journal:
        out_fm["journal"] = journal
    if doi:
        out_fm["doi"] = doi
    if url:
        out_fm["paper_url"] = url
    if abstract:
        out_fm["abstract"] = abstract
    out_fm["tags"] = tags

    md = "---\n" + yaml.dump(out_fm, allow_unicode=True, default_flow_style=False, sort_keys=False) + "---\n"
    out_path.write_text(md, encoding="utf-8")
    written += 1

print(f"Written: {written}  Skipped: {skipped}")
print(f"Years: {sorted(years_seen)}")
# Note: the Papers page builds its Method/Year filter buttons from the canonical
# data/tags.yaml registry and the imported papers themselves — no filter file to write.
