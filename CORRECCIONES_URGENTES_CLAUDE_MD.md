# Correcciones Urgentes para CLAUDE.md

**Fecha**: 2026-01-01
**Versión actual**: v4.1-CLEAN-ARCH
**Versión objetivo**: v4.2-CLEAN-ARCH

---

## 🚨 PROBLEMAS CRÍTICOS IDENTIFICADOS

Después de ejecutar el módulo Customer se identificaron **4 problemas CRÍTICOS** que deben corregirse en CLAUDE.md:

| # | Problema | Impacto |
|---|----------|---------|
| 1 | No genera tasks.json (PHASE 0.7) | Sin trazabilidad FR→Tasks→Code |
| 2 | No invoca qa-test-generator (PHASE 0.8) | Sin TDD, tests después de código |
| 3 | No ejecuta E2E tests (PHASE 5) | Entrega sin validación |
| 4 | No usa e2e-qa-agent | Agente especializado nunca se invoca |

---

## 📝 CORRECCIÓN 1: Implementar PHASE 0.7 (Task Generation)

**Ubicación en CLAUDE.md**: Después de PHASE 0.5 (Requirements Extraction)

### Agregar esta sección completa:

```markdown
---

### **PHASE 0.7: Task Generation**

**Objective**: Convert requirements into atomic, executable tasks with clear dependencies

**Agent**: Orchestrator (YOU)

**⚠️ CRITICAL**: This phase is MANDATORY. Do NOT skip. Tasks must be generated before any implementation.

**Steps:**

1. **Read Requirements and Module Map**:
\```python
Read: docs/analysis/requirements.json
Read: docs/analysis/module-map.json
\```

2. **Generate Tasks per Module** (in dependency order: level 0, 1, 2):

For each module:

**A) Generate Contract Task**:
\```json
{
  "id": "TASK-{MODULE}-001-CONTRACTS",
  "title": "Generate {Module} Contracts",
  "type": "contracts",
  "module": "{Module}",
  "assigned_to": "orchestrator",
  "implementation_layer": null,
  "status": "pending",
  "related_requirements": ["FR-001", "FR-002", "NFR-001"],
  "business_rules": ["BR-{MODULE}-001"],
  "dependencies": [],
  "deliverables": [
    "contracts/{Module}/openapi.yaml",
    "contracts/{Module}/types.ts",
    "contracts/{Module}/schema.sql",
    "contracts/{Module}/error-codes.json"
  ],
  "acceptance_criteria": [
    "OpenAPI spec validates with swagger-cli",
    "TypeScript types compile without errors",
    "SQL schema follows naming conventions"
  ]
}
\```

**B) Generate Domain Task**:
\```json
{
  "id": "TASK-{MODULE}-002-DOMAIN",
  "title": "Implement {Module} Domain Layer",
  "type": "implementation",
  "module": "{Module}",
  "assigned_to": "domain-agent",
  "implementation_layer": "domain",
  "status": "pending",
  "dependencies": ["TASK-{MODULE}-001-CONTRACTS"],
  "related_requirements": ["FR-001", "FR-002"],
  "business_rules": ["BR-{MODULE}-001", "BR-{MODULE}-002"],
  "deliverables": [
    "backend/app/domain/entities/{module}.py",
    "backend/app/domain/value_objects/*.py",
    "tests/unit/domain/**/*.py"
  ],
  "acceptance_criteria": [
    "All business rules enforced in domain layer",
    "No framework dependencies (pure Python)",
    "Unit tests pass with 100% coverage",
    "All value objects are immutable"
  ]
}
\```

**C) Generate Use Case Task**:
\```json
{
  "id": "TASK-{MODULE}-003-USE-CASE",
  "title": "Implement {Module} Use Cases",
  "type": "implementation",
  "module": "{Module}",
  "assigned_to": "use-case-agent",
  "implementation_layer": "use_case",
  "status": "pending",
  "dependencies": ["TASK-{MODULE}-002-DOMAIN"],
  "layer_dependencies": {
    "domain": ["TASK-{MODULE}-002-DOMAIN"]
  },
  "deliverables": [
    "backend/app/application/use_cases/{module}/*.py",
    "backend/app/application/dtos/*.py",
    "backend/app/application/interfaces/*.py",
    "tests/unit/application/**/*.py"
  ]
}
\```

**D) Generate Infrastructure Tasks**:
\```json
{
  "id": "TASK-{MODULE}-004-INFRA-DB",
  "title": "Implement {Module} Database Layer",
  "type": "implementation",
  "implementation_layer": "infrastructure",
  "assigned_to": "infrastructure-agent",
  "dependencies": ["TASK-{MODULE}-003-USE-CASE"]
},
{
  "id": "TASK-{MODULE}-005-INFRA-API",
  "title": "Implement {Module} API Endpoints",
  "type": "implementation",
  "implementation_layer": "infrastructure",
  "dependencies": ["TASK-{MODULE}-004-INFRA-DB"]
},
{
  "id": "TASK-{MODULE}-006-UI-DESIGN",
  "title": "Design {Module} UI with shadcn/ui",
  "type": "ui_design",
  "assigned_to": "shadcn-ui-agent",
  "dependencies": ["TASK-{MODULE}-005-INFRA-API"]
},
{
  "id": "TASK-{MODULE}-007-INFRA-FRONTEND",
  "title": "Implement {Module} Frontend",
  "type": "implementation",
  "implementation_layer": "infrastructure",
  "assigned_to": "infrastructure-agent",
  "dependencies": ["TASK-{MODULE}-006-UI-DESIGN"]
}
\```

**E) Generate E2E Task**:
\```json
{
  "id": "TASK-{MODULE}-008-E2E-QA",
  "title": "Execute E2E Tests for {Module}",
  "type": "e2e_testing",
  "assigned_to": "e2e-qa-agent",
  "dependencies": ["TASK-{MODULE}-007-INFRA-FRONTEND"],
  "target_pass_rate": 0.95,
  "max_iterations": 5
}
\```

3. **Write tasks.json**:
\```python
Write: docs/state/tasks.json
{
  "project_name": "{project}",
  "framework_version": "4.2-clean-arch",
  "generated_date": "{date}",
  "total_tasks": X,
  "tasks": [...]
}
\```

4. **Verify tasks.json Structure**:
\```python
Read: docs/state/tasks.json
# Verify all required fields present
# Verify dependencies are valid
\```

**Tasks Schema**: See `docs/schemas/tasks-schema.ts`

**⚠️ DO NOT PROCEED TO PHASE 0.8 WITHOUT GENERATING tasks.json**

---
```

