#!/usr/bin/env bash
# DESTRUCTIVE: permanently deletes logs/archive/*.log.gz older than N days (by file time).
# Usage: purge_archives.sh --older-than DAYS (--dry-run | --yes)
set -euo pipefail
LOGS="${LOGS_DIR:-$HOME/workspace/logs}"
DAYS=""
MODE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --older-than) DAYS="${2:-}"; shift 2 ;;
    --dry-run) MODE=dry; shift ;;
    --yes) MODE=delete; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
if ! [[ "$DAYS" =~ ^[0-9]+$ ]] || [ -z "$MODE" ]; then
  echo "usage: purge_archives.sh --older-than DAYS (--dry-run | --yes)" >&2
  exit 2
fi

mapfile -t victims < <(find "$LOGS/archive" -maxdepth 1 -name '*.log.gz' -mtime +"$DAYS" | sort)
if [ "${#victims[@]}" -eq 0 ]; then
  echo "nothing older than $DAYS days in archive/"
  exit 0
fi
for f in "${victims[@]}"; do
  if [ "$MODE" = dry ]; then
    echo "would delete archive/$(basename "$f") ($(stat -c %s "$f") bytes, $(date -r "$f" +%F))"
  else
    rm -f -- "$f"
    echo "deleted archive/$(basename "$f")"
  fi
done
[ "$MODE" = dry ] && echo "${#victims[@]} file(s) would be deleted. Re-run with --yes to delete them permanently."
exit 0
