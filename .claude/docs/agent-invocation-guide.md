# Agent Invocation Guide v4.4 (Hybrid Execution)

**📖 Documentation Navigation:**
- **← Previous**: [migration-phases.md](./migration-phases.md) - Complete phase-by-phase workflow
- **→ Agent Files**: [../agents/](../agents/) - Individual agent instruction files

---

## 🆕 v4.4 HYBRID INVOCATION PATTERN

**Key Change in v4.4**: Implementation agents are invoked TWICE per layer:

| Invocation | Phase | Purpose |
|------------|-------|---------|
| **1st** | PHASE A | Agent selects tasks, saves queue. **NO IMPLEMENTATION** |
| **2nd+** | PHASE B | Agent implements ONE task at a time. **REPEAT** for each task |

**Why**: Prevents agent context overload with 50-200+ tasks.

---

## 📚 AGENT INVOCATION REFERENCE

**Understanding Agent Architecture:**

The framework uses **11 specialized agents**. **10 are registered as dedicated subagents** in Claude Code with frontmatter:
- `sdd-analyzer`
- `tech-stack-validator`
- `qa-test-generator`
- `domain-agent`
- `use-case-agent`
- `infrastructure-agent`
- `context7-agent`
- `shadcn-ui-agent`
- `ui-approval-agent`
- `e2e-qa-agent`

**1 agent** is NOT a subagent:
- `smoke-test-agent` - orchestrator executes directly (Python/Bash scripts)

**Complete Invocation Matrix:**

| Agent | File | Invocation Method |
|-------|------|-------------------|
| sdd-analyzer | `.claude/agents/sdd-analyzer.md` | `Task(..., subagent_type="sdd-analyzer")` ✅ |
| tech-stack-validator | `.claude/agents/tech-stack-validator.md` | `Task(..., subagent_type="tech-stack-validator")` ✅ |
| qa-test-generator | `.claude/agents/qa-test-generator.md` | `Task(..., subagent_type="qa-test-generator")` ✅ |
| domain-agent | `.claude/agents/domain-agent.md` | `Task(..., subagent_type="domain-agent")` ✅ |
| use-case-agent | `.claude/agents/use-case-agent.md` | `Task(..., subagent_type="use-case-agent")` ✅ |
| infrastructure-agent | `.claude/agents/infrastructure-agent.md` | `Task(..., subagent_type="infrastructure-agent")` ✅ |
| shadcn-ui-agent | `.claude/agents/shadcn-ui-agent.md` | `Task(..., subagent_type="shadcn-ui-agent")` ✅ |
| ui-approval-agent | `.claude/agents/ui-approval-agent.md` | `Task(..., subagent_type="ui-approval-agent")` ✅ |
| context7-agent | `.claude/agents/context7-agent.md` | `Task(..., subagent_type="context7-agent")` ✅ |
| smoke-test-agent | `.claude/agents/smoke-test-agent.md` | **Orchestrator executes directly** ⚠️ |
| e2e-qa-agent | `.claude/agents/e2e-qa-agent.md` | `Task(..., subagent_type="e2e-qa-agent")` ✅ |

**✅ = Registered as dedicated subagent (has frontmatter)**
**⚠️ = Not a subagent (orchestrator executes directly via Python/Bash)**

---

## 🔄 v4.4 HYBRID INVOCATION PATTERNS

### Implementation Agents (domain, use-case, infrastructure)

**PHASE A: Task Selection**

```python
# Invoke agent for task selection ONLY
Task(
    description="{Agent} - Phase A: Task Selection",
    prompt="""
    You are the {agent-name}. Read .claude/agents/{agent-name}.md for instructions.

    **PHASE A: TASK SELECTION**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Identify YOUR tasks (layer = "{layer}", owner = null)
    3. Save queue to: docs/state/agent-queues/{queue-file}.json
    4. Update tasks.json (set owner = "{agent-name}", status = "queued")
    5. Return list of task IDs in your queue

    **DO NOT IMPLEMENT ANYTHING.**
    **ONLY select tasks and save queue.**
    """,
    subagent_type="{agent-name}",
    model="sonnet"
)
```

**PHASE B: Single Task Execution (repeat for each task)**

