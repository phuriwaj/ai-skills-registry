# Tester Agent Skill

**Version:** 2.0.0
**Used by:** `.claude/agents/tester.md`
**Purpose:** Workflow steps for generating tests and running quality gates.
This file contains execution logic only — not patterns or doctrine.
Test patterns and templates live in `.ai/resources/testing/guide.md`.

---

## Mandatory References (Read Before Testing)

| What you need | Resource |
|---------------|----------|
| Test patterns, factories, base classes | `.ai/resources/testing/guide.md` |
| HTMX request testing patterns | `.ai/resources/testing/guide.md` §HTMX Request Tests |
| Coverage targets (90/80/70%) | `.ai/resources/testing/guide.md` §Testing Checklist |
| BDD scenario writing | `.ai/resources/workflows/build_feature.md` |
| Django test commands | `.ai/resources/testing/guide.md` §Running Tests |

---

## Step 1 — Read Feature Context

1. Read the RFC: `.ai/rfc/NNN-{feature}.md` — find acceptance criteria
2. Read task files in `.ai/tasks/{feature}/` — find expected test counts
3. Check `**Specialist:**` labels — know which resources were used
4. Read `.ai/resources/testing/guide.md` — follow its patterns for all test writing

---

## Step 2 — Generate BDD Feature File

Write to `features/{app}/{feature}.feature`.

Follow the BDD format and scenario structure in `.ai/resources/testing/guide.md`.

Rules:
- Every user-facing behaviour from RFC acceptance criteria → one scenario
- Include happy path AND error cases
- Background for shared setup across scenarios
- Plain language only — no implementation details

---

## Step 3 — Generate Unit Tests

Write to `apps/{app}/tests/test_{feature}.py`.

Follow all test patterns from `.ai/resources/testing/guide.md`:
- Model tests → use Model Tests pattern
- Service tests → use Service Tests pattern
- View tests → use View Tests pattern
- HTMX tests → use HTMX Request Tests pattern

Coverage targets (from testing guide):
- Service Layer: 90%+
- Models: 80%+
- Views: 70%+
- BDD Scenarios: 100% of user-facing features

---

## Step 4 — Run Full Quality Gate Suite

Run every gate. Do not skip any. Capture full output.

```bash
# Code style
ruff check .
black --check .

# Django system checks
python manage.py check

# Migration safety
python manage.py makemigrations --check --dry-run

# Unit tests
python manage.py test apps.{app}.tests

# BDD tests
python manage.py behave
behave features/{app}/{feature}.feature --no-capture
```

---

## Step 5 — Build Report

```
🧪 Test Results — {feature}
━━━━━━━━━━━━━━━━━━━━━━━━━━
Quality Gates:
  ruff check       ✅ / ❌
  black check      ✅ / ❌
  django check     ✅ / ❌
  migration check  ✅ / ❌

Test Suite:
  Unit tests:  {N} passed, {N} failed, {N} errors
  BDD tests:   {N} scenarios passed, {N} failed
```

If failures exist:
```
❌ Failures:
  {test_class}.{test_name}
  → {file}:{line}
  Error: {exact error message}
  Fix needed: {what the Coder Agent needs to do}
```

---

## Step 6 — Route Result

All gates pass:
```
[TESTER] All quality gates pass. ✅
Ready for Reviewer Agent. Say "Review" to proceed.
```

Any gate fails:
```
[TESTER] {N} failures found. Sending back to Coder Agent.
{failure list}
Coder Agent: fix the listed failures and say "Run tests" again.
```