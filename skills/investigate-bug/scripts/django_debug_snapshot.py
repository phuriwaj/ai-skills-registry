#!/usr/bin/env python3
"""
Collect a minimal Django diagnostic snapshot for bug triage.

- No network calls
- Avoid dumping sensitive settings
- Supports --dry-run and --json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, check=False)
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out.strip()
    except Exception as e:
        return 1, f"{type(e).__name__}: {e}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manage-py", default="manage.py")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    manage_py = Path(args.manage_py)
    if not manage_py.exists():
        payload = {"status": "fail", "error": f"{manage_py} not found"}
        print(json.dumps(payload, indent=2) if args.json else payload["error"], file=sys.stderr)
        sys.exit(2)

    # We intentionally avoid printing environment variables or settings values.
    checks = {}

    checks["python_version"] = sys.version.split()[0]
    checks["platform"] = platform.platform()

    rc, out = run([sys.executable, "-c", "import django; print(django.get_version())"])
    checks["django_version"] = out if rc == 0 else f"error: {out}"

    rc, out = run([sys.executable, str(manage_py), "check"])
    checks["django_check_rc"] = rc
    checks["django_check"] = out[:4000]  # cap output

    rc, out = run([sys.executable, str(manage_py), "showmigrations", "--plan"])
    checks["migrations_plan_rc"] = rc
    checks["migrations_plan"] = out[:4000]

    rc, out = run([sys.executable, str(manage_py), "makemigrations", "--check", "--dry-run"])
    checks["migrations_drift_rc"] = rc
    checks["migrations_drift"] = out[:4000]

    payload = {
        "status": "ok",
        "dry_run": bool(args.dry_run),
        "snapshot": checks,
        "note": "This snapshot avoids printing settings/env secrets.",
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Django Debug Snapshot")
        for k, v in checks.items():
            print(f"- {k}: {v}")

    sys.exit(0)


if __name__ == "__main__":
    main()
