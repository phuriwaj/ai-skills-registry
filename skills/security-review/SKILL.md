---
name: security-review
version: 1.0.0
description: >
  Perform a structured application security review of a change set (feature, bugfix,
  refactor, config change) and produce a concrete risk assessment, required controls,
  and verification checklist aligned with OWASP guidance.

triggers:
  - security review
  - appsec review
  - secure review
  - threat review
  - owasp
  - auth check
  - permission review

inputs:
  required:
    - change_summary
    - affected_components
  optional:
    - threat_model_scope
    - data_types
    - authn_authz_changes
    - new_endpoints
    - config_changes
    - dependency_changes
    - storage_changes
    - logging_changes
    - rollout_context
    - compliance_context
    - evidence
    - dry_run

outputs:
  - risk_assessment
  - findings
  - required_controls
  - verification_plan
  - release_gates
  - security_notes

compatibility:
  runners:
    - claude-code
    - portable
  scripts:
    - bash
    - python

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

Provide a repeatable, auditable security review for software changes by:

- Identifying security-relevant change areas
- Mapping risks to concrete controls
- Requiring verification evidence (tests, checks, review items)
- Producing explicit release gates for high-risk changes

This skill is **general-purpose** and works across stacks.

# When to Use

Use when:
- Adding or changing authentication/authorization
- Adding new endpoints/APIs/webhooks
- Handling user input (forms, upload, parsing)
- Touching sensitive data (PII, financial, credentials)
- Changing infrastructure/configuration/secrets handling
- Adding dependencies
- Modifying logging, telemetry, or audit trails

Do NOT use when:
- Pure documentation changes
- Non-executable text changes with no operational impact

# Inputs

## Required
- **change_summary** — concise description of what changed
- **affected_components** — list of modules/services/endpoints touched

## Optional
- **threat_model_scope** — e.g., "public API", "admin-only UI", "internal service"
- **data_types** — e.g., PII, credentials, payment, health, internal-only
- **authn_authz_changes** — what changed in authn/authz (if any)
- **new_endpoints** — list of new/changed routes/endpoints and who can access
- **config_changes** — settings/env/config changes
- **dependency_changes** — new/updated packages/libs/images
- **storage_changes** — DB/schema/object storage changes
- **logging_changes** — new logs/telemetry/audit changes
- **rollout_context** — prod/staging/internal, feature flags, phased rollout
- **compliance_context** — ISO 27001, SOC2, PDPA/GDPR, internal policies
- **evidence** — any test results, scan outputs, design notes
- **dry_run** — no file modification

If required inputs are missing, request them before producing findings.

# Procedure

### 1) Classify Change Risk (Fast Triage)

Determine risk category and drivers:

- **Authn/Authz**: login, sessions, API keys, roles, permissions
- **Input Handling**: forms, query params, JSON bodies, file uploads
- **Data Sensitivity**: PII, credentials, secrets, financial records
- **Exposure**: public internet vs internal vs admin-only
- **Dependencies**: new packages, version bumps, container base images
- **Config/Infra**: headers, TLS, CSP, CORS, secrets management
- **Logging/Audit**: PII leakage, missing audit trails, tamper risks

Assign **overall risk**: low / medium / high.

### 2) Threat Modeling (Lightweight)

Use a minimal STRIDE-style check (only what applies):

- **S**poofing: can identity be faked (token/session/API key)?
- **T**ampering: can data be altered without authorization?
- **R**epudiation: do we have audit trails?
- **I**nformation disclosure: can data leak (logs, responses, storage)?
- **D**enial of service: can endpoints be abused (rate limits, heavy queries)?
- **E**levation of privilege: can users gain higher access?

Record:
- assets
- entry points
- trust boundaries
- abuse cases (top 3)

### 3) Review by Security Control Domains

Check applicable domains and list findings.

### A) Authentication
- MFA/session hardening (if relevant)
- secure token handling (no tokens in URLs)
- session fixation protections
- password reset flows safe (if applicable)

### B) Authorization (Most common failure)
- enforce server-side checks (not UI-only)
- object-level authorization where needed
- deny-by-default for new endpoints
- consistent role mapping

### C) Input Validation & Injection
- validate and normalize inputs at boundary
- protect against SQL/NoSQL injection, command injection
- enforce output encoding where relevant
- SSRF protection for URL fetchers (if any)

### D) CSRF/CORS/Browser Security (if web)
- CSRF for state-changing actions
- CORS only if required and locked down
- security headers (CSP, HSTS, X-Frame-Options as applicable)

### E) Secrets & Sensitive Config
- no secrets committed
- `.env` values never logged
- allowlist-based secret access patterns
- rotation notes for new secrets

### F) Data Protection
- encryption at rest/in transit where needed
- least-privilege DB roles
- safe migrations (backfill considerations)
- retention/deletion expectations

### G) Logging & Monitoring
- no PII in logs by default
- include correlation IDs (if used)
- audit trails for sensitive actions
- alerting hooks for auth failures if relevant

### H) Dependency & Supply Chain
- new dependency justification
- known vulnerability checks (if tool exists)
- pinning strategy and update plan

### I) Abuse & Rate Limiting
- rate limiting for auth & public endpoints
- payload size limits for uploads
- pagination limits and query caps

### 4) Define Required Controls and Release Gates

For each medium/high finding:
- required control(s)
- required verification step(s)
- release gate(s) (must-pass before merge/deploy)

### 5) Verification Plan (Evidence Required)

Prefer evidence:
- unit/integration tests (authz boundaries, validation)
- security scan outputs (if available)
- manual test checklist
- log review checklist

Do not fabricate evidence. Mark “Not provided”.

# Output Format (STRICT)

## Risk Assessment
- overall_risk: low|medium|high
- drivers:
  - ...
- exposure: public|internal|admin-only|mixed
- data_sensitivity: none|internal|PII|credentials|financial|other
- primary_entry_points:
  - ...

## Findings
| ID | Area | Severity | Finding | Evidence | Recommendation |
|----|------|----------|---------|----------|----------------|
| F-1 | Authorization | High | ... | Not provided / <evidence> | ... |

## Required Controls
- authorization:
  - ...
- input_validation:
  - ...
- secrets:
  - ...
- logging:
  - ...
- dependency:
  - ...
- rate_limiting:
  - ...

## Verification Plan
- automated:
  - check: ...
    command: ...
    expected: ...
- manual:
  - ...
- negative_tests:
  - ...

## Release Gates
- [ ] All High severity findings resolved OR explicitly accepted with rationale
- [ ] Authz tests added/updated for new/changed endpoints (if applicable)
- [ ] No secrets or credentials in code/config/logs
- [ ] Security-relevant configs reviewed (CORS/CSRF/headers) if applicable
- [ ] Dependency changes reviewed (licenses/vulns) if applicable

## Security Notes (for PR / ADR)
- summary: ...
- residual_risk: ...
- required_followups:
  - ...

# Guardrails

- Do not claim compliance; report evidence and gaps.
- Do not invent scan results or coverage numbers.
- Never include secrets or `.env` values.
- If you cannot assess due to missing inputs, explicitly list what’s missing.
- Prefer deny-by-default recommendations for access control.

# Example Invocation

Use enterprise skill: security-review
with:
  change_summary: "Added new REST endpoint to delete contracts; updated permissions logic."
  affected_components:
    - "apps/contracts/api.py"
    - "apps/contracts/permissions.py"
  new_endpoints:
    - "DELETE /api/contracts/{id}"
  data_types:
    - "internal"
  rollout_context: "production"