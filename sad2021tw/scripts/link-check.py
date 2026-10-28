#!/usr/bin/env python3
"""
link-check.py — after a build, follow every internal link in the output and
make sure a file is actually there. Prints what's broken; never stops the build.

Why this exists: a page can look fine and still 404 once it's online. Tiddler
titles with a slash in them (F/LOS, Aesthetics/Politics) only work because the
templates encode their links twice and GitHub Pages decodes them once. If that
ever changes (new host, new template), those pages break silently. This also
catches links to tiddlers that are left out of the site (private/hide,
system tiddlers) and images that point at a file on your own computer.

It sorts what it finds into three groups:
  broken     the link looks fine on the page but goes nowhere online
  local      file:///... addresses — they only work on the machine that made them
  unwritten  links TiddlyWiki already knows are to tiddlers that don't exist
             yet (the italic "missing" links). Normal in a wiki, so these are
             only counted, unless you ask for the list.

Usage:
    python3 sad2021tw/scripts/link-check.py [output_dir] [--unwritten]

    output_dir   defaults to ../output relative to this script
    --unwritten  also list every link to a tiddler that doesn't exist yet
"""

import html
import os
import re
import sys
from collections import defaultdict
from urllib.parse import unquote, urljoin, urlsplit

# Find every opening tag, then pull the href="..." or src="..." out of it.
# A regex is rough for HTML in general, but TiddlyWiki writes its tags
# plainly, so it's good enough here and needs nothing installed. Keeping the
# whole tag lets us see its class, which is how TiddlyWiki marks a link to a
# tiddler that doesn't exist: class="tc-tiddlylink tc-tiddlylink-missing".
TAG = re.compile(r"<[a-zA-Z][^>]*>")
LINK = re.compile(r'\b(?:href|src)="([^"]*)"')

# Known broken links that are fine to leave, so they stop showing up in every
# report. Keys are the page the link is on (as the report prints it); the value
# is either a set of targets to ignore on that page, or ALL for every link on
# it. Add to this when you decide a link is OK as it is.
ALL = "all"
IGNORE = {
    # Text pasted from tiddlywiki.com: links to its own documentation pages.
    "static/TiddlyWiki.html": ALL,
    # Mike Burns's essay, copied verbatim. The haircut photo link was relative
    # on his site; it's one of his jokes, not part of the reading list.
    "static/Why so empty?.html": {"/static/mike-burns-haircut-photo-by-chessie-monks-2009.jpg"},
    # A meta note about how the wiki works; LinkExplorer itself is a
    # template (tagged hide), so it has no page of its own.
    "static/LinkExplorer Explanation.html": {"/static/LinkExplorer.html"},
}


def ignored(page, target):
    rule = IGNORE.get(page)
    return rule == ALL or (rule is not None and target in rule)


def resolve(page_url, link):
    """Turn one link into the file the server would look for, or None to skip.

    page_url is the page's own address on the site, e.g. /static/F%252FLOS.html.
    """
    link = html.unescape(link)  # &amp; in the markup means & in the address
    parts = urlsplit(link)
    if parts.scheme == "file":
        return "file"
    if parts.scheme or parts.netloc:  # http:, mailto:, data:, //cdn... — not ours
        return None
    if not parts.path:  # "#section" or "?q=..." on the same page
        return None
    # Work out the full address the browser would ask for. urljoin does what
    # a browser does: "F%252FLOS.html" on a /static/ page becomes
    # /static/F%252FLOS.html, "/favicon.svg" stays as it is, and ".." works.
    # The browser leaves the %-codes alone, so this is still encoded.
    address = urljoin(page_url, parts.path)
    # The server decodes the address once, then looks for that file on disk.
    # This one unquote() is the whole point: it turns %252F into %2F (a file
    # that exists) but %2F into / (a folder that doesn't).
    path = unquote(address)
    if path.endswith("/"):
        path += "index.html"
    return path


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    list_unwritten = "--unwritten" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    out = args[0] if args else os.path.join(here, "..", "output")
    out = os.path.abspath(out)
    if not os.path.isdir(out):
        sys.exit(f"link-check: no build at {out}")

    # Each group maps a target -> the set of pages that link to it.
    broken, local, unwritten = defaultdict(set), defaultdict(set), defaultdict(set)
    checked = skipped = 0
    for folder, _, files in os.walk(out):
        for name in files:
            if not name.endswith(".html"):
                continue
            disk = os.path.join(folder, name)
            rel = os.path.relpath(disk, out).replace(os.sep, "/")
            # Files on disk are named the way the server finds them (decoded
            # once), so the page's own address is that name, percent-encoded
            # again. "%" -> "%25" is the only change these filenames need.
            page_url = "/" + rel.replace("%", "%25")
            with open(disk, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            page = unquote(rel)  # readable name for the report
            for tag in TAG.findall(text):
                found = LINK.search(tag)
                if not found:
                    continue
                path = resolve(page_url, found.group(1))
                if path is None:
                    continue
                checked += 1
                if path == "file":
                    local[found.group(1)].add(page)
                elif not os.path.isfile(os.path.join(out, path.lstrip("/"))):
                    if ignored(page, path):
                        skipped += 1
                        continue
                    group = unwritten if "tc-tiddlylink-missing" in tag else broken
                    group[path].add(page)

    print(f"Link check: {checked} internal links — {len(broken)} broken, "
          f"{len(local)} local-only, {len(unwritten)} unwritten tiddlers linked to "
          f"({skipped} known ones ignored, see IGNORE in link-check.py).")
    report("Broken (fine on the page, 404 online):", broken)
    report("Local-only (file:/// addresses, broken for everyone else):", local)
    if list_unwritten:
        report("Unwritten (links to tiddlers that don't exist yet):", unwritten)
    elif unwritten:
        print("  (add --unwritten to list the links to tiddlers that don't exist yet)")


def report(heading, group):
    """Print one group: each target, then up to three pages that link to it."""
    if not group:
        return
    print(heading)
    for target in sorted(group):
        pages = sorted(group[target])
        shown = ", ".join(pages[:3]) + (f" (+{len(pages) - 3} more)" if len(pages) > 3 else "")
        print(f"  {target}\n      linked from: {shown}")


if __name__ == "__main__":
    main()
