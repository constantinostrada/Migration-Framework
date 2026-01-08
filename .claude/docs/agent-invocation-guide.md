# Agent Invocation Guide v4.5 (TDD Per-Layer)

**📖 Documentation Navigation:**
- **← Previous**: [migration-phases.md](./migration-phases.md) - Phase workflows
- **→ Agent Files**: [../agents/](../agents/) - Individual agent instruction files

---

## 🆕 v4.5 TDD Per-Layer Pattern

Implementation agents are invoked **THREE times per layer**:

| Invocation | Phase | Purpose |
|------------|-------|---------|
| **1st** | PHASE A | Agent selects/extracts tasks, saves queue. **NO IMPLEMENTATION** |
| **2nd** | PHASE QA | qa-test-generator creates tests for queue tasks. **TDD** |
| **3rd+** | PHASE B | Agent implements ONE task at a time, makes tests GREEN. **REPEAT** |

**Key Change**: QA generates tests AFTER Phase A, only for tasks the agent accepted.

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

---

## 🔄 TDD Per-Layer Invocation Pattern

### Complete Flow for Each Layer

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER EXECUTION (Domain/Application/Infrastructure)            │
│                                                                 │
│  1. PHASE A: Implementation agent selects/extracts tasks        │
│     → Agent saves queue to agent-queues/{layer}-queue.json      │
│     → Returns WITHOUT implementing                               │
│                                                                 │
│  2. PHASE QA: qa-test-generator creates tests                   │
│     → Receives tasks from queue (not all tasks)                 │
│     → Writes test files for ONLY those tasks                    │
│     → Tests are RED (expected to fail)                          │
│                                                                 │
│  3. PHASE B: For each task in queue:                            │
│     → Invoke implementation agent with "Implement THIS task"    │
│     → Agent implements code to make tests GREEN                 │
│     → Updates status                                            │
│     → Repeat until queue empty                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Example: Domain Layer (v5.0 Extractor + TDD)

### PHASE A: Domain Extraction

```python
Task(
    description="Domain agent - Phase A: Domain Extraction",
    prompt="""
    # DOMAIN AGENT v5.0 - DOMAIN EXTRACTOR MODE

    ⚠️ You are a DOMAIN EXTRACTOR, NOT a task validator.
    ⚠️ DO NOT filter/reject tasks. EXTRACT domain concepts and CREATE tasks.

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Extract domain concepts from EVERY task (entities, VOs, rules)
    3. CREATE your own domain tasks (DOMAIN-001, DOMAIN-002, etc.)
    4. Save to: docs/state/domain-extracted-tasks.json
    5. Save queue to: docs/state/agent-queues/domain-queue.json

    **DO NOT IMPLEMENT. ONLY EXTRACT AND CREATE TASKS.**
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

### PHASE QA: Generate Domain Tests

```python
# Read what domain-agent extracted
domain_tasks = read_queue("domain-queue.json")

Task(
    description="QA - Generate tests for domain layer",
    prompt=f"""
    **TDD PER-LAYER MODE: Generate tests for DOMAIN layer ONLY**

    Tasks to generate tests for:
    {json.dumps(domain_tasks, indent=2)}

    YOUR MISSION:
    1. For EACH domain task above, write pytest files in tests/unit/domain/
    2. Tests verify: entities, value objects, business rules
    3. Update domain-extracted-tasks.json with test_files

    **Tests will be RED. Domain agent Phase B makes them GREEN.**
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

### PHASE B: Implement (for each task)

```python
for task in domain_tasks:
    Task(
        description=f"Domain agent - Execute {task['task_id']}",
        prompt=f"""
        **PHASE B: SINGLE TASK EXECUTION**

        Implement THIS domain task: {task['task_id']} - {task['title']}

        YOUR MISSION:
        1. Read test files for this task (tests/unit/domain/)
        2. Implement PURE domain code to make tests GREEN
        3. Run: pytest tests/unit/domain/ -v
        4. Update status to "completed"

        **CRITICAL**: Make tests GREEN. NO framework dependencies.
        """,
        subagent_type="domain-agent",
        model="sonnet"
    )
```

---

## 📋 Example: Application Layer (TDD Per-Layer)

### PHASE A: Task Selection

```python
Task(
    description="Use-case agent - Phase A: Task Selection",
    prompt="""
    **PHASE A: TASK SELECTION**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Verify domain layer is complete
    3. Identify YOUR tasks (layer = "application")
    4. VALIDATE and REJECT if needed
    5. Save queue to: docs/state/agent-queues/application-queue.json

    **DO NOT IMPLEMENT ANYTHING.**
    """,
    subagent_type="use-case-agent",
    model="sonnet"
)
```

### PHASE QA: Generate Application Tests

```python
application_tasks = read_queue("application-queue.json")

Task(
    description="QA - Generate tests for application layer",
    prompt=f"""
    **TDD PER-LAYER MODE: Generate tests for APPLICATION layer ONLY**

    Tasks to generate tests for:
    {json.dumps(application_tasks, indent=2)}

    YOUR MISSION:
    1. For EACH task above, write pytest files in tests/unit/application/
    2. Tests verify: use cases, DTOs, repository interfaces
    3. Update tasks.json with test_files

    **Tests will be RED. Use-case agent Phase B makes them GREEN.**
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

### PHASE B: Implement (same pattern)

---

## 📋 Example: Infrastructure Backend (TDD Per-Layer)

### PHASE A → PHASE QA → PHASE B (same pattern)

Tests go to `tests/integration/` and verify:
- Repository implementations
- API endpoints
- ORM models
- Database operations

---

## 📋 Example: Infrastructure Frontend (TDD Per-Layer)

### PHASE A → PHASE QA → PHASE B (same pattern)

Tests are Jest/Vitest and verify:
- Component rendering
- Form validation
- API client calls (mocked)
- User interactions

---

## 📊 Queue File Structure (v4.5)

```json
{
  "agent": "domain-agent",
  "created_at": "2026-01-07T10:00:00Z",
  "total_tasks": 12,
  "completed": 0,
  "queue": [
    {
      "position": 1,
      "task_id": "DOMAIN-001",
      "title": "Create Customer Entity",
      "status": "pending",
      "test_files": ["tests/unit/domain/entities/test_customer.py"]
    }
  ]
}
```

---

## 🔑 Key Points v4.5

1. **TDD Per-Layer is MANDATORY** - QA runs after each Phase A
2. **PHASE A**: Agent selects/extracts tasks, saves queue. **NO IMPLEMENTATION**
3. **PHASE QA**: qa-test-generator creates tests for queue tasks ONLY
4. **PHASE B**: Agent implements ONE task at a time, makes tests GREEN
5. **No wasted tests** - Tests only for accepted/created tasks
6. **Domain agent v5.0** - Extracts and CREATES tasks, doesn't validate

---

**Ready for TDD per-layer migration!** 🚀
