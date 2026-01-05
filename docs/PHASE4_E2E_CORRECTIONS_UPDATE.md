# PHASE 4 E2E Corrections - Update v4.2

**Date**: 2026-01-01
**Status**: ✅ Implemented

---

## Overview

Updated PHASE 4 (E2E QA) in CLAUDE.md to implement **agent-based corrections** instead of direct orchestrator fixes.

## Problem Solved

**Before**: Orchestrator was fixing code directly using `Edit` commands during E2E phase, which violated separation of concerns.

**After**: Orchestrator creates dynamic correction tasks and invokes specialized agents who originally wrote the code.

---

## Key Changes

### 1. CRITICAL RULES Updated (lines 751-762)

Added new rules:

```
4. YOU (Orchestrator) do NOT fix code directly - Invoke specialized agents
6. Create dynamic correction tasks for each iteration's failures
7. Invoke specialized agents based on failure category:
   - frontend_rendering, api_contract, timing_issue → infrastructure-agent
   - backend_logic, business_rule_violation → use-case-agent
   - data_validation → domain-agent
8. Loop continues: After agents fix code, re-invoke e2e-qa-agent
```

### 2. E2E Correction Loop (lines 848-972)

**New workflow**:

1. **Group failures by responsible agent**:
```python
failures_by_agent = {
    "infrastructure-agent": [],
    "use-case-agent": [],
    "domain-agent": []
}

category_agent_map = {
    "frontend_rendering": "infrastructure-agent",
    "api_contract": "infrastructure-agent",
    "timing_issue": "infrastructure-agent",
    "backend_logic": "use-case-agent",
    "data_validation": "domain-agent",
    "integration_issue": "infrastructure-agent",
    "business_rule_violation": "use-case-agent"
}
```

2. **Create dynamic correction tasks**:
```python
task_id = f"TASK-{module.upper()}-FIX-ITER{iteration}-{agent.split('-')[0].upper()}"

correction_task = {
    "id": task_id,
    "title": f"Fix E2E failures - {agent} (iteration {iteration})",
    "type": "correction",
    "module": module,
    "assigned_to": agent,
    "iteration": iteration,
    "failures_to_fix": agent_failures,
    "status": "pending"
}
```

3. **Append tasks to tasks.json dynamically**

4. **Invoke specialized agents** with failure context:
```python
Task(
    description=f"Fix {len(agent_failures)} E2E failures ({agent_name})",
    prompt=f"""
    MISSION: Fix E2E test failures from iteration {iteration}

    FAILURES TO FIX:
    - Test: {test_name}
    - Category: {category}
    - Root Cause: {root_cause}
    - Affected File: {file}:{line}
    - Suggested Fix: {fix}

    YOUR PROCESS:
    1. Read each affected file
    2. Apply suggested fix
    3. Run unit/integration tests
    4. Mark task as completed
    """,
    subagent_type=agent_name,
    model="sonnet"
)
```

5. **Loop continues** - e2e-qa-agent re-runs tests in next iteration

### 3. Complete Example Added (lines 1032-1130)

Added detailed example showing:
- Iteration 1: 3 failures (frontend, backend, domain)
- Orchestrator groups and creates 3 tasks
- Invokes 3 specialized agents
- Iteration 2: 1 new failure
- Iteration 3: All pass (100%)

**Key points highlighted**:
- ✅ Orchestrator NEVER edited code directly
- ✅ Each agent fixed their own layer
- ✅ Dynamic tasks created per iteration
- ✅ e2e-qa-agent re-executed tests after each fix

### 4. Updated CRITICAL RULES (lines 1193-1195)

Global rules section updated:

```
7. E2E Tests via Agent: Orchestrator does NOT write E2E test scripts
8. E2E Corrections via Agents: Orchestrator does NOT fix code directly
9. Fix Code, Not Tests: Agents fix APPLICATION CODE, not tests
```

---

## Workflow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    E2E TESTING LOOP                       │
└──────────────────────────────────────────────────────────┘

Iteration N:

1. Orchestrator invokes e2e-qa-agent
         │
         ▼
2. e2e-qa-agent (has Playwright MCP):
   - Writes/updates E2E tests
   - Executes tests with Playwright
   - Captures failures
   - Analyzes root causes
   - Writes report: docs/qa/e2e-report-{module}-iter-{n}.json
         │
         ▼
3. Orchestrator reads report:
   - Extracts pass_rate
   - Extracts failures list
         │
         ▼
4. If pass_rate < 95%:

   a) Group failures by agent (category_agent_map)
   b) Create dynamic correction tasks
   c) Append to tasks.json

         │
         ▼
   d) For each agent with failures:
      - Invoke infrastructure-agent (frontend/API/timing)
      - Invoke use-case-agent (backend logic)
      - Invoke domain-agent (data validation)
         │
         ▼
   e) Agents fix their code:
      - Read affected files
      - Apply suggested fixes
      - Run unit/integration tests
      - Mark task completed
         │
         ▼
5. Loop back to step 1 (Iteration N+1)

6. If pass_rate >= 95%:
   - Exit loop
   - Update global-state.json
   - Proceed to PHASE 5
```

---

## File Size Impact

- **Before**: 41,400 bytes (optimized from original)
- **After**: 45,715 bytes
- **Increase**: +4,315 bytes (10.4%)
- **Reason**: Critical functionality that ensures proper separation of concerns

---

## Benefits

1. **Separation of Concerns**: Each agent fixes their own layer
2. **Traceability**: Correction tasks documented in tasks.json
3. **Scalability**: Easy to add new failure categories
4. **Maintainability**: Clear responsibility mapping
5. **Testability**: Agents run unit tests after fixes
6. **Clean Architecture**: Layer boundaries preserved

---

## Category-to-Agent Mapping Reference

| Failure Category | Responsible Agent | Reasoning |
|------------------|-------------------|-----------|
| `frontend_rendering` | infrastructure-agent | UI components, React |
| `api_contract` | infrastructure-agent | FastAPI endpoints |
| `timing_issue` | infrastructure-agent | async/await, loading states |
| `backend_logic` | use-case-agent | Use case orchestration |
| `business_rule_violation` | use-case-agent | Business rules enforcement |
| `data_validation` | domain-agent | Value objects, entities |
| `integration_issue` | infrastructure-agent | Layer communication |

---

## Testing the Update

To verify the update works:

1. Start a migration with a module that will have E2E failures
2. Observe PHASE 4 behavior:
   - ✅ e2e-qa-agent creates and executes tests
   - ✅ Orchestrator does NOT use Edit commands
   - ✅ Orchestrator creates correction tasks in tasks.json
   - ✅ Orchestrator invokes specialized agents
   - ✅ Loop continues until 95% pass rate

---

## Next Steps

- [x] Update CLAUDE.md PHASE 4
- [x] Add CRITICAL RULES
- [x] Add complete example
- [x] Update global CRITICAL RULES section
- [ ] Test with real migration (Customer module)
- [ ] Monitor orchestrator behavior in PHASE 4
- [ ] Adjust category-agent mapping if needed

---

**Status**: ✅ Ready for testing in next migration
