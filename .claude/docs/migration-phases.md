# Migration Phases - Complete Workflow Guide v4.4

**📖 Documentation Navigation:**
- **← Previous**: [CLAUDE.md](../../CLAUDE.md) - Framework overview and architecture
- **→ Next**: [agent-invocation-guide.md](./agent-invocation-guide.md) - Agent invocation patterns

---

## 🆕 v4.4 HYBRID EXECUTION MODE

**Key Innovation**: Two-phase workflow prevents agent context overload when dealing with 50-200+ tasks.

| Phase | Mode | What Happens |
|-------|------|--------------|
| **PHASE A** | SELECTION | Agent reads ALL tasks, identifies theirs, saves queue file. **NO IMPLEMENTATION** |
| **PHASE B** | EXECUTION | Orchestrator sends ONE task at a time. Agent implements and returns. **REPEAT** |

**Benefits**:
- Agents never see more than 1 task during implementation
- No context overload (even with 200 tasks)
- Absolute traceability via queue files
- Agents complete ALL assigned tasks (no skipping)

**Queue Files Location**: `docs/state/agent-queues/`
- `domain-queue.json`
- `application-queue.json`
- `infrastructure-backend-queue.json`
- `infrastructure-frontend-queue.json`

---

## 🔄 v4.4 TASK REJECTION & RE-CLASSIFICATION

**Key Innovation**: Agents can REJECT incorrectly classified tasks and suggest the correct layer.

### Why This Matters

The initial layer assignment in PHASE 0.7 uses keyword detection which can be wrong:
- "Create CustomerDTO" might be assigned to `domain` (wrong - should be `application`)
- "Define IRepository interface" might be assigned to `infrastructure` (wrong - should be `application`)

### How Rejection Works

**During PHASE A (Task Selection)**, each agent:
1. Identifies candidate tasks by layer field
2. **VALIDATES each task** - Is this REALLY my layer?
3. **Accepts valid tasks** → Adds to queue
4. **Rejects invalid tasks** → Re-classifies in tasks.json

**Validation Criteria per Agent:**

| Agent | ACCEPT | REJECT |
|-------|--------|--------|
| **domain-agent** | Entities, Value Objects, Business Rules (pure Python) | DTOs, Use Cases, ORM, APIs, Components |
| **use-case-agent** | Use Cases, DTOs, Repository Interfaces | Entities, ORM implementations, APIs |
| **infrastructure-agent** | ORM, Repositories (concrete), APIs, React Components | Entities, Value Objects, Use Cases, DTOs |

### Queue File with Rejections

```json
{
  "agent": "use-case-agent",
  "total_tasks": 10,
  "completed": 0,
  "rejected_tasks": [
    {
      "task_id": "TASK-045",
      "title": "Implement CustomerRepositoryImpl with SQLAlchemy",
      "original_layer": "application",
      "suggested_layer": "infrastructure_backend",
      "reason": "Repository IMPLEMENTATION is infrastructure, not application"
    }
  ],
  "queue": [...]
}
```

### tasks.json with Rejection History

```json
{
  "id": "TASK-045",
  "title": "Implement CustomerRepositoryImpl with SQLAlchemy",
  "layer": "infrastructure_backend",
  "rejection_history": [
    {
      "rejected_by": "use-case-agent",
      "reason": "Task is not application layer - should be infrastructure_backend",
      "suggested_layer": "infrastructure_backend"
    }
  ]
}
```

### Orchestrator Handling of Rejected Tasks

After PHASE A completes, orchestrator should:

```python
Read: docs/state/agent-queues/{agent}-queue.json

if queue["rejected_tasks"]:
    print(f"⚠️ {len(queue['rejected_tasks'])} tasks rejected and re-classified")

    # Re-run task assignment for re-classified tasks
    # Or let the correct agent pick them up in their PHASE A
```

---

## 📋 MIGRATION PHASES

### **PHASE 0: SDD Analysis**

**Objective**: Analyze SDD and extract modules, business rules, and requirements

**Agent**: sdd-analyzer

**Steps:**

