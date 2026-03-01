#!/usr/bin/env bash
set -euo pipefail

# Template: enterprise skill helper script.
# Requirements:
# - support --dry-run
# - support --json (when applicable)
# - deterministic exit codes
# - no secrets in code; read env vars only

DRY_RUN="false"
JSON="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN="true"; shift ;;
    --json) JSON="true"; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ "$JSON" == "true" ]]; then
  printf '{\n  "status": "ok",\n  "dry_run": %s\n}\n' "$DRY_RUN"
else
  echo "OK"
fi