---

## 📝 CORRECCIÓN 2: Implementar PHASE 0.8 (TDD Test Specification)

**Ubicación en CLAUDE.md**: Después de PHASE 0.7 (Task Generation)

### Agregar esta sección completa:

```markdown
---

### **PHASE 0.8: Test Specification Enrichment (TDD)**

**Objective**: Enrich tasks.json with comprehensive test specifications BEFORE implementation

**Agent**: qa-test-generator

**⚠️ CRITICAL**: This phase is MANDATORY for TDD. Tests must be specified BEFORE code is written.

**Steps:**

1. **Verify tasks.json Exists**:
\```python
Read: docs/state/tasks.json
# If file doesn't exist, go back to PHASE 0.7
\```

2. **Invoke qa-test-generator**:
\```python
Task(
    description="Enrich tasks with TDD test specifications",
    prompt="""
    Read .claude/agents/qa-test-generator.md for your instructions.

    INPUT FILES:
    - docs/state/tasks.json (without test_strategy)
    - docs/analysis/requirements.json
    - docs/analysis/business-rules.json

    YOUR MISSION:
    For EACH implementation task (type="implementation"), add test_strategy:

    {
      "test_strategy": {
        "unit_tests": [
          {
            "name": "test_customer_creation_valid_data",
            "scenario": "Happy path - create customer with valid data",
            "description": "Customer should be created successfully with all valid fields",
            "arrange": "Create CustomerCreate DTO with valid name, email, phone, address, income, debt",
            "act": "Call Customer() constructor with valid data",
            "assert": "Customer is created, credit_score is calculated correctly (>= 750)",
            "mocks_required": [],
            "test_type": "unit",
            "target_layer": "domain"
          },
          {
            "name": "test_customer_creation_low_credit_score",
            "scenario": "Credit score below threshold (BR-CUST-001 violation)",
            "description": "Customer creation should fail if credit score < 750",
            "arrange": "Create data with income=10000, debt=9000",
            "act": "Call Customer() constructor",
            "assert": "Raises CreditScoreTooLowError with message 'Credit score 85 is below minimum 750'",
            "mocks_required": [],
            "test_type": "unit",
            "target_layer": "domain",
            "validates_business_rule": "BR-CUST-001"
          }
        ],
        "integration_tests": [
          {
            "name": "test_create_customer_api_endpoint",
            "scenario": "POST /api/v1/customers/ with valid data",
            "arrange": "Start test database, prepare valid customer JSON",
            "act": "POST to /api/v1/customers/",
            "assert": "Returns 201, customer saved in DB, credit_score calculated",
            "mocks_required": [],
            "test_type": "integration",
            "target_layer": "infrastructure"
          }
        ],
        "e2e_tests": [
          {
            "name": "test_create_customer_full_flow",
            "scenario": "User fills form, submits, sees success message",
            "user_story": "As a bank employee, I want to create a new customer so that they can open an account",
            "steps": [
              "Navigate to /customers/new",
              "Fill name: 'John Doe'",
              "Fill email: 'john@example.com'",
              "Fill phone: '+1234567890'",
              "Fill address: '123 Main St'",
              "Fill income: 50000",
              "Fill debt: 5000",
              "Observe credit score preview: 765",
              "Click 'Create Customer'",
              "Verify redirect to /customers/{id}",
              "Verify success toast appears",
              "Verify customer name displayed"
            ],
            "test_type": "e2e",
            "tools_required": ["playwright"]
          }
        ]
      }
    }

    OUTPUT:
    - docs/state/tasks.json (UPDATED with test_strategy for all implementation tasks)

    CRITICAL RULES:
    - Every implementation task MUST have test_strategy
    - Unit tests for domain + application layers
    - Integration tests for infrastructure layer
    - E2E tests for full user flows
    - Each test has: name, scenario, arrange, act, assert, mocks_required
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
\```

3. **Verify Enrichment**:
\```python
Read: docs/state/tasks.json
# Verify ALL implementation tasks have test_strategy
# Verify test_strategy has unit_tests, integration_tests, e2e_tests
\```

4. **Validation**:
\```python
for task in tasks:
    if task["type"] == "implementation":
        assert "test_strategy" in task
        assert len(task["test_strategy"]["unit_tests"]) > 0
\```

**⚠️ DO NOT PROCEED TO IMPLEMENTATION WITHOUT ENRICHED tasks.json**

---
```

