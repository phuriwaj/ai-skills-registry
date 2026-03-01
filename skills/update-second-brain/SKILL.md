---
name: update-second-brain
version: 1.0.0
description: >
  Update the project knowledge base after a development session by marking
  completed backlog items, appending a daily status entry, and creating ADRs
  when architectural decisions occurred.

triggers:
  - update second brain
  - end session
  - log session
  - update status
  - session summary

inputs:
  required:
    - session_summary
  optional:
    - commits
    - test_results
    - architecture_changes
    - remaining_work
    - usage_example
    - date_override
    - dry_run

outputs:
  - backlog_updates
  - status_entry_path
  - adr_created
  - commit_recommendation

compatibility:
  runners: [claude-code, portable]
  scripts: [bash]

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

Maintain institutional memory by updating the structured knowledge system
after each development session without rewriting historical records.

This skill enforces:
- append-only status logs
- backlog state integrity
- architecture decision traceability
- deterministic documentation structure

# When to Use

Use when:
- A feature was implemented
- A bug was fixed
- Tests were added or modified
- Configuration changed
- Architecture changed
- A session ended

Do NOT use when:
- No code changes occurred
- Only exploratory research was performed

# Inputs

## Required

- **session_summary** — One concise sentence describing what was accomplished.

## Optional

- **commits** — List of commit hashes or allow auto-detection from git log
- **test_results** — Structured results summary
- **architecture_changes** — Description of architectural decisions made
- **remaining_work** — Items for next session
- **usage_example** — Code snippet to include in status
- **date_override** — YYYY-MM-DD (defaults to today)
- **dry_run** — If true, do not modify files

# Procedure

### 1) Capture Session Evidence (Token Efficient)

Collect:
```bash
git status
git diff --staged
git log --oneline -5
```

Identify:
- Completed backlog items
- Modified files
- Commit hashes
- Test execution evidence (if available)

Do not scan entire repository history.

### 2) Update Backlog (State Transition Only)

Rules:
- Change matching items to `[DONE]`
- Add `Completed: YYYY-MM-DD`
- Add `Commit: <short-hash>`
- Move to "Recently Completed" section if applicable
- DO NOT delete old entries
- DO NOT rewrite historical content

Format:
```markdown
### [DONE] Feature Name
**Completed:** YYYY-MM-DD
**Commit:** <short-hash>

Brief description of what was done.
```

### 3) Append Daily Status Entry

Target file: `.ai/status/<YYYY-MM-DD>.md`

Rules:
- If file exists → append
- If file does not exist → create
- Never rewrite previous content
- Never remove past sessions

Use strict structure:
```markdown
# Development Session - YYYY-MM-DD

## Summary
<session_summary>

## Commits
- <hash> - message

## Changes Made
- Bullet summary

## Files Modified
- `path` — short description

## Testing Performed
- test_name — PASS/FAIL

## Architecture Changes
<if applicable>

## Remaining Work
<remaining_work>

## Notes
<observations>
```

### 4) Create ADR (If Architecture Changed)

If `architecture_changes` provided:

Create new file: `.ai/decisions/YYYY-MM-DD-<slug>.md`

Rules:
- Never modify old ADRs
- Status defaults to "Accepted"
- Keep structure consistent
- Use deterministic filename slug

Template:
```markdown
# ADR: Decision Title

**Date:** YYYY-MM-DD
**Status:** Accepted

## Context
What problem are we solving?

## Decision
What are we doing?

## Rationale
Why this approach? What alternatives were considered?

## Consequences

### Positive
- ...

### Negative
- ...

### Affected Components
- ...
```

### 5) Integrity Rules (Critical)

- Append-only to status logs
- No rewriting historical sessions
- No deletion of backlog entries
- ADRs are immutable once created
- Only update architecture.md if core stack changed
- Do not fabricate commit hashes
- Do not include secrets or environment variables

# Output Format (STRICT)

## Backlog Updates
```
items_marked_done:
  - "<title>" (commit: <hash>)

  none (if no changes)
```

## Status Entry
```
path: .ai/status/YYYY-MM-DD.md
created_or_appended: created|appended
```

## ADR
```
created: yes|no
path: <path or none>
```

## Commit Recommendation
```
message: "docs: update second brain for YYYY-MM-DD"
include_files:
  - .ai/backlog.md
  - .ai/status/YYYY-MM-DD.md
  - .ai/decisions/... (if created)
```

# Guardrails

- Never delete historical content
- Never rewrite previous session entries
- Do not fabricate commit hashes
- If git state is unavailable, request confirmation
- Do not expose secrets
- This skill should be the final step in a development session

# Example Invocation

Use enterprise skill: update-second-brain
with:
  session_summary: "Implemented email notification preference panel"
  remaining_work: "Add email provider fallback"
