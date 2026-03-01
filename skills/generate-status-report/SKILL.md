---
name: generate-status-report
version: 1.0.0
description: >
  Generate a structured development status report for a defined period
  using git activity, backlog state, status logs, and test/quality signals.

triggers:
  - status report
  - weekly report
  - sprint report
  - progress report
  - retrospective

inputs:
  required:
    - period_start
    - period_end
  optional:
    - audience
    - reporter_name
    - include_metrics
    - include_quality
    - include_tests
    - focus_area
    - dry_run

outputs:
  - executive_summary
  - completed_items
  - in_progress_items
  - blockers
  - metrics_summary
  - risk_register
  - next_period_goals
  - archive_links

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

Produce a structured, audience-aware development status report for a defined time period using objective signals from:

- Git history
- Backlog state
- `.ai/status/*.md`
- Test results (if provided)
- Code quality tools (if provided)

This skill ensures consistency, traceability, and executive clarity.

# When to Use

Use when:

- Weekly team updates
- Sprint reviews
- Stakeholder reporting
- Executive summaries
- Personal reflection of progress

Do NOT use when:

- No meaningful development occurred
- A single-task summary is sufficient

# Inputs

## Required

- **period_start** — YYYY-MM-DD  
- **period_end** — YYYY-MM-DD  

## Optional

- **audience** — `executive`, `team`, or `self` (default: team)  
- **reporter_name**  
- **include_metrics** — true/false (default: true)  
- **include_quality** — true/false (default: true)  
- **include_tests** — true/false (default: true)  
- **focus_area** — filter by module/app/domain  
- **dry_run** — no file modification  

If dates are missing or invalid, request clarification.

# Procedure

### 1) Collect Objective Signals (Token Efficient)

Use bounded commands only:

```bash
git log --since="<period_start>" --until="<period_end>" --oneline
git log --since="<period_start>" --until="<period_end>" --name-only --pretty=format: | sort -u
```
Count:
- Commits
- Files changed
- High-impact modules touched

Review:
- .ai/backlog.md for DONE items within period
- .ai/status/*.md entries within period
- Architecture decisions created within period

Do not scan full repository history.

### 2) Derive Structured Signals

Extract:

- Completed features  
- Bug fixes  
- In-progress items  
- Blockers  
- Risks  
- Architectural changes  
- Test execution summaries (if available)  
- Code quality signals (if available)  

---

### 3) Adjust Tone by Audience

If `audience = executive`:

- Emphasize business impact  
- Minimize technical depth  
- Highlight risk + mitigation  

If `audience = team`:

- Balanced technical + progress view  
- Include metrics  

If `audience = self`:

- Include lessons + improvement areas  

---

### 4) Generate Structured Report

Always follow the strict format below.

No emojis.  
No unnecessary commentary.  
No speculative metrics.  

---

# Output Format (STRICT)

# Development Status Report

**Period:** <period_start> to <period_end>  
**Reporter:** <reporter_name or N/A>  
**Audience:** <audience>  

---

## Executive Summary

2–4 concise sentences describing:

- Major accomplishments  
- Business or system impact  
- Current stability  
- Primary focus next period  

---

## Completed Features

| Feature | Description | Impact |
|--------|------------|--------|
| ... | ... | ... |

If none: write "None during this period."

---

## Bug Fixes

| Issue | Description | Resolution |
|------|------------|------------|
| ... | ... | ... |

---

## In Progress

| Task | Status | ETA |
|------|--------|-----|
| ... | ... | ... |

---

## Blockers

| Task | Blocker | Owner | Mitigation |
|------|---------|-------|-----------|
| ... | ... | ... | ... |

If none: write "No active blockers."

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Commits | X |
| Files Changed | X |
| Backlog Items Completed | X |
| ADRs Created | X |

Only include this section if `include_metrics = true`.

---

## Test & Quality Signals

### Tests
- Status: PASS / FAIL / Partial  
- Notes: ...  

### Code Quality
- ruff status: clean / issues found  
- Summary: ...  

Include only if enabled.

---

## Architecture Changes

List ADRs created or updated during period.

If none: write "No architecture changes."

---

## Risks & Issues

| Risk | Severity | Status | Mitigation |
|------|----------|--------|------------|
| ... | ... | ... | ... |

If none: write "No major risks identified."

---

## Next Period Goals

1. ...
2. ...
3. ...

---

## Archive References

- Commit range: `<period_start>..<period_end>`  
- Relevant ADRs: `<list or none>`  
- Related backlog items: `<list or none>`  

---

# Guardrails

- Do not fabricate metrics.  
- Do not invent coverage numbers.  
- Do not expose secrets.  
- Do not exaggerate impact.  
- Be honest about blockers and risks.  
- Keep executive summary concise.  
- Never scan entire repository history.  

---

# Example Invocation

Use enterprise skill: generate-status-report  
with:  
- period_start: "2026-02-20"  
- period_end: "2026-02-27"  
- audience: "executive"  
- reporter_name: "PhuriX"
