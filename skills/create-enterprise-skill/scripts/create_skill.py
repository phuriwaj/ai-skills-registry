#!/usr/bin/env python3
"""
Create an enterprise skill package from templates and update registry.yaml.

Design goals:
- deterministic output
- no network access
- no secrets handling beyond reading env allowlist path references
- idempotent updates (update if exists, else create)
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import yaml  # PyYAML


NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
IDENT_RE = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclasses.dataclass(frozen=True)
class SkillSpec:
    skill_name: str
    version: str
    description: str
    triggers: list[str]
    inputs_required: list[str]
    inputs_optional: list[str]
    outputs: list[str]
    runners: list[str]
    scripts: list[str]
    notes: str | None
    output_format: str | None


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def validate_spec(spec: SkillSpec) -> None:
    if not NAME_RE.match(spec.skill_name) or len(spec.skill_name) > 64:
        fail("Invalid skill_name. Must match ^[a-z0-9]+(-[a-z0-9]+)*$ and length <= 64.")

    if not spec.description.strip():
        fail("description is required.")

    if not (3 <= len(spec.triggers) <= 64):
        fail("triggers must be a non-empty list (recommend 3–12).")

    for s in spec.inputs_required + spec.inputs_optional + spec.outputs:
        if not IDENT_RE.match(s):
            fail(f"Invalid identifier '{s}'. Must match ^[a-z][a-z0-9_]*$")

    if not spec.inputs_required:
        fail("inputs_required must be non-empty.")
    if not spec.outputs:
        fail("outputs must be non-empty.")

    allowed_scripts = {"bash", "python"}
    for s in spec.scripts:
        if s not in allowed_scripts:
            fail(f"Unsupported script language: {s}. Allowed: bash, python.")


def load_text(path: Path) -> str:
    if not path.exists():
        fail(f"Missing required file: {path}")
    return path.read_text(encoding="utf-8")


def render_skill_md(template: str, spec: SkillSpec) -> str:
    # Minimal templating by replacement tokens.
    # Tokens are unlikely to collide and keep dependencies low.
    now = dt.date.today().isoformat()

    def qlist(items: list[str]) -> str:
        # YAML list as markdown (indented)
        return "\n".join([f"  - {i}" for i in items]) if items else "  -"

    inputs_optional_block = qlist(spec.inputs_optional) if spec.inputs_optional else "  -"
    scripts_block = qlist(spec.scripts) if spec.scripts else "  -"

    out = template
    out = out.replace("{{NAME}}", spec.skill_name)
    out = out.replace("{{VERSION}}", spec.version)
    out = out.replace("{{DESCRIPTION}}", spec.description.strip())
    out = out.replace("{{DATE}}", now)
    out = out.replace("{{TRIGGERS_YAML}}", qlist(spec.triggers))
    out = out.replace("{{INPUTS_REQUIRED_YAML}}", qlist(spec.inputs_required))
    out = out.replace("{{INPUTS_OPTIONAL_YAML}}", inputs_optional_block)
    out = out.replace("{{OUTPUTS_YAML}}", qlist(spec.outputs))
    out = out.replace("{{RUNNERS_YAML}}", qlist(spec.runners))
    out = out.replace("{{SCRIPTS_YAML}}", scripts_block)
    out = out.replace("{{NOTES}}", spec.notes.strip() if spec.notes else "")
    if spec.output_format:
        out = out.replace("{{OUTPUT_FORMAT_SECTION}}", spec.output_format.strip())
    else:
        out = out.replace("{{OUTPUT_FORMAT_SECTION}}", "")
    return out


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.write_text(content, encoding="utf-8")


def upsert_registry(registry_path: Path, spec: SkillSpec, dry_run: bool) -> dict:
    if not registry_path.exists():
        fail(f"registry.yaml not found at {registry_path}")

    data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    if data.get("version") is None:
        data["version"] = 1
    data.setdefault("skills", [])

    skills: list[dict] = data["skills"]
    entry = {
        "name": spec.skill_name,
        "description": spec.description.strip(),
        "triggers": spec.triggers,
        "inputs_required": spec.inputs_required,
        "outputs": spec.outputs,
        "runner_compat": spec.runners,
    }

    action = "created"
    for i, s in enumerate(skills):
        if s.get("name") == spec.skill_name:
            if s == entry:
                action = "no-change"
            else:
                skills[i] = entry
                action = "updated"
            break
    else:
        skills.append(entry)

    # Sort by name for stability
    skills.sort(key=lambda x: x.get("name", ""))

    if not dry_run:
        registry_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    return {"action": action, "entry": entry}


def create_script_stubs(skill_dir: Path, scripts: list[str], template_dir: Path, dry_run: bool) -> list[str]:
    created = []
    if not scripts:
        return created

    scripts_dir = skill_dir / "scripts"
    ensure_dir(scripts_dir)

    if "python" in scripts:
        py_tpl = load_text(template_dir / "script_python.template.py")
        py_path = scripts_dir / "main.py"
        write_file(py_path, py_tpl, dry_run)
        created.append(str(py_path))

    if "bash" in scripts:
        sh_tpl = load_text(template_dir / "script_bash.template.sh")
        sh_path = scripts_dir / "main.sh"
        write_file(sh_path, sh_tpl, dry_run)
        if not dry_run:
            os.chmod(sh_path, 0o755)
        created.append(str(sh_path))

    return created


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-name", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--triggers", required=True, help="JSON array of strings")
    p.add_argument("--inputs-required", required=True, help="JSON array of strings")
    p.add_argument("--inputs-optional", default="[]", help="JSON array of strings")
    p.add_argument("--outputs", required=True, help="JSON array of strings")
    p.add_argument("--runners", default='["claude-code","portable"]', help="JSON array of strings")
    p.add_argument("--scripts", default="[]", help='JSON array subset of ["bash","python"]')
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--notes", default="")
    p.add_argument("--output-format", default="")
    p.add_argument("--repo-root", default=".", help="Path to registry repo root")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON result")
    return p.parse_args()


def main() -> None:
    a = parse_args()
    try:
        spec = SkillSpec(
            skill_name=a.skill_name,
            version=a.version,
            description=a.description,
            triggers=json.loads(a.triggers),
            inputs_required=json.loads(a.inputs_required),
            inputs_optional=json.loads(a.inputs_optional),
            outputs=json.loads(a.outputs),
            runners=json.loads(a.runners),
            scripts=json.loads(a.scripts),
            notes=a.notes or None,
            output_format=a.output_format or None,
        )
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in arguments: {e}")

    validate_spec(spec)

    repo_root = Path(a.repo_root).resolve()
    template = load_text(repo_root / "templates" / "SKILL.template.md")
    registry_path = repo_root / "registry.yaml"

    skill_dir = repo_root / "skills" / spec.skill_name
    skill_md_path = skill_dir / "SKILL.md"

    created_files: list[str] = []
    ensure_dir(skill_dir)
    skill_md = render_skill_md(template, spec)
    write_file(skill_md_path, skill_md, a.dry_run)
    created_files.append(str(skill_md_path))

    created_files.extend(create_script_stubs(skill_dir, spec.scripts, repo_root / "templates", a.dry_run))

    reg_update = upsert_registry(registry_path, spec, a.dry_run)

    result = {
        "created_files": created_files,
        "registry_update": reg_update,
        "note": "dry-run (no files written)" if a.dry_run else "applied",
    }

    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print("Created/Updated Files:")
        for f in created_files:
            print(f"- {f}")
        print("\nRegistry Update:")
        print(f"- action: {reg_update['action']}")
        print(f"- name: {reg_update['entry']['name']}")

    sys.exit(0)


if __name__ == "__main__":
    main()