1. **Invoke sdd-analyzer**:
```python
Task(
    description="Analyze SDD and generate module map + requirements",
    prompt="""
    Read .claude/agents/sdd-analyzer.md for your instructions.

    INPUT FILES:
    - {sdd_path_from_user}

    REQUIRED OUTPUT FILES:
    - docs/analysis/module-map.json
    - docs/analysis/requirements.json (FR + NFR following IEEE 29148-2018)
    - docs/analysis/business-rules.json
    - docs/analysis/user-checklist.md

    YOUR MISSION:
    1. Read SDD thoroughly
    2. Identify functional modules (Customer, Account, Transaction, etc.)
    3. Extract Functional Requirements (FR) - what system must DO
    4. Extract Non-Functional Requirements (NFR) - how system must PERFORM
    5. Extract business rules per module
    6. Create dependency graph (level 0, 1, 2)
    7. Identify UNCLEAR rules needing user clarification
    8. Estimate complexity per module

    For requirements extraction, follow IEEE 29148-2018:
    - Each requirement has: id, title, description, priority, acceptance criteria
    - FR: User actions, data processing, business logic
    - NFR: Performance, security, usability, reliability, etc.
    - Verification method: test, inspection, demonstration, analysis
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

2. **Read Results**:
```python
Read: docs/analysis/module-map.json
Read: docs/analysis/requirements.json
Read: docs/analysis/business-rules.json
Read: docs/analysis/user-checklist.md
```

3. **User Clarification (if needed)**:
```python
# If unclear_rules exist in module-map.json
AskUserQuestion(questions=[...])
# Save decisions to docs/analysis/user-decisions.json
```

4. **Initialize Global State**:
```python
Write: docs/state/global-state.json
{
  "version": "4.4-hybrid",
  "project_name": "{project}",
  "phase": "requirements_extraction",
  "modules": {...}
}
```

---

### **PHASE 0.5: Tech Stack Validation** ⚠️ MANDATORY (v4.3+)

**Objective**: Validate tech stack compatibility BEFORE implementation to avoid architecture incompatibilities

**Agent**: tech-stack-validator

**Invocation**: `subagent_type="Explore"` (reads `.claude/agents/tech-stack-validator.md`)

**⚠️ CRITICAL**: This phase is MANDATORY. Do NOT skip. Validates library compatibility to prevent wasting days on E2E fixes.

**Why This Phase**: Customer module wasted 7 E2E iterations due to Radix UI DialogOverlay + Playwright incompatibility. This phase catches such issues in 30 minutes.

**Verification**: After this phase, `docs/tech-stack/compatibility-report.json` MUST exist and all critical blockers MUST be resolved or user-approved.

**Steps:**

1. **Invoke tech-stack-validator**:
```python
Task(
    description="Validate tech stack compatibility",
    prompt="""
    Read .claude/agents/tech-stack-validator.md for complete instructions.

    TECH STACK TO VALIDATE:
    - Backend: FastAPI + SQLAlchemy 2.0 + aiosqlite/asyncpg
    - Frontend: Next.js 15 + shadcn/ui (Radix UI) + Playwright
    - Forms: React Hook Form + Zod

    YOUR MISSION:
    1. Research each critical combination for compatibility issues
    2. Focus on E2E testing compatibility (UI library + Playwright) ⚠️ CRITICAL
    3. Search GitHub issues for known problems
    4. Generate compatibility report
    5. If CRITICAL issues found: STOP and present alternatives to user
    6. If SAFE: Proceed to task generation

    OUTPUT:
    - docs/tech-stack/compatibility-report.json
    - docs/tech-stack/tech-stack-config.json (approved stack)
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

2. **Read and analyze results**:
```python
Read: docs/tech-stack/compatibility-report.json

if report["critical_blockers"] > 0:
    print(f"❌ {report['critical_blockers']} critical incompatibility found")

    # Present to user
    AskUserQuestion(questions=[{
        "question": f"Tech stack incompatibility detected: {issue_summary}. How to proceed?",
        "header": "Tech Stack",
        "options": [
            {"label": "Use alternative", "description": f"Switch to {alternative}"},
            {"label": "Proceed anyway", "description": "Accept E2E test limitations"},
            {"label": "Manual research", "description": "I'll research more"}
        ]
    }])

    # If user chooses alternative, update tech stack config
```

3. **Verify validation completed** ⚠️ MANDATORY:
```python
Read: docs/tech-stack/compatibility-report.json
assert os.path.exists("docs/tech-stack/compatibility-report.json")
print(f"✅ Tech stack validated. {report['safe_combinations']} compatible, {report['critical_blockers']} blockers")
```

**Full documentation**: See `.claude/agents/tech-stack-validator.md`

**⚠️ DO NOT PROCEED TO PHASE 0.7 WITHOUT VALIDATING TECH STACK**

---

### **PHASE 0.7: Task Generation** ⚠️ MANDATORY

**Objective**: Convert requirements into atomic, executable tasks with clear dependencies

**Agent**: Orchestrator (YOU)

**⚠️ CRITICAL**: This phase is MANDATORY. Do NOT skip. Do NOT proceed to implementation without generating tasks.json.

**Verification**: After this phase, `docs/state/tasks.json` MUST exist.

**YOU (Orchestrator) MUST execute this phase. Do NOT delegate to agents. Do NOT skip.**

**Steps:**

1. **Read Requirements and Module Map**:
```python
Read: docs/analysis/requirements.json
Read: docs/analysis/module-map.json
```

Parse the JSON to extract:
- `project_name` from requirements.json
- `modules` array from module-map.json (each module has: name, functional_requirements, business_rules, dependencies)

2. **Generate Tasks per Module** (in dependency order: level 0, 1, 2):

**⚠️ CRITICAL**: Generate tasks for **ALL modules** in `module-map.json`. Do NOT ask user which modules to include. **Complete migration** is the default behavior.

For EACH module in `module-map.json`, generate 8 tasks:

**A) TASK-{MODULE}-001-CONTRACTS** - Generate contracts
**B) TASK-{MODULE}-002-DOMAIN** - Implement domain layer
**C) TASK-{MODULE}-003-USE-CASE** - Implement use cases
**D) TASK-{MODULE}-004-INFRA-DB** - Implement database layer
**E) TASK-{MODULE}-005-INFRA-API** - Implement API endpoints
**F) TASK-{MODULE}-006-UI-DESIGN** - Design UI with shadcn/ui
**G) TASK-{MODULE}-007-INFRA-FRONTEND** - Implement frontend
**H) TASK-{MODULE}-008-E2E-QA** - Execute E2E tests

**v4.4 Task Structure** (includes `layer` field for agent selection):

```json
{
  "id": "TASK-CUSTOMER-002-DOMAIN",
  "title": "Implement Customer Domain Layer",
  "type": "implementation",
  "module": "Customer",
  "layer": "domain",
  "owner": null,
  "status": "pending",
  "related_requirements": ["FR-CUST-001", "FR-CUST-002"],
  "business_rules": ["BR-CUST-001", "BR-CUST-002"],
  "dependencies": ["TASK-CUSTOMER-001-CONTRACTS"],
  "deliverables": [
    "backend/app/domain/entities/customer.py",
    "backend/app/domain/value_objects/email.py",
    "backend/app/domain/value_objects/credit_score.py"
  ],
  "test_files": []
}
```

3. **Write tasks.json**:

```python
# Build tasks array for ALL modules
all_tasks = []

for module in modules:  # From module-map.json
    module_name = module["name"]

    # TASK 1: Contracts
    all_tasks.append({
        "id": f"TASK-{module_name.upper()}-001-CONTRACTS",
        "title": f"Generate {module_name} Contracts",
        "type": "contracts",
        "module": module_name,
        "layer": null,
        "owner": "orchestrator",
        "status": "pending",
        ...
    })

    # TASK 2: Domain (layer = "domain")
    all_tasks.append({
        "id": f"TASK-{module_name.upper()}-002-DOMAIN",
        "title": f"Implement {module_name} Domain Layer",
        "type": "implementation",
        "layer": "domain",
        "owner": null,  # Will be claimed by domain-agent
        "status": "pending",
        ...
    })

    # TASK 3: Use Case (layer = "application")
    all_tasks.append({
        "id": f"TASK-{module_name.upper()}-003-USE-CASE",
        "layer": "application",
        "owner": null,  # Will be claimed by use-case-agent
        ...
    })

    # TASK 4-5: Infrastructure Backend (layer = "infrastructure_backend")
    all_tasks.append({
        "id": f"TASK-{module_name.upper()}-004-INFRA-DB",
        "layer": "infrastructure_backend",
        "owner": null,  # Will be claimed by infrastructure-agent
        ...
    })

    # TASK 6-7: Infrastructure Frontend (layer = "infrastructure_frontend")
    all_tasks.append({
        "id": f"TASK-{module_name.upper()}-007-INFRA-FRONTEND",
        "layer": "infrastructure_frontend",
        "owner": null,  # Will be claimed by infrastructure-agent
        ...
    })

    # ... etc

Write: docs/state/tasks.json
{
  "project_name": project_name,
  "framework_version": "4.4-hybrid",
  "generated_date": current_date,
  "total_tasks": len(all_tasks),
  "tasks": all_tasks
}
```

4. **Create agent-queues directory**:
```bash
mkdir -p docs/state/agent-queues
```

5. **Verify tasks.json was created** ⚠️ MANDATORY:
```python
Read: docs/state/tasks.json
assert len(tasks) > 0
print(f"✅ Generated {len(tasks)} tasks for migration")
```

**⚠️ DO NOT PROCEED TO PHASE 0.8 WITHOUT GENERATING AND VERIFYING tasks.json**

---

### **PHASE 0.8: Test Generation (TDD)** ⚠️ MANDATORY - v4.4 CHANGE

**Objective**: Generate REAL pytest files BEFORE implementation

**Agent**: qa-test-generator

**⚠️ v4.4 CRITICAL CHANGE**: qa-test-generator now writes **ACTUAL test files** (.py), not just test specifications in tasks.json.

**Why**: Implementation agents were overwhelmed writing tests + code. Now they ONLY write code to make tests GREEN.

**Tests Location**:
```
tests/
├── unit/
│   ├── domain/
│   │   ├── entities/test_customer.py
│   │   └── value_objects/test_email.py
│   └── application/
│       └── use_cases/test_create_customer.py
├── integration/
│   └── repositories/test_customer_repository.py
└── conftest.py
```

**Steps:**

1. **Verify tasks.json exists** ⚠️:
```python
Read: docs/state/tasks.json
assert os.path.exists("docs/state/tasks.json")
```

2. **Invoke qa-test-generator**:
```python
Task(
    description="Generate REAL test files for TDD",
    prompt="""
    Read .claude/agents/qa-test-generator.md for complete instructions.

    INPUT FILES:
    - docs/state/tasks.json
    - docs/analysis/requirements.json
    - docs/analysis/business-rules.json

    YOUR MISSION (v4.4):
    1. Read all tasks from tasks.json
    2. For each implementation task, write ACTUAL pytest files:
       - Domain tasks → tests/unit/domain/
       - Application tasks → tests/unit/application/
       - Infrastructure tasks → tests/integration/
    3. Tests should be in RED state (failing) - this is expected (TDD)
    4. Use skipif pattern for imports that don't exist yet
    5. Update tasks.json with test_files array for each task
    6. Generate conftest.py with shared fixtures
    7. Write test-generation-report.json

    OUTPUT FILES:
    - tests/unit/domain/**/*.py (REAL pytest files)
    - tests/unit/application/**/*.py (REAL pytest files)
    - tests/integration/**/*.py (REAL pytest files)
    - tests/conftest.py
    - docs/state/test-generation-report.json
    - docs/state/tasks.json (updated with test_files)

    CRITICAL:
    - Write REAL test code, not just specifications
    - Tests should use @pytest.mark.skipif(not IMPORTS_AVAILABLE, ...)
    - Include business rules in test names (test_br_cust_001_...)
    - Tests will FAIL initially - implementation agents make them GREEN
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

3. **Verify Test Files Created** ⚠️ MANDATORY:
```python
# Check test files exist
Glob: tests/unit/**/*.py
assert len(test_files) > 0, "No test files generated"

# Check tasks.json has test_files
Read: docs/state/tasks.json
for task in tasks:
    if task["type"] == "implementation":
        assert "test_files" in task, f"Task {task['id']} missing test_files"
        assert len(task["test_files"]) > 0, f"Task {task['id']} has no test files"

print(f"✅ Generated {len(test_files)} test files for TDD")
```

**⚠️ DO NOT PROCEED TO IMPLEMENTATION WITHOUT REAL TEST FILES**

---

### **PHASE 1: Contract Generation**

**Objective**: Generate OpenAPI, TypeScript, SQL, Error Codes for each module

**Agent**: Orchestrator (YOU)

**For each module (in dependency order):**

1. **Read Contract Task**:
```python
Read: docs/state/tasks.json
# Find task where type="contracts" and module="{Module}"
```

2. **Generate Contracts**:

**A) OpenAPI Spec** - `contracts/{Module}/openapi.yaml`
**B) TypeScript Types** - `contracts/{Module}/types.ts`
**C) SQL Schema** - `contracts/{Module}/schema.sql`
**D) Error Codes** - `contracts/{Module}/error-codes.json`

