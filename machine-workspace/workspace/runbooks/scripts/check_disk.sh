#!/usr/bin/env bash
# Read-only: disk usage of the filesystem holding the logs, and the size of each log file.
set -euo pipefail
LOGS="${LOGS_DIR:-$HOME/workspace/logs}"

df -h "$LOGS" | awk 'NR == 2 { printf "filesystem %s: %s used (%s of %s)\n", $6, $5, $3, $2 }'
printf 'logs/ total: %s\n' "$(du -sh "$LOGS" | cut -f1)"
find "$LOGS" -type f -printf '%TY-%Tm-%Td  %8s bytes  %P\n' | sort -k4
