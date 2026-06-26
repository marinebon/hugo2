#!/usr/bin/env python3
"""check internal links in the built Hugo site (default: ./public).

walks every .html file under the site root, extracts href / src / srcset
targets, and verifies that each internal link both:

  1. carries the site's base-path prefix (e.g. /hugo2), so it won't 404 when
     the site is served under a subpath, and
  2. resolves to a file that actually exists in the build.

check (1) is what catches the classic `relURL "/methods/x/"` bug: a leading
slash makes Hugo drop the base path, producing /methods/x/ instead of
/hugo2/methods/x/ — which 404s in production but "works" in a root-served
preview. when the site later moves to the domain root the base path becomes
empty and check (1) is simply a no-op, so this stays correct across that move.

external links (http, https, //, mailto, tel, data, javascript, blob) and
in-page anchors (#...) are skipped. broken links matched by a pattern in the
allow-file are reported as warnings instead of failing the build.

usage:
  python3 scripts/check_links.py [public_dir]
                                 [--allow scripts/linkcheck_allow.txt]
                                 [--base-path /hugo2]

base path is auto-detected from public_dir/sitemap.xml (falling back to
index.xml) unless --base-path is given. exit status is non-zero if any
non-allowed broken link is found.
"""

import argparse
import fnmatch
import os
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

# attributes that hold a URL, per element. (tag, attr) pairs we inspect.
URL_ATTRS = {
    "a": ("href",),
    "area": ("href",),
    "link": ("href",),
    "img": ("src", "srcset"),
    "script": ("src",),
    "source": ("src", "srcset"),
    "iframe": ("src",),
    "audio": ("src",),
    "video": ("src", "poster"),
    "embed": ("src",),
    "object": ("data",),
}

# schemes / prefixes we never check (external or non-navigational).
SKIP_PREFIXES = (
    "http://", "https://", "//", "mailto:", "tel:", "data:",
    "javascript:", "blob:", "#", " tel:",
)

# file extensions that mean "this is the file itself", not a pretty-URL dir.
FILE_EXTS = {
    ".html", ".htm", ".css", ".js", ".mjs", ".json", ".xml", ".txt", ".pdf",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".ico",
    ".webmanifest", ".zip", ".csv", ".woff", ".woff2", ".ttf", ".eot",
    ".mp4", ".webm", ".mp3", ".wav",
}


class LinkExtractor(HTMLParser):
    """collect (attr_value) URL strings from a single HTML document."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        wanted = URL_ATTRS.get(tag)
        if not wanted:
            return
        amap = dict(attrs)
        for attr in wanted:
            val = amap.get(attr)
            if not val:
                continue
            if attr == "srcset":
                # "url1 1x, url2 2x" -> first token of each comma-part
                for part in val.split(","):
                    token = part.strip().split()
                    if token:
                        self.links.append(token[0])
            else:
                self.links.append(val.strip())


def detect_base_path(public_dir):
    """derive the URL base path (e.g. '/hugo2', or '' at the root) from the
    built site's sitemap.xml home <loc>, falling back to index.xml."""
    sitemap = os.path.join(public_dir, "sitemap.xml")
    if os.path.isfile(sitemap):
        try:
            root = ET.parse(sitemap).getroot()
            paths = []
            for loc in root.iter():
                if loc.tag.endswith("loc") and loc.text:
                    paths.append(urlsplit(loc.text.strip()).path)
            if paths:
                # the home page has the shortest path; it IS base_path + "/"
                home = min(paths, key=len)
                if all(p.startswith(home) for p in paths):
                    return home.rstrip("/")
        except ET.ParseError:
            pass
    index_xml = os.path.join(public_dir, "index.xml")
    if os.path.isfile(index_xml):
        try:
            root = ET.parse(index_xml).getroot()
            link = root.find("./channel/link")
            if link is not None and link.text:
                return urlsplit(link.text.strip()).path.rstrip("/")
        except ET.ParseError:
            pass
    return ""


def load_allow(path):
    """read glob patterns (one per line; # comments) of links we tolerate."""
    patterns = []
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns


def html_files(public_dir):
    for dirpath, _dirs, files in os.walk(public_dir):
        for name in files:
            if name.endswith((".html", ".htm")):
                yield os.path.join(dirpath, name)


