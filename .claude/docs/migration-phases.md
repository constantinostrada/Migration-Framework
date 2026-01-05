# Migration Phases - Complete Workflow Guide

**📖 Documentation Navigation:**
- **← Previous**: [CLAUDE.md](../../CLAUDE.md) - Framework overview and architecture
- **→ Next**: [agent-invocation-guide.md](./agent-invocation-guide.md) - Agent invocation patterns

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
  "version": "4.2-clean-arch",
  "project_name": "{project}",
  "phase": "requirements_extraction",
  "modules": {...}
}
```

---

### **PHASE 0.5: Tech Stack Validation** ⚠️ MANDATORY (v4.3)

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

**Example for Customer module:**

```json
{
  "id": "TASK-CUSTOMER-001-CONTRACTS",
  "title": "Generate Customer Contracts",
  "type": "contracts",
  "module": "Customer",
  "assigned_to": "orchestrator",
  "implementation_layer": null,
  "status": "pending",
  "related_requirements": ["FR-CUST-001", "FR-CUST-002"],
  "business_rules": ["BR-CUST-001", "BR-CUST-002"],
  "dependencies": [],
  "deliverables": [
    "contracts/Customer/openapi.yaml",
    "contracts/Customer/types.ts",
    "contracts/Customer/schema.sql",
    "contracts/Customer/error-codes.json"
  ],
  "acceptance_criteria": [
    "OpenAPI spec validates with swagger-cli",
    "TypeScript types compile without errors",
    "SQL schema follows naming conventions"
  ]
}
```

3. **Write tasks.json**:

YOU MUST iterate over ALL modules and generate ALL 8 tasks per module:

```python
# Build tasks array
all_tasks = []

for module in modules:  # From module-map.json
    module_name = module["name"]

    # TASK 1: Contracts
    all_tasks.append({
        "id": f"TASK-{module_name.upper()}-001-CONTRACTS",
        "title": f"Generate {module_name} Contracts",
        "type": "contracts",
        "module": module_name,
        "assigned_to": "orchestrator",
        "status": "pending",
        "related_requirements": module["functional_requirements"],
        "business_rules": module["business_rules"],
        "dependencies": [],
        "deliverables": [
            f"contracts/{module_name}/openapi.yaml",
            f"contracts/{module_name}/types.ts",
            f"contracts/{module_name}/schema.sql",
            f"contracts/{module_name}/error-codes.json"
        ]
    })

    # TASK 2: Domain
    all_tasks.append({
        "id": f"TASK-{module_name.upper()}-002-DOMAIN",
        "title": f"Implement {module_name} Domain Layer",
        "type": "implementation",
        "implementation_layer": "domain",
        "module": module_name,
        "assigned_to": "domain-agent",
        "status": "pending",
        "dependencies": [f"TASK-{module_name.upper()}-001-CONTRACTS"],
        "related_requirements": module["functional_requirements"],
        "business_rules": module["business_rules"]
    })

    # TASK 3: Use Case
    all_tasks.append({
        "id": f"TASK-{module_name.upper()}-003-USE-CASE",
        "title": f"Implement {module_name} Use Cases",
        "type": "implementation",
        "implementation_layer": "use_case",
        "module": module_name,
        "assigned_to": "use-case-agent",
        "status": "pending",
        "dependencies": [f"TASK-{module_name.upper()}-002-DOMAIN"]
    })

    # TASK 4-8: Infrastructure + E2E (similar pattern)
    # ... generate remaining 5 tasks

