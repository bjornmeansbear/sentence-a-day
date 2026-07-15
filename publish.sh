#!/bin/bash
# The "shebang" — tells the OS to run this file with bash, so you can execute
# it directly (./publish.sh) instead of typing `bash publish.sh` every time.

set -e
# Abort the whole script the instant any command fails (non-zero exit code).
# Without this, bash just shrugs off a failure and keeps going to the next
# line — which is exactly how the old build.sh silently produced broken
# output for months. `set -e` turns "silent partial failure" into "loud stop".

BJORNPAEDIA_DIR="${BJORNPAEDIA_DIR:-$HOME/Code/bjornpaedia}"
# Variable assignment with a fallback default: ${VAR:-default} means "use
# $BJORNPAEDIA_DIR if it's already set in the environment, otherwise use
# $HOME/Code/bjornpaedia". This lets you override the target repo location
# for one run without editing the script, e.g.:
#   BJORNPAEDIA_DIR=/some/other/path bash publish.sh

if [ ! -d "$BJORNPAEDIA_DIR" ]; then
  # `-d` tests "does this path exist AND is it a directory". `!` negates it.
  echo "bjornpaedia repo not found at $BJORNPAEDIA_DIR (set BJORNPAEDIA_DIR to override)"
  exit 1
  # Explicit non-zero exit — fail loudly with a clear reason rather than
  # letting later commands crash with a confusing "no such file" error.
fi

echo "== Building sad2021tw =="
bash build.sh
# Runs the whole other script as a subprocess. Because of `set -e` above, if
# build.sh exits non-zero (e.g. TiddlyWiki crashes mid-render), this script
# stops right here — nothing gets synced or published from a broken build.

echo "== Syncing static/ into $BJORNPAEDIA_DIR =="
rsync -av --delete sad2021tw/output/static/ "$BJORNPAEDIA_DIR/static/"
# rsync copies files, but smarter than `cp`: it only touches files that
# actually changed, and prints what it does.
#   -a  "archive" mode — recurse into subfolders, preserve timestamps/perms
#   -v  verbose — print each file as it's copied/deleted
#   --delete  remove files in the destination that no longer exist in the
#             source. This is what purges stale/renamed/newly-private
#             tiddler pages from bjornpaedia automatically.
# Trailing slashes on both paths matter: `static/` (with slash) means "the
# *contents* of this folder", not the folder itself.

echo "== Copying index.html =="
rm -f "$BJORNPAEDIA_DIR/static.html" "$BJORNPAEDIA_DIR/alltiddlers.html"
# These two used to be separate build outputs (a "live" interactive wiki
# homepage and a single-file all-tiddlers dump). Both embedded the full
# text of every tiddler with no way to exclude private/hide-tagged ones —
# confirmed leaking a private-tagged entry into the published site. They've
# been retired; this cleans up the stale copies already committed here so
# the leak doesn't linger in the working tree (git history still has it —
# see CLAUDE.md).
cp sad2021tw/output/index.html "$BJORNPAEDIA_DIR/"
# `index.html` is now rendered straight from the static (filtered) build —
# same private/hide exclusion as everything in static/. Plain `cp` because
# it's one file, always overwritten wholesale.

cd "$BJORNPAEDIA_DIR"
# Switch the shell's working directory into the target repo. Every command
# from here on runs as if you'd `cd`'d there yourself in the terminal.

git add -A
# Stage every change in bjornpaedia — new files, edits, and deletions alike
# (the rsync --delete above already removed files on disk; `git add -A` is
# what tells git those removals should be part of the next commit).

echo
echo "== bjornpaedia git status =="
git status
# Print exactly what's about to be committed, so you can eyeball it before
# anything is written to git history or pushed anywhere.

echo
read -p "Commit and push bjornpaedia? [y/N] " confirm
# `read -p "prompt" varname` prints the prompt and pauses the script,
# waiting for you to type a response and hit enter. Whatever you type gets
# stored in the shell variable $confirm. This is the script's only
# interactive moment — everything before it runs unattended.

if [[ "$confirm" =~ ^[Yy]$ ]]; then
  # `[[ ... =~ regex ]]` tests $confirm against a regular expression:
  #   ^        start of string
  #   [Yy]     a single "Y" or "y"
  #   $        end of string
  # So this matches only if you typed exactly "y" or "Y" — anything else
  # (blank, "n", "yes", a typo) falls through to the else branch, which is
  # the safe default given this step pushes to a public, deployed repo.
  git commit -m "Publish update from sentence-a-day"
  git push
  echo "Pushed. GitHub Pages will deploy bjornpaedia.wjerk.shop shortly."
else
  echo "Left uncommitted in $BJORNPAEDIA_DIR — review and commit manually when ready."
  # Nothing is lost here — `git add -A` already staged everything, so you
  # can inspect it (`git diff --cached`), amend the commit message, or just
  # come back and commit later.
fi
