#!/usr/bin/env python3
"""Give each wiki tiddler a link to its Wjerk case study.

The pairing of case study and wiki page is written down in ONE place:
~/Code/a.wjerk.shop/connections.json. Each case study there can list tiddlers
under two keys:

  "tiddler"  the write-ups. Linked BOTH ways: the a.wjerk.shop build prints
             "Essay: ..." on the case study page, and this script links the
             tiddler back to the case study.
  "related"  pages that touch on the project. Linked ONE way: the tiddler
             points to the case study, and the case study page is unchanged.

This script reads that file and sets a `casestudy` field on each named
tiddler. A tiddler named under several case studies gets all of them:

    casestudy: [[Chair-ness at a.wjerk.shop|https://a.wjerk.shop/case-study-chairness]]

A tiddler that is no longer named anywhere in the file has its field removed,
so the file stays the single record of what is connected.

MetaInfoFields lists `casestudy`, so the field prints as a "Case study" row in
the top matter of the tiddler, in the wiki and on the published site.

So to connect a new pair: add the tiddler's title to connections.json, then
run this. Never type the field by hand; this script would overwrite it.
To disconnect one: take its title out of the file and run this again.

Run from the repo root:

    python3 sad2021tw/scripts/case-study-links.py            # make the changes
    python3 sad2021tw/scripts/case-study-links.py --dry-run  # only report

How it writes depends on whether the dev server is running, because the
server does not notice files changed underneath it (see
TIDDLYWIKI_CUSTOMIZATIONS.md):
  - server running -> ask the server to save the tiddler (its HTTP API)
  - server stopped -> edit the .tid file's header directly
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

WJERK = os.path.expanduser("~/Code/a.wjerk.shop")
TIDDLERS = os.path.join(os.path.dirname(__file__), "..", "tiddlers")
SITE = "https://a.wjerk.shop"
API = "http://127.0.0.1:8080/recipes/default/tiddlers/"
FIELD = "casestudy"
DRY = "--dry-run" in sys.argv


def case_study_title(slug):
    """The case study's own name, read from the <h1> of its page."""
    path = os.path.join(WJERK, f"case-study-{slug}.html")
    if not os.path.exists(path):
        return None
    m = re.search(r"<h1>(.*?)</h1>", open(path, encoding="utf-8").read(), re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else slug


def wanted_links():
    """{tiddler title: field value} for every pairing in connections.json."""
    connections = json.load(open(os.path.join(WJERK, "connections.json"), encoding="utf-8"))
    out = {}
    for slug, entry in connections.items():
        if not isinstance(entry, dict):
            continue  # the _comment line
        titles = []
        for key in ("tiddler", "related"):
            value = entry.get(key, [])
            titles += value if isinstance(value, list) else [value]
        if not titles:
            continue  # a case study with no wiki pages yet
        name = case_study_title(slug)
        if name is None:
            print(f"  ! connections.json has '{slug}' but there is no case-study-{slug}.html")
            continue
        # Cloudflare serves the page without ".html" (the .html address redirects).
        link = f"[[{name} at a.wjerk.shop|{SITE}/case-study-{slug}]]"
        for title in titles:
            links = out.setdefault(title, [])
            if link not in links:
                links.append(link)
    # one field value per tiddler; several case studies are separated by commas
    return {title: ", ".join(links) for title, links in out.items()}


def server_running():
    return subprocess.run(["pgrep", "-f", "tiddlywiki sad2021tw"], capture_output=True).returncode == 0


def now():
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "000"


# --- writing through the running server ------------------------------------

def server_request(title, tiddler=None):
    """GET a tiddler from the server, or PUT one back when `tiddler` is given."""
    req = urllib.request.Request(
        API + urllib.parse.quote(title, safe=""),
        data=json.dumps(tiddler).encode() if tiddler else None,
        method="PUT" if tiddler else "GET",
        headers={"Content-Type": "application/json", "X-Requested-With": "TiddlyWiki"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp) if not tiddler else None


def server_titles_with_field():
    # the "skinny" list is every tiddler's fields without its text
    every = json.load(urllib.request.urlopen(API.rstrip("/") + ".json", timeout=20))
    return [t["title"] for t in every if t.get(FIELD)]


def set_via_server(title, value):
    """Set the field to `value`, or remove it when `value` is None."""
    try:
        tid = server_request(title)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return "missing"
        raise  # anything else is a real problem, not a wrong title
    fields = tid.setdefault("fields", {})
    if fields.get(FIELD) == value:
        return "same"
    if not DRY:
        if value is None:
            del fields[FIELD]
        else:
            fields[FIELD] = value
        tid["modified"] = now()
        tid.pop("revision", None)
        tid.pop("bag", None)
        server_request(title, tid)
    return "set"


# --- writing the .tid files directly ---------------------------------------

def read_tid(path):
    """A .tid file as (header lines, everything after them, its line ending).

    newline="" stops Python translating line endings, and surrogateescape
    carries any odd bytes through untouched, so writing the file back changes
    only the header lines we meant to change. (Many of the imported tiddlers
    have Windows line endings; see TIDDLYWIKI_CUSTOMIZATIONS.md.)
    """
    raw = open(path, encoding="utf-8", errors="surrogateescape", newline="").read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    head, sep, body = raw.partition(eol + eol)
    return head.split(eol), sep + body, eol


def tiddler_files():
    """{title: path} for every .tid file, read once."""
    found = {}
    for name in os.listdir(TIDDLERS):
        if name.endswith(".tid"):
            path = os.path.join(TIDDLERS, name)
            for line in read_tid(path)[0]:
                if line.startswith("title: "):
                    found[line[len("title: "):]] = path
    return found


def set_in_file(path, value):
    """Set the field to `value`, or remove it when `value` is None."""
    if path is None:
        return "missing"
    lines, rest, eol = read_tid(path)
    wanted = None if value is None else f"{FIELD}: {value}"
    current = next((l for l in lines if l.startswith(FIELD + ": ")), None)
    if current == wanted:
        return "same"
    lines = [l for l in lines if not l.startswith((FIELD + ": ", "modified: "))]
    lines += [f"modified: {now()}"] + ([wanted] if wanted else [])
    if not DRY:
        # TiddlyWiki writes header fields in alphabetical order; keep to that
        # so its next save of this tiddler does not reshuffle the file.
        with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            fh.write(eol.join(sorted(lines)) + rest)
    return "set"


if __name__ == "__main__":
    links = wanted_links()
    live = server_running()
    print(f"{len(links)} tiddlers named in connections.json; writing via the {'running server' if live else 'tiddler files'}"
          + (" (dry run)" if DRY else ""))
    if live:
        write = set_via_server
        linked_now = server_titles_with_field()
    else:
        files = tiddler_files()
        write = lambda title, value: set_in_file(files.get(title), value)
        linked_now = [t for t, path in files.items() if any(l.startswith(FIELD + ": ") for l in read_tid(path)[0])]
    notes = {"set": "linked", "missing": "NO SUCH TIDDLER - fix the title in connections.json"}
    for title, value in sorted(links.items()):
        result = write(title, value)
        if result != "same":
            print(f"  {notes[result]:16} {title}")
    stale = [t for t in linked_now if t not in links]
    for title in stale:
        write(title, None)
        print(f"  {'unlinked':16} {title}  (no longer in connections.json)")
    print(f"done: {len(links)} linked, {len(stale)} unlinked")
