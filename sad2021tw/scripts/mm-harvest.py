#!/usr/bin/env python3
"""Build a Miscellaneous Materials (MM) issue draft from one month of Are.na.

It does three things:

  1. Asks Are.na for every block you added in the month.
  2. Sorts them into themes, using the channels you filed each block in
     (the THEMES table below), and writes one tiddler:
         MM: MM051 (020260900)
     with a "New in Bjørnpaedia" section listing the wiki pages created
     that month.
  3. Only with --channel: makes an Are.na channel of the same name and
     connects every listed block to it.

Run from the repo root:

    python3 sad2021tw/scripts/mm-harvest.py 2026-09 051             # tiddler only
    python3 sad2021tw/scripts/mm-harvest.py 2026-09 051 --dry-run   # only report
    python3 sad2021tw/scripts/mm-harvest.py 2026-09 051 --channel   # tiddler + Are.na channel

What is left out: private blocks, and blocks that sit only in private
channels. The tiddler is published on the site and the MM channel is public,
so neither should show what you filed privately.

The Are.na token is read from .env at the repo root (ARENA_ACCESS_TOKEN).
Writing the tiddler needs the dev server to be stopped, because the server
does not notice files changed underneath it (see TIDDLYWIKI_CUSTOMIZATIONS.md).
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TIDDLERS = os.path.join(ROOT, "sad2021tw", "tiddlers")
API = "https://api.are.na"
USER = "kristian-bjornard"

# Which channels belong together. Each theme is a heading in the tiddler; the
# channels under it are sub-headings, in this order. A channel that is not
# listed here lands under "Everything else", so a new channel never drops
# blocks: it only needs adding here to be filed properly next time.
THEMES = [
    ("Teaching: Structured Creativity (DI200)", ["di200-structured-creativity"]),
    ("Teaching: lectures and exhibiting", [
        "exhibiting-qnc3nvfpw98", "lecture-some-semiotics",
        "lecture-design-for-the-future-today",
        "mica-professional-practice-and-portfolio-flexible-design-studio"]),
    ("Wjerk: Union Watershed", ["wjerk-union-watershed"]),
    ("Chairs and wonderful objects", [
        "chair-ness", "wonderful-design-objet",
        "fuck-graphic-design-become-a-wood-worker", "wjerk-use-this-for-something",
        "wjerk-shop"]),
    ("A design philosophy", [
        "designarchy", "the-bits-that-make-up-a-design-philosophy",
        "the-sustainabilitist", "sustainable-aesthetics", "form-content-context",
        "what-is-art-anyway", "design-is-ideological",
        "flosd-free-libre-open-design", "to-read-pjd2xzxnaoa", "bjornpaedia"]),
    ("Carbon, circularity, land", [
        "carbon-sequestering-book",
        "carbon-capture-sequester-whatever-reduce-carbon",
        "circular-economy-uq6c2kdhqg4", "for-the-farm-commune",
        "permaculture-orchard"]),
    ("People doing people things", ["people-doing-people-things"]),
    ("The web, interfaces, type and tools", [
        "websites-used-to-be-interesting", "useful-simple-tools",
        "for-my-layout-robot", "what-is-an-interface-rzshps-oytc",
        "cape-pure-content", "type-lettering"]),
    ("Trying to understand AI", [
        "trying-to-understand-machine-learning-llm-ai-gan-diffusion"]),
    ("Bikes, clothes, food, gifts", [
        "cargo-bike-and-other-bike-parts", "dapper-gentleperson",
        "gift-guide-toppapqsrcq", "recipes-1531444041"]),
]
OTHER = "Everything else"


def token():
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip()
        if line.startswith("ARENA_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("No ARENA_ACCESS_TOKEN in .env")


def api(path, method="GET", data=None, **params):
    """One Are.na request. Waits and retries when Are.na says "slow down"."""
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    for attempt in range(8):
        req = urllib.request.Request(
            url, method=method,
            data=json.dumps(data).encode() if data is not None else None,
            headers={"Authorization": "Bearer " + TOKEN,
                     "Accept": "application/json",
                     "Content-Type": "application/json",
                     # Are.na's Cloudflare rejects Python's default User-Agent
                     "User-Agent": "sentence-a-day-mm-harvest/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as err:
            if err.code not in (429, 500, 502, 503) or attempt == 7:
                raise
            # 429 means "too many requests"; Are.na says how long to wait in
            # the Retry-After header. Without one, wait longer each try.
            time.sleep(int(err.headers.get("Retry-After") or 0) or 15 * (attempt + 1))


def month_blocks(month):
    """Every block added in `month` ("2026-09"), newest first."""
    found, page = [], 1
    while True:
        data = api(f"/v3/users/{USER}/contents", sort="created_at_desc", per=100, page=page).get("data", [])
        if not data:
            break
        found += [x for x in data if x.get("base_type") == "Block" and x["created_at"].startswith(month)]
        if min(x["created_at"] for x in data)[:7] < month:
            break  # this page already reaches back past the month
        page += 1
    return found


def channels_of(block):
    """The channels a block is filed in, leaving out private ones and MM issues."""
    data = api(f"/v3/blocks/{block['id']}/connections", per=50).get("data", [])
    return [c for c in data if c.get("visibility") != "private" and not c["slug"].startswith("mm-mm")]


def safe(text, limit):
    """Plain text that cannot be read as wikitext markup, cut to `limit`."""
    text = re.sub(r"\s+", " ", text or "").strip()
    for bad, good in (("[", "("), ("]", ")"), ("|", "/"), ("{", "("), ("}", ")"), ("<", "‹"), (">", "›")):
        text = text.replace(bad, good)
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def plain(field):
    """Are.na gives descriptions and text as {markdown, html, plain}."""
    return (field or {}).get("plain") or (field or {}).get("markdown") or ""


def item(block):
    """One bullet, in the same shape as MM050's."""
    arena = f"https://www.are.na/block/{block['id']}"
    day = datetime.strptime(block["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %-d")
    note = plain(block.get("description")) or plain(block.get("content"))
    title = safe(block.get("title") or note or block["type"], 125)
    source = (block.get("source") or {}).get("url")
    for bad in "[]|":  # these would end the [[title|address]] link early
        source = source and source.replace(bad, urllib.parse.quote(bad))
    if source:
        line = f"* //{day}// [[{title}|{source}]] ([[are.na|{arena}]]) ''({block['type']})''"
    else:
        line = f"* //{day}// [[{title}|{arena}]] ''({block['type']})''"
    lines = [line]
    thumb = ((block.get("image") or {}).get("small") or {}).get("src")
    if thumb:
        lines.append(f'<$image source="{thumb}" width="100" loading="lazy"/>')
    if note and safe(note, 125) != title:
        # <$text> prints the note as plain text. Wrapping it in //italics//
        # instead would let a "//" inside the note (any web address) close the
        # italics early and swallow the headings further down the page.
        quoted = safe(note, 220).replace('"', "”")
        lines.append(f': <em><$text text="{quoted}"/></em>')
    return "\n".join(lines)


def wiki_additions(month):
    """Wiki pages created in the month, grouped by their first tag."""
    stamp = month.replace("-", "")
    groups, stubs = defaultdict(list), 0
    for name in sorted(os.listdir(TIDDLERS)):
        if not name.endswith(".tid") or name.startswith("$__"):
            continue
        head, _, body = open(os.path.join(TIDDLERS, name), encoding="utf-8", errors="replace").read().partition("\n\n")
        fields = dict(l.split(": ", 1) for l in head.splitlines() if ": " in l)
        tags = [a or b for a, b in re.findall(r"\[\[(.*?)\]\]|(\S+)", fields.get("tags", ""))]
        if not fields.get("created", "").startswith(stamp) or {"hide", "private"} & set(tags):
            continue
        if not body.strip():
            stubs += 1  # a page that only exists to be linked to
            continue
        groups[tags[0] if tags else "Untagged"].append(fields.get("title", name[:-4]))
    lines = []
    for tag, titles in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        shown = ", ".join(f"[[{t}]]" for t in titles[:12])
        more = f", and {len(titles) - 12} more" if len(titles) > 12 else ""
        label = tag if tag == "Untagged" else f"[[{tag}]]"
        lines.append(f"* ''{label}'' ({len(titles)}): {shown}{more}")
    if stubs:
        lines.append(f"* plus {stubs} stub pages (people, albums and the like) made so those pages have something to link to")
    return lines


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2 or not re.fullmatch(r"\d{4}-\d{2}", args[0]):
        sys.exit(__doc__)
    month, issue = args
    dry, make_channel = "--dry-run" in sys.argv, "--channel" in sys.argv
    year, mm = month.split("-")
    title = f"MM: MM{issue} (0{year}{mm}00)"
    month_name = datetime(int(year), int(mm), 1).strftime("%B %Y")

    blocks = [b for b in month_blocks(month) if b.get("visibility") != "private"]
    with ThreadPoolExecutor(4) as pool:  # four requests at a time: quick, but gentle on Are.na
        filed = dict(zip((b["id"] for b in blocks), pool.map(channels_of, blocks)))
    blocks = [b for b in blocks if filed[b["id"]]]  # drops blocks filed only in private channels

    # A block in several channels is listed once, under the most specific one:
    # the channel that took the fewest blocks this month.
    busy = Counter(c["slug"] for chans in filed.values() for c in chans)
    theme_of = {slug: theme for theme, slugs in THEMES for slug in slugs}
    order = {slug: i for i, slug in enumerate(s for _, slugs in THEMES for s in slugs)}
    groups, names = defaultdict(list), {}
    for b in sorted(blocks, key=lambda b: b["created_at"]):
        known = [c for c in filed[b["id"]] if c["slug"] in theme_of]
        home = min(known or filed[b["id"]], key=lambda c: busy[c["slug"]])
        groups[home["slug"]].append(b)
        names[home["slug"]] = home["title"]

    out = [
        "\\rules except wikilink",
        f"Everything added across Are.na in {month_name}, pulled via the Are.na v3 API "
        f"({len(blocks)} blocks). Grouped by what goes together, using the channels each block was filed in. "
        "Fill in the ''why/how'' under each group, cut what doesn't earn its place, then this becomes the "
        f"MM{issue} issue.",
        ""]
    themes = THEMES + [(OTHER, sorted((s for s in groups if s not in theme_of), key=lambda s: -len(groups[s])))]
    for theme, slugs in themes:
        slugs = [s for s in slugs if s in groups]
        if not slugs:
            continue
        out += [f"! {theme} ({sum(len(groups[s]) for s in slugs)})", ""]
        for slug in slugs:
            out += [f"!! [[{safe(names[slug], 80)}|https://www.are.na/channel/{slug}]] ({len(groups[slug])})", "",
                    ": » ''why/how:'' ", ""]
            out += [item(b) + "\n" for b in groups[slug]]
    added = wiki_additions(month)
    if added:
        out += ["! New in Bjørnpaedia", "", f"Pages added to the wiki in {month_name}.", ""] + added

    print(f"{title}: {len(blocks)} blocks in {len(groups)} channels")
    for theme, slugs in themes:
        n = sum(len(groups[s]) for s in slugs if s in groups)
        if n:
            print(f"  {n:4}  {theme}")
    if dry:
        return

    if subprocess.run(["pgrep", "-f", "tiddlywiki sad2021tw"], capture_output=True).returncode == 0:
        sys.exit("The dev server is running and would not see this file. Stop it, then run this again.")
    now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "000"
    path = os.path.join(TIDDLERS, re.sub(r'[/\\:*?"<>|]', "_", title) + ".tid")
    created = now
    if os.path.exists(path):  # re-running a month keeps the page's original date
        created = re.search(r"^created: (\d+)", open(path, encoding="utf-8").read(), re.M).group(1)
    header = f"created: {created}\nmodified: {now}\ntags: Are.na MM\ntitle: {title}\ntype: text/vnd.tiddlywiki\n\n"
    open(path, "w", encoding="utf-8").write(header + "\n".join(out) + "\n")
    print("wrote", os.path.relpath(path, ROOT))

    if make_channel:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        try:
            channel = api(f"/v3/channels/{slug}")
            print(f"channel already exists: https://www.are.na/{USER}/{slug}")
        except urllib.error.HTTPError as err:
            if err.code != 404:
                raise
            channel = api("/v3/channels", "POST", {"title": title, "visibility": "public"})
            print(f"created channel: https://www.are.na/{USER}/{channel['slug']}")
        # Skip what is already there, so a second run only adds what is new.
        have, page = set(), 1
        while True:
            data = api(f"/v3/channels/{channel['id']}/contents", per=100, page=page).get("data", [])
            have |= {x["id"] for x in data}
            if len(data) < 100:
                break
            page += 1
        todo = [b for b in sorted(blocks, key=lambda b: b["created_at"]) if b["id"] not in have]
        for n, b in enumerate(todo, 1):
            api("/v3/connections", "POST",
                {"connectable_id": b["id"], "connectable_type": "Block", "channel_ids": [channel["id"]]})
            time.sleep(0.5)  # a few hundred writes in a burst trips Are.na's rate limit
            if n % 50 == 0:
                print(f"  connected {n} of {len(todo)}")
        print(f"connected {len(todo)} blocks ({len(have)} were already there)")


if __name__ == "__main__":
    TOKEN = token()
    main()
