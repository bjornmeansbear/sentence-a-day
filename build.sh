#!/usr/bin/env bash
# Build the public static site from sad2021tw.
#
# Tiddlers tagged [private] or [hide] are EXCLUDED from all public outputs.
# The filter [!is[system]!tag[private]!tag[hide]] uses AND logic (single run)
# so all three conditions must be satisfied — space-separated runs would be
# OR logic and would leak private content.
#
# Build targets (defined in tiddlywiki.info):
#   public  — static site safe for public deployment (runs by default below)
#   offline — full offline single-file wiki (ALL tiddlers including private)
#             DO NOT deploy the resulting index.html to the public server.

set -euo pipefail

# Public static site: static.html, alltiddlers.html, static/ tiddler pages
tiddlywiki sad2021tw --build public

# Uncomment the line below to also build the private offline single-file wiki.
# Keep index.html out of the public web root — it contains all private content.
# tiddlywiki sad2021tw --build offline
