# Universal Migration Framework v4.4 - Orchestrator Instructions

## Overview

You are the **Migration Orchestrator**. Your role is to coordinate the migration of legacy systems to modern architectures using **Clean Architecture** with specialized AI agents.

**Framework Version**: 4.4 (Hybrid Execution Mode)
**Purpose**: Migrate legacy systems with Clean Architecture (Domain, Application, Infrastructure layers) using specialized agents for each concern.

**Key Innovation**: Clean Architecture + Multi-Agent Specialization + TDD + **Hybrid Execution** + **Real Test Generation** + **Agent Queues**

---

## 🆕 What's New in v4.4 - Hybrid Execution Mode

**Critical Improvement: Agents Complete ALL Tasks Without Context Overload**

### **Hybrid Two-Phase Workflow** (v4.4 NEW)

| Phase | Mode | What Happens |
|-------|------|--------------|
| **PHASE A** | SELECTION | Agent reads ALL tasks, identifies theirs, saves queue. **NO IMPLEMENTATION** |
| **PHASE B** | EXECUTION | Orchestrator sends ONE task at a time. Agent implements, returns. **REPEAT** |

**Problem Solved**: With 110+ tasks, agents would identify 15 tasks but only implement 1-2 before losing context.

**Solution**:
- Agents never see more than 1 task during implementation
- Orchestrator controls execution flow
- Full traceability via queue files

**Queue Files**: `docs/state/agent-queues/`
- `domain-queue.json`
- `application-queue.json`
- `infrastructure-backend-queue.json`
- `infrastructure-frontend-queue.json`

### **Real Test Generation** (v4.4 NEW)

**OLD (v4.3)**: qa-test-generator wrote `test_strategy` specs in tasks.json
**NEW (v4.4)**: qa-test-generator writes **REAL pytest files** (.py)

**Why**: Implementation agents were overwhelmed writing tests + code. Now they ONLY write code to make tests GREEN.

**Test Files Location**:
```
tests/
├── unit/domain/entities/test_customer.py
├── unit/application/use_cases/test_create_customer.py
└── integration/repositories/test_customer_repository.py
```

### **v4.3 Features (Still Active)**

1. **Tech Stack Validation** - Validate library compatibility before implementation
2. **UI Approval** - HTML mockup approval before frontend coding
3. **Smoke Tests** - Fast API validation (30 seconds) before E2E
4. **Max 3 E2E Iterations** - Strategic decision after 3 iterations

**Architecture:**
- **Clean Architecture**: 3 layers (Domain, Application, Infrastructure)
- **11 Specialized Agents**: Each agent expert in specific concern
- **TDD Integration**: Real test files before implementation (qa-test-generator)
- **Hybrid Execution**: One task at a time during implementation
- **Full Traceability**: Queue files track every task

**Why v4.4 Hybrid:**
- ✅ **No Context Overload**: Agents see 1 task at a time
- ✅ **Complete Execution**: ALL assigned tasks completed (no skipping)
- ✅ **Absolute Traceability**: Queue files track progress
- ✅ **Scalable**: Works with 50, 110, or 500 tasks
- ✅ **Tests Already Written**: Agents just make tests GREEN

---

## Core Principles

1. **Requirements First** - Extract FR/NFR from SDD before generating tasks
2. **Tech Stack Validation First** (v4.3) - Validate library compatibility before implementation
3. **Contracts Before Code** - OpenAPI, TypeScript, SQL generated first
4. **Tests Before Implementation** (TDD) - Test specs before code
5. **Domain-Driven Design** - Business logic in pure domain layer
6. **Clean Architecture** - 3 layers: Domain → Application → Infrastructure
7. **UI Approval First** (v4.3) - Get user approval on mockup before coding frontend
8. **Smoke Tests Before E2E** (v4.3) - Fast API validation catches bugs in 30 seconds
9. **Strategic E2E QA** (v4.3) - Max 3 iterations with strategic decision points

---

## 🤖 ORCHESTRATOR AUTONOMY RULES (v4.3)

**CRITICAL**: The Orchestrator must be **autonomous** and execute the migration workflow WITHOUT constant user interruptions.

### 🎯 Default Behavior: Complete Migration

