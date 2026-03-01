#!/usr/bin/env python3
"""
Validate SKILL.md structure and basic security rules.

Checks:
- YAML frontmatter present
- required metadata fields exist
- required sections exist
- no obvious secret leakage patterns
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml  # PyYAML


REQUIRED_META = [
    "name",
    "version",
    "description",
    "inputs",
    "outputs",
    "compatibility",
    "security",
]

REQUIRED_SECTIONS = [
    "# Purpose",
    "# When to Use",
    "# Inputs",
    "# Procedure",
    "# Output Format",
    "# Guardrails",
    "# Example Invocation",
]

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),            # AWS access key (common)
    re.compile(r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*\S+"),
    re.compile(r"(?i)secret\s*[:=]\s*\S+"),
    re.compile(r"(?i)password\s*[:=]\s*\S+"),
]


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        fail("Missing YAML frontmatter (must start with ---).")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        fail("Invalid frontmatter delimiter structure.")
    _, yaml_part, body = parts[0], parts[1], parts[2]
    meta = yaml.safe_load(yaml_part) or {}
    return meta, body


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_md", help="Path to SKILL.md")
    args = ap.parse_args()

    p = Path(args.skill_md)
    if not p.exists():
        fail(f"File not found: {p}")

    text = p.read_text(encoding="utf-8")
    meta, body = split_frontmatter(text)

    for k in REQUIRED_META:
        if k not in meta:
            fail(f"Missing required metadata field: {k}")

    # Security pointer fields
    sec = meta.get("security") or {}
    for k in ["secrets", "env_allowlist", "fs_allowlist", "network_policy"]:
        if k not in sec:
            fail(f"Missing security.{k} in metadata")

    # Sections
    for h in REQUIRED_SECTIONS:
        if h not in body:
            fail(f"Missing required section heading: {h}")

    # Secrets detection (best-effort)
    for pat in SECRET_PATTERNS:
        if pat.search(text):
            fail(f"Possible secret detected matching pattern: {pat.pattern}")

    print("OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
