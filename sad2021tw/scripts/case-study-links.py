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


def set_via_server(title, value):
    url = API + urllib.parse.quote(title, safe="")
    try:
        tid = json.load(urllib.request.urlopen(url, timeout=10))
    except Exception:
        return "missing"
    fields = tid.get("fields") or {}
    if fields.get(FIELD) == value:
        return "same"
    if not DRY:
        fields[FIELD] = value
        tid["fields"] = fields
        tid["modified"] = now()
        tid.pop("revision", None)
        tid.pop("bag", None)
        req = urllib.request.Request(
            url, data=json.dumps(tid).encode(), method="PUT",
            headers={"Content-Type": "application/json", "X-Requested-With": "TiddlyWiki"})
        urllib.request.urlopen(req, timeout=10)
    return "set"


def linked_now():
    """Titles of tiddlers that currently carry the field, to find stale ones."""
    if server_running():
        # the "skinny" list is every tiddler's fields without its text
        every = json.load(urllib.request.urlopen(API.rstrip("/") + ".json", timeout=20))
        return [t["title"] for t in every if t.get(FIELD)]
    found = []
    for name in os.listdir(TIDDLERS):
        if name.endswith(".tid"):
            head = open(os.path.join(TIDDLERS, name), encoding="utf-8", errors="replace").read().partition("\n\n")[0]
            m = re.search(r"^title: (.*)$", head, re.M)
            if m and re.search(r"^" + FIELD + r": ", head, re.M):
                found.append(m.group(1))
    return found


def clear_via_server(title):
    url = API + urllib.parse.quote(title, safe="")
    tid = json.load(urllib.request.urlopen(url, timeout=10))
    (tid.get("fields") or {}).pop(FIELD, None)
    tid["modified"] = now()
    tid.pop("revision", None)
    tid.pop("bag", None)
    req = urllib.request.Request(
        url, data=json.dumps(tid).encode(), method="PUT",
        headers={"Content-Type": "application/json", "X-Requested-With": "TiddlyWiki"})
    urllib.request.urlopen(req, timeout=10)


def clear_in_file(title):
    for name in os.listdir(TIDDLERS):
        if not name.endswith(".tid"):
            continue
        path = os.path.join(TIDDLERS, name)
        head, sep, body = open(path, encoding="utf-8", errors="replace").read().partition("\n\n")
        if re.search(r"^title: " + re.escape(title) + r"$", head, re.M):
            lines = [l for l in head.split("\n") if not l.startswith(FIELD + ": ")]
            open(path, "w", encoding="utf-8").write("\n".join(lines) + sep + body)
            return


def set_in_file(title, value):
    for name in os.listdir(TIDDLERS):
        if not name.endswith(".tid"):
            continue
        path = os.path.join(TIDDLERS, name)
        raw = open(path, encoding="utf-8", errors="replace").read()
        head, sep, body = raw.partition("\n\n")
        if not re.search(r"^title: " + re.escape(title) + r"$", head, re.M):
            continue
        lines = [l for l in head.split("\n") if not l.startswith(FIELD + ": ")]
        if len(lines) < len(head.split("\n")) and f"{FIELD}: {value}" in head.split("\n"):
            return "same"
        lines = [l for l in lines if not l.startswith("modified: ")]
        lines += [f"{FIELD}: {value}", f"modified: {now()}"]
        if not DRY:
            open(path, "w", encoding="utf-8").write("\n".join(sorted(lines)) + sep + body)
        return "set"
    return "missing"


if __name__ == "__main__":
    links = wanted_links()
    live = server_running()
    print(f"{len(links)} tiddlers named in connections.json; writing via the {'running server' if live else 'tiddler files'}"
          + (" (dry run)" if DRY else ""))
    for title, value in sorted(links.items()):
        result = set_via_server(title, value) if live else set_in_file(title, value)
        note = {"set": "linked", "same": "already linked", "missing": "NO SUCH TIDDLER - fix the title in connections.json"}[result]
        if result != "same":
            print(f"  {note:16} {title}")
    stale = [t for t in linked_now() if t not in links]
    for title in stale:
        if not DRY:
            clear_via_server(title) if live else clear_in_file(title)
        print(f"  {'unlinked':16} {title}  (no longer in connections.json)")
    print(f"done: {len(links)} linked, {len(stale)} unlinked")
