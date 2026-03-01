---
name: investigate-bug
version: 1.0.0
description: >
  Systematically triage, reproduce, isolate, and fix a bug with evidence,
  regression protection, and documented resolution.

triggers:
  - bug
  - error
  - exception
  - traceback
  - failing test
  - 500
  - regression
  - IntegrityError
  - DoesNotExist
  - PermissionDenied

inputs:
  required:
    - symptoms
    - expected_behavior
    - environment
  optional:
    - steps_to_reproduce
    - error_message
    - stack_trace
    - logs
    - timeframe
    - suspected_area
    - affected_users
    - recent_changes

outputs:
  - repro_assessment
  - repro_steps
  - isolation_hypothesis
  - root_cause_hypothesis
  - fix_plan
  - verification_plan
  - regression_test_plan
  - resolution_note

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
  project_fallback_allowed: true
---

# Purpose

Produce a deterministic, evidence-based bug investigation that ends with:
1) a reproducible case (or a clear request for missing data),
2) a root cause hypothesis supported by evidence,
3) a fix and verification plan,
4) a regression prevention plan (test),
5) a short resolution note suitable for status logs.

# When to Use

Use when:
- A bug is reported and root cause is unknown.
- There is a failing test or production error requiring structured triage.
- You need consistent evidence, isolation, and verification steps.

Do NOT use when:
- The request is purely “how does X work?” (use documentation/patterns).
- The issue is already fully diagnosed and only needs implementation.

# Inputs

## Required

- **symptoms**: what is observed (user-visible effect, error seen)
- **expected_behavior**: what should happen instead
- **environment**: runtime context (dev/staging/prod, browser/device if UI, user role if relevant)

## Optional

- **steps_to_reproduce**: numbered steps (best effort)
- **error_message**: exact error text
- **stack_trace**: full trace if available
- **logs**: relevant log excerpts (time-bounded)
- **timeframe**: when it started / regression window
- **suspected_area**: app/module/view if known
- **affected_users**: impacted roles/segments (no PII)
- **recent_changes**: related PRs/commits/releases

If required inputs are missing, request them before proceeding beyond triage.

# Procedure

### 1) Capture a minimal bug report (evidence first)

Collect, as available:
- Symptom (what happened)
- Expected behavior
- Steps to reproduce (or note missing)
- Error message / stack trace
- Environment details
- Timeframe and whether regression/new

Use this structure internally:
- Title
- Symptom
- Expected
- Repro steps
- Error / trace
- Environment
- Started when

### 2) Reproduction attempt (local first)

Attempt reproduction in the lowest-risk environment:
- local dev → staging/UAT → production only if explicitly required and safe

If Django:
- Start server and observe logs.
- Prefer deterministic reproduction steps.

If cannot reproduce:
- stop and request missing inputs (steps, logs, environment, timeframe)
- do not guess root cause without evidence

### 3) Isolate the fault domain (fast classification)

Classify into one primary domain:
- Frontend (HTMX/JS/CSS)
- Backend (view/service/model)
- Data (missing/corrupt records, constraints, indexes)
- Configuration (settings/env differences)
- Permissions (role-based access)

Apply this isolation checklist:
- Works with test data? → data domain likely
- Works in dev but not prod? → config/env domain likely
- Works without JS? → frontend domain likely
- Works with superuser? → permission domain likely

### 4) Instrumentation (minimal and reversible)

Add debugging only as needed:
- Prefer logging at boundary points (inputs/outputs), not noisy internals.
- Use breakpoints locally only.
- Avoid print statements in committed code unless explicitly required.

For Django, prefer:
- structured logging or temporary debug logs
- minimal scope + remove after diagnosis

### 5) Check common failure patterns (targeted)

Use only checks relevant to the isolation hypothesis:

- DB integrity/constraints: nulls, FK, unique constraints
- Migration drift: pending migrations, missing schema changes
- Dependency/config drift: versions, settings, feature flags
- Permission checks: user role, object permissions
- Performance side effects: N+1, timeouts, race conditions

### 6) Create a reproduction test plan (regression prevention)

Plan a test that fails before the fix and passes after:
- unit test (preferred)
- integration test if boundaries are involved
- keep it minimal and focused on the bug

Do not implement the test unless requested; produce a plan and file path guidance.

### 7) Root cause hypothesis (evidence-backed)

State:
- hypothesis
- evidence supporting it (repro results, logs, traces, code path)
- alternative hypotheses considered and why rejected
- the smallest fix that resolves the bug

Common root cause families:
- race condition
- N+1 query
- missing null check/guard
- wrong data type/serialization
- missing migration
- template/context mismatch
- permission enforcement mismatch

### 8) Fix plan and verification

Fix plan must include:
- target files/modules
- change summary
- risk note (what might break)
- rollback note if relevant

Verification plan must include:
- test(s) to run
- manual checks
- edge cases

### 9) Document resolution (status-ready)

Produce a resolution note suitable for `.ai/status/<YYYY-MM-DD>.md` containing:
- issue
- root cause
- fix
- files modified (planned)
- verification steps

# Output Format (STRICT)

## Repro Assessment
- reproducible: yes|no|intermittent
- environment_used: <dev|staging|prod|other>
- missing_info_needed: <list or "none">

## Repro Steps
1. ...
2. ...
3. ...

## Isolation Hypothesis
- primary_domain: <frontend|backend|data|config|permissions>
- rationale: ...

## Root Cause Hypothesis
- hypothesis: ...
- evidence:
  - ...
  - ...
- alternatives_considered:
  - ...
- confidence: <low|medium|high>

## Fix Plan
- changes:
  - file: <path>
    summary: <what to change>
- risks:
  - ...
- rollback:
  - ...

## Verification Plan
- automated:
  - command: ...
    expected: ...
- manual:
  - ...
- edge_cases:
  - ...

## Regression Test Plan
- test_type: <unit|integration|e2e>
- suggested_path: <path>
- test_outline:
  - setup: ...
  - execute: ...
  - assert: ...

## Resolution Note (for status log)
### Bug Fix: <Title>
**Issue:** ...
**Root Cause:** ...
**Fix:** ...
**Files Modified:**
- `...`
**Verification:**
- [ ] Unit test added/updated
- [ ] Manual test passed

# Guardrails

- Never include secrets or `.env` values in output.
- Do not instruct production debugging that risks data/security without explicit requirement.
- Do not scan the entire repo; load only files relevant to suspected area.
- Prefer minimal, reversible instrumentation.
- Do not claim root cause without evidence.

# Script Hooks (Optional)

If helpful and allowed, use scripts (loaded only when needed):
- `scripts/django_debug_snapshot.py` to capture environment + basic checks (local only)
- Scripts must support `--dry-run` and `--json` where applicable.

# Example Invocation

Use enterprise skill: investigate-bug
with:
- symptoms: "Users get a 500 when deleting a contract"
- expected_behavior: "Contract is deleted and UI shows success toast"
- environment: "prod, Chrome 122, role=manager"
- steps_to_reproduce: "Open contract → click delete → confirm"
- error_message: "IntegrityError: null value in column ..."
