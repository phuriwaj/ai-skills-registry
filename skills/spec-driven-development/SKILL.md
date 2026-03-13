---
name: spec-driven-development
version: 2.0.0
description: >
  Automated spec-driven development workflow with agent orchestration: RFC -> Planning -> Implementation -> Testing -> Review -> Finalization.
  Automatically sequences PLANNER, CODER, TESTER, and REVIEWER agents to implement features from specification.

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
  - "automated implementation"
  - "full workflow"

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

orchestration:
  mode: sequential
  stop_on_error: true
  continue_on_failure: false
  max_retries_per_step: 2

  phases:
    - name: validate_input
      type: validation
      required_inputs:
        - feature_name
        - feature_description
        - change_level
      validation_rules:
        - feature_name: "kebab-case, no spaces"
        - change_level: "one_of: Small, Feature, Architecture"
        - feature_description: "min_length: 10"

    - name: determine_process_scope
      type: decision
      agent: planner
      decision_logic:
        - if: change_level == "Small"
          then:
            skip_rfc: true
            skip_bdd: true
            process_type: direct
        - if: change_level == "Feature"
          then:
            skip_rfc: false
            skip_bdd: false
            process_type: full
        - if: change_level == "Architecture"
          then:
            skip_rfc: false
            skip_bdd: false
            create_adr: true
            process_type: full
      output:
        process_scope: "determined scope"
        required_phases: "list of phases to execute"

    - name: create_or_validate_rfc
      type: conditional
      condition: not skip_rfc
      agent: planner
      inputs:
        feature_name: from_input
        feature_description: from_input
        change_level: from_input
        rfc_template: ".ai/rfc/.template.md"
        rfc_directory: ".ai/rfc/"
      actions:
        - if: rfc_id not provided
          then:
            - determine_next_rfc_number
            - create_rfc_from_template
            - fill_rfc_sections
            - run_rfc_quality_gates
            - set_rfc_status_approved
        - if: rfc_id provided
          then:
            - validate_existing_rfc
            - ensure_rfc_approved
      outputs:
        rfc_path: ".ai/rfc/{rfc_id}-{feature_name}.md"
        rfc_status: "Approved"
        quality_gates: "pass/fail report"
      success_criteria:
        - RFC exists at rfc_path
        - RFC status is "Approved"
        - All quality gates pass
      on_failure:
        - report: "RFC creation failed"
        - stop: true

    - name: create_task_breakdown
      type: planning
      agent: planner
      inputs:
        rfc_path: from_previous_phase
        feature_name: from_input
        app_name: from_input
      actions:
        - read_rfc_document
        - analyze_codebase_impact
        - break_feature_into_tasks
        - identify_task_dependencies
        - create_task_markdown_files
        - create_task_readme_with_dependency_graph
      outputs:
        task_directory: ".ai/tasks/{feature_name}/"
        task_files: "list of created task files"
        task_count: "number of tasks"
        dependency_graph: "mermaid or text representation"
      success_criteria:
        - task_directory exists
        - task_count > 0
        - README.md with dependency graph created
        - each task references RFC and constitution
      on_failure:
        - report: "Task breakdown failed"
        - stop: true

    - name: implement_tasks
      type: implementation
      agent: coder
      inputs:
        task_directory: from_previous_phase
        feature_name: from_input
        constitution: ".ai/constitution.md"
        django_guide: ".ai/resources/django/guide.md"
      actions:
        - for_each: task in task_files (dependency order)
          execute:
            - read_task_file
            - read_referenced_spec_sections
            - implement_only_what_task_specifies
            - update_task_status_to_in_progress
            - follow_django_patterns
            - follow_javascript_patterns
            - run_quality_gates_after_task
            - update_task_status_to_done
            - report_completion
      outputs:
        implemented_files: "list of modified/created files"
        completed_tasks: "list of task IDs"
        quality_gate_results: "ruff, check, test results"
      success_criteria:
        - all tasks marked DONE
        - ruff check passes
        - python manage.py check passes
        - python manage.py test passes
      on_failure:
        - report: "Implementation failed"
        - retry: true
        - max_retries: 2

    - name: generate_bdd_tests
      type: testing
      agent: tester
      inputs:
        rfc_path: from_phase: create_or_validate_rfc
        feature_name: from_input
        app_name: from_input
        test_tags: from_input
      actions:
        - generate_bdd_feature_file
        - create_step_definitions
        - verify_behave_configuration
      outputs:
        feature_file: "features/{app_name}/{feature_name}.feature"
        step_definitions: "features/{app_name}/steps/{feature_name}_steps.py"
        scenario_count: "number of scenarios"
      success_criteria:
        - feature file created
        - step definitions created
        - scenarios cover RFC acceptance criteria
      on_failure:
        - report: "BDD generation failed"
        - continue: true  # BDD may already exist

    - name: run_tests
      type: testing
      agent: tester
      inputs:
        feature_name: from_input
        app_name: from_input
        test_tags: from_input
      actions:
        - run_unit_tests
        - run_bdd_tests
        - collect_coverage_metrics
        - report_failures_with_file_and_line
      outputs:
        unit_test_results: "pytest output"
        bdd_test_results: "behave output"
        coverage_report: "coverage percentage"
        failing_tests: "list of failures with context"
      success_criteria:
        - unit tests pass (90%+ coverage for services)
        - bdd scenarios pass (100% of user-facing features)
        - no critical failures
      on_failure:
        - report: "Tests failed"
        - pass_to: coder  # Send back to coder for fixes
        - retry: true
        - max_retries: 2

    - name: review_implementation
      type: review
      agent: reviewer
      inputs:
        rfc_path: from_phase: create_or_validate_rfc
        implemented_files: from_phase: implement_tasks
        test_results: from_phase: run_tests
        constitution: ".ai/constitution.md"
      checks:
        - category: security
          rules:
            - all_views_use_authentication
            - no_raw_sql
            - no_sensitive_data_in_logs
            - all_post_forms_have_csrf_token
            - input_validated_before_use
            - tier_elevation_prevention
          severity: CRITICAL
          block_on_failure: true
        - category: architecture
          rules:
            - business_logic_in_services_not_views
            - service_methods_are_static
            - no_circular_imports
            - no_n_plus_one_queries
            - all_list_views_paginate
            - follows_naming_conventions
          severity: CRITICAL
          block_on_failure: true
        - category: code_quality
          rules:
            - no_dead_code
            - no_commented_out_blocks
            - functions_do_one_thing
            - no_exception_suppression
            - ruff_check_passes
            - manage_py_check_passes
          severity: WARNING
          block_on_failure: false
        - category: rfc_compliance
          rules:
            - all_acceptance_criteria_implemented
            - test_strategy_documented
            - security_considerations_addressed
            - rollback_plan_exists
          severity: CRITICAL
          block_on_failure: true
      outputs:
        verdict: "APPROVED or REJECTED"
        issues_found: "list of CRITICAL and WARNING issues"
        review_summary: "detailed report"
      success_criteria:
        - no CRITICAL issues
        - verdict == APPROVED
      on_failure:
        - report: "Review failed - see issues"
        - pass_to: coder  # Send back to coder for fixes
        - retry: true
        - max_retries: 2

    - name: finalize_feature
      type: finalization
      agent: planner
      inputs:
        rfc_id: from_phase: create_or_validate_rfc
        feature_name: from_input
        rfc_path: from_phase: create_or_validate_rfc
        verdict: from_phase: review_implementation
      actions:
        - extract_permanent_decisions_to_spec
        - update_backlog_to_done
        - update_rfc_status_to_implemented
        - create_commit_summary
      outputs:
        spec_path: ".ai/specs/{feature_name}.md"
        backlog_status: "DONE"
        commit_message: "formatted commit message"
        completion_date: "current timestamp"
      success_criteria:
        - spec extracted
        - backlog updated
        - RFC status updated
      on_failure:
        - report: "Finalization failed - manual intervention required"
        - continue: false

