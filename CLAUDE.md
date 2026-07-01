# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal writing project ("A Sentence A Day") by Kristian Bjornard, focused on sustainability, design, and related thinking. Writing exists in two forms:

1. **Flat markdown/text files** at the repo root — earlier writing (2019–2022) in `.md` and `.txt` files, plus thematic essays in `otherIdeas/`.
2. **TiddlyWiki** (`sad2021tw/`) — the primary ongoing writing environment since mid-2021. Tiddlers are stored as individual `.tid` files in `sad2021tw/tiddlers/`. Images are in `sad2021tw/i/`. Custom plugins live in `sad2021tw/plugins/` (edit-comptext, relink, relink-markdown, relink-titles).

The site title is "The Sustainabilitist: Essays Every Day?" and the static output publishes to `bjornpaedia.wjerk.shop`.

## TiddlyWiki commands

Start the local dev server (live editing at localhost:8080):
```
tiddlywiki sad2021tw --listen
```

Build static output (cleans `sad2021tw/output/`, then renders all non-system tiddlers + index + CSS):
```
bash build.sh
```

The build script outputs into `sad2021tw/output/`: `static/` (individual tiddler HTML files), `static.html` (all tiddlers page), `alltiddlers.html`, and `index.html` (offline single-file TiddlyWiki via the tiddlyweb save plugin).

Build just the single-file offline index:
```
tiddlywiki sad2021tw --build index
```

## Publishing

The live site is a *separate* local repo, `~/Code/bjornpaedia` (github.com/bjornmeansbear/bjornpaedia), deployed via GitHub Pages to `bjornpaedia.wjerk.shop`. This repo (`sentence-a-day`) is the source; the site is not built or deployed from here directly.

To ship a new build:
```
bash publish.sh
```
This rebuilds via `build.sh`, syncs the generated `static/`, `index.html`, `static.html`, and `alltiddlers.html` into `~/Code/bjornpaedia` (leaving that repo's own `CNAME`/`README.md`/`CLAUDE.md`/legacy files untouched), shows a `git status` diff, and asks for confirmation before committing and pushing there. Override the target repo path with `BJORNPAEDIA_DIR` if needed.

## Tiddler file format

Each `.tid` file has a metadata header followed by a blank line and the body in TiddlyWiki markup (WikiText):

```
created: 20210611173024273
modified: 20210618141411123
tags: sustainability design
title: My Tiddler Title

Body text here in WikiText format.
```

System tiddlers (configuration, UI state) have filenames starting with `$__`. Content tiddlers follow a `YYYYMMDDHHMMSS Title.tid` naming pattern.

## Repo structure at a glance

- `sad2021tw/tiddlers/` — all wiki content and config as individual `.tid` files
- `sad2021tw/i/` — images referenced by tiddlers
- `sad2021tw/output/` — generated static site output (gitignored, not committed)
- `sad2021tw/plugins/` — custom TiddlyWiki plugins
- `sad2021tw/tiddlywiki.info` — wiki configuration (plugins, themes, build targets)
- `build.sh` — primary build script (cleans and rebuilds `sad2021tw/output/`); `renderTiddlers.sh` has older/alternate render commands
- `publish.sh` — builds and syncs output into the separate `~/Code/bjornpaedia` deploy repo
- Root `.md`/`.txt` files — earlier writing archive (2019–2022)
- `otherIdeas/` — standalone essay drafts
