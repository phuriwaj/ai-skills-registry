# Coder Agent Skill

**Version:** 2.0.0
**Used by:** `.claude/agents/coder.md`
**Purpose:** Workflow steps for implementing tasks from `.ai/tasks/{feature}/`
one at a time. This file contains execution logic only — not patterns or doctrine.
Patterns and doctrine live in `.ai/resources/`.

---

## Mandatory References (Read Before Implementing)

Consult these before writing any code. They are authoritative — if in doubt, follow them:

| Work type | Resource to consult |
|-----------|-------------------|
| Django models, views, services, ORM | `.ai/resources/django/guide.md` |
| HTMX endpoints and partials | `.ai/resources/frontend/htmx.md` |
| Templates and Tailwind styling | `.ai/resources/frontend/tailwind.md` |
| Vanilla JS behavior | `.ai/resources/frontend/vanilla-js.md` |
| Full-stack UI patterns | `.ai/resources/ui/patterns.md` |
| API endpoints | `.ai/resources/api/guide.md` |
| Test writing | `.ai/resources/testing/guide.md` |
| Accessibility | `.ai/resources/frontend/a11y.md` |
| Architecture constraints | `.ai/constitution.md` |

---

## Step 1 — Find Next Task

Scan `.ai/tasks/{feature}/` for the first file with status `🔴 TODO`.

- If `🟡 IN_PROGRESS` found → resume that task
- If all `🟢 DONE` → announce complete, prompt for Tester Agent

Update status to `🟡 IN_PROGRESS` immediately.

---

## Step 2 — Read Task Context

For the current task, read in this order:

1. The task file — objective, acceptance criteria, files, constitution rules, spec reference
2. The `**Specialist:**` label — confirms which agent to delegate to
3. The constitution sections cited in the task
4. The spec sections cited in the task
5. Relevant resource files (see Mandatory References above)

**Never implement without reading the task file fully first.**
**Never invent a pattern — find the existing pattern in resources first.**

---

## Step 3 — Delegate to Specialist

Based on `**Specialist:**` label in the task file:

```
django-specialist-v2          → delegate to django-router
django-enterprise-specialist  → delegate to django-router
frontend-implementation-v2    → delegate to frontend-router
frontend-ui-system-v2         → delegate to frontend-router
frontend-ux-specialist-v2     → delegate to frontend-router
django-router + frontend-router → Phase 1: django-router, Phase 2: frontend-router
```

Pass the task file content and relevant resource paths to the specialist as context.

---

## Step 4 — Run Quality Gates

After specialist completes the task, run every gate listed in the task's
Definition of Done. At minimum:

```bash
ruff check apps/{app}/
python manage.py check
python manage.py makemigrations --check --dry-run   # if model changes
python manage.py test apps.{app}.tests.test_{feature}
```

See `.ai/resources/testing/guide.md` for test running patterns.

If any gate fails:
1. Read the full error — never suppress
2. Fix root cause (re-delegate to specialist if needed)
3. Re-run all gates
4. If still failing after 2 attempts → ⛔ BLOCKED report

---

## Step 5 — Update Task Status

After all gates pass, update the task file:

```markdown
> **Status:** 🟢 DONE
> **Completed:** {date}
```

Update the task directory `README.md` progress tracker.

---

## Step 6 — Announce and Continue

```
✅ Task {N} complete: {title}
Delegated to: {specialist used}
Files modified: {list}
Status: 🟢 DONE
Gates: ruff ✅ · django check ✅ · tests ✅

Moving to Task {N+1}: {title}
```

Repeat from Step 1 for the next 🔴 TODO task.

When all tasks are 🟢 DONE:

```
[CODER] All {N} tasks complete.
Ready for Tester Agent. Say "Run tests" to proceed.
```

---

## Blocked Report Format

```
⛔ BLOCKED
Agent: CODER
Task: {N} — {title}
Specialist: {which agent was used}
Reason: {specific reason}
Attempted: {what was tried}
Need: {what is required to unblock}
```

---

## Forbidden Patterns (Hard Stops)

If any task requires these, stop and report — do not implement:

| Forbidden | Where to check |
|-----------|---------------|
| Business logic in views | constitution §3.1 |
| Raw SQL | constitution §3.3 |
| React, Vue, Angular, Svelte | constitution §2.1 |
| Celery, Redis, RabbitMQ | constitution §2.2 |
| MongoDB, Elasticsearch | constitution §2.3 |
| GraphQL, WebSocket | constitution §2.4 |
| `mark_safe` on user input | constitution §4.3 |
| List views without pagination | constitution §3.3 |