---

## 📝 CORRECCIÓN 3: Implementar PHASE 5 (E2E QA - MANDATORY)

**Ubicación en CLAUDE.md**: Reemplazar completamente la sección "PHASE 4: E2E QA"

### Reemplazar con:

```markdown
---

## PHASE 5: E2E QA with e2e-qa-agent ⚠️ MANDATORY

**Objective**: Execute E2E tests and validate user flows BEFORE delivering to user

**Agent**: e2e-qa-agent

**⚠️ CRITICAL**: This phase is MANDATORY. Do NOT skip. Do NOT deliver to user without passing E2E tests.

**When to Execute**: AFTER frontend is implemented (TASK-{MODULE}-007-INFRA-FRONTEND is completed)

**Steps:**

1. **Verify Prerequisites**:
\```python
# Backend must be running
Bash: curl -s http://localhost:8000/health
# If fails → start backend

# Frontend must be running
Bash: curl -s http://localhost:3001
# If fails → start frontend
\```

2. **Iterative E2E Testing Loop**:
\```python
iteration = 0
max_iterations = 5
pass_rate = 0.0

while iteration < max_iterations and pass_rate < 0.95:
    iteration += 1

    print(f"🧪 E2E Testing Iteration {iteration}/{max_iterations}")

    # Update global state
    Write: docs/state/global-state.json
    # modules[{module}]["e2e_iterations"] = iteration

    # Invoke e2e-qa-agent
    Task(
        description=f"Execute E2E tests for {module} (iteration {iteration})",
        prompt=f\"\"\"
        Read .claude/agents/e2e-qa-agent.md for your instructions.

        MODULE: {module}
        ITERATION: {iteration}
        MAX_ITERATIONS: {max_iterations}

        YOUR MISSION:
        1. Verify backend is running: curl http://localhost:8000/health
           - If not running: provide instructions to start
        2. Verify frontend is running: curl http://localhost:3001
           - If not running: provide instructions to start
        3. Execute Playwright tests: npx playwright test tests/e2e/{module}/
        4. For EACH failure:
           - Capture screenshot
           - Analyze error message
           - Categorize: frontend_rendering | backend_logic | api_contract | data_validation | timing_issue
           - Identify root cause
           - Identify affected file and line number
           - Suggest specific fix
        5. Calculate pass rate: passed_tests / total_tests
        6. Generate report: docs/qa/e2e-report-{module}-iter-{iteration}.json
        7. Update global-state.json with pass_rate

        REPORT FORMAT:
        {{
          "module": "{module}",
          "iteration": {iteration},
          "timestamp": "2026-01-01T12:00:00Z",
          "total_tests": 10,
          "passed": 8,
          "failed": 2,
          "pass_rate": 0.80,
          "failures": [
            {{
              "test_name": "test_create_customer_full_flow",
              "test_file": "tests/e2e/customer/test_create_customer.spec.ts",
              "error_message": "Timeout waiting for selector 'button[type=submit]'",
              "screenshot": "docs/qa/screenshots/iter-1-test-1-failure.png",
              "category": "frontend_rendering",
              "root_cause": "Button selector changed in customer-form.tsx",
              "affected_file": "frontend/components/customers/customer-form.tsx",
              "affected_line": 45,
              "suggested_fix": "Change selector to 'button[data-testid=\"submit-customer\"]'"
            }}
          ]
        }}

        DELIVERABLES:
        - docs/qa/e2e-report-{module}-iter-{iteration}.json
        - docs/qa/screenshots/ (failure screenshots)
        - Updated global-state.json with pass_rate
        \"\"\",
        subagent_type="e2e-qa-agent",
        model="sonnet"
    )

    # Read E2E report
    Read: docs/qa/e2e-report-{module}-iter-{iteration}.json
    pass_rate = report["pass_rate"]

    # Check if passed
    if pass_rate >= 0.95:
        print(f"✅ {module} E2E tests PASSED with {pass_rate*100}% pass rate")
        break

    # Analyze and fix failures (YOU - Orchestrator)
    print(f"🔧 Iteration {iteration}: Pass rate {pass_rate*100}%, fixing {len(report['failures'])} failures...")

    for failure in report["failures"]:
        print(f"  - Fixing: {failure['test_name']} ({failure['category']})")

        # Read affected file
        Read: {failure["affected_file"]}

        # Apply fix based on category and suggested_fix
        if failure["category"] == "frontend_rendering":
            # Fix React component
            Edit: {failure["affected_file"]}
            # Apply suggested_fix

        elif failure["category"] == "backend_logic":
            # Fix use case or domain logic
            Edit: {failure["affected_file"]}

        elif failure["category"] == "api_contract":
            # Fix API endpoint
            Edit: {failure["affected_file"]}

        elif failure["category"] == "data_validation":
            # Fix validation logic
            Edit: {failure["affected_file"]}

        # Re-run specific test to verify fix
        Bash: npx playwright test {failure["test_file"]} --grep "{failure['test_name']}"

# After loop: Check final result
if pass_rate < 0.95:
    # Max iterations reached without achieving 95%
    print(f"⚠️  E2E tests did not reach 95% pass rate after {max_iterations} iterations")
    print(f"    Current pass rate: {pass_rate*100}%")

    # Ask user what to do
    AskUserQuestion(
        questions=[{
            "question": f"E2E tests pass rate is {pass_rate*100}% (target: 95%). What would you like to do?",
            "header": "E2E Tests",
            "multiSelect": false,
            "options": [
                {
                    "label": "Continue fixing",
                    "description": f"Run {max_iterations} more iterations to reach 95%"
                },
                {
                    "label": "Deliver as-is",
                    "description": f"Accept current {pass_rate*100}% pass rate and deliver to user"
                },
                {
                    "label": "Manual review",
                    "description": "Review failures manually before deciding"
                }
            ]
        }]
    )

    # If user chooses "Continue fixing": run loop again
    # If user chooses "Deliver as-is": proceed to PHASE 6
    # If user chooses "Manual review": pause and wait for user

else:
    print(f"✅ E2E tests PASSED with {pass_rate*100}% pass rate after {iteration} iteration(s)")

# Update global state with final results
Write: docs/state/global-state.json
modules[{module}]["e2e_tested"] = True
modules[{module}]["e2e_pass_rate"] = pass_rate
modules[{module}]["e2e_iterations"] = iteration
modules[{module}]["e2e_report"] = f"docs/qa/e2e-report-{module}-iter-{iteration}.json"
\```

**⚠️ DO NOT PROCEED TO DELIVERY (PHASE 6) WITHOUT:**
- ✅ E2E tests executed (e2e-qa-agent invoked)
- ✅ Pass rate >= 95% OR user explicitly approved lower rate
- ✅ All failures analyzed and documented

---
```

