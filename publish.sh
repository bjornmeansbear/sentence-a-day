#!/bin/bash
set -e

BJORNPAEDIA_DIR="${BJORNPAEDIA_DIR:-$HOME/Code/bjornpaedia}"

if [ ! -d "$BJORNPAEDIA_DIR" ]; then
  echo "bjornpaedia repo not found at $BJORNPAEDIA_DIR (set BJORNPAEDIA_DIR to override)"
  exit 1
fi

echo "== Building sad2021tw =="
bash build.sh

echo "== Syncing static/ into $BJORNPAEDIA_DIR =="
rsync -av --delete sad2021tw/output/static/ "$BJORNPAEDIA_DIR/static/"

echo "== Copying index.html, static.html, alltiddlers.html =="
cp sad2021tw/output/index.html sad2021tw/output/static.html sad2021tw/output/alltiddlers.html "$BJORNPAEDIA_DIR/"

cd "$BJORNPAEDIA_DIR"
git add -A
echo
echo "== bjornpaedia git status =="
git status

echo
read -p "Commit and push bjornpaedia? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  git commit -m "Publish update from sentence-a-day"
  git push
  echo "Pushed. GitHub Pages will deploy bjornpaedia.wjerk.shop shortly."
else
  echo "Left uncommitted in $BJORNPAEDIA_DIR — review and commit manually when ready."
fi
