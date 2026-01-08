# Migration Phases - Task-Driven Workflow v4.5

**📖 Documentation Navigation:**
- **← Previous**: [CLAUDE.md](../../CLAUDE.md) - Framework overview
- **→ Next**: [agent-invocation-guide.md](./agent-invocation-guide.md) - Agent invocation patterns

---

## 🆕 v4.5 TDD Per-Layer Mode

This framework executes migrations from **pre-generated task lists** with **TRUE TDD per layer**.

**Key Change v4.5**: QA generates tests AFTER each agent's Phase A, not upfront.

---

## 🔄 New Three-Phase Execution Per Layer

| Phase | Mode | What Happens |
|-------|------|--------------|
| **PHASE A** | SELECTION/EXTRACTION | Agent identifies/extracts tasks, saves queue. **NO IMPLEMENTATION** |
| **PHASE QA** | TEST GENERATION | qa-test-generator creates tests for ONLY the tasks in queue. **TDD** |
| **PHASE B** | EXECUTION | Agent implements ONE task at a time, makes tests GREEN. **REPEAT** |

**Benefits**:
- True TDD: Tests written specifically for what the agent found
- No wasted tests for rejected/reclassified tasks
- Tests match actual extracted domain concepts (for domain-agent v5.0)

**Queue Files**: `docs/state/agent-queues/`
- `domain-queue.json`
- `application-queue.json`
- `infrastructure-backend-queue.json`
- `infrastructure-frontend-queue.json`

---

## 📋 MIGRATION PHASES

### **PHASE 1: Task Import & Validation**

**Objective**: Import pre-generated tasks and assign layer field

**Executor**: Orchestrator (YOU)

**Steps:**

1. **User provides task file path**:
```
User: docs/input/ai_agent_tasks.json
```

2. **Read and validate tasks**:
```python
Read: {user_provided_path}

# Validate structure
for task in all_tasks:
    assert "id" in task
    assert "title" in task
    assert "description" in task
```

3. **Assign layer field to each task**:
```python
for task in all_tasks:
    title = task["title"].lower()
    description = task.get("description", "").lower()

    # Domain layer
    if any(kw in title or kw in description for kw in ["entity", "value object", "business rule"]):
        task["layer"] = "domain"
    # Application layer
    elif any(kw in title or kw in description for kw in ["use case", "dto", "repository interface"]):
        task["layer"] = "application"
    # Infrastructure backend
    elif any(kw in title or kw in description for kw in ["orm", "sqlalchemy", "api endpoint", "fastapi"]):
        task["layer"] = "infrastructure_backend"
    # Infrastructure frontend
    elif any(kw in title or kw in description for kw in ["react", "component", "next.js", "frontend"]):
        task["layer"] = "infrastructure_frontend"
    else:
        task["layer"] = None  # Will be classified during PHASE A

    # Add v4.5 fields
    task["owner"] = None
    task["status"] = "pending"
    task["test_files"] = []
```

4. **Save processed tasks**:
```python
Write: docs/state/tasks.json
{
  "framework_version": "4.5-tdd-per-layer",
  "imported_from": "{user_provided_path}",
  "total_tasks": len(all_tasks),
  "tasks": all_tasks
}
```

5. **Create directories**:
```bash
mkdir -p docs/state/agent-queues
mkdir -p tests/unit/domain tests/unit/application tests/integration
```

---

### **PHASE 2: Domain Layer (TDD Per-Layer)**

**Agent**: domain-agent

**🆕 v5.0 PARADIGM**: Domain agent is a **DOMAIN EXTRACTOR**, not a task validator.

#### PHASE 2A: Domain Extraction

```python
Task(
    description="Domain agent - Phase A: Domain Extraction",
    prompt="""
    # DOMAIN AGENT v5.0 - DOMAIN EXTRACTOR MODE

    ⚠️ CRITICAL: You are a DOMAIN EXTRACTOR, NOT a task validator.
    ⚠️ DO NOT filter/reject tasks. EXTRACT domain concepts and CREATE domain tasks.

    ## YOUR MISSION (PHASE A - EXTRACTION ONLY)

    1. Read ALL tasks from docs/state/tasks.json (ALL 110 tasks)
    2. For EACH task, extract domain concepts:
       - ENTITIES: Customer, Account, Transaction, etc.
       - VALUE OBJECTS: Money, Email, CreditScore, etc.
       - BUSINESS RULES: "MORTGAGE cannot use PAYMENT", "daily limit $10,000"
       - DOMAIN SERVICES: Validation services, calculation services
    3. CREATE your own domain tasks (DOMAIN-001, DOMAIN-002, etc.)
    4. Save to: docs/state/domain-extracted-tasks.json
    5. Save queue to: docs/state/agent-queues/domain-queue.json

    **DO NOT IMPLEMENT. ONLY EXTRACT AND CREATE TASKS.**
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

#### PHASE 2-QA: Generate Domain Tests (TDD)

```python
# Read what domain-agent extracted
Read: docs/state/agent-queues/domain-queue.json
domain_tasks = queue["queue"]