def target_exists(public_dir, url_path):
    """does an absolute, base-stripped url_path map to a file in the build?
    handles pretty URLs (/x/ -> x/index.html) and extension-less links."""
    rel = unquote(url_path).lstrip("/")
    base = os.path.normpath(os.path.join(public_dir, rel)) if rel else public_dir
    # guard against paths escaping the build dir via ../
    if os.path.relpath(base, public_dir).startswith(".."):
        return False
    _, ext = os.path.splitext(os.path.basename(rel))
    candidates = []
    if url_path.endswith("/") or not rel:
        candidates.append(os.path.join(base, "index.html"))
    elif ext.lower() in FILE_EXTS:
        candidates.append(base)
    else:
        # extension-less, no trailing slash: try file, pretty dir, .html
        candidates += [base, os.path.join(base, "index.html"), base + ".html"]
    return any(os.path.isfile(c) for c in candidates)


def check(public_dir, base_path, allow_patterns):
    """return (broken, allowed, n_files, n_links).
    broken / allowed are dicts: link -> sorted list of source pages."""
    broken, allowed = {}, {}
    n_files = n_links = 0

    for path in html_files(public_dir):
        n_files += 1
        with open(path, encoding="utf-8", errors="replace") as f:
            parser = LinkExtractor()
            parser.feed(f.read())
        src_page = "/" + os.path.relpath(path, public_dir).replace(os.sep, "/")

        for raw in parser.links:
            low = raw.lower()
            if not raw or any(low.startswith(p.strip()) for p in SKIP_PREFIXES):
                continue
            n_links += 1
            split = urlsplit(raw)
            if split.scheme or split.netloc:
                continue  # belt-and-suspenders for any non-skipped scheme
            link_path = split.path
            if not link_path:
                continue  # pure ?query or #frag on the same page

            reason = None
            if link_path.startswith("/"):
                if base_path and not (
                    link_path == base_path or link_path.startswith(base_path + "/")
                ):
                    reason = "missing base prefix '%s/'" % base_path
                else:
                    stripped = link_path[len(base_path):] if base_path else link_path
                    if not target_exists(public_dir, stripped):
                        reason = "target not found in build"
            else:
                # relative link: resolve against this page's directory.
                # src_page is relative to the build root (files aren't nested
                # under the base path on disk), so the result is too.
                page_dir = os.path.dirname(src_page)
                resolved = os.path.normpath(os.path.join(page_dir, link_path))
                resolved = "/" + resolved.lstrip("/")
                if not target_exists(public_dir, resolved):
                    reason = "target not found in build (relative)"

            if reason is None:
                continue
            bucket = allowed if matches_allow(raw, allow_patterns) else broken
            bucket.setdefault((raw, reason), set()).add(src_page)

    return broken, allowed, n_files, n_links


def matches_allow(link, patterns):
    return any(fnmatch.fnmatch(link, pat) for pat in patterns)


def fmt(bucket):
    lines = []
    for (link, reason), pages in sorted(bucket.items()):
        sample = sorted(pages)
        shown = ", ".join(sample[:3])
        more = "" if len(sample) <= 3 else " (+%d more)" % (len(sample) - 3)
        lines.append("  %s  [%s]\n      on: %s%s" % (link, reason, shown, more))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="check internal links in a built Hugo site")
    ap.add_argument("public_dir", nargs="?", default="public",
                    help="path to the built site (default: public)")
    ap.add_argument("--allow", default="scripts/linkcheck_allow.txt",
                    help="file of glob patterns for tolerated broken links")
    ap.add_argument("--base-path", default=None,
                    help="URL base path (e.g. /hugo2); auto-detected if omitted")
    args = ap.parse_args()

    if not os.path.isdir(args.public_dir):
        print("error: '%s' is not a directory — build the site first "
              "(hugo --gc --minify)" % args.public_dir, file=sys.stderr)
        return 2

    base_path = args.base_path if args.base_path is not None else detect_base_path(args.public_dir)
    base_path = base_path.rstrip("/")
    allow_patterns = load_allow(args.allow)

    broken, allowed, n_files, n_links = check(args.public_dir, base_path, allow_patterns)

    print("link check: %d html files, %d internal links, base path '%s'"
          % (n_files, n_links, base_path or "(root)"))
    if allow_patterns:
        print("            %d allow-pattern(s) from %s" % (len(allow_patterns), args.allow))

    if allowed:
        print("\n%d allowed (broken but in allow-file):" % len(allowed))
        print(fmt(allowed))

    if broken:
        print("\n%d BROKEN internal link(s):" % len(broken), file=sys.stderr)
        print(fmt(broken), file=sys.stderr)
        print("\nfix the link, or add a glob pattern to %s to allow it."
              % args.allow, file=sys.stderr)
        return 1

    print("\nno broken internal links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
