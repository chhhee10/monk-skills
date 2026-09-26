#!/usr/bin/env bash
# Lays out ~/workspace, Ledgerly's shared ops box: code with git history, the billing database,
# AWS/IAM/helpdesk exports, logs, runbooks and notes. Offline and idempotent: a second run leaves
# ~/workspace alone (it only refreshes the sqlite3 shim, if this script installed one).
#
# Usage: setup.sh            build ~/workspace if it isn't there yet
#        setup.sh --reset    delete ~/workspace (and every change made in it) and rebuild it
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="${WORKSPACE_DIR:-$HOME/workspace}"
VERSION=1
started=$(date +%s.%N)

# sqlite3 CLI: install the Python-backed shim when the real one is missing, and refresh a shim an
# earlier run installed (a long-lived sandbox keeps /usr/local/bin across skill updates).
current_sqlite="$(command -v sqlite3 || true)"
if [ -w /usr/local/bin ] && { [ -z "$current_sqlite" ] || grep -qs 'python sqlite3 module shim' "$current_sqlite"; }; then
  install -m 0755 "$SKILL_DIR/sqlite3_shim.py" /usr/local/bin/sqlite3
fi

if [ "${1:-}" = "--reset" ]; then
  rm -rf "$WS"
fi
if [ -f "$WS/.workspace-version" ]; then
  echo "workspace already set up at $WS"
  exit 0
fi

tmp="$(mktemp -d "${WS%/}.build.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
cp -a "$SKILL_DIR/workspace/." "$tmp/"

# Billing database from the dump, with Python's sqlite3 module (the CLI may be missing).
python3 - "$tmp/db/ledgerly.sql" "$tmp/db/ledgerly.db" <<'PY'
import sqlite3, sys
db = sqlite3.connect(sys.argv[2])
with open(sys.argv[1], encoding="utf-8") as f:
    db.executescript(f.read())
db.close()
PY

# ledgerly-api: replay the history stages as dated commits. Fixed dates and authors give the same
# commit ids on every machine.
repo="$tmp/projects/ledgerly-api"
hist="$SKILL_DIR/history/ledgerly-api"
mkdir -p "$repo"
git -C "$repo" init -q -b main
git -C "$repo" config user.name "Ledgerly Engineering"
git -C "$repo" config user.email "eng@ledgerly.example"
git -C "$repo" config commit.gpgsign false
git -C "$repo" config tag.gpgsign false
while IFS=$'\t' read -r stage when author message tag; do
  if [ -z "$stage" ] || [ "${stage:0:1}" = "#" ]; then
    continue
  fi
  cp -a "$hist/$stage/." "$repo/"
  git -C "$repo" add -A
  GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" \
    git -C "$repo" -c core.hooksPath=/dev/null commit -q --author="$author" -m "$message"
  if [ -n "$tag" ]; then
    GIT_COMMITTER_DATE="$when" git -C "$repo" tag -a "$tag" -m "ledgerly-api $tag"
  fi
done < "$hist/log.tsv"

# Rotated logs: weekly archives since the last purge, dated by file time (the runbook purges by age).
arch="$tmp/logs/archive"
mkdir -p "$arch"
for day in 2026-07-03 2026-07-10 2026-07-17 2026-07-24 2026-07-31 2026-08-07 2026-08-14 2026-08-21 2026-08-28 2026-09-04 2026-09-11 2026-09-18; do
  nginx_day=$(date -d "$day" +%d/%b/%Y)
  head -n 400 "$tmp/logs/app.log" | sed "s/2026-09-25/$day/g" | gzip -n > "$arch/app-$day.log.gz"
  head -n 400 "$tmp/logs/nginx/access.log" | sed "s#25/Sep/2026#$nginx_day#g" | gzip -n > "$arch/nginx-$day.log.gz"
  touch -d "$day 23:59:00" "$arch/app-$day.log.gz" "$arch/nginx-$day.log.gz"
done

# No sqlite3 on PATH and /usr/local/bin not writable: leave the shim in the workspace instead.
if ! command -v sqlite3 > /dev/null 2>&1; then
  mkdir -p "$tmp/bin"
  install -m 0755 "$SKILL_DIR/sqlite3_shim.py" "$tmp/bin/sqlite3"
  echo "note: sqlite3 shim installed at $WS/bin/sqlite3 (not on PATH)"
fi

echo "$VERSION" > "$tmp/.workspace-version"
if [ -d "$WS" ]; then
  cp -a "$tmp/." "$WS/"
else
  mv "$tmp" "$WS"
fi

elapsed=$(awk -v s="$started" -v e="$(date +%s.%N)" 'BEGIN { printf "%.1f", e - s }')
echo "workspace ready at $WS in ${elapsed}s. Start with: cat $WS/README.md"