3. **Validate**:
```bash
swagger-cli validate contracts/{Module}/openapi.yaml
tsc --noEmit contracts/{Module}/types.ts
```

4. **Update Task Status**:
```python
# Update task in tasks.json: status = "completed"
```

---

### **PHASE 2-3: Implementation (v4.4 Hybrid Execution)**

**Objective**: Implement Domain → Application → Infrastructure layers using hybrid two-phase workflow

**v4.4 Hybrid Flow per Layer:**

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                          │
│                                                          │
│  1. Invoke agent for PHASE A (Selection)                │
│     → Agent reads tasks, identifies theirs, saves queue │
│     → Agent returns list of tasks to execute            │
│                                                          │
│  2. For each task in queue:                             │
│     → Invoke agent for PHASE B (Execution)              │
│     → Agent implements ONE task                         │
│     → Agent runs tests, updates status                  │
│     → Agent returns completion report                   │
│     → Orchestrator continues to next task               │
│                                                          │
│  3. All tasks complete → Proceed to next layer          │
└─────────────────────────────────────────────────────────┘
```

---

#### **Step 1: DOMAIN LAYER (v4.4 Hybrid)**

**Agent**: domain-agent

**PHASE A: Task Selection**

```python
Task(
    description="Domain agent - Phase A: Task Selection",
    prompt="""
    Read .claude/agents/domain-agent.md for complete instructions.

    PHASE A: TASK SELECTION

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Identify YOUR tasks (layer = "domain", owner = null)
    3. VALIDATE each task - Is it REALLY a domain task?
    4. REJECT tasks that are NOT domain layer (re-classify them)
    5. Save queue to: docs/state/agent-queues/domain-queue.json
    6. Update tasks.json (set owner, status, rejection_history)
    7. Return list of accepted + rejected tasks

    DO NOT IMPLEMENT ANYTHING.
    ONLY select tasks, validate, and save queue.

    OUTPUT:
    - docs/state/agent-queues/domain-queue.json (with rejected_tasks)
    - docs/state/tasks.json (updated with ownership + rejections)
    - Report: list of accepted tasks + rejected tasks with suggested layers
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

**Read domain-agent's queue and handle rejections:**
```python
Read: docs/state/agent-queues/domain-queue.json
domain_tasks = queue["queue"]
rejected = queue.get("rejected_tasks", [])

print(f"📋 Domain agent accepted {len(domain_tasks)} tasks")
if rejected:
    print(f"⚠️ Rejected {len(rejected)} tasks (re-classified in tasks.json)")
```

**PHASE B: Execute Each Task One-by-One**

```python
for task in domain_tasks:
    task_id = task["task_id"]
    task_title = task["title"]

    print(f"🔄 Executing: {task_id} - {task_title}")

    Task(
        description=f"Domain agent - Execute {task_id}",
        prompt=f"""
        Read .claude/agents/domain-agent.md for complete instructions.

        PHASE B: SINGLE TASK EXECUTION

        Implement THIS task: {task_id} - {task_title}

        YOUR MISSION:
        1. Read test files for this task (from tasks.json)
        2. Understand what tests expect
        3. Implement domain code to make tests GREEN
        4. Run tests until ALL pass
        5. Update tasks.json (status = "completed")
        6. Update queue file (task status = "completed")

        CRITICAL:
        - Tests already exist (qa-test-generator wrote them)
        - You write CODE, not tests
        - Make tests GREEN
        - NO framework dependencies (pure Python only)
        """,
        subagent_type="domain-agent",
        model="sonnet"
    )

    # Verify completion
    Read: docs/state/tasks.json
    assert task["status"] == "completed"
    print(f"✅ Completed: {task_id}")
```

**Validate Domain Layer:**
```bash
pytest tests/unit/domain/ -v --cov=backend/app/domain
```

---

#### **Step 2: APPLICATION LAYER (v4.4 Hybrid)**

**Agent**: use-case-agent

**PHASE A: Task Selection**

```python
Task(
    description="Use-case agent - Phase A: Task Selection",
    prompt="""
    Read .claude/agents/use-case-agent.md for complete instructions.

    PHASE A: TASK SELECTION

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Verify domain layer is complete (required dependency)
    3. Identify YOUR tasks (layer = "application", owner = null)
    4. VALIDATE each task - Is it REALLY an application task?
    5. REJECT tasks that are NOT application layer (re-classify them)
    6. Save queue to: docs/state/agent-queues/application-queue.json
    7. Update tasks.json (set owner, status, rejection_history)

    DO NOT IMPLEMENT ANYTHING.
    ONLY select tasks, validate, and save queue.
    """,
    subagent_type="use-case-agent",
    model="sonnet"
)
```

**Read use-case-agent's queue and handle rejections:**
```python
Read: docs/state/agent-queues/application-queue.json
application_tasks = queue["queue"]
rejected = queue.get("rejected_tasks", [])

print(f"📋 Use-case agent accepted {len(application_tasks)} tasks")
if rejected:
    print(f"⚠️ Rejected {len(rejected)} tasks (re-classified in tasks.json)")
```

**PHASE B: Execute Each Task One-by-One**

```python
for task in application_tasks:
    task_id = task["task_id"]

    Task(
        description=f"Use-case agent - Execute {task_id}",
        prompt=f"""
        Read .claude/agents/use-case-agent.md for complete instructions.

        PHASE B: SINGLE TASK EXECUTION

        Implement THIS task: {task_id} - {task["title"]}

        YOUR MISSION:
        1. Read test files (tests already exist)
        2. Read domain entities (already implemented)
        3. Implement use case to make tests GREEN
        4. Define repository INTERFACE only (abstract class)
        5. Create DTOs (Pydantic models)
        6. Run tests until ALL pass
        7. Update task status

        CRITICAL:
        - Tests already exist
        - You write CODE to pass tests
        - Repository is INTERFACE only (not implementation)
        """,
        subagent_type="use-case-agent",
        model="sonnet"
    )
```

**Validate Application Layer:**
```bash
pytest tests/unit/application/ -v --cov=backend/app/application
```

---

#### **Step 3: INFRASTRUCTURE LAYER - BACKEND (v4.4 Hybrid)**

**Agent**: infrastructure-agent (1st invocation)

**Layer**: `infrastructure_backend`

**PHASE A: Task Selection**

```python
Task(
    description="Infrastructure agent (backend) - Phase A: Task Selection",
    prompt="""
    Read .claude/agents/infrastructure-agent.md for complete instructions.

    PHASE A: TASK SELECTION (Backend)

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Verify domain AND application layers are complete
    3. Identify YOUR tasks (layer = "infrastructure_backend", owner = null)
    4. VALIDATE each task - Is it REALLY an infrastructure_backend task?
    5. REJECT tasks that are NOT infrastructure_backend (re-classify them)
    6. Save queue to: docs/state/agent-queues/infrastructure-backend-queue.json
    7. Update tasks.json (set owner, status, rejection_history)

    DO NOT IMPLEMENT ANYTHING.
    ONLY select tasks, validate, and save queue.
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

**Read infrastructure-agent's queue and handle rejections:**
```python
Read: docs/state/agent-queues/infrastructure-backend-queue.json
backend_tasks = queue["queue"]
rejected = queue.get("rejected_tasks", [])

print(f"📋 Infrastructure agent (backend) accepted {len(backend_tasks)} tasks")
if rejected:
    print(f"⚠️ Rejected {len(rejected)} tasks (re-classified in tasks.json)")
```

**PHASE B: Execute Each Task**

```python
for task in backend_tasks:
    task_id = task["task_id"]

    Task(
        description=f"Infrastructure agent - Execute {task_id}",
        prompt=f"""
        Read .claude/agents/infrastructure-agent.md for complete instructions.

        PHASE B: SINGLE TASK EXECUTION

        Implement THIS task: {task_id} - {task["title"]}

        YOUR MISSION:
        1. Read test files (tests already exist)
        2. Invoke context7-agent if needed for patterns
        3. Implement ORM models / repositories / API endpoints
        4. Run tests until ALL pass
        5. Update task status

        CRITICAL:
        - Tests already exist
        - Match contracts exactly (OpenAPI, SQL schema)
        - Implement repository INTERFACE from use-case layer
        """,
        subagent_type="infrastructure-agent",
        model="sonnet"
    )
```

**Validate Backend:**
```bash
pytest tests/integration/ -v
```

---

#### **Step 4: UI Design & Approval**

**Agents**: shadcn-ui-agent, ui-approval-agent

1. **Invoke shadcn-ui-agent** for UI design:
```python
Task(
    description="Design {Module} UI",
    prompt="""
    Read .claude/agents/shadcn-ui-agent.md for instructions.
    Design UI for {module} using shadcn/ui components.
    Output: docs/ui-design/{module}-form-design.md
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

2. **Invoke ui-approval-agent** for mockup:
```python
Task(
    description="Generate UI mockup for approval",
    prompt="""
    Read .claude/agents/ui-approval-agent.md for instructions.
    Generate HTML mockup at: docs/ui-mockups/{module}-mockup.html
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

3. **Get User Approval**:
```python
AskUserQuestion(questions=[{
    "question": "Please review UI mockup. What's your feedback?",
    "header": "UI Approval",
    "options": [
        {"label": "APPROVE", "description": "Proceed with implementation"},
        {"label": "REQUEST CHANGES", "description": "Modify design"},
        {"label": "REJECT", "description": "Redesign from scratch"}
    ]
}])
```

---

#### **Step 5: INFRASTRUCTURE LAYER - FRONTEND (v4.4 Hybrid)**

**Agent**: infrastructure-agent (2nd invocation)

**Layer**: `infrastructure_frontend`

**⚠️ PREREQUISITE**: UI mockup MUST be approved.

**PHASE A: Task Selection**

```python
Task(
    description="Infrastructure agent (frontend) - Phase A: Task Selection",
    prompt="""
    Read .claude/agents/infrastructure-agent.md for complete instructions.

    PHASE A: TASK SELECTION (Frontend)

    YOUR MISSION:
    1. Verify UI mockup is approved
    2. Verify backend infrastructure is complete
    3. Identify YOUR tasks (layer = "infrastructure_frontend", owner = null)
    4. VALIDATE each task - Is it REALLY an infrastructure_frontend task?
    5. REJECT tasks that are NOT infrastructure_frontend (re-classify them)
    6. Save queue to: docs/state/agent-queues/infrastructure-frontend-queue.json
    7. Update tasks.json (set owner, status, rejection_history)

    DO NOT IMPLEMENT ANYTHING.
    ONLY select tasks, validate, and save queue.
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

**Read infrastructure-agent's queue and handle rejections:**
```python
Read: docs/state/agent-queues/infrastructure-frontend-queue.json
frontend_tasks = queue["queue"]
rejected = queue.get("rejected_tasks", [])

print(f"📋 Infrastructure agent (frontend) accepted {len(frontend_tasks)} tasks")
if rejected:
    print(f"⚠️ Rejected {len(rejected)} tasks (re-classified in tasks.json)")
```

**PHASE B: Execute Each Task**

```python
for task in frontend_tasks:
    Task(
        description=f"Infrastructure agent - Execute {task["task_id"]}",
        prompt=f"""
        Read .claude/agents/infrastructure-agent.md for instructions.

        PHASE B: SINGLE TASK EXECUTION

        Implement THIS task: {task["task_id"]} - {task["title"]}

        YOUR MISSION:
        1. Read approved UI mockup
        2. Read UI design document
        3. Invoke context7-agent for Next.js patterns
        4. Implement React component / page
        5. Run E2E tests

        CRITICAL:
        - Follow approved UI design precisely
        - Use shadcn/ui components
        """,
        subagent_type="infrastructure-agent",
        model="sonnet"
    )
```

**Validate Frontend:**
```bash
npm run build
npm run test
```

---

### **PHASE 4.5: Smoke Tests** ⚠️ MANDATORY

**Objective**: Fast API validation with REAL payloads BEFORE expensive E2E tests

**Agent**: smoke-test-agent (Orchestrator executes directly)

**⚠️ CRITICAL**: This phase catches DTO bugs in 30 seconds. **DO NOT proceed to E2E tests without 100% smoke test pass rate.**

**Steps:**

1. **Verify backend is running**:
```bash
curl -s http://localhost:8000/health
```

2. **Execute 6 critical smoke tests**:

```python
# Test 1: Health Check
# Test 2: Create Entity (MOST CRITICAL)
# Test 3: Get by ID
# Test 4: List All
# Test 5: Update
# Test 6: Delete
```

3. **Decision Logic**:
```python
if pass_rate == 1.0:
    print("✅ SMOKE TESTS PASSED - Proceed to E2E")
else:
    print("❌ SMOKE TESTS FAILED - Fix before E2E")
    # Invoke infrastructure-agent to fix
```

**Full documentation**: See `.claude/agents/smoke-test-agent.md`

---

### **PHASE 4: E2E QA with e2e-qa-agent** ⚠️ MANDATORY

**Objective**: Execute E2E tests and validate user flows

**Agent**: e2e-qa-agent (has Playwright MCP)

**⚠️ v4.3+ Rules**:
- Maximum 3 iterations before strategic decision
- Orchestrator does NOT fix code directly
- Create dynamic correction tasks per failure

**Steps:**

1. **Invoke e2e-qa-agent**:
```python
Task(
    description=f"Execute E2E tests for {module}",
    prompt="""
    Read .claude/agents/e2e-qa-agent.md for instructions.
    Execute E2E tests using Playwright MCP.
    Write report: docs/qa/e2e-report-{module}-iter-{n}.json
    """,
    subagent_type="e2e-qa-agent",
    model="sonnet"
)
```

2. **If failures, create correction tasks and invoke specialized agents**:
```python
# Group failures by responsible agent
failures_by_agent = {
    "infrastructure-agent": [...],  # frontend_rendering, api_contract
    "use-case-agent": [...],        # backend_logic
    "domain-agent": [...]           # data_validation
}

# Invoke each agent with their failures
for agent, failures in failures_by_agent.items():
    Task(
        description=f"Fix {len(failures)} E2E failures",
        prompt=f"""
        Fix these failures:
        {failures}
        """,
        subagent_type=agent,
        model="sonnet"
    )
```

3. **Strategic Decision (after 3 iterations)**:
```python
if iteration >= 3 and pass_rate < 0.95:
    AskUserQuestion(questions=[{
        "question": "E2E tests at {pass_rate}% after 3 iterations. What to do?",
        "options": [
            {"label": "Change approach", "description": "Switch tech stack"},
            {"label": "Continue (1 more)", "description": "Try 1 more iteration"},
            {"label": "Deliver as-is", "description": "Accept and document"}
        ]
    }])
```

---

### **PHASE 5: Final Validation & Delivery**

**Objective**: Validate everything works and deliver to user

**⚠️ CRITICAL CHECKLIST** (ALL must pass):

```python
# 1. tasks.json exists and all tasks completed
assert os.path.exists("docs/state/tasks.json")
assert all(t["status"] == "completed" for t in tasks)

# 2. All tests pass
assert unit_test_pass_rate == 1.0
assert integration_test_pass_rate == 1.0
assert e2e_pass_rate >= 0.95

# 3. Code coverage >= 90%
assert coverage >= 0.90

# 4. Backend + Frontend start successfully
# 5. Generate final report and README
```

**Success Message:**
```
═══════════════════════════════════════════════════════════
✅ MIGRATION COMPLETE (v4.4 Hybrid)
═══════════════════════════════════════════════════════════

📂 Project: {project_name}
📊 Statistics:
   - Modules: {total}
   - Tasks: {total}
   - Test Files: {total}
   - Pass Rate: {rate}%

📁 Code: output/{project_name}/
🚀 Run: docker-compose up

✅ All agents completed ALL assigned tasks
✅ No context overload (hybrid execution)
✅ Full traceability via queue files
═══════════════════════════════════════════════════════════
```

---

## 📊 v4.4 QUEUE FILE STRUCTURE

Each agent maintains a queue file:

```json
{
  "agent": "domain-agent",
  "created_at": "2026-01-06T10:00:00Z",
  "total_tasks": 15,
  "completed": 15,
  "queue": [
    {
      "position": 1,
      "task_id": "TASK-CUST-DOM-001",
      "title": "Implement Customer Entity",
      "module": "Customer",
      "status": "completed",
      "test_files": ["tests/unit/domain/entities/test_customer.py"]
    },
    {
      "position": 2,
      "task_id": "TASK-CUST-DOM-002",
      "title": "Implement Email Value Object",
      "module": "Customer",
      "status": "completed",
      "test_files": ["tests/unit/domain/value_objects/test_email.py"]
    }
    // ... more tasks
  ]
}
```

---

**📖 Continue Reading:**
- **→ Next**: [agent-invocation-guide.md](./agent-invocation-guide.md) - How to invoke each specialized agent
- **← Back**: [CLAUDE.md](../../CLAUDE.md) - Return to main documentation
