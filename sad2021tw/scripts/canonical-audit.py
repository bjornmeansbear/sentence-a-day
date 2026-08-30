#!/usr/bin/env python3
"""
canonical-audit.py — find clusters of near-duplicate tiddlers so you can pick
one canonical survivor per idea in a single pass.

Why this exists: the wiki has abundance and no canon. Nothing outside the wiki
(a case study, a lecture, a product page) can link *at* an idea until exactly
one tiddler is the address for it. This lists the decisions waiting to be made.

Usage:
    python3 scripts/canonical-audit.py [tiddlers_dir] [--loose] [--min N]

    tiddlers_dir  defaults to ../tiddlers relative to this script
    --loose       also show containment clusters (one title inside another).
                  Noisier; review these, don't trust them.
    --min N       only show clusters of at least N tiddlers (default 2)
"""

import os
import re
import sys
from collections import defaultdict

# Title noise that marks a draft/fragment rather than a distinct idea.
# Deliberately does NOT include meaningful words like "new" — "New Design
# Commons" is a different idea from "Design Commons" and shouldn't be flattened.
NOISE = {
    "entry", "entries", "note", "notes", "idea", "ideas", "aggregate",
    "bibliography", "outline", "outlines", "reference", "references",
    "draft", "drafts", "misc", "related", "toomuchcontent", "wip",
    "old", "copy", "final", "revised", "rough", "part", "pt", "p",
    "v", "version",
}
LEADING_ARTICLES = {"a", "an", "the"}


def parse_tid(path):
    """Return (title, tags, modified, body_words) for one .tid file."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            raw = fh.read()
    except OSError:
        return None

    # Header is key: value lines up to the first blank line; body follows.
    parts = raw.split("\n\n", 1)
    header, body = parts[0], (parts[1] if len(parts) > 1 else "")
    fields = {}
    for line in header.split("\n"):
        if ":" in line:
            k, _, v = line.partition(":")
            fields[k.strip().lower()] = v.strip()

    title = fields.get("title") or os.path.basename(path)[:-4]
    return {
        "path": path,
        "title": title,
        "tags": fields.get("tags", ""),
        "modified": fields.get("modified", "")[:8],  # YYYYMMDD
        "words": len(body.split()),
        "canonical": fields.get("canonical", ""),
    }


def normalize(title):
    """Collapse a title to the idea it names, dropping draft scaffolding."""
    t = title.lower()
    t = re.sub(r"\([^)]*\)", " ", t)          # (0202209252330), (P1), (Amish)
    t = re.sub(r"\b0?2?0?\d{6,}\b", " ", t)   # 020221001201944, 202007271900
    t = re.sub(r"[^a-z0-9]+", " ", t)         # punctuation, underscores
    # Keep short numbers — "Found Note 06" vs "Found Note 07" are siblings,
    # not drafts of each other. Long timestamps were already stripped above.
    words = [w for w in t.split() if not (w.isdigit() and len(w) > 3)]
    while words and words[0] in LEADING_ARTICLES:
        words.pop(0)
    words = [w for w in words if w not in NOISE]
    return "".join(words)


def pick_survivor(group):
    """Best guess at the keeper: longest body, then most recently modified."""
    return max(group, key=lambda t: (t["words"], t["modified"]))


def report(clusters, label, min_size):
    shown = 0
    for key, group in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        if len(group) < min_size:
            continue
        shown += 1
        survivor = pick_survivor(group)
        total = sum(t["words"] for t in group)
        print(f"\n  {key}  —  {len(group)} tiddlers, {total} words total")
        for t in sorted(group, key=lambda t: -t["words"]):
            mark = "KEEP?" if t is survivor else "     "
            flag = " [canonical]" if t["canonical"] else ""
            mod = t["modified"] or "--------"
            print(f"    {mark} {t['words']:>5}w  {mod}  {t['title']}{flag}")
            if t["tags"]:
                print(f"             tags: {t['tags']}")
    if not shown:
        print(f"  (no {label} clusters at this threshold)")
    return shown


def main():
    args = [a for a in sys.argv[1:]]
    loose = "--loose" in args
    args = [a for a in args if a != "--loose"]
    min_size = 2
    if "--min" in args:
        i = args.index("--min")
        min_size = int(args[i + 1])
        del args[i:i + 2]

    default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tiddlers")
    tdir = os.path.abspath(args[0] if args else default_dir)

    tiddlers = []
    for name in sorted(os.listdir(tdir)):
        if not name.endswith(".tid") or name.startswith("$__"):
            continue
        t = parse_tid(os.path.join(tdir, name))
        if t:
            tiddlers.append(t)

    marked = sum(1 for t in tiddlers if t["canonical"])
    print(f"{len(tiddlers)} content tiddlers in {tdir}")
    print(f"{marked} already marked canonical:\n")

    exact = defaultdict(list)
    for t in tiddlers:
        key = normalize(t["title"])
        if key:
            exact[key].append(t)

    print("=" * 72)
    print("EXACT CLUSTERS — same idea, different drafts. Pick one per block.")
    print("=" * 72)
    n = report(exact, "exact", min_size)

    dupes = sum(len(g) - 1 for g in exact.values() if len(g) >= min_size)
    print("\n" + "-" * 72)
    print(f"{n} clusters · {dupes} tiddlers to demote, merge, or leave as drafts")

    if loose:
        print("\n" + "=" * 72)
        print("LOOSE CLUSTERS — one title contained in another. Review, don't trust.")
        print("=" * 72)
        singles = {k: g for k, g in exact.items() if len(g) < min_size}
        keys = sorted(singles, key=len)
        loose_groups = defaultdict(list)
        for i, short in enumerate(keys):
            if len(short) < 6:
                continue
            for long in keys[i + 1:]:
                if short in long:
                    loose_groups[short].extend(singles[short] + singles[long])
        for k in loose_groups:
            seen, uniq = set(), []
            for t in loose_groups[k]:
                if t["path"] not in seen:
                    seen.add(t["path"])
                    uniq.append(t)
            loose_groups[k] = uniq
        report(loose_groups, "loose", min_size)

    print("\nNext: add `canonical: true` to the keeper in each cluster, then")
    print("filter the static build on that field in build.sh.")


if __name__ == "__main__":
    main()