---

## 📝 CORRECCIÓN 4: Actualizar PHASE 6 (Final Validation)

**Ubicación en CLAUDE.md**: Reemplazar la sección PHASE 6

### Reemplazar con:

```markdown
---

## PHASE 6: Final Validation & Delivery

**Objective**: Validate everything works and generate documentation ONLY IF all checks pass

**⚠️ CRITICAL VALIDATION CHECKLIST** (ALL must pass):

\```python
# 1. Verify tasks.json was generated
assert os.path.exists("docs/state/tasks.json")
assert len(tasks) > 0

# 2. Verify all tasks completed
for task in tasks:
    assert task["status"] == "completed"

# 3. Verify E2E tests passed
assert modules[{module}]["e2e_tested"] == True
assert modules[{module}]["e2e_pass_rate"] >= 0.95

# 4. Verify backend + frontend start successfully
assert backend_health_check_passes()
assert frontend_loads_successfully()

# 5. Verify all unit + integration tests pass
assert unit_tests_pass_rate == 1.0
assert integration_tests_pass_rate == 1.0

# 6. Verify code coverage
assert code_coverage >= 0.90
\```

**If ANY check fails:**
- ❌ **DO NOT DELIVER TO USER**
- 🔧 **FIX the issue**
- 🔄 **RE-RUN the checks**

**Only when ALL checks pass:**

1. **Generate Final Report**:
\```python
Write: output/{project}/docs/final-report.json
{
  "project_name": "{project}",
  "version": "4.2-clean-arch",
  "completion_date": "{date}",
  "modules_completed": X,
  "total_endpoints": Y,
  "total_tests": Z,
  "pass_rate": W,
  "code_coverage": V,
  "e2e_pass_rate": E
}
\```

2. **Generate README**:
\```python
Write: output/{project}/README.md
# Include:
# - Running with Docker
# - Running without Docker (SQLite)
# - Running tests
# - Project structure
# - API documentation
\```

3. **Success Message**:
\```
═══════════════════════════════════════════════════════════
✅ 🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE 🎉
═══════════════════════════════════════════════════════════

📂 Proyecto: {project_name}
📊 Estadísticas:
   - Módulos: {total}
   - Endpoints: {total}
   - Tests: {total}
   - Unit/Integration pass rate: 100%
   - E2E pass rate: {rate}%
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

═══════════════════════════════════════════════════════════
\```

---
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

Para implementar estas correcciones en CLAUDE.md:

- [ ] 1. Abrir `/Users/constantinostrada/Desktop/Migration-Framework/CLAUDE.md`
- [ ] 2. Buscar "PHASE 0.5: Requirements Extraction"
- [ ] 3. Después de PHASE 0.5, insertar **CORRECCIÓN 1** (PHASE 0.7)
- [ ] 4. Después de PHASE 0.7, insertar **CORRECCIÓN 2** (PHASE 0.8)
- [ ] 5. Buscar "PHASE 4: E2E QA" o similar
- [ ] 6. Reemplazar completamente con **CORRECCIÓN 3** (PHASE 5)
- [ ] 7. Buscar "PHASE 6: Final Validation"
- [ ] 8. Reemplazar completamente con **CORRECCIÓN 4** (PHASE 6 actualizado)
- [ ] 9. Guardar CLAUDE.md
- [ ] 10. Hacer backup de CLAUDE.md antes de probar

---

## 🧪 PLAN DE PRUEBA

Después de aplicar las correcciones:

1. **Borrar output del Customer module anterior**:
   ```bash
   rm -rf output/modern-banking-system
   rm -rf docs/state/*
   rm -rf docs/analysis/*
   ```

2. **Ejecutar migración desde cero**:
   ```bash
   /migrate-start
   # Proporcionar SDD path
   # Responder preguntas
   # Elegir módulo Customer
   ```

3. **Verificar que se ejecuten las nuevas fases**:
   - ✅ PHASE 0.7: Se genera `docs/state/tasks.json`
   - ✅ PHASE 0.8: tasks.json se enriquece con `test_strategy`
   - ✅ PHASE 5: Se invoca `e2e-qa-agent`
   - ✅ PHASE 6: Solo entrega si E2E >= 95%

4. **Resultado esperado**:
   - Código generado Y validado
   - E2E tests ejecutados
   - Pass rate >= 95%
   - Usuario recibe aplicación funcionando

---

## 📊 IMPACTO ESPERADO

**Antes (v4.1)**:
- ❌ Sin tasks.json
- ❌ Sin test_strategy (TDD)
- ❌ Sin E2E validation
- ❌ Entrega sin garantías
- 🎯 Confianza: 40%

**Después (v4.2)**:
- ✅ tasks.json generado
- ✅ test_strategy por tarea (TDD)
- ✅ E2E tests ejecutados
- ✅ Entrega solo si >= 95% pass
- 🎯 Confianza: 95%

---

**Generado**: 2026-01-01
**Autor**: Post-análisis Customer module implementation
**Prioridad**: **URGENTE - CRÍTICO**