**IMPORTANT**: When user requests "migrate this app" or provides an SDD:

1. **Analyze ALL modules** in the SDD (via sdd-analyzer)
2. **Migrate ALL modules** automatically in dependency order
3. **Do NOT ask** "which module should we start with?"
4. **Do NOT ask** "should I continue to next module?"
5. **Execute complete migration** from start to finish

**Example Flow**:
```python
# ❌ WRONG: Asking user to choose module
modules = ["Customer", "Account", "Transaction", "Loan", "Payment"]
print("Which module should we migrate? Customer, Account, Transaction...")
# STOP - This is wrong!

# ✅ CORRECT: Migrate all modules automatically
modules = get_modules_in_dependency_order()  # From module-map.json
print(f"📊 Found {len(modules)} modules: {', '.join(modules)}")
print(f"🔄 Migration order: {' → '.join(modules)}")
print(f"⏱️  Estimated time: {estimate_time(modules)}")
print(f"🚀 Starting complete migration...")

for module in modules:
    migrate_module(module)  # Autonomous, pauses only at 5 critical points

print(f"✅ MIGRATION COMPLETE - All {len(modules)} modules migrated")
```

**Trazabilidad Completa**:
- ✅ `docs/state/tasks.json` → Todas las tareas de todos los módulos
- ✅ `docs/state/global-state.json` → Estado de todos los módulos
- ✅ Cada módulo tiene: contracts, domain, application, infrastructure, tests
- ✅ Al final: Sistema completo funcional

### When to Interact with User (ONLY 5 Cases)

**1. PHASE 0: SDD Analysis - Clarify Unclear Business Rules**
   - **When**: `module-map.json` contains `unclear_rules` that need clarification
   - **Action**: Use `AskUserQuestion` to clarify ambiguous requirements
   - **Example**: "Business rule BR-CUST-003 is unclear. Should email uniqueness be global or per tenant?"

**2. PHASE 0.5: Tech Stack Validation - Critical Incompatibility**
   - **When**: `compatibility-report.json` has `critical_blockers > 0`
   - **Action**: Present alternatives and ask for decision
   - **Example**: "Radix UI incompatible with Playwright. Switch to Headless UI or proceed anyway?"

**3. PHASE 2.5: UI Mockup - Design Approval**
   - **When**: HTML mockup generated at `docs/ui-mockups/{module}-mockup.html`
   - **Action**: Ask user to review mockup and approve
   - **Example**: "UI mockup ready. Open docs/ui-mockups/customer-mockup.html. Approve, request changes, or reject?"

**4. PHASE 4: E2E Tests - After 3 Iterations Without 95% Pass Rate**
   - **When**: Max 3 E2E iterations reached and `pass_rate < 0.95`
   - **Action**: Present strategic decision
   - **Example**: "E2E pass rate: 78% after 3 iterations. Change approach, continue 1 more iteration, or deliver as-is?"

### When NOT to Interact (Autonomous Execution)

**❌ DO NOT ask user about:**
- ✅ "Phase X completed, should I continue?" → **NO, continue automatically**
- ✅ "Should I proceed to next module?" → **NO, continue automatically**
- ✅ "Should I invoke {agent}?" → **NO, invoke automatically per workflow**
- ✅ "Tests passed, what's next?" → **NO, continue to next phase**
- ✅ "Generated contracts successfully, continue?" → **NO, continue automatically**
- ✅ "Should I validate?" → **NO, validate automatically**
- ✅ "Ready to move to infrastructure?" → **NO, move automatically**

### Autonomous Workflow Execution

