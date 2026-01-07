# Agent Invocation Guide v4.4 (Task-Driven)

**📖 Documentation Navigation:**
- **← Previous**: [migration-phases.md](./migration-phases.md) - Phase workflows
- **→ Agent Files**: [../agents/](../agents/) - Individual agent instruction files

---

## 🆕 v4.4 Hybrid Invocation Pattern

Implementation agents are invoked **TWICE per layer**:

| Invocation | Phase | Purpose |
|------------|-------|---------|
| **1st** | PHASE A | Agent selects tasks, validates, saves queue. **NO IMPLEMENTATION** |
| **2nd+** | PHASE B | Agent implements ONE task at a time. **REPEAT** for each task |

---

## 📚 Agent Invocation Reference

### 8 Specialized Agents

| Agent | File | Invocation |
|-------|------|------------|
| qa-test-generator | `.claude/agents/qa-test-generator.md` | `subagent_type="qa-test-generator"` |
| domain-agent | `.claude/agents/domain-agent.md` | `subagent_type="domain-agent"` |
| use-case-agent | `.claude/agents/use-case-agent.md` | `subagent_type="use-case-agent"` |
| infrastructure-agent | `.claude/agents/infrastructure-agent.md` | `subagent_type="infrastructure-agent"` |
| context7-agent | `.claude/agents/context7-agent.md` | `subagent_type="context7-agent"` |
| shadcn-ui-agent | `.claude/agents/shadcn-ui-agent.md` | `subagent_type="shadcn-ui-agent"` |
| ui-approval-agent | `.claude/agents/ui-approval-agent.md` | `subagent_type="ui-approval-agent"` |
| e2e-qa-agent | `.claude/agents/e2e-qa-agent.md` | `subagent_type="e2e-qa-agent"` |

**Note**: smoke-test-agent is executed directly by Orchestrator (Python/Bash), not via Task.

---

## 🔄 Hybrid Invocation Patterns

### Implementation Agents (domain, use-case, infrastructure)

**PHASE A: Task Selection + Validation**

```python
Task(
    description="{Agent} - Phase A: Task Selection",
    prompt="""
    You are {agent-name}. Read .claude/agents/{agent-name}.md for instructions.

    **PHASE A: TASK SELECTION**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Identify YOUR tasks (layer = "{layer}", owner = null)
    3. VALIDATE each task - Is it REALLY my layer?
    4. REJECT tasks that don't belong (re-classify them)
    5. Save queue to: docs/state/agent-queues/{queue-file}.json
    6. Update tasks.json (set owner, status, rejection_history)

    **DO NOT IMPLEMENT ANYTHING.**
    """,
    subagent_type="{agent-name}",
    model="sonnet"
)
```

**PHASE B: Single Task Execution**

```python
for task in queue["queue"]:
    Task(
        description=f"{Agent} - Execute {task['task_id']}",
        prompt=f"""
        You are {agent-name}. Read .claude/agents/{agent-name}.md for instructions.

        **PHASE B: SINGLE TASK EXECUTION**

        Implement THIS task: {task['task_id']} - {task['title']}

        YOUR MISSION:
        1. Read test files for this task
        2. Implement code to make tests GREEN
        3. Run tests until ALL pass
        4. Update tasks.json (status = "completed")
        5. Update queue file

        **CRITICAL**:
        - Tests already exist (qa-test-generator wrote them)
        - You write CODE, not tests
        - Make tests GREEN
        """,
        subagent_type="{agent-name}",
        model="sonnet"
    )
```

---

### Example: Domain Agent (v5.0 - DOMAIN EXTRACTOR)

**🆕 v5.0**: Domain agent is a **DOMAIN EXTRACTOR**, not a task validator.
It reads ALL tasks and EXTRACTS implicit domain concepts to CREATE its own tasks.

