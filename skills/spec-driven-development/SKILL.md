---
name: spec-driven-development
version: 1.0.0
description: >
  Complete spec-driven development workflow: RFC -> Spec -> Implementation -> BDD Tests -> Fix loop.
  Use for any feature requiring specification-first development with automated testing.

triggers:
  - "spec driven"
  - "spec-driven"
  - "sdd"
  - "rfc workflow"
  - "spec to bdd"
  - "feature development"
  - "tdd workflow"
  - "rfc process"
  - "create feature"
  - "implement rfc"
  - "feature from spec"

inputs:
  required:
    - feature_name
    - feature_description
    - change_level
  optional:
    - rfc_id
    - existing_spec
    - skip_rfc
    - skip_tests
    - app_name
    - test_tags

outputs:
  - rfc_document
  - bdd_tests
  - implementation_files
  - test_results
  - commit_summary

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
  json_output_supported: true
  idempotent: false

routing:
  precedence: enterprise
  project_fallback_allowed: true
---

# Purpose

Guide through the complete spec-driven development workflow for new features: from RFC creation through BDD test generation, implementation, testing, and documentation. Ensures all features follow the project's RFC -> Spec -> Implementation -> Test process with proper quality gates and traceability.

# When to Use

Use when:
- Developing a new feature that requires specification
- Implementing an approved RFC
- Creating a feature with BDD test requirements
- Following the project's spec-driven development process

Do NOT use when:
- Making trivial changes (typos, color changes, simple fixes)
- Debugging existing code (use investigate-bug instead)
- Creating documentation-only changes
- Performing routine maintenance without new features

# Inputs

## Required

- **feature_name**: Name of the feature (kebab-case preferred, e.g., "user-notifications")
- **feature_description**: Clear description of what the feature does and why it's needed
- **change_level**: One of "Small", "Feature", or "Architecture" (determines process rigor)

## Optional

- **rfc_id**: Existing RFC ID if resuming from approved RFC (e.g., "001")
- **existing_spec**: Path to existing spec document if skipping RFC phase
- **skip_rfc**: Set true to skip RFC creation (only if RFC already exists)
- **skip_tests**: Set true to skip BDD test generation (not recommended)
- **app_name**: Django app name if implementing in specific app (e.g., "gprocurement")
- **test_tags**: Comma-separated tags for BDD scenarios (e.g., "@smoke,@critical")

# Procedure

### 1) Determine change level and process scope

Evaluate the change level to determine required process:

| Change Level | RFC Required | BDD Required | ADR Required |
|--------------|--------------|--------------|--------------|
| Small | No | No | No |
| Feature | Yes | Yes | No |
| Architecture | Yes | Yes | Yes |

- If `change_level == "Small"` and not `skip_rfc`: Proceed directly to implementation
- If `change_level == "Feature"` or `"Architecture"`: Follow full workflow

### 2) Create RFC document (if required)

**Only if:** `change_level in ["Feature", "Architecture"]` and not `skip_rfc`

2.1. Determine next RFC number:
```bash
ls -1 .ai/rfc/ | grep -E '^[0-9]{3}' | wc -l
```

2.2. Create RFC from template:
```bash
RFC_NUM=$(printf "%03d" $((N+1)))
cp .ai/rfc/.template.md .ai/rfc/${RFC_NUM}-${feature_name}.md
```

2.3. Fill RFC sections:
- Problem Statement: Clear articulation of the problem
- Proposed Solution: High-level approach
- Alternatives Considered: At least 2 alternatives
- Implementation Plan: Phased approach
- Test Plan: Acceptance criteria and test types
- Security Considerations: Auth, authorization, data validation
- Rollback Plan: How to revert if needed
- Monitoring: Metrics and observability

2.4. Run RFC quality gates:
- [ ] Problem clearly defined
- [ ] At least two alternatives evaluated
- [ ] Implementation phases defined
- [ ] Test strategy documented
- [ ] Monitoring metrics defined
- [ ] Rollback plan documented (if applicable)
- [ ] Security considerations addressed

2.5. Set RFC status to "Approved" after gates pass

### 3) Generate BDD tests from spec

3.1. Create feature file:
```bash
# Determine app location or use shared
FEATURE_PATH="features/${app_name:-shared}/${feature_name}.feature"
```

3.2. Generate feature file structure:
```gherkin
Feature: [Feature Name]

  As a [user role]
  I want [action/feature]
  So that [business value]

  Scenario: [Scenario name]
    Given [precondition]
    And [additional preconditions]
    When [action]
    Then [expected outcome]
    And [additional outcomes]

  Scenario: [Edge case or error path]
    Given [precondition]
    When [action]
    Then [error handling outcome]
```

3.3. Create step definitions if needed:
```bash
# Create feature-specific steps directory
mkdir -p features/${app_name:-shared}/steps
touch features/${app_name:-shared}/steps/${feature_name}_steps.py
```

3.4. Verify Behave configuration:
- Check `behave.ini` for correct settings
- Ensure `features/conftest.py` has Django setup
- Verify test database configuration

### 4) Implement feature following spec

4.1. Determine implementation location:
- If `app_name` provided: Use that Django app
- If new app needed: Create Django app structure
- If shared utility: Use appropriate shared module

