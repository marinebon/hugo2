#!/usr/bin/env bash
# Rebuild the LOCAL search index so `hugo server` (http://localhost:1313) shows fresh
# /search/ results. Pagefind (the search index) is a build step — `hugo server` never
# rebuilds it, so /search/ otherwise serves whatever stale index sits in static/pagefind/.
#
# Run this whenever you want /search/ to reflect your latest content, then hard-reload
# the /search/ page (Pagefind also caches the index in the browser).
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf public                                      # clean — Hugo's --gc clears the cache, not stale output files
hugo --gc --minify                                 # build ./public (root-relative URLs for localhost)
npx --yes pagefind --site public                   # index it → ./public/pagefind
rm -rf static/pagefind && cp -r public/pagefind static/pagefind  # serve it from `hugo server`

echo "✓ search index refreshed → static/pagefind/  (hard-reload /search/ to pick it up)"