Task(
    description="QA - Generate tests for domain layer",
    prompt=f"""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **TDD MODE: Generate tests for DOMAIN layer ONLY**

    Tasks to generate tests for:
    {json.dumps(domain_tasks, indent=2)}

    YOUR MISSION:
    1. Read docs/state/domain-extracted-tasks.json for full task details
    2. For EACH domain task, write pytest files in tests/unit/domain/
    3. Tests should verify:
       - Entity creation and validation
       - Value object immutability and validation
       - Business rule enforcement
       - Domain service behavior
    4. Update domain-extracted-tasks.json with test_files array
    5. Generate tests/unit/domain/conftest.py with fixtures

    OUTPUT:
    - tests/unit/domain/entities/test_*.py
    - tests/unit/domain/value_objects/test_*.py
    - tests/unit/domain/services/test_*.py
    - tests/unit/domain/conftest.py

    **CRITICAL**: Tests will be RED. Domain agent Phase B makes them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

#### PHASE 2B: Implement Domain Tasks

```python
for task in domain_tasks:
    task_id = task["task_id"]
    task_title = task["title"]

    Task(
        description=f"Domain agent - Execute {task_id}",
        prompt=f"""
        You are domain-agent. Read .claude/agents/domain-agent.md for instructions.

        **PHASE B: SINGLE TASK EXECUTION**

        Implement THIS domain task: {task_id} - {task_title}

        YOUR MISSION:
        1. Read test files for this task (tests/unit/domain/)
        2. Implement PURE domain code to make tests GREEN
        3. Run: pytest tests/unit/domain/ -v
        4. Update domain-extracted-tasks.json (status = "completed")

        **CRITICAL**:
        - NO framework dependencies (pure Python only)
        - Make tests GREEN
        """,
        subagent_type="domain-agent",
        model="sonnet"
    )
```

**Validate:**
```bash
pytest tests/unit/domain/ -v
```

---

### **PHASE 3: Application Layer (TDD Per-Layer)**

**Agent**: use-case-agent

#### PHASE 3A: Task Selection

```python
Task(
    description="Use-case agent - Phase A: Task Selection",
    prompt="""
    You are use-case-agent. Read .claude/agents/use-case-agent.md for instructions.

    **PHASE A: TASK SELECTION**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Verify domain layer is complete
    3. Identify YOUR tasks (layer = "application", owner = null)
    4. VALIDATE each task - Is it REALLY an application task?
    5. REJECT tasks that are NOT application layer
    6. Save queue to: docs/state/agent-queues/application-queue.json

    **DO NOT IMPLEMENT ANYTHING.**
    """,
    subagent_type="use-case-agent",
    model="sonnet"
)
```

#### PHASE 3-QA: Generate Application Tests (TDD)

```python
Read: docs/state/agent-queues/application-queue.json
application_tasks = queue["queue"]

Task(
    description="QA - Generate tests for application layer",
    prompt=f"""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **TDD MODE: Generate tests for APPLICATION layer ONLY**

    Tasks to generate tests for:
    {json.dumps(application_tasks, indent=2)}

    YOUR MISSION:
    1. Read docs/state/tasks.json for full task details
    2. For EACH application task, write pytest files in tests/unit/application/
    3. Tests should verify:
       - Use case execution flow
       - DTO validation
       - Repository interface contracts (mock implementations)
       - Application exceptions
    4. Update tasks.json with test_files array for these tasks
    5. Generate tests/unit/application/conftest.py with fixtures

    OUTPUT:
    - tests/unit/application/use_cases/test_*.py
    - tests/unit/application/dtos/test_*.py
    - tests/unit/application/conftest.py

    **CRITICAL**: Tests will be RED. Use-case agent Phase B makes them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

#### PHASE 3B: Implement Application Tasks

```python
for task in application_tasks:
    task_id = task["task_id"]
    task_title = task["title"]

    Task(
        description=f"Use-case agent - Execute {task_id}",
        prompt=f"""
        You are use-case-agent. Read .claude/agents/use-case-agent.md for instructions.

        **PHASE B: SINGLE TASK EXECUTION**

        Implement THIS task: {task_id} - {task_title}

        YOUR MISSION:
        1. Read test files for this task
        2. Implement code to make tests GREEN
        3. Run: pytest tests/unit/application/ -v
        4. Update tasks.json (status = "completed")

        **CRITICAL**: Make tests GREEN. Don't write tests.
        """,
        subagent_type="use-case-agent",
        model="sonnet"
    )
```

**Validate:**
```bash
pytest tests/unit/application/ -v
```

---

### **PHASE 4: Infrastructure Backend (TDD Per-Layer)**

**Agent**: infrastructure-agent

#### PHASE 4A: Task Selection

```python
Task(
    description="Infrastructure agent (backend) - Phase A",
    prompt="""
    You are infrastructure-agent. Read .claude/agents/infrastructure-agent.md for instructions.

    **PHASE A: TASK SELECTION (Backend)**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Verify domain AND application layers are complete
    3. Identify YOUR tasks (layer = "infrastructure_backend", owner = null)
    4. VALIDATE each task - Is it REALLY infrastructure_backend?
    5. REJECT tasks that don't belong
    6. Save queue to: docs/state/agent-queues/infrastructure-backend-queue.json

    **DO NOT IMPLEMENT ANYTHING.**
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

#### PHASE 4-QA: Generate Backend Integration Tests (TDD)

```python
Read: docs/state/agent-queues/infrastructure-backend-queue.json
backend_tasks = queue["queue"]

Task(
    description="QA - Generate tests for infrastructure backend",
    prompt=f"""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **TDD MODE: Generate tests for INFRASTRUCTURE BACKEND ONLY**

    Tasks to generate tests for:
    {json.dumps(backend_tasks, indent=2)}

    YOUR MISSION:
    1. Read docs/state/tasks.json for full task details
    2. For EACH backend task, write pytest files in tests/integration/
    3. Tests should verify:
       - Repository implementations (with test DB)
       - API endpoint responses and status codes
       - ORM model mappings
       - Database migrations
    4. Update tasks.json with test_files array for these tasks
    5. Generate tests/integration/conftest.py with DB fixtures

    OUTPUT:
    - tests/integration/repositories/test_*.py
    - tests/integration/api/test_*.py
    - tests/integration/conftest.py

    **CRITICAL**: Tests will be RED. Infrastructure agent Phase B makes them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

#### PHASE 4B: Implement Backend Tasks

(Same pattern as previous layers)

**Validate:**
```bash
pytest tests/integration/ -v
```

---

### **PHASE 5: UI Design & Approval**

**Agents**: shadcn-ui-agent, ui-approval-agent

(Same as before - no changes)

---

### **PHASE 6: Infrastructure Frontend (TDD Per-Layer)**

**Agent**: infrastructure-agent (2nd invocation)

**⚠️ PREREQUISITE**: UI mockup MUST be approved

#### PHASE 6A: Task Selection

```python
Task(
    description="Infrastructure agent (frontend) - Phase A",
    prompt="""
    You are infrastructure-agent. Read .claude/agents/infrastructure-agent.md for instructions.

    **PHASE A: TASK SELECTION (Frontend)**

    YOUR MISSION:
    1. Verify UI mockup is approved
    2. Verify backend infrastructure is complete
    3. Identify YOUR tasks (layer = "infrastructure_frontend", owner = null)
    4. VALIDATE each task - Is it REALLY infrastructure_frontend?
    5. REJECT tasks that don't belong
    6. Save queue to: docs/state/agent-queues/infrastructure-frontend-queue.json

    **DO NOT IMPLEMENT ANYTHING.**
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

#### PHASE 6-QA: Generate Frontend Tests (TDD)

```python
Read: docs/state/agent-queues/infrastructure-frontend-queue.json
frontend_tasks = queue["queue"]

Task(
    description="QA - Generate tests for infrastructure frontend",
    prompt=f"""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **TDD MODE: Generate tests for INFRASTRUCTURE FRONTEND ONLY**

    Tasks to generate tests for:
    {json.dumps(frontend_tasks, indent=2)}

    YOUR MISSION:
    1. Read docs/state/tasks.json for full task details
    2. For EACH frontend task, write test files
    3. Tests should verify:
       - Component rendering
       - Form validation
       - API client calls (mocked)
       - User interactions
    4. Update tasks.json with test_files array

    OUTPUT:
    - Frontend test files (Jest/Vitest)
    - Component tests

    **CRITICAL**: Tests will be RED. Infrastructure agent Phase B makes them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

#### PHASE 6B: Implement Frontend Tasks

(Same pattern)

**Validate:**
```bash
npm run build
npm run test
```

---

### **PHASE 7: E2E Testing**

**Agent**: e2e-qa-agent

(Same as before - max 3 iterations)

---

### **PHASE 8: Completion**

**Success Criteria:**
- ✅ All tasks completed
- ✅ All tests GREEN
- ✅ E2E pass rate ≥ 95%

---

## 📊 New Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: Task Import                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: Domain Layer                                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Phase A    │ →  │  Phase QA   │ →  │  Phase B    │         │
│  │ (Extract)   │    │ (Tests)     │    │ (Implement) │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: Application Layer                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Phase A    │ →  │  Phase QA   │ →  │  Phase B    │         │
│  │ (Select)    │    │ (Tests)     │    │ (Implement) │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: Infrastructure Backend                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Phase A    │ →  │  Phase QA   │ →  │  Phase B    │         │
│  │ (Select)    │    │ (Tests)     │    │ (Implement) │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: UI Design & Approval                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6: Infrastructure Frontend                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Phase A    │ →  │  Phase QA   │ →  │  Phase B    │         │
│  │ (Select)    │    │ (Tests)     │    │ (Implement) │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 7: E2E Testing (max 3 iterations)                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 8: Completion                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

**📖 Next**: [agent-invocation-guide.md](./agent-invocation-guide.md)