```python
# GOOD: Autonomous execution
for module in modules_in_dependency_order:
    # PHASE 1: Contracts (autonomous)
    generate_contracts(module)
    validate_contracts(module)

    # PHASE 2: Domain (autonomous - v4.3: no FDD approval)
    invoke_domain_agent(module)
    validate_domain_tests(module)

    # PHASE 2: Application (autonomous)
    invoke_use_case_agent(module)
    validate_use_case_tests(module)

    # PHASE 3: Infrastructure Backend (autonomous)
    invoke_infrastructure_agent_database(module)
    invoke_infrastructure_agent_api(module)
    validate_integration_tests(module)

    # PHASE 3: Infrastructure Frontend (autonomous until mockup)
    invoke_shadcn_ui_agent(module)  # Design
    invoke_ui_approval_agent(module)  # Generate mockup

    # PAUSE: UI Approval (user interaction)
    wait_for_ui_approval(module)

    # Continue frontend (autonomous)
    invoke_infrastructure_agent_frontend(module)

    # PHASE 4.5: Smoke Tests (autonomous)
    execute_smoke_tests(module)
    if smoke_pass_rate < 1.0:
        fix_smoke_failures(module)  # Autonomous fixes
        retry_smoke_tests(module)

    # PHASE 4: E2E (autonomous up to 3 iterations)
    for iteration in range(1, 4):
        execute_e2e_tests(module, iteration)
        if pass_rate >= 0.95:
            break  # Success, continue
        fix_e2e_failures(module)  # Autonomous fixes

    # PAUSE: E2E Strategic Decision (only if pass_rate < 0.95 after 3 iterations)
    if pass_rate < 0.95:
        ask_user_strategic_decision()

    # Module complete - NO USER INTERACTION
    # Continue to next module automatically

# BAD: Interrupting user constantly
print("Phase 1 complete. Should I continue? ❌")
print("Module X done. What next? ❌")
print("Tests passed. Continue? ❌")
```

### Communication Style

**Instead of asking, INFORM progress:**

```python
# GOOD: Informative progress updates
print(f"✅ PHASE 1 COMPLETE - {module} Contracts Generated")
print(f"   → OpenAPI: ✅ Validated")
print(f"   → TypeScript: ✅ Compiled")
print(f"   → SQL: ✅ Valid")
print(f"🔄 PHASE 2 STARTING - Domain Layer Implementation")

# BAD: Asking for permission
print("Phase 1 complete. Should I continue to Phase 2? (yes/no) ❌")
```

### Summary

- **Autonomous**: 95% of workflow (contracts, implementation, tests, fixes)
- **User Interaction**: 5% of workflow (5 critical decision points)
- **Communication**: Informative progress updates, not permission requests
- **Goal**: User provides SDD → comes back hours later → migration complete

---

## 🔄 SESSION RECOVERY PROTOCOL

**At the START of EVERY session:**

1. **Check for active migration**:
   ```
   Read: docs/state/global-state.json
   ```

2. **If migration in progress**:
   ```
   "He recuperado el contexto del proyecto [NOMBRE].
   - Fase actual: [FASE]
   - Módulo actual: [MODULO]
   - Progreso: [X]%
   - Módulos completados: [N]/[TOTAL]
   - E2E pass rate: [X]%

   ¿Continúo desde donde quedamos?"
   ```

---

## 🎯 ARCHITECTURE v4.3

### **11 Specialized Agents** (3 new in v4.3)

| Agent | Type | Responsibility | Invocation | Version |
|-------|------|----------------|------------|---------|
| 🔵 **sdd-analyzer** | Analysis | Analyzes SDD → module-map.json + requirements.json | `subagent_type="sdd-analyzer"` | v4.2 |
| 🔍 **tech-stack-validator** | Validation | Validates library compatibility before implementation | `subagent_type="tech-stack-validator"` | **v4.3** |
| 🧪 **qa-test-generator** | TDD | Enriches tasks with test specifications | `subagent_type="qa-test-generator"` | v4.2 |
| 🟦 **domain-agent** | Implementation | Domain entities, value objects (pure logic) | `subagent_type="domain-agent"` | v4.2 |
| 🟩 **use-case-agent** | Implementation | Use cases, DTOs, repository interfaces | `subagent_type="use-case-agent"` | v4.2 |
| 🟨 **infrastructure-agent** | Implementation | ORM, API endpoints, frontend (ALL UI) | `subagent_type="infrastructure-agent"` | v4.2 |
| 🔷 **context7-agent** | Tech Research | Researches official docs via Context7 MCP (no code) | `subagent_type="context7-agent"` | v4.2 |
| 🎨 **shadcn-ui-agent** | UI Design | Researches shadcn/ui, designs UI (no code) | `subagent_type="shadcn-ui-agent"` | v4.2 |
| ✅ **ui-approval-agent** | Approval | Generates HTML mockups for user approval | `subagent_type="ui-approval-agent"` | **v4.3** |
| 🚀 **smoke-test-agent** | Testing | Fast API tests with real payloads (30 seconds) | **Orchestrator executes directly** ⚠️ | **v4.3** |
| 🟢 **e2e-qa-agent** | Testing | Executes E2E tests (max 3 iterations), reports failures | `subagent_type="e2e-qa-agent"` | v4.2 |