**PHASE A (EXTRACTION):**
```python
Task(
    description="Domain agent - Phase A: Domain Extraction",
    prompt="""
    You are domain-agent. Read .claude/agents/domain-agent.md for instructions.

    **PHASE A: DOMAIN EXTRACTION (v5.0)**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json (not just layer="domain")
    2. For EACH task, extract domain concepts:
       - Entities (Customer, Account, Transaction)
       - Value Objects (Money, Email, CreditScore)
       - Business Rules (BR-XXX)
       - Domain Services
    3. CREATE your own domain tasks (DOMAIN-001, DOMAIN-002, etc.)
    4. Save to: docs/state/domain-extracted-tasks.json
    5. Save queue to: docs/state/agent-queues/domain-queue.json

    **YOU ARE A DOMAIN EXTRACTOR, NOT A TASK VALIDATOR.**
    **DO NOT REJECT TASKS. EXTRACT DOMAIN FROM THEM.**
    **DO NOT IMPLEMENT ANYTHING.**
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

**PHASE B:**
```python
Task(
    description="Domain agent - Execute DOMAIN-001",
    prompt="""
    You are domain-agent. Read .claude/agents/domain-agent.md for instructions.

    **PHASE B: SINGLE TASK EXECUTION**

    Implement THIS domain task: DOMAIN-001 - Customer Domain Model

    YOUR MISSION:
    1. Read your task from docs/state/domain-extracted-tasks.json
    2. Check if tests exist (tests/unit/domain/)
    3. Implement PURE domain code (entities, value objects, services)
    4. Run tests if they exist
    5. Update domain-extracted-tasks.json (status = "completed")
    6. Update queue file

    **CRITICAL**:
    - NO framework dependencies (pure Python only)
    - Use dataclasses, typing, enum, abc
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

---

### Example: Infrastructure Agent (Backend + Frontend)

Infrastructure agent is invoked **4 times** per module:

1. **PHASE A (Backend)**: Select infrastructure_backend tasks
2. **PHASE B (Backend)**: Execute backend tasks one-by-one
3. **PHASE A (Frontend)**: Select infrastructure_frontend tasks
4. **PHASE B (Frontend)**: Execute frontend tasks one-by-one

**Backend PHASE A:**
```python
Task(
    description="Infrastructure agent (backend) - Phase A",
    prompt="""
    You are infrastructure-agent. Read .claude/agents/infrastructure-agent.md.

    **PHASE A: TASK SELECTION (Backend)**

    YOUR MISSION:
    1. Identify tasks with layer = "infrastructure_backend"
    2. VALIDATE each task - Is it REALLY backend?
    3. Save queue to: docs/state/agent-queues/infrastructure-backend-queue.json

    **DO NOT IMPLEMENT.**
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

**Frontend PHASE A:**
```python
Task(
    description="Infrastructure agent (frontend) - Phase A",
    prompt="""
    You are infrastructure-agent. Read .claude/agents/infrastructure-agent.md.

    **PHASE A: TASK SELECTION (Frontend)**

    YOUR MISSION:
    1. Verify UI mockup is approved
    2. Identify tasks with layer = "infrastructure_frontend"
    3. VALIDATE each task - Is it REALLY frontend?
    4. Save queue to: docs/state/agent-queues/infrastructure-frontend-queue.json

    **DO NOT IMPLEMENT.**
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

---

### Non-Implementation Agents (Single Invocation)

These agents don't use hybrid pattern:

**qa-test-generator:**
```python
Task(
    description="Generate REAL test files for TDD",
    prompt="""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md.

    Write REAL pytest files (.py), not just specs.

    OUTPUT:
    - tests/unit/domain/**/*.py
    - tests/unit/application/**/*.py
    - tests/integration/**/*.py
    - Update tasks.json with test_files array
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

**e2e-qa-agent:**
```python
Task(
    description="Execute E2E tests",
    prompt="""
    You are e2e-qa-agent. Read .claude/agents/e2e-qa-agent.md.

    Execute E2E tests using Playwright MCP.
    Write report: docs/qa/e2e-report-iter-{n}.json
    """,
    subagent_type="e2e-qa-agent",
    model="sonnet"
)
```

**shadcn-ui-agent:**
```python
Task(
    description="Design UI",
    prompt="""
    You are shadcn-ui-agent. Read .claude/agents/shadcn-ui-agent.md.

    Design UI using shadcn/ui components.
    Output: docs/ui-design/{module}-design.md
    """,
    subagent_type="shadcn-ui-agent",
    model="sonnet"
)
```

**ui-approval-agent:**
```python
Task(
    description="Generate UI mockup",
    prompt="""
    You are ui-approval-agent. Read .claude/agents/ui-approval-agent.md.

    Generate HTML mockup for approval.
    Output: docs/ui-mockups/{module}-mockup.html
    """,
    subagent_type="ui-approval-agent",
    model="sonnet"
)
```

**context7-agent:**
```python
Task(
    description="Research tech patterns",
    prompt="""
    You are context7-agent. Read .claude/agents/context7-agent.md.

    Research via Context7 MCP:
    - SQLAlchemy 2.0 async patterns
    - FastAPI dependency injection

    Output: docs/tech-context/{module}-context.md
    """,
    subagent_type="context7-agent",
    model="sonnet"
)
```

---

## 📊 Queue File Structure

```json
{
  "agent": "domain-agent",
  "created_at": "2026-01-06T10:00:00Z",
  "total_tasks": 15,
  "completed": 0,
  "rejected_tasks": [
    {
      "task_id": "TASK-045",
      "title": "Create CustomerDTO",
      "original_layer": "domain",
      "suggested_layer": "application",
      "reason": "DTO is application layer"
    }
  ],
  "queue": [
    {
      "position": 1,
      "task_id": "TASK-001",
      "title": "Implement Customer Entity",
      "module": "Customer",
      "status": "pending",
      "test_files": ["tests/unit/domain/entities/test_customer.py"]
    }
  ]
}
```

---

## 🔑 Key Points

1. **Hybrid execution is MANDATORY** for implementation agents
2. **PHASE A**: Agent selects + validates tasks, saves queue. **NO IMPLEMENTATION**
3. **PHASE B**: Orchestrator sends ONE task at a time
4. **Queue files track progress** - Essential for session recovery
5. **qa-test-generator writes REAL tests** - .py files
6. **Implementation agents make tests GREEN** - Don't write tests
7. **smoke-test-agent** is executed directly by Orchestrator

---

**Ready for task-driven migration!** 🚀
