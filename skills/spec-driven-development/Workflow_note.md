Complete Workflow: From Backlog to Done                                                            
                                                   
  Based on your .ai/ and .claude/ setup, here's the complete workflow:                               
                                                                                                     
  ---
  📊 Overview Diagram                                                                                
                  
  ┌─────────────────────────────────────────────────────────────────────┐
  │                    BACKLOG (.ai/backlog-new.md)                         │
  │  Source of truth for executable work. Claude reads this to know     │
  │  what to build next.                                                │
  └─────────────────────────────────────────────────────────────────────┘
                                      │
                      ┌───────────────┴───────────────┐
                      │                               │
                [Small Change]                 [Feature/Architecture]
                      │                               │
                      ↓                               ↓
             ┌─────────────────┐              ┌──────────────┐
             │ DIRECT TO WORK  │              │ RFC REQUIRED │
             │ (typo, color)   │              │ (.ai/rfc/)   │
             └─────────────────┘              └──────────────┘
                                                      │
                      ┌───────────────────────────────┤
                      │                               │
                [Feature]                       [Architecture]
                      │                               │
                      ↓                               ↓
             ┌──────────────┐               ┌─────────────────┐
             │ RFC → Spec   │               │ RFC → ADR    	  │
             │ (.ai/specs/) │               │ (.ai/decisions/)│
             └──────────────┘               └─────────────────┘
                      │                               │
                      └───────────────┬───────────────┘
                                      ↓
                      ┌───────────────────────────────┐
                      │   RFC APPROVED?               │
                      │   Update status: Approved     │
                      └───────────────────────────────┘
                                      │
                                      ↓
  ┌─────────────────────────────────────────────────────────────────────┐
  │              AGENT PIPELINE (.claude/agents/)                       │
  ├─────────────────────────────────────────────────────────────────────┤
  │                                                                     │
  │  ┌──────────────────────────────────────────────────────────────┐   │
  │  │  1. PLANNER AGENT                                            │   │
  │  │  Trigger: "Plan {feature}", "create tasks", "implement RFC"  │   │
  │  │  Reads: RFC (.ai/rfc/NNN-*.md), Spec (.ai/specs/)            │   │
  │  │  Output: .ai/tasks/{feature}/ (01_*.md, 02_*.md...)          │   │
  │  │  Creates: Task files + README.md with dependencies           │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  │                                   │                                 │
  │                                   ↓                                 │
  │  ┌──────────────────────────────────────────────────────────────┐   │
  │  │  2. CODER AGENT                                              │   │
  │  │  Trigger: "Implement", "Execute tasks"                       │   │
  │  │  Reads: Task files one by one                                │   │
  │  │  Routes to: django-specialist-v2, frontend-router, etc.      │   │
  │  │  Output: Working code + tests                                │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  │                                   │                                 │
  │                                   ↓                                 │
  │  ┌──────────────────────────────────────────────────────────────┐   │
  │  │  3. TESTER AGENT                                             │   │
  │  │  Trigger: "Run tests", "Validate"                            │   │
  │  │  Runs: Quality gates (ruff, black, django check, tests)      │   │
  │  │  Output: Test results + BDD scenarios                        │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  │                                   │                                 │
  │                                   ↓                                 │
  │  ┌──────────────────────────────────────────────────────────────┐   │
  │  │  4. REVIEWER AGENT                                           │   │
  │  │  Trigger: "Review", "Check constitution"                     │   │
  │  │  Reads: .ai/constitution.md, resources, changed files        │   │
  │  │  Output: Approved/Rejected with specific issues              │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                      [APPROVED]              [REJECTED]
                          │                       │
                          ↓                       ↓
              ┌───────────────────┐      ┌──────────────┐
              │ Update Backlog    │      │ Back to CODER│
              │ Status: DONE      │      │ Fix issues   │
              │ Add commit hash   │      └──────────────┘
              └───────────────────┘
                          │
                          ↓
  ┌─────────────────────────────────────────────────────────────────────┐
  │                      FINAL STEPS                                    │
  ├─────────────────────────────────────────────────────────────────────┤
  │  1. Generate PR description (.ai/tasks/{feature}/PR_DESCRIPTION.md) │
  │  2. Commit all changes                                              │
  │  3. Push to origin                                                  │
  │  4. Update status files (.ai/status/YYYY-MM-DD.md, YYYY-MM.md)      │
  │  5. Extract permanent decisions → .ai/specs/ or .ai/decisions/      │
  └─────────────────────────────────────────────────────────────────────┘

  ---
  📋 Step-by-Step Instructions

  Phase 1: From Backlog to RFC

  ┌──────┬────────────────────────┬───────────────────────────────────┬──────────────────────────┐
  │ Step │         Action         │          Command/Trigger          │          Output          │
  ├──────┼────────────────────────┼───────────────────────────────────┼──────────────────────────┤
  │ 1    │ Pick item from backlog │ Claude reads .ai/backlog-new.md       │ Find [READY] item        │
  ├──────┼────────────────────────┼───────────────────────────────────┼──────────────────────────┤
  │ 2    │ Check if RFC exists    │ Look in .ai/rfc/                  │ If yes → skip to Phase 2 │
  ├──────┼────────────────────────┼───────────────────────────────────┼──────────────────────────┤
  │ 3    │ Create RFC             │ Use spec-driven-development skill │ .ai/rfc/NNN-feature.md   │
  ├──────┼────────────────────────┼───────────────────────────────────┼──────────────────────────┤
  │ 4    │ Fill RFC sections      │ Use .ai/rfc/.template.md          │ Complete RFC             │
  ├──────┼────────────────────────┼───────────────────────────────────┼──────────────────────────┤
  │ 5    │ Self-approve           │ Review quality gates              │ Status: Approved         │
  ├──────┼────────────────────────┼───────────────────────────────────┼──────────────────────────┤
  │ 6    │ Update backlog         │ Add RFC link                      │ [READY] item now has RFC │
  └──────┴────────────────────────┴───────────────────────────────────┴──────────────────────────┘

  Phase 2: From RFC to Tasks

  ┌──────┬──────────────────────┬─────────────────────────────────────────┬──────────────────────┐
  │ Step │        Action        │             Command/Trigger             │        Output        │
  ├──────┼──────────────────────┼─────────────────────────────────────────┼──────────────────────┤
  │ 7    │ Activate PLANNER     │ "Plan {feature}" or "Implement RFC      │ .ai/tasks/{feature}/ │
  │      │                      │ {NNN}"                                  │                      │
  ├──────┼──────────────────────┼─────────────────────────────────────────┼──────────────────────┤
  │ 8    │ PLANNER creates      │ 01_*.md, 02_*.md...                     │ Task files with deps │
  │      │ tasks                │                                         │                      │
  ├──────┼──────────────────────┼─────────────────────────────────────────┼──────────────────────┤
  │ 9    │ PLANNER creates      │ Task table + dependency graph           │ Overview file        │
  │      │ README               │                                         │                      │
  └──────┴──────────────────────┴─────────────────────────────────────────┴──────────────────────┘

  Phase 3: Implementation Loop

  ┌──────┬───────────────────┬─────────────────────────────┬───────────────────────────┐
  │ Step │      Action       │       Command/Trigger       │          Output           │
  ├──────┼───────────────────┼─────────────────────────────┼───────────────────────────┤
  │ 10   │ Activate CODER    │ "Implement"                 │ Executes tasks 1, 2, 3... │
  ├──────┼───────────────────┼─────────────────────────────┼───────────────────────────┤
  │ 11   │ CODER routes work │ Uses **Specialist:** labels │ Delegates to right agent  │
  ├──────┼───────────────────┼─────────────────────────────┼───────────────────────────┤
  │ 12   │ Activate TESTER   │ "Run tests"                 │ Quality gates + BDD       │
  ├──────┼───────────────────┼─────────────────────────────┼───────────────────────────┤
  │ 13   │ Activate REVIEWER │ "Review"                    │ Approved/Rejected         │
  ├──────┼───────────────────┼─────────────────────────────┼───────────────────────────┤
  │ 14   │ Loop if rejected  │ Back to CODER               │ Fix issues                │
  └──────┴───────────────────┴─────────────────────────────┴───────────────────────────┘

  Phase 4: Completion

  ┌──────┬───────────────┬────────────────────────────────┬───────────────────────────────────────┐
  │ Step │    Action     │        Command/Trigger         │                Output                 │
  ├──────┼───────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ 15   │ Generate PR   │ "Generate PR description"      │ .ai/tasks/{feature}/PR_DESCRIPTION.md │
  ├──────┼───────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ 16   │ Commit        │ git commit                     │ Commit hash                           │
  │      │ changes       │                                │                                       │
  ├──────┼───────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ 17   │ Update        │ Mark [DONE] with commit hash   │ Item complete                         │
  │      │ backlog       │                                │                                       │
  ├──────┼───────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ 18   │ Extract       │ Move to .ai/specs/ or          │ Permanent docs                        │
  │      │ decisions     │ .ai/decisions/                 │                                       │
  ├──────┼───────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ 19   │ Update status │ .ai/status/YYYY-MM-DD.md       │ Session log                           │
  ├──────┼───────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ 20   │ Push to       │ git push                       │ Deployed                              │
  │      │ origin        │                                │                                       │
  └──────┴───────────────┴────────────────────────────────┴───────────────────────────────────────┘

  ---
  🗂️  File Locations Reference

  ┌──────────────┬────────────────────────────────────┬──────────────────────────────┐
  │   Purpose    │                Path                │            Format            │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ Backlog      │ .ai/backlog-new.md                     │ Markdown with status tags    │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ RFCs         │ .ai/rfc/NNN-feature.md             │ RFC template                 │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ Specs        │ .ai/specs/system-name.md           │ Permanent system spec        │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ ADRs         │ .ai/decisions/YYYY-MM-DD-*.md      │ Architecture Decision Record │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ Tasks        │ .ai/tasks/{feature}/01_*.md        │ Task files                   │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ Constitution │ .ai/constitution.md                │ Architecture rules           │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ Resources    │ .ai/resources/{topic}/*.md         │ Reference patterns           │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ Skills       │ .ai/skills-registry/skills/{name}/ │ Enterprise skills            │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ Agents       │ .claude/agents/{name}.md           │ Agent definitions            │
  ├──────────────┼────────────────────────────────────┼──────────────────────────────┤
  │ Status       │ .ai/status/YYYY-MM-DD.md           │ Daily session logs           │
  └──────────────┴────────────────────────────────────┴──────────────────────────────┘

  ---
  🎯 Quick Reference Commands

  ┌───────────────┬───────────────────────────────────────────────────────────┐
  │     Goal      │                       Say to Claude                       │
  ├───────────────┼───────────────────────────────────────────────────────────┤
  │ Create RFC    │ "Use spec-driven-development to create RFC for {feature}" │
  ├───────────────┼───────────────────────────────────────────────────────────┤
  │ Plan tasks    │ "Plan {feature}" or "Create tasks for RFC {NNN}"          │
  ├───────────────┼───────────────────────────────────────────────────────────┤
  │ Implement     │ "Implement" (after PLANNER done)                          │
  ├───────────────┼───────────────────────────────────────────────────────────┤
  │ Run tests     │ "Run tests" or "Validate"                                 │
  ├───────────────┼───────────────────────────────────────────────────────────┤
  │ Review        │ "Review {feature}"                                        │
  ├───────────────┼───────────────────────────────────────────────────────────┤
  │ Generate PR   │ "Generate PR description"                                 │
  ├───────────────┼───────────────────────────────────────────────────────────┤
  │ Full pipeline │ "Implement {feature} using full agent pipeline"           │
  └───────────────┴───────────────────────────────────────────────────────────┘

  ---
  ✅ Quality Gates Checklist

  RFC Level (before PLANNER):
  - Problem clearly defined
  - At least 2 alternatives evaluated
  - Implementation phases defined
  - Test strategy documented
  - Rollback plan (if applicable)

  Task Level (before CODER):
  - Each task ≤ 3 files
  - Each task ≤ 2 hours
  - Acceptance criteria explicit
  - Constitution rules referenced
  - Dependencies identified

  Implementation Level (before REVIEWER):
  - ruff check passes
  - black check passes
  - python manage.py check passes
  - All tests passing
  - BDD scenarios passing
  - No forbidden technologies

  Final Level (before DONE):
  - PR description created
  - Committed with hash
  - Backlog marked [DONE]
  - Status files updated
  - Pushed to origin
  - Permanent decisions extracted
