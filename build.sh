#!/bin/bash
set -e

rm -rf sad2021tw/output

tiddlywiki sad2021tw --build static

# The site icons live in sad2021tw/icons/ (the two exports with spaces in their
# names are just the design sources). The templates point at them from the site
# root, e.g. <link rel="icon" href="/favicon.svg">, so they have to land at the
# top of the output folder, next to index.html.
cp sad2021tw/icons/favicon.svg sad2021tw/icons/favicon.ico sad2021tw/icons/apple-touch-icon.png sad2021tw/output/
