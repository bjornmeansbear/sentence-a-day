#!/bin/bash
set -e

rm -rf sad2021tw/output

tiddlywiki sad2021tw --build static

# Tags that have no tiddler of their own still get a page (a short note plus the
# "Tagged with" list), so every tag pill on the site has somewhere to go. The
# build renders them into their own folder because a second --rendertiddlers
# into static/ would wipe out the pages the first one just wrote. Merge them in
# here, then remove the scratch folder. A tag that later gets a real tiddler is
# no longer "missing", so its real page replaces the generated one automatically.
cp -R sad2021tw/output/static-tags/. sad2021tw/output/static/
rm -rf sad2021tw/output/static-tags

# The site icons live in sad2021tw/icons/ (the two exports with spaces in their
# names are just the design sources). The templates point at them from the site
# root, e.g. <link rel="icon" href="/favicon.svg">, so they have to land at the
# top of the output folder, next to index.html.
cp sad2021tw/icons/favicon.svg sad2021tw/icons/favicon.ico sad2021tw/icons/apple-touch-icon.png sad2021tw/output/