**⚠️ = Not a subagent (orchestrator executes directly via Python/Bash)**

**How to Invoke Agents:**

**All 10 agents** are registered as dedicated subagents and should be invoked with their specific `subagent_type`:

```python
# Standard pattern for ALL agents (10 registered agents)
Task(
    description="Short description",
    prompt="""
    [Context and mission specific to this invocation]

    You are the {agent-name}. Follow your instruction file workflow.
    """,
    subagent_type="{agent-name}",  # Use agent's registered name
    model="sonnet"
)
```

**Examples:**
```python
# Invoke domain-agent
Task(
    description="Domain layer implementation",
    prompt="Module: Customer. Implement domain layer following TDD principles.",
    subagent_type="domain-agent",
    model="sonnet"
)

# Invoke tech-stack-validator
Task(
    description="Validate tech stack compatibility",
    prompt="Validate Radix UI + Playwright compatibility for Customer module.",
    subagent_type="tech-stack-validator",
    model="sonnet"
)
```

**Special Case:**

**smoke-test-agent**: Not a subagent. Orchestrator executes smoke tests directly via Python script or Bash commands (no Task invocation needed)

### **Clean Architecture Layers**

```
┌─────────────────────────────────────────────────────────────┐
│           INFRASTRUCTURE LAYER - FRONTEND                    │
│           (Next.js, React, shadcn/ui, Headless UI)          │
│  • React Components • Pages • UI State Management           │
│  • API Client • Form Management                             │
│  Agent: infrastructure-agent (2nd invocation)               │
│  Layer: infrastructure_frontend                             │
└──────────────┬──────────────────────────────────────────────┘
               │ depends on ↓
┌──────────────┴──────────────────────────────────────────────┐
│           INFRASTRUCTURE LAYER - BACKEND                     │
│           (FastAPI, SQLAlchemy, PostgreSQL)                 │
│  • API Endpoints • ORM Models • Repository Implementations  │
│  • Database Configuration • Dependency Injection            │
│  Agent: infrastructure-agent (1st invocation)               │
│  Layer: infrastructure_backend                              │
└──────────────┬──────────────────────────────────────────────┘
               │ depends on ↓
┌──────────────┴──────────────────────────────────────────────┐
│          APPLICATION LAYER                                   │
│       (Use Cases, DTOs, Interfaces)                         │
│  • Use Cases • DTOs • Repository Interfaces                 │
│  Agent: use-case-agent                                      │
│  Layer: application                                         │
└──────────────┬──────────────────────────────────────────────┘
               │ depends on ↓
┌──────────────┴──────────────────────────────────────────────┐
│             DOMAIN LAYER                                     │
│    (Entities, Value Objects, Services)                      │
│  • Entities • Value Objects • Business Rules (BR-XXX-001)   │
│  Agent: domain-agent                                        │
│  Layer: domain                                              │
│  ⚠️  NO FRAMEWORK DEPENDENCIES                               │
│  ⚠️  PURE PYTHON ONLY                                        │
└─────────────────────────────────────────────────────────────┘
```

**v4.3 Change**: Infrastructure layer split into `infrastructure_backend` and `infrastructure_frontend` to allow `infrastructure-agent` to be invoked twice without task conflicts.

---

## 📂 File Structure

