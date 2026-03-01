---
name: htmx-endpoint-review
version: 1.0.0
description: >
  Review HTMX endpoints for correct swap targets, OOB updates, CSRF coverage,
  partial rendering, and progressive enhancement to prevent UI drift.

triggers:
  - htmx review
  - endpoint review
  - htmx endpoint
  - swap target
  - oob update
  - partial rendering
  - htmx check

inputs:
  required:
    - endpoint_files
    - expected_behavior
  optional:
    - csrf_exempt
    - uses_oob
    - swap_targets
    - rendering_mode
    - dom_id_strategy

outputs:
  - findings
  - csrf_assessment
  - oob_assessment
  - template_assessment
  - swap_target_assessment
  - recommendations

compatibility:
  runners:
    - claude-code
    - portable
  scripts: []

security:
  secrets: never-inline
  env_source: .env
  env_allowlist: policy/env_allowlist.txt
  fs_allowlist: policy/fs_allowlist.txt
  network_policy: policy/network_policy.yaml
  pii: forbidden

execution:
  dry_run_supported: true
  json_output_supported: false
  idempotent: true

routing:
  precedence: enterprise
  project_fallback_allowed: true
---

# Purpose

Prevent UI drift in HTMX-first applications by systematically reviewing endpoints for:

- Correct `hx-target` / `hx-swap` combinations
- OOB (Out-of-Band) swap consistency
- CSRF protection coverage
- Partial vs full template correctness
- Progressive enhancement compliance
- UUIDv7 safe usage in DOM IDs

HTMX-first architectures are prone to subtle UI bugs from incorrect swap targets, missing OOB updates, or improper partial rendering. This skill catches these issues before production.

# When to Use

Use when:
- Creating or modifying HTMX endpoints
- Reviewing pull requests that touch template/views
- Debugging UI update issues
- Conducting code reviews for HTMX-based features

Do NOT use when:
- Reviewing non-HTMX endpoints (standard API routes)
- Pure frontend changes (HTML/CSS/JS only)
- Static page reviews

# Inputs

## Required

- **endpoint_files** — List of view and template files to review (e.g., `["apps/myapp/views.py", "apps/myapp/templates/myapp/partial.html"]`)
- **expected_behavior** — Description of what the endpoint should do (e.g., "Update notification count in topbar badge")

## Optional

- **csrf_exempt** — Whether the endpoint intentionally bypasses CSRF (default: false)
- **uses_oob** — Whether the endpoint uses OOB swaps (default: auto-detect)
- **swap_targets** — Expected swap targets if known (default: auto-detect from templates)
- **rendering_mode** — "partial" or "full" (default: auto-detect)
- **dom_id_strategy** — How DOM IDs are generated: "uuidv7", "model_pk", "custom" (default: auto-detect)

# Procedure

### 1) Load and parse files

Load the specified files:
- View function: Extract decorators, return statement, context
- Template: Extract HTMX attributes, swap targets, OOB swaps

Do not scan the entire repository.

### 2) CSRF coverage check

Verify:
- [ ] State-changing operations use `@require_POST` or `@require_http_methods`
- [ ] CSRF exempt is intentional and documented
- [ ] Forms include `{% csrf_token %}`
- [ ] AJAX/HTMX requests include CSRF token header

### 3) Swap target analysis

For each `hx-target` in templates:
- [ ] Target selector is specific enough (avoid overly broad targets)
- [ ] Target exists in the DOM at time of swap
- [ ] `hx-swap` modifier matches the use case:
  - `innerHTML` — Replace content (default)
  - `outerHTML` — Replace element
  - `beforebegin` / `afterbegin` / `beforeend` / `afterend` — Insert content
  - `delete` — Remove element
  - `none` — No visual update (trigger only)
- [ ] Swap preserves event listeners if needed (use `hx-swap-oob` for OOB)

### 4) OOB consistency check

For each OOB swap (`hx-swap-oob`):
- [ ] OOB target exists in the DOM (or is conditionally rendered)
- [ ] OOB swap id matches exactly (typos cause silent failures)
- [ ] Multiple OOB swaps are properly separated
- [ ] OOB content type matches target structure (don't swap full response into partial)

### 5) Template rendering correctness

Verify partial vs full template usage:
- [ ] HTMX endpoints return partial templates (fragments, not full pages)
- [ ] Full page endpoints do not have HTMX attributes (or handle both)
- [ ] Template extends base only for full page responses
- [ ] Context includes all required variables for partial render

### 6) Progressive enhancement check

Verify graceful degradation:
- [ ] Links work without JS (use `hx-boost` or fallback actions)
- [ ] Forms submit without JS (standard POST with redirect)
- [ ] Critical paths don't rely solely on HTMX
- [ ] Loading states indicate activity (hx-indicator)

### 7) DOM ID safety (UUIDv7)

Check DOM ID generation:
- [ ] IDs using model PKs are safe from collision (UUIDv7 or similar)
- [ ] No sequential integers in IDs (enumeration risk)
- [ ] Dynamic IDs are properly escaped in templates
- [ ] IDs used as CSS selectors are properly scoped

# Output Format (STRICT)

## Findings

| ID | Category | Severity | Issue | Evidence | Fix |
|----|----------|----------|-------|----------|-----|
| H-1 | Swap Target | High | ... | Line X | ... |
| H-2 | OOB | Medium | ... | Line Y | ... |
| H-3 | CSRF | Low | ... | Line Z | ... |

## CSRF Assessment
- coverage: complete|partial|missing
- notes: ...

## OOB Assessment
- uses_oob: true|false
- oob_count: X
- issues: ...

## Template Assessment
- rendering_mode: partial|full|mixed
- extends_base: true|false
- issues: ...

## Swap Target Assessment
- unique_targets: X
- overbroad_targets: [...]
- complex_selectors: [...]

## Recommendations

Prioritized list:
1. ...
2. ...
3. ...

# Guardrails

- Do not invent findings without evidence.
- Do not suggest major rewrites for minor issues.
- Respect intentional design decisions (document exceptions).
- Focus on bugs that cause UI drift, not style preferences.

# Example Invocation

Use enterprise skill: htmx-endpoint-review
with:
  - endpoint_files: |
      ["apps/app_notifications/views.py", "apps/app_notifications/templates/partials/notification_row.html"]
  - expected_behavior: "Mark notification as read and update the row style plus unread badge count"
  - uses_oob: true