---

# Purpose

**Automated** spec-driven development workflow that sequences PLANNER, CODER, TESTER, and REVIEWER agents to implement features from RFC to production. No manual agent invocation required - just say "implement rfc 017" and the system orchestrates the entire workflow automatically.

# When to Use

Use when:
- Implementing an RFC from start to finish
- Developing a new feature that requires full workflow
- Running complete spec-driven development with automation
- Wanting hands-off implementation with agent orchestration

Do NOT use when:
- Making trivial changes (typos, color changes, simple fixes) → use direct implementation
- Debugging existing code → use investigate-bug skill instead
- Creating documentation-only changes → use doc-skills:doc
- Only planning tasks → use agent planner directly
- Only reviewing code → use agent reviewer directly
- Only running tests → use agent tester directly

# How Automation Works

**Traditional approach** (manual agent invocation):
```
User: "Use agent planner to create tasks for RFC 017"
User: "Implement task 01"
User: "Use agent tester to run tests"
User: "Use agent reviewer to review implementation"
```

**With spec-driven-development v2.0** (automatic):
```
User: "Implement RFC 017"
      ↓
System automatically sequences:
  1. PLANNER validates RFC, creates tasks
  2. CODER implements each task (with retries)
  3. TESTER generates BDD, runs tests (with retries)
  4. REVIEWER checks compliance (with retries)
  5. PLANNER finalizes (extracts to spec, updates backlog)
      ↓
Done! Feature implemented, tested, reviewed, and finalized.
```

# When to Use Agents Directly vs This Skill

| Situation | Use This | Use Direct |
|-----------|----------|-----------|
| Full feature implementation | ✅ This skill | ❌ |
| Task breakdown only | ❌ | ✅ `agent planner` |
| Code fix only | ❌ | ✅ `agent coder` |
| Test run only | ❌ | ✅ `agent tester` |
| Security review only | ❌ | ✅ `agent reviewer` |
| RFC creation only | ❌ | ✅ `create-rfc` skill |
| Bug investigation | ❌ | ✅ `investigate-bug` skill |