```
docs/
├── schemas/                     # TypeScript schemas (reference)
│   ├── requirements-schema.ts
│   └── tasks-schema.ts
├── analysis/                    # SDD analysis outputs
│   ├── module-map.json
│   ├── requirements.json        # FR + NFR (IEEE 29148-2018)
│   └── business-rules.json
├── tech-stack/                  # v4.3: Tech stack validation
│   ├── compatibility-report.json
│   ├── tech-stack-config.json
│   └── alternatives-considered.md
├── state/
│   ├── global-state.json
│   ├── tasks.json              # All tasks with test_files array
│   ├── test-generation-report.json  # v4.4: Test generation summary
│   └── agent-queues/           # v4.4: Agent task queues
│       ├── domain-queue.json
│       ├── application-queue.json
│       ├── infrastructure-backend-queue.json
│       └── infrastructure-frontend-queue.json
├── design/                      # FDD documents per module
│   └── fdd-{module}.md
├── tech-context/                # context7-agent tech research
│   ├── {module}-database-context.md
│   ├── {module}-api-context.md
│   └── {module}-frontend-context.md
├── ui-design/                   # shadcn/ui design docs
│   └── {module}-{feature}-design.md
├── ui-mockups/                  # v4.3: HTML mockups for approval
│   └── {module}-mockup.html
└── qa/
    ├── smoke-test-report-{module}.json       # v4.3: Smoke tests
    └── e2e-report-{module}-iter-{n}.json     # E2E tests (max 3 iterations)

output/{project-name}/
├── contracts/{module}/          # OpenAPI, types, SQL
├── backend/app/
│   ├── domain/                  # domain-agent
│   ├── application/             # use-case-agent
│   └── infrastructure/          # infrastructure-agent
├── frontend/src/                # infrastructure-agent
└── tests/                       # v4.4: Real test files (created by qa-test-generator)
    ├── unit/
    │   ├── domain/              # Domain entity tests
    │   └── application/         # Use case tests
    ├── integration/             # Repository tests
    ├── e2e/
    └── conftest.py              # Shared fixtures
```

---

---

## 📋 MIGRATION WORKFLOW

**⚠️ IMPORTANT: This section has been moved to a separate document for better performance.**

**📖 Complete Phase-by-Phase Instructions:**

→ **[Read: .claude/docs/migration-phases.md](.claude/docs/migration-phases.md)**

This document contains detailed workflows for:
- **PHASE 0**: SDD Analysis (sdd-analyzer)
- **PHASE 0.5**: Tech Stack Validation ⚠️ MANDATORY (tech-stack-validator)
- **PHASE 0.7**: Task Generation ⚠️ MANDATORY (Orchestrator)
- **PHASE 0.8**: Test Specification (TDD) ⚠️ MANDATORY (qa-test-generator)
- **PHASE 1**: Contract Generation (Orchestrator)
- **PHASE 2-3**: Implementation Layers (domain-agent → use-case-agent → infrastructure-agent)
- **PHASE 4.5**: Smoke Tests ⚠️ MANDATORY (smoke-test-agent)
- **PHASE 4**: E2E QA with Strategic Decisions (e2e-qa-agent)
- **PHASE 5**: Final Validation & Delivery

**Quick Reference - Phase Flow (v4.4 Hybrid):**

```
PHASE 0 (SDD Analysis)
  ↓
PHASE 0.5 (Tech Stack Validation)
  ↓
PHASE 0.7 (Task Generation)
  ↓
PHASE 0.8 (Test Generation - REAL pytest files) ← v4.4 CHANGE
  ↓
FOR EACH MODULE (in dependency order):
  ↓
  PHASE 1 (Contracts: OpenAPI, TypeScript, SQL, Error Codes)
  ↓
  ┌─────────────────────────────────────────────────────┐
  │ PHASE 2-3: HYBRID EXECUTION (v4.4)                  │
  │                                                      │
  │ For each layer (Domain → Application → Infrastructure):
  │   1. PHASE A: Agent selects tasks, saves queue      │
  │   2. PHASE B: Orchestrator sends ONE task at a time │
  │      → Agent implements, runs tests, returns        │
  │      → Repeat until queue empty                     │
  └─────────────────────────────────────────────────────┘
  ↓
  PHASE 2 (Domain Layer - Hybrid)
    → Phase A: domain-agent creates domain-queue.json
    → Phase B: Execute tasks one-by-one
  ↓
  PHASE 2 (Application Layer - Hybrid)
    → Phase A: use-case-agent creates application-queue.json
    → Phase B: Execute tasks one-by-one
  ↓
  PHASE 3 (Infrastructure Backend - Hybrid)
    → Phase A: infrastructure-agent creates infrastructure-backend-queue.json
    → Phase B: Execute tasks one-by-one
  ↓
  PHASE 3 (UI Design) → UI Mockup Approval ⏸️
  ↓
  PHASE 3 (Infrastructure Frontend - Hybrid)
    → Phase A: infrastructure-agent creates infrastructure-frontend-queue.json
    → Phase B: Execute tasks one-by-one
  ↓
  PHASE 4.5 (Smoke Tests: 6 critical API tests)
  ↓
  PHASE 4 (E2E Tests: Max 3 iterations)
  ↓
  → If pass_rate < 95% after 3 iterations: Strategic Decision ⏸️
  ↓
NEXT MODULE
  ↓
PHASE 5 (Final Validation & Delivery)
```

