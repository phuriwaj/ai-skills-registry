---
name: create-enterprise-skill
version: 1.0.0
description: >
  Create a new enterprise skill package from templates, update registry.yaml,
  and validate schema/security. Use when adding portable skills to the registry.

triggers:
  - "create skill"
  - "new enterprise skill"
  - "skill template"
  - "add skill to registry"
  - "skill factory"

inputs:
  required:
    - skill_name
    - description
    - triggers
    - inputs_required
    - outputs
  optional:
    - inputs_optional
    - runners
    - scripts
    - output_format
    - notes
    - version
    - dry_run

outputs:
  - created_files
  - registry_update
  - validation_report
  - next_steps

compatibility:
  runners: [claude-code, portable]
  scripts: [bash, python]

security:
  secrets: never-inline
  env_source: .env
  env_allowlist: policy/env_allowlist.txt
  fs_allowlist: policy/fs_allowlist.txt
  network_policy: policy/network_policy.yaml
  pii: forbidden

execution:
  dry_run_supported: true
  json_output_supported: true
  idempotent: true

routing:
  precedence: enterprise
  project_fallback_allowed: false
---

# Purpose

Generate a new enterprise skill package in `skills/<skill-name>/`, using registry templates, and register it in `registry.yaml` with validation and guardrails.

# When to Use

Use when you need to add a new portable enterprise skill to this registry.

Do NOT use for:
- repo-specific project procedures (those belong in a project’s `.ai/skills/`)
- exploratory brainstorming (use normal planning instead)

# Inputs

## Required

- **skill_name**: lowercase letters/digits/hyphens only (e.g., `investigate-bug`)
- **description**: one sentence describing what the skill does and when to use it
- **triggers**: list of keywords/phrases for routing (3–12 recommended)
- **inputs_required**: list of required input names (snake_case)
- **outputs**: list of output artifact names (snake_case)

## Optional

- **inputs_optional**: list of optional input names (snake_case)
- **runners**: list; default `[claude-code, portable]`
- **scripts**: list subset of `[bash, python]`; default `[]`
- **output_format**: override Output Format section; otherwise uses template default
- **notes**: additional constraints/guardrails
- **version**: semver; default `1.0.0`
- **dry_run**: boolean; default `false`

# Procedure

### 1) Validate inputs (strict)
- Enforce naming rules:
  - `skill_name`: `^[a-z0-9]+(-[a-z0-9]+)*$` and max length 64
  - input/output names: `^[a-z][a-z0-9_]*$`
- If validation fails, stop and request corrected inputs.

### 2) Token-optimized loading
Load only the minimum:
- `templates/SKILL.template.md`
- `registry.yaml`
- `policy/*` (for references only; do not embed contents)

Do not scan the entire repository.

### 3) Generate files
Create:
- `skills/<skill_name>/SKILL.md` from template
- `skills/<skill_name>/scripts/` if scripts requested (with template stubs)
- Optional: `skills/<skill_name>/references/` folder (empty, created only if requested)

### 4) Update `registry.yaml` (idempotent)
- If skill exists, update its fields to match provided inputs
- Else append a new entry
- Keep registry sorted by `name` (recommended)

### 5) Validate
Run `scripts/validate_skill.py` on the created SKILL.md:
- YAML frontmatter required fields present
- security pointers exist
- no secrets or `.env` values appear inline
- strict section presence: Purpose, When to Use, Inputs, Procedure, Output Format, Guardrails, Example Invocation

### 6) Produce output
Return outputs in the strict format below.

# Output Format (STRICT)

## Created/Updated Files
- <path>
- <path>

## Registry Update
- action: created|updated|no-change
- entry: {name, description, triggers, inputs_required, outputs, runner_compat}

## Validation Report
- schema: pass|fail (with notes)
- naming: pass|fail (with notes)
- security: pass|fail (with notes)
- token_loading: pass|fail (with notes)

## Next Steps
- bullet list of follow-ups (examples, scripts, tests, release tag)

# Guardrails

- Never embed secrets or values from `.env` into generated files.
- Keep content minimal and reusable; avoid project-specific paths in enterprise skills.
- Do not add new schema fields to registry.yaml unless explicitly requested.
- Do not generate scripts that require network unless the repo policy allows it.
- Prefer deterministic output and clear invocation grammar.

# Script Hooks

Use `python` scripts under:
- `skills/create-enterprise-skill/scripts/create_skill.py`
- `skills/create-enterprise-skill/scripts/validate_skill.py`

# Example Invocation

Use enterprise skill: create-enterprise-skill
with:
- skill_name: "example-skill"
- description: "Summarize CSV files into a standardized report."
- triggers: ["csv", "report", "summarize data"]
- inputs_required: ["input_file"]
- outputs: ["summary", "report_markdown"]
- inputs_optional: ["filters"]
- scripts: ["python"]
- dry_run: true