4.2. Create implementation files (as needed):
- Models: `apps/${app_name}/models.py` or new model file
- Views: `apps/${app_name}/views/` or new view module
- Forms: `apps/${app_name}/forms.py`
- Templates: `apps/${app_name}/templates/`
- URLs: `apps/${app_name}/urls.py`
- Services: `apps/${app_name}/services/`
- Tests: `apps/${app_name}/tests/`

4.3. Follow project conventions:
- Django: See `.ai/resources/django/guide.md`
- Frontend: See `.ai/resources/frontend/*.md`
- Use HTMX + Vanilla JS patterns from `CLAUDE.md`
- Follow existing code style and structure

4.4. Implement in priority order:
1. Models and migrations
2. Core business logic (services)
3. Views and URL routing
4. Templates and frontend
5. Tests (unit + integration)
6. BDD step implementations

### 5) Run tests and fix issues

5.1. Run Django tests:
```bash
python manage.py test apps.${app_name}.tests
```

5.2. Run BDD tests:
```bash
# Run all features
python manage.py behave

# Run specific feature
behave features/${app_name:-shared}/${feature_name}.feature

# Run with tags
behave --tags=${test_tags:-@smoke}
```

5.3. Fix failures iteratively:
- For Django test failures: Fix code logic
- For BDD failures: Fix code OR update step definitions
- Re-run tests after each fix
- Continue until all tests pass

5.4. Verify quality gates:
- All tests passing
- No console errors or warnings
- BDD scenarios match RFC acceptance criteria
- Code follows style guidelines

### 6) Update backlog and commit

6.1. Update `.ai/backlog.md`:
- Mark feature as DONE
- Add completion date
- Link to RFC and BDD tests

6.2. Extract permanent decisions:
- If architecture changed: Create ADR in `.ai/decisions/`
- Update relevant specs in `.ai/specs/`

6.3. Create commit with message:
```
feat(${app_name}): implement ${feature_name}

Implements RFC ${rfc_id}.

- Key change 1
- Key change 2

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

# Output Format (STRICT)

## Workflow Summary
- **Change Level:** <Small|Feature|Architecture>
- **Process Scope:** <Direct|Full SDD>
- **Feature:** <feature_name>

## Created Documents

### RFC Document
- **Path:** `.ai/rfc/<rfc_id>-<feature_name>.md`
- **Status:** <Draft|Approved|Implemented>
- **Quality Gates:** <PASS|FAIL> (notes if fail)

### BDD Tests
- **Feature File:** `features/<app_name>/<feature_name>.feature`
- **Scenarios:** <count> scenarios defined
- **Step Definitions:** `features/<app_name>/steps/<feature_name>_steps.py`

## Implementation

### Files Created/Modified
- **Models:** <file_path or N/A>
- **Views:** <file_path or N/A>
- **Templates:** <file_path or N/A>
- **URLs:** <file_path or N/A>
- **Services:** <file_path or N/A>
- **Frontend:** <file_path or N/A>

### Tests
- **Unit Tests:** <count> tests, <PASS|FAIL>
- **BDD Tests:** <count> scenarios, <PASS|FAIL>

## Test Results

### Django Tests
```
<test output summary>
```

### BDD Tests
```
<behave output summary>
```

## Actions Taken
1. <action 1>
2. <action 2>
...

## Backlog Updates
- **Backlog Item:** <item_name>
- **Status:** READY -> DONE
- **RFC Link:** `.ai/rfc/<rfc_id>-<feature_name>.md`

## Next Steps
- [ ] Review generated RFC and approve
- [ ] Review BDD scenarios for completeness
- [ ] Run full test suite locally
- [ ] Create pull request
- [ ] Update documentation

# Guardrails

- Never skip RFC for Feature or Architecture level changes
- Always run BDD tests before marking complete
- Never commit failing tests without fix plan
- Follow project security guidelines from CLAUDE.md
- Use Django/Frontend guides for implementation patterns
- Keep step definitions DRY and reusable
- Verify all quality gates before marking RFC as Approved

# Example Invocations

**New feature with full SDD workflow:**
```
Use enterprise skill: spec-driven-development
with:
- feature_name: "user-dashboard"
- feature_description: "Add user dashboard with analytics and activity feed"
- change_level: "Feature"
- app_name: "accounts"
```

**Implement existing RFC:**
```
Use enterprise skill: spec-driven-development
with:
- feature_name: "contract-api"
- feature_description: "REST API for contract CRUD operations"
- change_level: "Feature"
- rfc_id: "002"
- skip_rfc: true
- app_name: "gprocurement"
```

**Small change (direct implementation):**
```
Use enterprise skill: spec-driven-development
with:
- feature_name: "fix-button-color"
- feature_description: "Change submit button color to brand primary"
- change_level: "Small"
- skip_rfc: true
- skip_tests: true
```

# Change Log

## 1.0.0 (2026-03-08)
- Initial version
- Supports full SDD workflow: RFC -> BDD -> Implementation -> Tests
- Handles three change levels: Small, Feature, Architecture
- Integrates with project RFC, BDD, and backlog processes