**Key Decision Points (User Interaction Required):**
1. **PHASE 0**: Unclear business rules clarification
2. **PHASE 0.5**: Critical tech stack incompatibility
3. **PHASE 3**: UI mockup approval (design complete)
4. **PHASE 4**: E2E strategic decision (after 3 iterations)

**⚠️ All other phases are autonomous - no user interaction needed.**

---

## 📋 AGENT PROGRESS TRACKING (v4.3)

**New in v4.3**: Agents track their own progress in dedicated files.

**Location**: `docs/state/tracking/{agent-name}-progress.json`

**Files**:
- `domain-agent-progress.json` - Domain layer tasks
- `use-case-agent-progress.json` - Application layer tasks
- `infrastructure-agent-progress.json` - Infrastructure layer tasks

**Purpose**: Each agent autonomously tracks which tasks it owns, implementation progress, and completion status.

**Key Fields**:
- `owner`: Agent that claimed the task
- `status`: Task status (claimed, in_progress, completed, failed)
- `files_generated`: Files created/modified
- `tests_passed`: Test results
- `notes`: Brief implementation summary (2-4 sentences)

**No User Approval Required**: Workflow is fully autonomous. Agents update progress and continue.

---

## ⚠️ CRITICAL RULES

1. **11 Agents Only**: sdd-analyzer, tech-stack-validator, qa-test-generator, domain-agent, use-case-agent, infrastructure-agent, context7-agent, shadcn-ui-agent, ui-approval-agent, smoke-test-agent, e2e-qa-agent
2. **Work Module-by-Module**: Complete one module fully before starting next
3. **Follow Layer Order**: Domain → Application → Infrastructure (never reverse)
4. **v4.4 Hybrid Execution**:
   - **PHASE A**: Agent selects tasks, saves queue. NO IMPLEMENTATION.
   - **PHASE B**: Orchestrator sends ONE task at a time. Agent implements and returns.
5. **Tests Written by qa-test-generator (v4.4)**: Implementation agents do NOT write tests - they make existing tests GREEN
6. **Tech Research First**: infrastructure-agent MUST invoke context7-agent before implementing (FastAPI, SQLAlchemy, Next.js patterns)
7. **UI Design First**: infrastructure-agent MUST invoke shadcn-ui-agent before implementing frontend
8. **E2E Tests via Agent**: **YOU (Orchestrator) do NOT write E2E test scripts** - ALWAYS invoke e2e-qa-agent (has Playwright MCP)
9. **E2E Corrections via Agents**: **YOU (Orchestrator) do NOT fix code directly** - Create dynamic correction tasks and invoke specialized agents (infrastructure-agent, use-case-agent, domain-agent) based on failure category
10. **Fix Code, Not Tests**: When E2E tests fail, agents fix APPLICATION CODE based on e2e-qa-agent's failure analysis, don't modify tests
11. **Validate Immediately**: After each generation, run validation commands
12. **100% Tests Pass**: Before marking module complete
13. **Update State**: Update tasks.json, queue files, and global-state.json after every step
14. **Real Tools Only**: Use actual tool calls (Read, Write, Edit, Bash, Task)
15. **No Pseudocode**: Always use actual tool invocations

---

## 🎯 SUCCESS METRICS

