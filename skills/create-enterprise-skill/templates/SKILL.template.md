---
name: {{NAME}}
version: {{VERSION}}
description: >
  {{DESCRIPTION}}

triggers:
{{TRIGGERS_YAML}}

inputs:
  required:
{{INPUTS_REQUIRED_YAML}}
  optional:
{{INPUTS_OPTIONAL_YAML}}

outputs:
{{OUTPUTS_YAML}}

compatibility:
  runners:
{{RUNNERS_YAML}}
  scripts:
{{SCRIPTS_YAML}}

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
  project_fallback_allowed: true
---

# Purpose

(Outcome statement: what this skill accomplishes.)

# When to Use

Use when:
- ...

Do NOT use when:
- ...

{{NOTES}}

# Inputs

## Required
- ...

## Optional
- ...

# Procedure

### 1) Validate inputs
- Ensure required inputs exist.
- Ask for missing inputs before proceeding.

### 2) Token-optimized context loading
- Load only what is required.
- Do not scan entire repositories.

### 3) Execute
- Step-by-step deterministic workflow.
- If scripts are used, reference them explicitly.

### 4) Validate results
- Confirm outputs match required structure.

# Output Format (STRICT)

## Summary
...

## Results
...

## Actions
...

## Verification
...

{{OUTPUT_FORMAT_SECTION}}

# Guardrails

- Never inline secrets.
- Respect policy pointers in `security`.
- Avoid project-specific paths unless this skill is explicitly project-scoped.
- Do not add extra output sections beyond Output Format.

# Example Invocation

Use enterprise skill: {{NAME}}
with:
- <input>: <value>

# Change Log

## {{VERSION}} ({{DATE}})
- Initial version
