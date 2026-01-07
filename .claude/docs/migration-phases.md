# Migration Phases - Task-Driven Workflow v4.4

**📖 Documentation Navigation:**
- **← Previous**: [CLAUDE.md](../../CLAUDE.md) - Framework overview
- **→ Next**: [agent-invocation-guide.md](./agent-invocation-guide.md) - Agent invocation patterns

---

## 🆕 v4.4 Task-Driven Mode

This framework executes migrations from **pre-generated task lists**. Tasks are provided as JSON files - NO SDD analysis or task generation.

---

## 🔄 Hybrid Two-Phase Execution

| Phase | Mode | What Happens |
|-------|------|--------------|
| **PHASE A** | SELECTION | Agent reads tasks, identifies theirs, validates, saves queue. **NO IMPLEMENTATION** |
| **PHASE B** | EXECUTION | Orchestrator sends ONE task at a time. Agent implements, returns. **REPEAT** |

**Benefits**:
- Agents never see more than 1 task during implementation
- No context overload (even with 200 tasks)
- Full traceability via queue files
- Agents complete ALL assigned tasks

**Queue Files**: `docs/state/agent-queues/`
- `domain-queue.json`
- `application-queue.json`
- `infrastructure-backend-queue.json`
- `infrastructure-frontend-queue.json`

---

## 🔄 Task Rejection & Re-Classification

Agents can REJECT incorrectly classified tasks and suggest the correct layer.

**During PHASE A**, each agent:
1. Identifies candidate tasks by `layer` field
2. **VALIDATES each task** - Is this REALLY my layer?
3. **Accepts valid tasks** → Adds to queue
4. **Rejects invalid tasks** → Re-classifies in tasks.json

**Validation Criteria:**

| Agent | ACCEPT | REJECT |
|-------|--------|--------|
| **domain-agent** | Entities, Value Objects, Business Rules (pure Python) | DTOs, Use Cases, ORM, APIs, Components |
| **use-case-agent** | Use Cases, DTOs, Repository Interfaces | Entities, ORM implementations, APIs |
| **infrastructure-agent** | ORM, Repositories (concrete), APIs, React Components | Entities, Value Objects, Use Cases, DTOs |

**Queue File with Rejections:**
```json
{
  "agent": "use-case-agent",
  "total_tasks": 10,
  "completed": 0,
  "rejected_tasks": [
    {
      "task_id": "TASK-045",
      "title": "Implement CustomerRepositoryImpl",
      "original_layer": "application",
      "suggested_layer": "infrastructure_backend",
      "reason": "Repository IMPLEMENTATION is infrastructure"
    }
  ],
  "queue": [...]
}
```

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
    deliverables = " ".join(task.get("deliverables", [])).lower()

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

    # Add v4.4 fields
    task["owner"] = None
    task["status"] = "pending"
    task["test_files"] = []