```python
# Read queue file
Read: docs/state/agent-queues/{queue-file}.json
tasks = queue["queue"]

# Execute each task one-by-one
for task in tasks:
    Task(
        description=f"{Agent} - Execute {task['task_id']}",
        prompt=f"""
        You are the {agent-name}. Read .claude/agents/{agent-name}.md for instructions.

        **PHASE B: SINGLE TASK EXECUTION**

        Implement THIS task: {task['task_id']} - {task['title']}

        YOUR MISSION:
        1. Read test files for this task (from tasks.json → test_files)
        2. Understand what tests expect
        3. Implement code to make tests GREEN
        4. Run tests until ALL pass
        5. Update tasks.json (status = "completed")
        6. Update queue file (task status = "completed")

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

### Example: Domain Agent Hybrid Invocation

**PHASE A:**

```python
Task(
    description="Domain agent - Phase A: Task Selection",
    prompt="""
    You are the domain-agent. Read .claude/agents/domain-agent.md for instructions.

    **PHASE A: TASK SELECTION**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Identify YOUR tasks (layer = "domain", owner = null)
    3. Save queue to: docs/state/agent-queues/domain-queue.json
    4. Update tasks.json (set owner = "domain-agent", status = "queued")

    **DO NOT IMPLEMENT ANYTHING.**
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

**PHASE B (for each task):**

```python
Task(
    description="Domain agent - Execute TASK-CUST-DOM-001",
    prompt="""
    You are the domain-agent. Read .claude/agents/domain-agent.md for instructions.

    **PHASE B: SINGLE TASK EXECUTION**

    Implement THIS task: TASK-CUST-DOM-001 - Implement Customer Entity

    YOUR MISSION:
    1. Read test files: tests/unit/domain/entities/test_customer.py
    2. Understand what tests expect
    3. Implement domain code to make tests GREEN
    4. Run: pytest tests/unit/domain/entities/test_customer.py -v
    5. Update tasks.json (status = "completed")
    6. Update queue file

    **CRITICAL**:
    - Tests already exist
    - NO framework dependencies (pure Python only)
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
    You are the infrastructure-agent. Read .claude/agents/infrastructure-agent.md.

    **PHASE A: TASK SELECTION (Backend)**

    YOUR MISSION:
    1. Identify tasks with layer = "infrastructure_backend"
    2. Save queue to: docs/state/agent-queues/infrastructure-backend-queue.json

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
    You are the infrastructure-agent. Read .claude/agents/infrastructure-agent.md.

    **PHASE A: TASK SELECTION (Frontend)**

    YOUR MISSION:
    1. Verify UI mockup is approved
    2. Identify tasks with layer = "infrastructure_frontend"
    3. Save queue to: docs/state/agent-queues/infrastructure-frontend-queue.json

    **DO NOT IMPLEMENT.**
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

---

### Non-Implementation Agents (Single Invocation)

These agents don't use hybrid pattern - single invocation:

**qa-test-generator (v4.4 - writes REAL tests):**

```python
Task(
    description="Generate REAL test files for TDD",
    prompt="""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md.

    **v4.4 MISSION**: Write REAL pytest files (.py), not just specs.

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

**sdd-analyzer:**

```python
Task(
    description="Analyze SDD",
    prompt="""
    Read .claude/agents/sdd-analyzer.md for instructions.

    Analyze SDD and generate:
    - docs/analysis/module-map.json
    - docs/analysis/requirements.json
    - docs/analysis/business-rules.json
    """,
    subagent_type="sdd-analyzer",
    model="sonnet"
)
```

**tech-stack-validator:**

```python
Task(
    description="Validate tech stack compatibility",
    prompt="""
    Read .claude/agents/tech-stack-validator.md for instructions.

    Validate compatibility:
    - Radix UI + Playwright
    - FastAPI + SQLAlchemy

    Output: docs/tech-stack/compatibility-report.json
    """,
    subagent_type="tech-stack-validator",
    model="sonnet"
)
```

**e2e-qa-agent:**

```python
Task(
    description="Execute E2E tests",
    prompt="""
    Read .claude/agents/e2e-qa-agent.md for instructions.

    Execute E2E tests using Playwright MCP.
    Write report: docs/qa/e2e-report-{module}-iter-{n}.json
    """,
    subagent_type="e2e-qa-agent",
    model="sonnet"
)
```

---

## 📊 v4.4 QUEUE FILE STRUCTURE

Each implementation agent creates a queue file during PHASE A:

```json
{
  "agent": "domain-agent",
  "created_at": "2026-01-06T10:00:00Z",
  "total_tasks": 15,
  "completed": 0,
  "queue": [
    {
      "position": 1,
      "task_id": "TASK-CUST-DOM-001",
      "title": "Implement Customer Entity",
      "module": "Customer",
      "status": "pending",
      "test_files": ["tests/unit/domain/entities/test_customer.py"]
    },
    {
      "position": 2,
      "task_id": "TASK-CUST-DOM-002",
      "title": "Implement Email Value Object",
      "module": "Customer",
      "status": "pending",
      "test_files": ["tests/unit/domain/value_objects/test_email.py"]
    }
  ]
}
```

**Queue Files Location**: `docs/state/agent-queues/`
- `domain-queue.json`
- `application-queue.json`
- `infrastructure-backend-queue.json`
- `infrastructure-frontend-queue.json`

---

## 🔑 KEY POINTS (v4.4)

1. **Hybrid execution is MANDATORY** for implementation agents (domain, use-case, infrastructure)
2. **PHASE A**: Agent selects tasks, saves queue. **NO IMPLEMENTATION**
3. **PHASE B**: Orchestrator sends ONE task at a time. Agent implements and returns
4. **Queue files track progress** - essential for session recovery
5. **qa-test-generator writes REAL tests** - .py files, not just specs
6. **Implementation agents don't write tests** - they make existing tests GREEN
7. **smoke-test-agent** is executed directly by Orchestrator (not a Task invocation)

---

**Ready to migrate legacy systems with v4.4 Hybrid Execution!** 🚀
