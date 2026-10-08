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

# Version-stamp the stylesheet link on every page. Cloudflare and browsers hold
# on to static.css for hours, while the pages themselves refresh in minutes, so
# right after a publish a visitor could get a new page with an old stylesheet
# (this happened on 2026-10-08: the new homepage showed up unstyled). Adding
# ?v=<something> to the link makes it a different address, so nobody is handed
# the stale copy.
#
# The "something" is the first 8 characters of the stylesheet's checksum
# (shasum prints a fingerprint of a file's contents). It only changes when the
# CSS changes, so an unchanged stylesheet keeps its address and stays cached.
CSS_VERSION=$(shasum sad2021tw/output/static/static.css | cut -c1-8)
# find lists every .html file in the output; perl -pi edits each one in place,
# turning   static.css"   into   static.css?v=1a2b3c4d"   wherever it appears
# (the homepage, tiddler pages, tag pages and 404 page each spell the path
# differently, but they all end the link with static.css").
find sad2021tw/output -name '*.html' -print0 | xargs -0 perl -pi -e "s/static\\.css\"/static.css?v=${CSS_VERSION}\"/g"
echo "Stylesheet version stamped: ${CSS_VERSION}"