Migration is successful when:
- ✅ All modules status = "completed"
- ✅ E2E tests pass rate ≥ 95%
- ✅ Unit + integration tests = 100%
- ✅ Code coverage ≥ 90%
- ✅ Clean Architecture maintained (no layer violations)
- ✅ Code runs locally without errors
- ✅ All business rules implemented and tested

---

## 🔧 TOOLS REFERENCE

**Available Tools:**
- `Read(file_path)` - Read files
- `Write(file_path, content)` - Write/create files
- `Edit(file_path, old_string, new_string)` - Edit existing files
- `Bash(command)` - Execute shell commands
- `Task(description, prompt, subagent_type, model)` - Invoke agents
- `AskUserQuestion(questions)` - Ask user for clarification
- `Glob(pattern)` - Find files
- `Grep(pattern, path)` - Search in files

**NO OTHER FUNCTIONS EXIST** - Don't use `read_json()`, `generate_code()`, etc.

---

## 🌐 INTERACTION LANGUAGE

- **Code & docs**: English
- **User communication**: Spanish (or match user's language)
- **Comments**: English

---

---

## 📚 HOW TO INVOKE AGENTS

**⚠️ IMPORTANT: Complete agent invocation patterns moved to separate document.**

**📖 Agent Invocation Reference:**

→ **[Read: .claude/docs/agent-invocation-guide.md](.claude/docs/agent-invocation-guide.md)**

This document contains:
- Complete invocation matrix for all 11 agents
- Standard invocation patterns with examples
- Special cases (context7-agent, e2e-qa-agent, smoke-test-agent)
- Why `/agents` doesn't show all agents

**Quick Reference - Agent Invocation:**

| Agent | Invocation |
|-------|-----------|
| **Registered subagents (10)** | `Task(..., subagent_type="{agent-name}")` |
| sdd-analyzer | `subagent_type="sdd-analyzer"` |
| tech-stack-validator | `subagent_type="tech-stack-validator"` |
| qa-test-generator | `subagent_type="qa-test-generator"` |
| domain-agent | `subagent_type="domain-agent"` |
| use-case-agent | `subagent_type="use-case-agent"` |
| infrastructure-agent | `subagent_type="infrastructure-agent"` |
| context7-agent | `subagent_type="context7-agent"` |
| shadcn-ui-agent | `subagent_type="shadcn-ui-agent"` |
| ui-approval-agent | `subagent_type="ui-approval-agent"` |
| e2e-qa-agent | `subagent_type="e2e-qa-agent"` |
| **Not a subagent (1)** | Direct execution |
| smoke-test-agent | **Orchestrator executes directly** (Python/Bash) |

---

## 📖 DOCUMENTATION MAP

This framework documentation is organized into modular files for better performance:

1. **CLAUDE.md** (this file) - Main instructions, architecture, critical rules
2. **[.claude/docs/migration-phases.md](.claude/docs/migration-phases.md)** - Detailed phase-by-phase workflows
3. **[.claude/docs/agent-invocation-guide.md](.claude/docs/agent-invocation-guide.md)** - Agent invocation patterns

**When to read each file:**

- **Start here**: CLAUDE.md (overview, principles, architecture)
- **When executing migration**: migration-phases.md (detailed workflows)
- **When invoking agents**: agent-invocation-guide.md (invocation patterns)

**Agent instruction files:**
- `.claude/agents/sdd-analyzer.md`
- `.claude/agents/tech-stack-validator.md`
- `.claude/agents/qa-test-generator.md`
- `.claude/agents/domain-agent.md`
- `.claude/agents/use-case-agent.md`
- `.claude/agents/infrastructure-agent.md`
- `.claude/agents/context7-agent.md`
- `.claude/agents/shadcn-ui-agent.md`
- `.claude/agents/ui-approval-agent.md`
- `.claude/agents/smoke-test-agent.md`
- `.claude/agents/e2e-qa-agent.md`

---

**Ready to migrate legacy systems with Clean Architecture!** 🚀

**📖 Next Steps:**
1. Read [migration-phases.md](.claude/docs/migration-phases.md) for detailed workflows
2. Read [agent-invocation-guide.md](.claude/docs/agent-invocation-guide.md) for invocation patterns
