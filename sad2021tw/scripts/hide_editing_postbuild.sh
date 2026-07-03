#!/usr/bin/env bash
set -euo pipefail

# Usage: ./hide_editing_postbuild.sh [output_dir]
OUTDIR=${1:-"$(dirname "$0")/../output"}
OUTDIR=$(cd "$OUTDIR" && pwd)

CSS='<style id="hide-editing-style">.tc-tiddler-controls{display:none!important;}button[title*="Edit"]{display:none!important;}button[title*="Create"]{display:none!important;}button[title*="Delete"]{display:none!important;}button[aria-label*="Edit"]{display:none!important;}button[aria-label*="new here"]{display:none!important;}</style>'

echo "Injecting hide-editing CSS into HTML under: $OUTDIR"

find "$OUTDIR" -type f -name "*.html" | while IFS= read -r file; do
  if grep -q "hide-editing-style" "$file"; then
    continue
  fi
  # insert CSS before closing </head>
  perl -0777 -pe "s#</head>#$CSS</head>#is" -i.bak "$file"
done

echo "Injection complete. Backups saved with .bak extensions."