# Inputs

## Required

- **feature_name**: Name of the feature (kebab-case preferred, e.g., "user-notifications")
- **feature_description**: Clear description of what the feature does and why it's needed
- **change_level**: One of "Small", "Feature", or "Architecture" (determines process rigor)

## Optional

- **rfc_id**: Existing RFC ID if resuming from approved RFC (e.g., "017")
- **existing_spec**: Path to existing spec document if skipping RFC phase
- **skip_rfc**: Set true to skip RFC creation (only if RFC already exists)
- **skip_tests**: Set true to skip BDD test generation (not recommended)
- **app_name**: Django app name if implementing in specific app (e.g., "gprocurement")
- **test_tags**: Comma-separated tags for BDD scenarios (e.g., "@smoke,@critical")

# Invocation

## Automatic (Recommended)

Just use one of the trigger phrases:

```
"Implement RFC 017"
"Use spec-driven development for user notifications"
"Create feature: contract-api using sdd"
```

The system will automatically:
1. Load the spec-driven-development skill
2. Parse your inputs
3. Orchestrate all agents in sequence
4. Report progress at each phase
5. Provide final summary

## Manual (Advanced)

If you need more control:

```
Use enterprise skill: spec-driven-development
with:
  feature_name: "user-notifications"
  feature_description: "Add real-time notifications to user dashboard"
  change_level: "Feature"
  app_name: "accounts"
  rfc_id: "018"
  skip_rfc: true
```

# Procedure (Reference)

**Note:** This section documents what the orchestration does automatically. You don't need to run these steps manually - the skill handles it. Use this for understanding what's happening under the hood.

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

6.1. Update `.ai/backlog-new.md`:
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

## Full automation (just say the magic words)

```
User: "Implement RFC 017"

[spec-driven-development] Starting automated workflow...
[PLANNER] Reading RFC 017...
[PLANNER] Creating task breakdown...
[CODER] Implementing 5 tasks...
[TESTER] Generating BDD tests...
[TESTER] Running tests (12/12 passing)...
[REVIEWER] Checking compliance...
[REVIEWER] ✅ APPROVED
[PLANNER] Finalizing... Spec extracted, backlog updated
[spec-driven-development] 🎉 COMPLETE in 8 minutes
```

## Manual invocation with specific inputs

```
Use enterprise skill: spec-driven-development
with:
  feature_name: "user-dashboard"
  feature_description: "Add user dashboard with analytics and activity feed"
  change_level: "Feature"
  app_name: "accounts"
```

## Implement existing RFC (skip RFC creation)

```
Use enterprise skill: spec-driven-development
with:
  feature_name: "contract-api"
  feature_description: "REST API for contract CRUD operations"
  change_level: "Feature"
  rfc_id: "002"
  skip_rfc: true
  app_name: "gprocurement"
```

## Small change (direct implementation, skips most phases)

```
Use enterprise skill: spec-driven-development
with:
  feature_name: "fix-button-color"
  feature_description: "Change submit button color to brand primary"
  change_level: "Small"
  skip_rfc: true
  skip_tests: true
```

# Progress Monitoring

During execution, the skill reports progress at each phase:

```
[spec-driven-development] Phase 3/9: create_or_validate_rfc
[PLANNER] Validating RFC 017...
[PLANNER] ✅ RFC approved, quality gates passed
[spec-driven-development] Phase 4/9: create_task_breakdown
```

If a phase fails, the system:
1. Reports the failure with context
2. Passes to the appropriate agent for fixes (coder/tester)
3. Retries up to 2 times
4. Stops if max retries exceeded

# Error Handling

Each phase has `on_failure` handlers:

| Phase | On Failure | Action |
|-------|-----------|--------|
| create_or_validate_rfc | Any error | Stop workflow, report RFC issues |
| create_task_breakdown | Any error | Stop workflow, report task issues |
| implement_tasks | Code/test failures | Retry (max 2x), pass to coder |
| generate_bdd_tests | Generation errors | Continue (BDD may exist) |
| run_tests | Test failures | Retry (max 2x), pass to coder |
| review_implementation | CRITICAL issues | Retry (max 2x), pass to coder |
| finalize_feature | Any error | Report, manual intervention |

# Change Log

## 2.0.0 (2026-03-13)
- **BREAKING CHANGE:** Now orchestrates agents automatically
- Added `orchestration` section with sequential phase execution
- PLANNER agent creates task breakdowns from RFCs
- CODER agent implements tasks with retry logic
- TESTER agent generates BDD and runs tests
- REVIEWER agent validates against constitution
- Automatic pass-through between phases on failure
- Progress reporting at each phase
- Added more trigger phrases for easier invocation
- Added progress monitoring section
- Added error handling documentation

## 1.0.0 (2026-03-08)
- Initial version
- Supports full SDD workflow: RFC -> BDD -> Implementation -> Tests
- Handles three change levels: Small, Feature, Architecture
- Integrates with project RFC, BDD, and backlog processes
