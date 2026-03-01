---
name: write-pr
version: 1.0.0
description: >
  Produce a high-quality pull request description with scope, rationale,
  risk, testing evidence, rollout/rollback notes, and reviewer guidance.

triggers:
  - write pr
  - pull request
  - pr description
  - release notes
  - change summary

inputs:
  required:
    - title
    - summary
  optional:
    - context
    - scope
    - related_issues
    - user_impact
    - risk_level
    - test_evidence
    - rollout_plan
    - rollback_plan
    - screenshots
    - migration_notes
    - dependencies
    - reviewers
    - checklist_overrides
    - commit_range
    - dry_run

outputs:
  - pr_title
  - pr_body
  - review_checklist
  - release_notes

compatibility:
  runners:
    - claude-code
    - portable
  scripts:
    - bash

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

Standardize PR quality and review efficiency by producing a complete, auditable PR description that covers:

- What changed and why
- User/system impact
- Risk and mitigation
- Testing evidence
- Rollout/rollback considerations
- Reviewer guidance

# When to Use

Use when:
- Opening a new PR
- Updating a PR description before review
- Preparing a release candidate PR

Do NOT use when:
- The change is trivial and your org explicitly uses “title-only” PRs (rare)

# Inputs

## Required
- **title** — concise PR title
- **summary** — 2–5 bullets describing the change at a high level

## Optional
- **context** — background/problem statement
- **scope** — in-scope vs out-of-scope
- **related_issues** — links/IDs (no raw URLs required)
- **user_impact** — who is affected and how
- **risk_level** — low|medium|high (default: medium if unclear)
- **test_evidence** — commands + results (preferred)
- **rollout_plan** — steps and safety checks
- **rollback_plan** — how to revert safely
- **screenshots** — notes on UI diffs
- **migration_notes** — DB migrations, backfills, data changes
- **dependencies** — feature flags, external services, configs
- **reviewers** — suggested reviewers/teams
- **checklist_overrides** — explicit deviations from standard checklist
- **commit_range** — e.g., `main..feature/my-branch`
- **dry_run** — no file modification

If required inputs are missing, request them before generating output.

# Procedure

### 1) Normalize Inputs
- Ensure title is imperative and specific.
- Convert summary into clear “what/why” bullets.
- If risk_level missing, infer from scope:
  - data migrations/auth/security/payment ⇒ high
  - moderate refactors/UX changes ⇒ medium
  - docs-only/small isolated fix ⇒ low

### 2) Assemble Review-Ready Content
- Explicitly list:
  - Key changes
  - Rationale
  - Testing evidence
  - Risk + mitigations
  - Rollout/rollback
- Keep narrative concise; prefer bullet lists.
- Do not invent evidence. If missing, mark as “Not provided”.

### 3) Produce Checklist
- Include baseline checklist
- Include conditional items (migrations, flags, security)
- If checklist_overrides exist, add “Deviation” section

# Output Format (STRICT)

## PR Title
<title>

## PR Body

### Summary
- ...

### Context
- ...

### Scope
**In scope:**
- ...
**Out of scope:**
- ...

### Changes
- ...

### User Impact
- ...

### Risk
- level: low|medium|high
- risks:
  - ...
- mitigations:
  - ...

### Testing Evidence
- command: ...
  result: PASS/FAIL/Not provided

### Rollout Plan
- ...

### Rollback Plan
- ...

### Migration / Data Notes
- ...

### Dependencies
- ...

### Reviewer Notes
- focus areas:
  - ...
- suggested reviewers:
  - ...

## Review Checklist
- [ ] Scope matches summary
- [ ] Tests executed and results recorded
- [ ] Logging/monitoring considered (if applicable)
- [ ] Feature flags used where appropriate (if applicable)
- [ ] Migration safety reviewed (if applicable)
- [ ] Security implications reviewed (if applicable)
- [ ] Docs/second brain updated (if applicable)

## Release Notes (Optional)
- ...

# Guardrails

- Do not fabricate test results, coverage, metrics, or links.
- Do not include secrets or environment variable values.
- Keep the PR body concise; avoid walls of text.
- Prefer auditable statements (“Not provided” over guessing).

# Example Invocation
Use enterprise skill: write-pr
with:
  title: "Add notification preferences display grouping"
  summary:
    - "Added Display & Behavior tab controls for event types"
    - "Updated backend filter semantics for snoozed/unread"
  risk_level: "medium"
  test_evidence:
    - "python manage.py test apps.app_notifications"
