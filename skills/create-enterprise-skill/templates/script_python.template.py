#!/usr/bin/env python3
"""
Template: enterprise skill helper script.

Requirements:
- support --dry-run
- support --json
- deterministic exit codes
- no secrets in code; read env vars only
"""

from __future__ import annotations

import argparse
import json
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    result = {
        "status": "ok",
        "dry_run": bool(args.dry_run),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("OK")

    sys.exit(0)


if __name__ == "__main__":
    main()
