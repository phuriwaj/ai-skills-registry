# Planner Agent Skill

**Version:** 1.0.0
**Used by:** `.claude/agents/planner.md`
**Purpose:** Detailed step-by-step instructions for breaking an approved RFC
into ordered markdown task files for the Coder Agent.

---

## Step 1 — Validate RFC

Read `.ai/rfc/NNN-{feature}.md`. Verify all quality gates:

- [ ] Problem clearly defined
- [ ] At least two alternatives evaluated
- [ ] Implementation phases defined
- [ ] Test strategy documented
- [ ] Security considerations addressed

If any gate is missing → stop and report exactly which gates are missing.
Do not proceed until RFC is complete.

---

## Step 2 — Read Supporting Documents

In order:
1. `.ai/constitution.md` — architecture rules to embed in tasks
2. `.ai/specs/{feature}.md` — if a spec exists, read it fully
3. Scan `apps/` directory to understand existing patterns for this feature's app

---

## Step 3 — Identify Components

List every component the RFC requires:

| Component | Type | App | Estimated Tasks |
|-----------|------|-----|-----------------|
| {e.g. Workspace model} | Model | workspaces | 1 |
| {e.g. WorkspaceService} | Service | workspaces | 1 |
| {e.g. Middleware} | Middleware | workspaces | 1 |
| {e.g. Views} | Views | workspaces | 1-2 |
| {e.g. Templates} | Templates | workspaces | 1 |
| {e.g. Signup integration} | Integration | accounts | 1 |
| {e.g. Integration tests} | Tests | workspaces | 1 |

Target: **1 task per component**, 1-3 files per task, ~1-2 hours each.

---

## Step 4 — Create Task Directory

```bash
mkdir -p .ai/tasks/{feature-name}
```

Use kebab-case for directory name matching RFC slug.

---

## Step 5 — Write Task Files

For each component, write a task file following this exact template:

**Filename:** `{NN}_{task_name}.md` (zero-padded number, snake_case name)

```markdown
# Task {NN}: {Task Title}

> **Feature:** {Feature Name}
> **RFC:** .ai/rfc/{NNN}-{feature}.md
> **Spec:** .ai/specs/{spec-name}.md
> **Status:** 🔴 TODO

## Objective
{One sentence — what this task accomplishes, nothing more}

## Acceptance Criteria
- [ ] {Specific, testable criterion}
- [ ] {Specific, testable criterion}
- [ ] {N} tests passing

## Files to Create
- `apps/{app}/path/to/file.py` ({N} lines estimated)

## Files to Modify
- `apps/{app}/path/to/existing.py` ({what specifically changes})

## Dependencies
- Task {NN-1}: {title} (reason why)

## Constitution Rules to Follow
- §3.1 Service Layer: {specific rule relevant to this task}
- §4.1 Authentication: {if relevant}
- §3.3 ORM Only: {if relevant}

## Spec Reference
- See {spec-name}.md "{Section Name}" section
- Invariants {XX-YY} must be enforced

## Definition of Done
- [ ] All files created/modified as listed
- [ ] All acceptance criteria met
- [ ] `ruff check apps/{app}/` passes
- [ ] `python manage.py check` passes
- [ ] `python manage.py test apps.{app}.tests.test_{feature}` passes

## Estimated Time
{N} hours

## Notes
{Any important context, gotchas, or references the Coder needs}
```

---

## Step 6 — Write Task Directory README

Create `.ai/tasks/{feature-name}/README.md`:

```markdown
# {Feature Name} Tasks

> **RFC:** .ai/rfc/{NNN}-{feature}.md
> **Spec:** .ai/specs/{spec-name}.md
> **Status:** 🔴 0/{N} tasks complete
> **Started:** {date}

## Task List

| # | Task | Status | Files | Tests |
|---|------|--------|-------|-------|
| 01 | [{title}](./01_{name}.md) | 🔴 TODO | {N} | {N} |
| 02 | [{title}](./02_{name}.md) | 🔴 TODO | {N} | {N} |

**Total:** 0/{N} tasks · 0 files · 0 tests

## Task Dependencies

\`\`\`
01: {title} (foundation)
  ↓
02: {title}
  ↓
03: {title} ──┐
              ├─→ 0N: Integration & Testing
04: {title} ──┘
\`\`\`

## Estimated Total
{N} hours across {N} tasks
```

---

## Step 7 — Final Output

Announce:
```
[PLANNER] Complete.

Tasks created in .ai/tasks/{feature}/
  01_{name}.md — {title}
  02_{name}.md — {title}
  ...
  README.md — task index and dependency graph

Total: {N} tasks, ~{N} hours estimated

Next: Say "Implement" for Coder Agent to begin task 01.
```

---

## Task Granularity Rules

**Good tasks:**
- 1 concept (create model, add service method, implement view)
- 1-3 files created or modified
- 1-2 hours to implement
- Can be verified independently

**Bad tasks (split these up):**
- "Implement {feature}" — too large
- "Phase 1: Foundation" — too vague
- Touches 5+ files — split by component

**Standard task sequence for Django features:**
```
01_create_models.md
02_add_service_layer.md
03_add_{specific_service}.md   (if service is large)
04_add_middleware.md           (if needed)
05_add_views.md
06_add_templates.md
07_integrate_{external}.md     (if cross-app)
08_integration_testing.md
```