#!/usr/bin/env bash
# Compresses app.log and nginx/access.log into logs/archive/<name>-<YYYY-MM-DD>.log.gz and
# truncates them. Reversible: gunzip the archive back into place. --dry-run prints the plan only.
set -euo pipefail
LOGS="${LOGS_DIR:-$HOME/workspace/logs}"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1
stamp=$(date +%F)
mkdir -p "$LOGS/archive"

for rel in app.log nginx/access.log; do
  src="$LOGS/$rel"
  name=app
  [ "$rel" = nginx/access.log ] && name=nginx
  dst="$LOGS/archive/$name-$stamp.log.gz"
  if [ ! -s "$src" ]; then
    echo "skip $rel: empty or missing"
    continue
  fi
  if [ -e "$dst" ]; then
    echo "refusing: $dst already exists (rotated today?)" >&2
    exit 1
  fi
  if [ "$DRY" = 1 ]; then
    echo "would compress $rel ($(stat -c %s "$src") bytes) -> archive/$(basename "$dst"), then truncate $rel"
    continue
  fi
  gzip -c "$src" > "$dst"
  : > "$src"
  echo "rotated $rel -> archive/$(basename "$dst")"
done