# Write tasks.json
Write: docs/state/tasks.json
{
  "project_name": project_name,
  "framework_version": "4.2-clean-arch",
  "generated_date": current_date,
  "total_tasks": len(all_tasks),
  "tasks": all_tasks
}
```

4. **Verify tasks.json was created** ⚠️ MANDATORY:
```python
Read: docs/state/tasks.json
assert len(tasks) > 0
print(f"✅ Generated {len(tasks)} tasks for migration")
```

**Tasks Schema**: See `docs/schemas/tasks-schema.ts`

**⚠️ DO NOT PROCEED TO PHASE 0.8 WITHOUT GENERATING AND VERIFYING tasks.json**

---

### **PHASE 0.8: Test Specification Enrichment (TDD)** ⚠️ MANDATORY

**Objective**: Enrich tasks.json with comprehensive test specifications BEFORE implementation

**Agent**: qa-test-generator

**⚠️ CRITICAL**: This phase is MANDATORY for TDD. Tests must be specified BEFORE code is written. Do NOT proceed to implementation without enriched tasks.json.

**YOU (Orchestrator) MUST invoke qa-test-generator agent. Do NOT skip this phase.**

**Verification**: After this phase, ALL implementation tasks in `docs/state/tasks.json` MUST have `test_strategy` field.

**Steps:**

1. **Verify tasks.json exists** ⚠️:
```python
Read: docs/state/tasks.json
# If file doesn't exist, STOP and go back to PHASE 0.7
assert os.path.exists("docs/state/tasks.json")
```

2. **Invoke qa-test-generator**:
```python
Task(
    description="Enrich tasks with TDD test specifications",
    prompt="""
    Read .claude/agents/qa-test-generator.md for instructions.

    INPUT FILES:
    - docs/state/tasks.json
    - docs/analysis/requirements.json

    YOUR MISSION:
    For each implementation task, add test_strategy:
    - Unit tests (for domain and use case layers)
    - Integration tests (for infrastructure layer)
    - E2E tests (for frontend)

    For each test case, specify:
    - name, scenario, description
    - arrange (setup), act (action), assert (expected outcome)
    - mocks_required

    OUTPUT:
    - docs/state/tasks.json (updated with test_strategy for all tasks)
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

3. **Verify Enrichment** ⚠️ MANDATORY:
```python
Read: docs/state/tasks.json
# Verify ALL implementation tasks have test_strategy
for task in tasks:
    if task["type"] == "implementation":
        assert "test_strategy" in task, f"Task {task['id']} missing test_strategy"
        assert len(task["test_strategy"]["unit_tests"]) > 0, f"Task {task['id']} has no unit tests"

print(f"✅ All {implementation_task_count} implementation tasks enriched with test specifications")
```

**⚠️ DO NOT PROCEED TO IMPLEMENTATION (PHASE 1-4) WITHOUT ENRICHED tasks.json**

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

### **PHASE 2-3: Implementation (Clean Architecture Layers)**

**Objective**: Implement Domain → Application → Infrastructure layers

**For each module:**

#### **Step 1: DOMAIN LAYER (v4.3 - Auto-Assignment)**

**Agent**: domain-agent

1. **Invoke domain-agent** (generic prompt, NO task assignment):
```python
Task(
    description="Domain layer auto-implementation",
    prompt="""
    Read .claude/agents/domain-agent.md for complete instructions.

    YOUR MISSION (v4.3 - Auto-Assignment):
    1. Read ALL tasks from docs/state/tasks.json
    2. Identify YOUR tasks (implementation_layer = "domain", owner = null)
    3. Check for conflicts (read other progress files)
    4. Claim ownership (update tasks.json with owner = "domain-agent")
    5. Initialize your progress file: docs/state/tracking/domain-agent-progress.json
    6. For each task:
       - Read test_strategy (TDD specs)
       - Generate tests FIRST
       - Implement domain entities, value objects, services
       - Run tests until 100% pass
       - Update progress.json with brief notes (2-4 sentences)
       - Update tasks.json status = "completed"

    CRITICAL:
    - NO framework dependencies (pure Python only)
    - NO FDD document generation (v4.3 change)
    - Work autonomously without orchestrator guidance
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

2. **Validate** (optional verification):
```bash
pytest tests/unit/domain/ -v --cov=backend/app/domain
```

3. **Read Agent Progress** (v4.3):
```python
Read: docs/state/tracking/domain-agent-progress.json
```

4. **NO User Approval Required** (v4.3 Change):

```
═══════════════════════════════════════════════════════════
✅ DOMAIN LAYER COMPLETE (Autonomous)
═══════════════════════════════════════════════════════════

Module: {Module}

✅ Domain entities implemented: {count}
✅ Value objects implemented: {count}
✅ Business rules enforced: {count}
✅ Tests: {passed}/{total} (100% pass rate)
✅ Code coverage: {coverage}%

📄 Progress tracked in:
   docs/state/tracking/domain-agent-progress.json

v4.3 Change: NO FDD document, NO user approval pause.
Workflow continues automatically to application layer.
═══════════════════════════════════════════════════════════
```

**Proceed immediately to application layer** (no approval wait).

---

#### **Step 2: APPLICATION LAYER (Use Cases)**

**Agent**: use-case-agent

1. **Invoke use-case-agent**:
```python
Task(
    description="Implement {Module} Use Cases",
    prompt="""
    Read .claude/agents/use-case-agent.md for instructions.

    Read your assigned tasks from docs/state/tasks.json:
    - Filter: implementation_layer = "use_case", module = "{Module}"

    For task TASK-{MODULE}-003-USE-CASE:
    1. Read domain entities (from domain-agent output)
    2. Define repository interface (ICustomerRepository) - ABSTRACT CLASS
    3. Create DTOs (Pydantic models)
    4. Generate tests with MOCKED repository
    5. Implement use cases (CreateCustomerUseCase, etc.)
    6. Run tests until 100% pass
    7. Update task status

    CRITICAL: Repository is INTERFACE only. Use domain entities.
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

2. **Validate**:
```bash
pytest tests/unit/application/ -v --cov=backend/app/application
```

---

#### **Step 3: INFRASTRUCTURE LAYER - BACKEND**

**Agent**: infrastructure-agent (1st invocation)

**Layer**: `infrastructure_backend`

**⚠️ IMPORTANT**: infrastructure-agent will invoke context7-agent AUTOMATICALLY before implementing backend.

**A) Backend Database**:
```python
Task(
    description="Implement {Module} Infrastructure - Database",
    prompt="""
    Read .claude/agents/infrastructure-agent.md for instructions.

    Task: TASK-{MODULE}-004-INFRA-DB

    WORKFLOW:
    1. Invoke context7-agent to research SQLAlchemy 2.0 patterns
    2. Read context document: docs/tech-context/{module}-database-context.md
    3. Read domain entities and use case interfaces
    4. Create SQLAlchemy ORM models (using patterns from context7-agent)
    5. Implement repository (CustomerRepositoryImpl implements ICustomerRepository)
    6. Convert: Domain Entity ↔ ORM Model
    7. Run integration tests with test database

    CRITICAL:
    - Follow context7-agent patterns (SQLAlchemy 2.0 syntax)
    - Implement interface from use-case layer
    - Use current best practices (no deprecated patterns)
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

**B) Backend API**:
```python
Task(
    description="Implement {Module} Infrastructure - API",
    prompt="""
    Task: TASK-{MODULE}-005-INFRA-API

    WORKFLOW:
    1. Invoke context7-agent to research FastAPI patterns
    2. Read context document: docs/tech-context/{module}-api-context.md
    3. Create dependency injection (FastAPI Depends)
    4. Create API endpoints matching OpenAPI spec
    5. Map domain exceptions to HTTP errors (using context7-agent patterns)
    6. Use error codes from error-codes.json
    7. Run integration tests

    CRITICAL:
    - Match OpenAPI spec exactly
    - Follow context7-agent FastAPI patterns (dependency injection, exception handling)
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

**C) UI Design** (shadcn-ui-agent):
```python
Task(
    description="Design {Module} Form UI",
    prompt="""
    Read .claude/agents/shadcn-ui-agent.md for instructions.

    Task: TASK-{MODULE}-006-UI-DESIGN

    Read context:
    - contracts/{Module}/openapi.yaml
    - contracts/{Module}/types.ts
    - contracts/{Module}/error-codes.json

    Research shadcn/ui components and create design document at:
    docs/ui-design/{module}-form-design.md

    Include:
    - Component selection (Form, Input, Button, Alert, Card)
    - Component structure (tree)
    - Validation schema (zod)
    - Error handling for all error codes
    - Accessibility plan
    - Responsive design
    - Installation commands

    CRITICAL: You only design, not implement.
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

**C.5) UI Approval** (ui-approval-agent) - ⚠️ v4.3 MANDATORY:

**Agent**: ui-approval-agent
**Invocation**: `subagent_type="Explore"` (reads `.claude/agents/ui-approval-agent.md`)

```python
Task(
    description="Generate UI mockup and get user approval for {Module}",
    prompt="""
    Read .claude/agents/ui-approval-agent.md for complete instructions.

    MODULE: {module}

    YOUR MISSION:
    1. Read UI design document: docs/ui-design/{module}-form-design.md
    2. Read OpenAPI spec: contracts/{module}/openapi.yaml
    3. Generate static HTML mockup with Tailwind CSS at:
       docs/ui-mockups/{module}-mockup.html
    4. Include:
       - All screens (list, create form, detail view)
       - Sample data
       - Interactive feedback section
    5. Present to user for approval using AskUserQuestion
    6. Iterate on feedback until approved
    7. Update global-state.json with ui_approved = True

    CRITICAL:
    - Frontend implementation BLOCKED until approval
    - User must explicitly approve design
    - Mockup must be fully styled and visually accurate
    """,
    subagent_type="Explore",
    model="sonnet"
)

# Present to user
print(f"""
═══════════════════════════════════════════════════════════
🎨 UI MOCKUP READY FOR APPROVAL
═══════════════════════════════════════════════════════════

Module: {module}

✅ HTML mockup generated: docs/ui-mockups/{module}-mockup.html

Please open the file in your browser to review the design:
- All screens included (list, create, detail)
- Fully styled with Tailwind CSS
- Sample data for realistic preview

⚠️  Frontend implementation will NOT proceed without approval
═══════════════════════════════════════════════════════════
""")

AskUserQuestion(questions=[{
    "question": f"Please review the UI mockup at docs/ui-mockups/{module}-mockup.html. What's your feedback?",
    "header": "UI Approval",
    "multiSelect": False,
    "options": [
        {"label": "APPROVE", "description": "Design looks great, proceed with implementation"},
        {"label": "REQUEST CHANGES", "description": "Modify colors/spacing/layout/components"},
        {"label": "REJECT", "description": "Redesign from scratch"}
    ]
}])

# If not approved, loop until approval
while user_response != "APPROVE":
    # Re-invoke ui-approval-agent with feedback
    # ... iterative refinement

# Once approved:
Write: docs/state/global-state.json
modules[{module}]["ui_approved"] = True
modules[{module}]["ui_mockup"] = f"docs/ui-mockups/{module}-mockup.html"
print("✅ UI approved. Proceeding to frontend implementation.")
```

**Full documentation**: See `.claude/agents/ui-approval-agent.md`

---

#### **Step 4: INFRASTRUCTURE LAYER - FRONTEND**

**Agent**: infrastructure-agent (2nd invocation)

**Layer**: `infrastructure_frontend`

**⚠️ PREREQUISITE**: UI mockup MUST be approved before this step.

**Invocation**:
```python
Task(
    description="Frontend auto-implementation",
    prompt="""
    Read .claude/agents/infrastructure-agent.md for complete instructions.

    YOUR MISSION (v4.3 - Auto-Assignment):
    1. Read ALL tasks from docs/state/tasks.json
    2. Identify YOUR tasks (implementation_layer = "infrastructure_frontend", owner = null)
    3. Claim ownership (update owner = "infrastructure-agent")
    4. For each task:
       - Invoke context7-agent to research Next.js/React patterns FIRST
       - Read approved UI mockup: docs/ui-mockups/{module}-mockup.html
       - Read UI design: docs/ui-design/{module}-form-design.md
       - Implement components following approved design
       - Create API client
       - Create pages (Next.js App Router)
       - Update progress.json with notes

    CRITICAL:
    - Only claim tasks with layer = "infrastructure_frontend"
    - Follow approved UI design precisely
    - Use Headless UI for Dialog/Modal components (not Radix UI)
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

**Validate**:
```bash
npm run build
npm run test
```

---

### **PHASE 4.5: Smoke Tests** ⚠️ MANDATORY (v4.3)

**Objective**: Fast API validation with REAL payloads BEFORE expensive E2E tests

**Agent**: smoke-test-agent

**Invocation**: **Orchestrator executes directly** (no Task tool needed - just write Python script or use Bash)

**Note**: This is NOT invoked via Task tool. The Orchestrator (you) writes a simple Python script or Bash commands to execute the 6 smoke tests directly.

**⚠️ CRITICAL**: This phase is MANDATORY. Catches DTO bugs, validation errors, and broken endpoints in 30 seconds. **DO NOT proceed to E2E tests without 100% smoke test pass rate.**

**Why This Phase**: Customer module had 152 unit/integration tests passing (100%), but API endpoint failed with real payload. Bug found after 7 E2E iterations (hours wasted). Smoke tests would have caught this in 30 seconds.

**When to Run**: AFTER infrastructure implementation (backend + frontend running) but BEFORE E2E tests.

**Verification**: After this phase:
- `docs/qa/smoke-test-report-{module}.json` MUST exist
- `pass_rate` MUST be 1.0 (100%)
- All 6 smoke tests MUST pass

**Steps:**

1. **Verify backend and frontend are running**:
```python
# Backend health check
try:
    Bash: curl -s http://localhost:8000/health
    print("✅ Backend running")
except:
    raise AssertionError("❌ Backend NOT running - start backend first")

# Frontend health check (optional for smoke tests)
try:
    Bash: curl -s http://localhost:3001
    print("✅ Frontend running")
except:
    print("⚠️  Frontend not running (not required for API smoke tests)")
```

2. **Execute 6 critical smoke tests** (directly or via Python script):

```python
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
module = "{module}"  # e.g., "Customer"

# Read exact payload from OpenAPI spec
Read: contracts/{module}/openapi.yaml
# Extract example payload from POST endpoint

results = []

# Test 1: Health Check
try:
    response = httpx.get(f"{BASE_URL}/health", timeout=5)
    assert response.status_code == 200
    results.append({"test_id": "SMOKE-001", "name": "Health Check", "status": "passed"})
except Exception as e:
    results.append({"test_id": "SMOKE-001", "name": "Health Check", "status": "failed", "error": str(e)})

# Test 2: Create Entity (MOST CRITICAL) - Use exact payload from OpenAPI
try:
    example_payload = {...}  # From OpenAPI spec
    response = httpx.post(
        f"{BASE_URL}/api/v1/{module.lower()}/",
        json=example_payload,
        timeout=10
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    created_id = response.json()["id"]
    results.append({"test_id": "SMOKE-002", "name": "Create with Real Payload", "status": "passed"})
except Exception as e:
    results.append({"test_id": "SMOKE-002", "name": "Create with Real Payload", "status": "failed", "error": str(e)})
    created_id = None

# Test 3-6: Get, List, Update, Delete (only if Test 2 passed)
if created_id:
    # ... similar pattern for remaining tests

# Generate report
report = {
    "module": module,
    "phase": "4.5-smoke-tests",
    "execution_date": datetime.now().isoformat(),
    "total_tests": 6,
    "passed": len([r for r in results if r["status"] == "passed"]),
    "failed": len([r for r in results if r["status"] == "failed"]),
    "pass_rate": len([r for r in results if r["status"] == "passed"]) / 6,
    "tests": results
}

Write: docs/qa/smoke-test-report-{module}.json
# Write report as JSON
```

3. **Decision Logic** ⚠️ MANDATORY:

```python
Read: docs/qa/smoke-test-report-{module}.json

if report["pass_rate"] == 1.0:
    print(f"✅ SMOKE TESTS PASSED (6/6)")
    print(f"✅ All basic API functionality works")
    print(f"✅ PROCEED to PHASE 4 (E2E Tests)")

    # Update global state
    Write: docs/state/global-state.json
    modules[{module}]["smoke_tests_executed"] = True
    modules[{module}]["smoke_tests_pass_rate"] = 1.0

else:
    print(f"❌ SMOKE TESTS FAILED")
    print(f"❌ Pass rate: {report['pass_rate']*100}% (Required: 100%)")
    print(f"❌ {report['failed']} test(s) failed")
    print(f"⚠️  DO NOT PROCEED to E2E tests")
    print(f"⚠️  FIX SMOKE TEST FAILURES FIRST")

    # Analyze failures
    for test in report["tests"]:
        if test["status"] == "failed":
            print(f"   - {test['name']}: {test['error']}")

            # Identify which agent to invoke
            if "SMOKE-002" in test["test_id"]:  # Create endpoint
                print(f"   → Invoke infrastructure-agent to fix API endpoint")
                print(f"   → Likely DTO mismatch or validation error")

    # STOP - Do not proceed
    raise AssertionError("Smoke tests failed - fix before E2E")
```

**Full documentation**: See `.claude/agents/smoke-test-agent.md`

**Time Saved**: 3-5 hours per module (catches bugs in 30 seconds instead of multiple E2E iterations)

**⚠️ DO NOT PROCEED TO PHASE 4 (E2E TESTS) WITHOUT 100% SMOKE TEST PASS RATE**

---

### **PHASE 4: E2E QA with e2e-qa-agent** ⚠️ MANDATORY

**Objective**: Execute E2E tests and validate user flows BEFORE delivering to user

**Agent**: e2e-qa-agent (has Playwright MCP installed)

**⚠️ CRITICAL RULES**:
1. This phase is **MANDATORY**. Do NOT skip.
2. Do NOT deliver to user without passing E2E tests.
3. **YOU (Orchestrator) do NOT write test scripts** - e2e-qa-agent has Playwright MCP and writes tests.
4. **YOU (Orchestrator) do NOT fix code directly** - Invoke specialized agents who wrote the original code.
5. **e2e-qa-agent executes tests** via Playwright MCP and returns failure analysis.
6. **Create dynamic correction tasks** for each iteration's failures (grouped by agent).
7. **Invoke specialized agents** to fix their code based on failure category:
   - `frontend_rendering`, `api_contract`, `timing_issue` → infrastructure-agent
   - `backend_logic`, `business_rule_violation` → use-case-agent
   - `data_validation` → domain-agent
8. **Loop continues**: After agents fix code, re-invoke e2e-qa-agent to verify fixes.

**When to Execute**: AFTER frontend is implemented (infrastructure-agent completes TASK-{MODULE}-007-INFRA-FRONTEND)

**Verification**: After this phase:
- `docs/qa/e2e-report-{module}-iter-{n}.json` MUST exist
- `pass_rate` MUST be >= 0.95 OR user explicitly approved lower rate
- `modules[{module}]["e2e_tested"]` MUST be True

**Steps:**

1. **Verify Prerequisites** ⚠️ MANDATORY:
```python
# Backend must be running
try:
    Bash: curl -s http://localhost:8000/health
    print("✅ Backend is running")
except:
    print("❌ Backend is NOT running. Starting backend...")
    # Start backend or provide instructions

# Frontend must be running
try:
    Bash: curl -s http://localhost:3001
    print("✅ Frontend is running")
except:
    print("❌ Frontend is NOT running. Starting frontend...")
    # Start frontend or provide instructions
```

2. **Iterative E2E Testing Loop** (Maximum 3 iterations):
```python
iteration = 0
max_iterations = 3  # v4.3: Limit to 3 iterations to prevent infinite loops
pass_rate = 0.0

while iteration < max_iterations and pass_rate < 0.95:
    iteration += 1

    # Update state
    Write: docs/state/global-state.json
    # modules.{module}.e2e_iterations = iteration

    # Invoke E2E QA Agent (has Playwright MCP)
    Task(
        description=f"Execute E2E tests for {module} (iteration {iteration})",
        prompt=f"""
        Read .claude/agents/e2e-qa-agent.md for instructions.

        MODULE: {module}
        ITERATION: {iteration}

        YOU have access to Playwright MCP for executing E2E tests.

        YOUR MISSION:
        1. Use Playwright MCP to execute E2E tests for {module}
        2. If tests don't exist yet, CREATE them based on:
           - docs/ui-design/{module}-*-design.md (user flows)
           - contracts/{module}/openapi.yaml (API endpoints to test)
           - User stories from requirements.json
        3. Execute tests with Playwright
        4. Capture screenshots of failures
        5. Analyze each failure:
           - Category (backend_logic, frontend_rendering, api_contract, data_validation, timing_issue)
           - Root cause
           - Affected file and line number
           - Suggested fix (specific code change)
        6. Write report: docs/qa/e2e-report-{module}-iter-{iteration}.json
        7. Update global-state.json with pass_rate

        CRITICAL:
        - Use Playwright MCP tools (you have access)
        - Write actual Playwright test files if they don't exist
        - Execute tests and capture real results
        - Provide actionable failure analysis with file paths and line numbers
        """,
        subagent_type="e2e-qa-agent",
        model="sonnet"
    )

    # Read report from e2e-qa-agent
    Read: docs/qa/e2e-report-{module}-iter-{iteration}.json

    # Extract pass_rate from report
    pass_rate = report["pass_rate"]
    failures = report["failures"]

    # Check pass rate
    if pass_rate >= 0.95:
        print(f"✅ {module} E2E tests PASSED with {pass_rate*100}% pass rate")
        break

    # ⚠️ CRITICAL: YOU (Orchestrator) do NOT fix code directly
    # YOU invoke specialized agents who wrote the original code

    print(f"🔧 Iteration {iteration}: Pass rate {pass_rate*100}%, fixing {len(failures)} failures...")

    # Step 1: Group failures by responsible agent
    failures_by_agent = {
        "infrastructure-agent": [],  # frontend_rendering, api_contract, timing_issue
        "use-case-agent": [],        # backend_logic (use case layer)
        "domain-agent": []           # data_validation (value objects)
    }

    # Category-to-Agent mapping
    category_agent_map = {
        "frontend_rendering": "infrastructure-agent",
        "api_contract": "infrastructure-agent",
        "timing_issue": "infrastructure-agent",
        "backend_logic": "use-case-agent",      # Most backend logic is use cases
        "data_validation": "domain-agent",      # Value object validation
        "integration_issue": "infrastructure-agent",
        "business_rule_violation": "use-case-agent"
    }

    for failure in failures:
        responsible_agent = category_agent_map.get(failure["category"], "infrastructure-agent")
        failures_by_agent[responsible_agent].append(failure)

    # Step 2: Create dynamic correction tasks for this iteration
    correction_tasks = []

    for agent, agent_failures in failures_by_agent.items():
        if len(agent_failures) == 0:
            continue

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

        correction_tasks.append(correction_task)

    # Append correction tasks to tasks.json (dynamic task generation)
    Read: docs/state/tasks.json
    tasks_data = json.loads(tasks_json)
    tasks_data["tasks"].extend(correction_tasks)
    Write: docs/state/tasks.json
    # Write updated tasks_data

    print(f"📝 Created {len(correction_tasks)} correction tasks")

    # Step 3: Invoke each specialized agent with their failures
    for task in correction_tasks:
        agent_name = task["assigned_to"]
        agent_failures = task["failures_to_fix"]

        print(f"  🔧 Invoking {agent_name} to fix {len(agent_failures)} failure(s)")

        # Build detailed prompt with failure context
        failures_context = ""
        for f in agent_failures:
            failures_context += f"""
            ---
            Test: {f['test_name']}
            Category: {f['category']}
            Root Cause: {f['root_cause']}
            Affected File: {f['affected_file']}:{f['affected_line']}
            Expected: {f['expected_behavior']}
            Actual: {f['actual_behavior']}
            Suggested Fix: {f['suggested_fix']}
            Business Rule: {f.get('business_rule', 'N/A')}
            """

        # Invoke the specialized agent
        Task(
            description=f"Fix {len(agent_failures)} E2E failures ({agent_name})",
            prompt=f"""
            Read .claude/agents/{agent_name}.md for instructions.

            MISSION: Fix E2E test failures from iteration {iteration}

            MODULE: {module}
            ITERATION: {iteration}
            YOUR TASK ID: {task['id']}

            FAILURES TO FIX ({len(agent_failures)} total):
            {failures_context}

            YOUR PROCESS:
            1. Read each affected file listed above
            2. Understand the root cause from e2e-qa-agent's analysis
            3. Apply the suggested fix (or better solution if you see one)
            4. If business rule violation: ensure rule is properly implemented
            5. Run related unit/integration tests to verify fix doesn't break anything
            6. Mark task {task['id']} as completed in tasks.json

            CRITICAL:
            - Fix ONLY the application code, NOT the E2E tests
            - E2E tests are correct - the code has bugs
            - Preserve Clean Architecture layer boundaries
            - Run unit/integration tests after each fix
            - Update task status when done
            """,
            subagent_type=agent_name,
            model="sonnet"
        )

        # Update task status
        task["status"] = "completed"

    # Update tasks.json with completed correction tasks
    Write: docs/state/tasks.json
    # Write tasks_data with updated status

    print(f"✅ All {len(correction_tasks)} correction tasks completed")
    print(f"🔄 Re-running E2E tests to verify fixes...")

    # Loop continues - next iteration will re-invoke e2e-qa-agent

# After loop: Check final result
if pass_rate < 0.95:
    # Max iterations reached without achieving 95%
    print(f"⚠️  E2E tests did not reach 95% pass rate after {max_iterations} iterations")
    print(f"    Current pass rate: {pass_rate*100}%")
    print(f"⚠️  STRATEGIC DECISION REQUIRED")

    # Analyze failure patterns to suggest approach change
    failure_categories = {}
    for failure in failures:
        category = failure["category"]
        failure_categories[category] = failure_categories.get(category, 0) + 1

    # Detect architecture incompatibility patterns
    architecture_issue = False
    if "timing_issue" in failure_categories and failure_categories["timing_issue"] >= 3:
        architecture_issue = True
        issue_type = "UI library + E2E tool incompatibility (e.g., DialogOverlay blocking clicks)"
    elif iteration >= 3 and pass_rate < 0.30:
        architecture_issue = True
        issue_type = "Multiple fundamental issues detected"

    # Ask user what to do
    options = []

    if architecture_issue:
        options.append({
            "label": "Change approach",
            "description": f"Architecture issue detected: {issue_type}. Switch tech stack (recommended)"
        })

    options.extend([
        {
            "label": "Continue fixing (1 iteration)",
            "description": "Run 1 more iteration to attempt fixes"
        },
        {
            "label": "Deliver as-is",
            "description": f"Accept {pass_rate*100}% pass rate and document known issues"
        },
        {
            "label": "Manual review",
            "description": "Review failures and decide next steps manually"
        }
    ])

    AskUserQuestion(
        questions=[{
            "question": f"E2E tests: {pass_rate*100}% pass rate after {max_iterations} iterations (target: 95%). Strategic decision required.",
            "header": "E2E Strategy",
            "multiSelect": false,
            "options": options
        }]
    )

    # Handle responses
    if user_choice == "Change approach":
        print("⚠️  ARCHITECTURE CHANGE REQUIRED")
        print("   Recommended: Invoke tech-stack-validator to find alternative")
        print("   Example: Switch from Radix UI to Headless UI or Material-UI")
        # Invoke tech-stack-validator or restart with different tech stack
    elif user_choice == "Continue fixing (1 iteration)":
        max_iterations = iteration + 1
        print(f"🔄 Running 1 additional iteration (total: {max_iterations})")
        # Loop continues for 1 more iteration
    elif user_choice == "Deliver as-is":
        print(f"⚠️  USER ACCEPTED RISK - Delivering with {pass_rate*100}% pass rate")
        print("   Known issues will be documented in delivery report")
        # Proceed to PHASE 5
    else:  # Manual review
        print("⏸️  PAUSED - Waiting for user research and decision")
        # Pause and wait for user

else:
    print(f"✅ E2E tests PASSED with {pass_rate*100}% pass rate after {iteration} iteration(s)")

# Update global state with final results
Write: docs/state/global-state.json
modules[{module}]["e2e_tested"] = True
modules[{module}]["e2e_pass_rate"] = pass_rate
modules[{module}]["e2e_iterations"] = iteration
modules[{module}]["e2e_report"] = f"docs/qa/e2e-report-{module}-iter-{iteration}.json"
```

**⚠️ DO NOT PROCEED TO DELIVERY (PHASE 5) WITHOUT:**
- ✅ E2E tests executed (e2e-qa-agent invoked)
- ✅ Pass rate >= 95% OR user explicitly approved lower rate
- ✅ All failures analyzed and documented
- ✅ global-state.json updated with e2e_tested=True

---

### **PHASE 4 - COMPLETE EXAMPLE FLOW**

**Example: Customer module E2E testing with 3 failures**

**Iteration 1:**

1. **e2e-qa-agent executes tests** and reports:
```json
{
  "iteration": 1,
  "module": "Customer",
  "pass_rate": 0.77,
  "passed": 10,
  "failed": 3,
  "failures": [
    {
      "test_name": "Customer creation shows success message",
      "category": "frontend_rendering",
      "root_cause": "Success message component not displaying after API call",
      "affected_file": "frontend/src/components/Customer/CustomerForm.tsx",
      "affected_line": 145,
      "suggested_fix": "Add success state and display <Alert variant='success'>"
    },
    {
      "test_name": "Duplicate email returns 409 error",
      "category": "backend_logic",
      "root_cause": "CreateCustomerUseCase not checking for duplicate email",
      "affected_file": "backend/app/application/use_cases/customer/create_customer.py",
      "affected_line": 28,
      "suggested_fix": "Query repository for existing email before creating"
    },
    {
      "test_name": "Credit score validation rejects invalid values",
      "category": "data_validation",
      "root_cause": "CreditScore value object not validating range",
      "affected_file": "backend/app/domain/value_objects/credit_score.py",
      "affected_line": 15,
      "suggested_fix": "Add validation: if not 0 <= value <= 850: raise ValueError"
    }
  ]
}
```

2. **Orchestrator groups failures by agent**:
```python
failures_by_agent = {
    "infrastructure-agent": [failure_1],  # frontend_rendering
    "use-case-agent": [failure_2],        # backend_logic
    "domain-agent": [failure_3]           # data_validation
}
```

3. **Orchestrator creates 3 dynamic correction tasks**:
```json
[
  {
    "id": "TASK-CUSTOMER-FIX-ITER1-INFRASTRUCTURE",
    "assigned_to": "infrastructure-agent",
    "failures_to_fix": [failure_1]
  },
  {
    "id": "TASK-CUSTOMER-FIX-ITER1-USE-CASE",
    "assigned_to": "use-case-agent",
    "failures_to_fix": [failure_2]
  },
  {
    "id": "TASK-CUSTOMER-FIX-ITER1-DOMAIN",
    "assigned_to": "domain-agent",
    "failures_to_fix": [failure_3]
  }
]
```

4. **Orchestrator invokes infrastructure-agent** with failure_1 context → fixes CustomerForm.tsx
5. **Orchestrator invokes use-case-agent** with failure_2 context → adds email uniqueness check
6. **Orchestrator invokes domain-agent** with failure_3 context → adds CreditScore validation

7. **Loop continues** → Iteration 2 starts → **e2e-qa-agent re-runs tests**

**Iteration 2:**
- 3 previous failures now pass
- New pass_rate: 0.92 (12/13 passed)
- 1 new failure found (timing issue)
- Orchestrator creates 1 correction task → invokes infrastructure-agent
- Fixes async/await issue

**Iteration 3:**
- All tests pass
- pass_rate: 1.0 (13/13 passed)
- Loop exits
- Proceeds to PHASE 5

**Key Points:**
- ✅ Orchestrator NEVER edited code directly
- ✅ Each agent fixed their own layer
- ✅ Dynamic tasks created per iteration
- ✅ e2e-qa-agent re-executed tests after each fix
- ✅ Loop continued until 95%+ pass rate

---

### **PHASE 5: Final Validation & Delivery**

**Objective**: Validate everything works and generate documentation ONLY IF all checks pass

**⚠️ CRITICAL VALIDATION CHECKLIST** (ALL must pass before delivery):

```python
# 1. Verify tasks.json was generated
assert os.path.exists("docs/state/tasks.json"), "❌ tasks.json not found - PHASE 0.7 was skipped!"
tasks = read_json("docs/state/tasks.json")
assert len(tasks) > 0, "❌ No tasks generated"
print("✅ tasks.json exists with {len(tasks)} tasks")

# 2. Verify all tasks completed
for task in tasks:
    assert task["status"] == "completed", f"❌ Task {task['id']} not completed"
print("✅ All tasks completed")

# 3. Verify E2E tests passed
assert modules[{module}]["e2e_tested"] == True, "❌ E2E tests were NOT executed - PHASE 4 was skipped!"
assert modules[{module}]["e2e_pass_rate"] >= 0.95, f"❌ E2E pass rate {modules[{module}]['e2e_pass_rate']} < 95%"
print(f"✅ E2E tests passed with {modules[{module}]['e2e_pass_rate']*100}% pass rate")

# 4. Verify backend + frontend start successfully
try:
    Bash: curl -s http://localhost:8000/health
    print("✅ Backend starts successfully")
except:
    raise AssertionError("❌ Backend does NOT start")

try:
    Bash: curl -s http://localhost:3001
    print("✅ Frontend starts successfully")
except:
    raise AssertionError("❌ Frontend does NOT start")

# 5. Verify all unit + integration tests pass
unit_pass_rate = run_unit_tests()
integration_pass_rate = run_integration_tests()
assert unit_pass_rate == 1.0, f"❌ Unit tests pass rate {unit_pass_rate} < 100%"
assert integration_pass_rate == 1.0, f"❌ Integration tests pass rate {integration_pass_rate} < 100%"
print("✅ All unit and integration tests pass (100%)")

# 6. Verify code coverage
coverage = get_code_coverage()
assert coverage >= 0.90, f"❌ Code coverage {coverage} < 90%"
print(f"✅ Code coverage: {coverage*100}%")
```

**If ANY check fails:**
- ❌ **DO NOT DELIVER TO USER**
- 🔧 **FIX the issue**
- 🔄 **RE-RUN the checks**
- ⚠️ **DO NOT skip any phase**

**Only when ALL checks pass, proceed with:**

1. **Run Full Test Suite**:
```bash
pytest output/{project}/tests/ -v --cov --cov-report=json
```

2. **Run All E2E Tests**:
```bash
npx playwright test output/{project}/tests/e2e/ --reporter=html
```

3. **Generate Final Report**:
```python
Write: output/{project}/docs/final-report.json
{
  "project_name": "{project}",
  "version": "4.2-clean-arch",
  "completion_date": "{date}",
  "modules_completed": X,
  "total_endpoints": Y,
  "total_tests": Z,
  "unit_integration_pass_rate": 1.0,
  "e2e_pass_rate": E,
  "code_coverage": V
}
```

4. **Generate README**:
```python
Write: output/{project}/README.md
# Include:
# - Running with Docker (docker-compose up)
# - Running without Docker (./start-local.sh with SQLite)
# - Running tests (pytest, playwright)
# - Project structure (Clean Architecture layers)
# - API documentation (http://localhost:8000/docs)
```

5. **Success Message**:
```
═══════════════════════════════════════════════════════════
✅ 🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE 🎉
═══════════════════════════════════════════════════════════

📂 Proyecto: {project_name}
📊 Estadísticas:
   - Módulos: {total}
   - Endpoints: {total}
   - Tests: {total}
   - Unit/Integration pass rate: 100%
   - E2E pass rate: {e2e_rate}%
   - Code coverage: {coverage}%

📁 Código generado en: output/{project_name}/

🚀 Para ejecutar localmente:
   cd output/{project_name}
   docker-compose up    # Con Docker
   ./start-local.sh     # Sin Docker (SQLite)

   Backend: http://localhost:8000
   Frontend: http://localhost:3001
   API Docs: http://localhost:8000/docs

✅ Validado con E2E tests: {e2e_pass_rate}%
✅ Todos los user flows funcionando correctamente
✅ TODAS las fases obligatorias completadas

═══════════════════════════════════════════════════════════
```

---

---

**📖 Continue Reading:**
- **→ Next**: [agent-invocation-guide.md](./agent-invocation-guide.md) - How to invoke each specialized agent
- **← Back**: [CLAUDE.md](../../CLAUDE.md) - Return to main documentation
