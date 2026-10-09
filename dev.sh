#!/bin/bash
# dev.sh — preview the static site locally, and re-render just the CSS
# whenever you edit a system tiddler or a .css file (templates, stylesheets).
#
# Usage:
#   bash dev.sh          full build once, then serve + watch for CSS edits
#   bash dev.sh --fast   skip the full build (reuse what's already in
#                        sad2021tw/output/) — use when you only want to
#                        poke at CSS and the pages haven't changed
#
# Open http://localhost:8000/ — everything stays on your machine. This never
# touches ~/Code/bjornpaedia and never pushes anything; publish.sh is still
# the only thing that does that.

set -e
# Stop the script on the first failing command instead of ploughing on.

PORT="${PORT:-8000}"
# ${VAR:-default}: use $PORT from the environment if set, otherwise 8000.
# e.g.  PORT=9000 bash dev.sh

cd "$(dirname "$0")"
# Always run from the folder this script lives in, so it works no matter
# where you launched it from. `$0` is the script's own path; `dirname` strips
# the filename off it.

if [ "$1" != "--fast" ]; then
  echo "== Full build (about 10 seconds) =="
  bash build.sh
  # build.sh wipes sad2021tw/output/ and re-renders every page + the CSS.
fi

if [ ! -d sad2021tw/output/static ]; then
  echo "No build found in sad2021tw/output/ — run without --fast first."
  exit 1
fi

echo "== Serving sad2021tw/output at http://localhost:$PORT/ =="
python3 -m http.server "$PORT" --directory sad2021tw/output >/dev/null 2>&1 &
# python3 ships with macOS and has a one-line static file server built in.
#   -m http.server    run the standard-library module as a program
#   --directory       which folder to serve (the build output)
#   >/dev/null 2>&1   hide its per-request log chatter
#   &                 run it in the background so this script can keep going
SERVER_PID=$!
# $! is the process ID of the most recent background job — saved so we can
# stop the server again later.

sleep 1
if ! kill -0 $SERVER_PID 2>/dev/null; then
  # `kill -0` sends no signal at all; it only asks "is this process alive?".
  # The server quits straight away when the port is taken, and because its
  # output is hidden above, this is the only way you would find out.
  echo "The server did not start. Is port $PORT already in use? Try: PORT=9000 bash dev.sh"
  exit 1
fi

trap 'kill $SERVER_PID 2>/dev/null; echo; echo "Stopped."' EXIT
# `trap ... EXIT` registers a cleanup that runs whenever the script ends
# (including when you press Ctrl-C), so a stray server isn't left running.

echo "== Watching system tiddlers and .css files for changes (Ctrl-C to stop) =="
touch /tmp/sad2021tw-dev-marker
# A marker file whose modification time means "the last time we looked".

while true; do
  sleep 1
  # Poll once a second. Simple and dependable, no extra tools to install.

  CHANGED=$(find sad2021tw/tiddlers \( -name '$__*' -o -name '*.css' -o -name 'Wjerk Tokens.tid' \) -newer /tmp/sad2021tw-dev-marker | head -1)
  # `find ... -newer FILE`: files modified more recently than FILE.
  # Three kinds of file matter: system tiddlers (filenames starting `$__`,
  # where the static templates, the palette and the template's CSS live),
  # plain .css files like "OOKB Styles.css", the main custom stylesheet, and
  # "Wjerk Tokens.tid", the one stylesheet saved as a .tid. `\( ... -o ... \)`
  # means "this OR that". `head -1` just asks "is there at least one?".

  if [ -n "$CHANGED" ]; then
    # -n: the string is non-empty, i.e. something changed.
    touch /tmp/sad2021tw-dev-marker
    echo "Changed: $CHANGED — re-rendering CSS"
    tiddlywiki sad2021tw --output sad2021tw/output \
      --rendertiddler '$:/core/templates/static.template.css' static/static.css text/plain \
      >/dev/null 2>&1 || echo "  (render failed — check the tiddler you just edited)"
    # Same render step build.sh runs for the CSS, but alone: about 2 seconds
    # instead of 10. Output goes straight into the folder being served, so a
    # browser refresh picks it up. `||` means "if that failed, print a hint
    # instead of stopping the whole script".
  fi
done