```

4. **Save processed tasks**:
```python
Write: docs/state/tasks.json
{
  "framework_version": "4.4-task-driven",
  "imported_from": "{user_provided_path}",
  "total_tasks": len(all_tasks),
  "tasks": all_tasks
}
```

5. **Create agent-queues directory**:
```bash
mkdir -p docs/state/agent-queues
```

---

### **PHASE 2: Test Generation (TDD)**

**Objective**: Generate REAL pytest files before implementation

**Agent**: qa-test-generator

**Steps:**

1. **Invoke qa-test-generator**:
```python
Task(
    description="Generate REAL pytest files for TDD",
    prompt="""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **YOUR MISSION**:
    1. Read ALL tasks from docs/state/tasks.json
    2. For EACH implementation task, write ACTUAL pytest files:
       - Domain tasks → tests/unit/domain/
       - Application tasks → tests/unit/application/
       - Infrastructure tasks → tests/integration/
    3. Use @pytest.mark.skipif(not IMPORTS_AVAILABLE, ...) pattern
    4. Update tasks.json with test_files array
    5. Generate conftest.py with shared fixtures

    **OUTPUT**:
    - tests/unit/domain/**/*.py (REAL pytest files)
    - tests/unit/application/**/*.py
    - tests/integration/**/*.py
    - tests/conftest.py
    - docs/state/tasks.json (updated with test_files)

    **CRITICAL**: Tests will be in RED state. Implementation agents make them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

2. **Verify tests created**:
```python
Glob: tests/**/*.py
assert len(test_files) > 0

Read: docs/state/tasks.json
# Verify test_files populated
```

---

### **PHASE 3: Domain Layer (Hybrid) - v5.0 DOMAIN EXTRACTOR**

**Agent**: domain-agent

**🆕 v5.0 PARADIGM**: Domain agent is now a **DOMAIN EXTRACTOR**, not a task validator.
It reads ALL tasks (even infrastructure) and EXTRACTS implicit domain concepts to CREATE its own domain tasks.

**PHASE A: Domain Extraction**

```python
Task(
    description="Domain agent - Phase A: Domain Extraction",
    prompt="""
    You are domain-agent. Read .claude/agents/domain-agent.md for instructions.

    **PHASE A: DOMAIN EXTRACTION (v5.0)**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json (not just layer="domain")
    2. For EACH task, extract domain concepts:
       - What entities are mentioned? (Customer, Account, Transaction)
       - What business rules are implied? (MORTGAGE cannot use PAYMENT)
       - What value objects are needed? (Money, Email, CreditScore)
       - What domain services are required?
    3. CREATE your own domain tasks (DOMAIN-001, DOMAIN-002, etc.)
    4. Save to: docs/state/domain-extracted-tasks.json
    5. Save queue to: docs/state/agent-queues/domain-queue.json

    **YOU ARE A DOMAIN EXTRACTOR, NOT A TASK VALIDATOR.**
    **DO NOT REJECT TASKS. EXTRACT DOMAIN FROM THEM.**
    **DO NOT IMPLEMENT ANYTHING YET.**
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

**Read extraction results:**
```python
Read: docs/state/domain-extracted-tasks.json
domain_tasks = data["extracted_domain_tasks"]
extraction_summary = data["extraction_summary"]

print(f"📦 Entities extracted: {len(extraction_summary['entities_found'])}")
print(f"💎 Value Objects: {len(extraction_summary['value_objects_found'])}")
print(f"📜 Business Rules: {len(extraction_summary['business_rules_found'])}")
print(f"📋 Domain Tasks Created: {len(domain_tasks)}")
```

**PHASE B: Execute Each Domain Task**

```python
for task in domain_tasks:
    task_id = task["task_id"]  # DOMAIN-001, DOMAIN-002, etc.
    task_title = task["title"]

    Task(
        description=f"Domain agent - Execute {task_id}",
        prompt=f"""
        You are domain-agent. Read .claude/agents/domain-agent.md for instructions.

        **PHASE B: SINGLE TASK EXECUTION**

        Implement THIS domain task: {task_id} - {task_title}

        YOUR MISSION:
        1. Read your extracted task from docs/state/domain-extracted-tasks.json
        2. Check if tests exist (tests/unit/domain/)
        3. Implement PURE domain code (entities, value objects, domain services)
        4. Run tests if they exist
        5. Update domain-extracted-tasks.json (status = "completed")
        6. Update queue file

        **CRITICAL**:
        - NO framework dependencies (pure Python only)
        - Use dataclasses, typing, enum, abc
        - Implement business rules from task description
        """,
        subagent_type="domain-agent",
        model="sonnet"
    )

    print(f"✅ Completed: {task_id}")
```

**Validate:**
```bash
pytest tests/unit/domain/ -v
```

---

### **PHASE 4: Application Layer (Hybrid)**

**Agent**: use-case-agent

**PHASE A: Task Selection + Validation**

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

**PHASE B: Execute Each Task** (same pattern as domain)

**Validate:**
```bash
pytest tests/unit/application/ -v
```

---

### **PHASE 5: Infrastructure Backend (Hybrid)**

**Agent**: infrastructure-agent (1st invocation)

**PHASE A: Task Selection + Validation**

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

**PHASE B: Execute Each Task** (same pattern)

**Validate:**
```bash
pytest tests/integration/ -v
```

---

### **PHASE 6: UI Design & Approval**

**Agents**: shadcn-ui-agent, ui-approval-agent

1. **Design UI**:
```python
Task(
    description="Design UI",
    prompt="""
    Read .claude/agents/shadcn-ui-agent.md for instructions.
    Design UI for module using shadcn/ui components.
    Output: docs/ui-design/{module}-design.md
    """,
    subagent_type="shadcn-ui-agent",
    model="sonnet"
)
```

2. **Generate mockup**:
```python
Task(
    description="Generate UI mockup",
    prompt="""
    Read .claude/agents/ui-approval-agent.md for instructions.
    Generate HTML mockup: docs/ui-mockups/{module}-mockup.html
    """,
    subagent_type="ui-approval-agent",
    model="sonnet"
)
```

3. **Get user approval**:
```python
AskUserQuestion(questions=[{
    "question": "Please review UI mockup. What's your feedback?",
    "header": "UI Approval",
    "options": [
        {"label": "APPROVE", "description": "Proceed with implementation"},
        {"label": "CHANGES", "description": "Request modifications"},
        {"label": "REJECT", "description": "Redesign"}
    ],
    "multiSelect": False
}])
```

---

### **PHASE 7: Infrastructure Frontend (Hybrid)**

**Agent**: infrastructure-agent (2nd invocation)

**⚠️ PREREQUISITE**: UI mockup MUST be approved

**PHASE A: Task Selection + Validation**

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

**PHASE B: Execute Each Task** (same pattern)

**Validate:**
```bash
npm run build
npm run test
```

---

### **PHASE 8: E2E Testing**

**Agent**: e2e-qa-agent

**Max 3 iterations**:

```python
for iteration in range(1, 4):
    Task(
        description=f"Execute E2E tests - Iteration {iteration}",
        prompt=f"""
        You are e2e-qa-agent. Execute E2E tests using Playwright MCP.
        Write report: docs/qa/e2e-report-iter-{iteration}.json
        """,
        subagent_type="e2e-qa-agent",
        model="sonnet"
    )

    Read: docs/qa/e2e-report-iter-{iteration}.json
    if pass_rate >= 0.95:
        print("✅ E2E tests passed!")
        break

    if iteration < 3:
        # Fix failures and retry
        fix_failures_with_agents()
```

**Strategic decision (after 3 iterations):**
```python
if pass_rate < 0.95:
    AskUserQuestion(questions=[{
        "question": f"E2E pass rate: {pass_rate*100}% after 3 iterations. What to do?",
        "header": "E2E Decision",
        "options": [
            {"label": "Continue", "description": "1 more iteration"},
            {"label": "Deliver", "description": "Accept and document issues"},
            {"label": "Stop", "description": "Manual review needed"}
        ],
        "multiSelect": False
    }])
```

---

### **PHASE 9: Completion**

**Success Criteria:**
- ✅ All tasks completed
- ✅ All tests GREEN
- ✅ E2E pass rate ≥ 95%

**Final Report:**
```
═══════════════════════════════════════════════════════════
✅ MIGRATION COMPLETE (v4.4 Task-Driven)
═══════════════════════════════════════════════════════════

📊 Statistics:
   - Total tasks: {total}
   - Completed: {completed}
   - Tests: {passed}/{total}

📁 Output: output/{project}/

🚀 Run:
   cd output/{project}
   docker-compose up

═══════════════════════════════════════════════════════════
```

---

## 📊 Queue File Structure

```json
{
  "agent": "domain-agent",
  "created_at": "2026-01-06T10:00:00Z",
  "total_tasks": 15,
  "completed": 15,
  "rejected_tasks": [],
  "queue": [
    {
      "position": 1,
      "task_id": "TASK-001",
      "title": "Implement Customer Entity",
      "module": "Customer",
      "status": "completed",
      "test_files": ["tests/unit/domain/entities/test_customer.py"]
    }
  ]
}
```

---

**📖 Next**: [agent-invocation-guide.md](./agent-invocation-guide.md)
