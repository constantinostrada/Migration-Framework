# 🚀 Migrate Start - Task-Driven Migration Framework v4.4 (Hybrid Execution)

You are starting a **task-driven migration** using the Universal Migration Framework v4.4.

## Key Changes in v4.4

**v4.3**: Agents received ALL tasks → Overwhelmed, implemented 1-2 then stopped
**v4.4**: Hybrid two-phase execution → Agents complete ALL assigned tasks

| Phase | What Happens |
|-------|--------------|
| **PHASE A** | Agent selects tasks, saves queue. **NO IMPLEMENTATION** |
| **PHASE B** | Orchestrator sends ONE task at a time. Agent implements, returns. **REPEAT** |

**Additional v4.4 Changes:**
- `qa-test-generator` writes REAL pytest files (not just specs)
- Implementation agents just make tests GREEN (don't write tests)
- Queue files track progress: `docs/state/agent-queues/`

## Your Mission

Execute a migration based on a **pre-generated task list** (JSON file with 40, 90, or 200+ tasks).

**Stack objetivo**:
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js + React + TypeScript
- **Testing**: Pytest + Playwright (TDD approach)

---

## EXECUTION STEPS

### STEP 1: Greet User (Task-Driven Mode v4.4)

```
🤖 ¡Bienvenido al Universal Migration Framework v4.4 (Hybrid Execution Mode)!

Este framework ejecuta migraciones basadas en **listas de tareas pre-generadas**.

**Modo de operación v4.4**:
1. Tú me proporcionas un archivo JSON con la lista de tareas
2. qa-test-generator escribe TESTS REALES (.py) para cada tarea
3. Cada agente:
   - FASE A: Selecciona sus tareas, guarda cola
   - FASE B: Recibe UNA tarea a la vez, implementa, retorna
4. Los agentes hacen los tests GREEN (no escriben tests)

**Ventajas v4.4**:
- Sin sobrecarga de contexto (1 tarea a la vez)
- Todos los agentes completan TODAS sus tareas
- Trazabilidad absoluta via archivos de cola

**Stack objetivo**:
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: Next.js + React + TypeScript
- Tests: Pytest + Playwright (TDD)

**¿Dónde está el archivo de tareas?**
Por favor, indícame la ruta al archivo JSON con las tareas.
Ejemplo: docs/input/ai_agent_tasks.json
```

### STEP 2: Wait for User to Provide Task File Path

User will provide path like: `docs/input/ai_agent_tasks.json`

---

### STEP 3: PHASE 0 - Task Import & Validation

**Orquestador ejecuta directamente (NO invocar agente)**

```python
# 1. Leer archivo de tareas
task_file_path = "{user_provided_path}"
Read(task_file_path)

# 2. Parse y validar estructura
# - IDs únicos
# - Campos requeridos
# - Dependencias válidas

# 3. Agregar campo "layer" a cada tarea (v4.4 CRITICAL)
for task in all_tasks:
    # Determinar layer basado en keywords/deliverables
    if "domain" in task['deliverables'] or "entity" in task['title'].lower():
        task['layer'] = "domain"
    elif "use case" in task['title'].lower() or "DTO" in task['title']:
        task['layer'] = "application"
    elif "ORM" in task['title'] or "API" in task['title'] or "database" in task['title'].lower():
        task['layer'] = "infrastructure_backend"
    elif "React" in task['title'] or "frontend" in task['title'].lower() or "component" in task['title'].lower():
        task['layer'] = "infrastructure_frontend"
    else:
        task['layer'] = None  # Will be assigned later

    # v4.4: Add owner and test_files fields
    task['owner'] = None
    task['test_files'] = []

# 4. Guardar tasks.json
Write: docs/state/tasks.json

# 5. Crear directorio de colas
mkdir -p docs/state/agent-queues
```

### STEP 4: Present Validation Summary

```
═══════════════════════════════════════════════════════════
📊 FASE 0 COMPLETADA: Importación y Validación de Tareas
═══════════════════════════════════════════════════════════

✅ **Validaciones exitosas**:
   - Tareas cargadas: {total_tasks}
   - IDs únicos: ✓
   - Estructura completa: ✓
   - Dependencias válidas: ✓

📈 **Distribución por layer (v4.4)**:
   - domain: {domain_count} tareas
   - application: {application_count} tareas
   - infrastructure_backend: {backend_count} tareas
   - infrastructure_frontend: {frontend_count} tareas

📁 **Archivos generados**:
   - docs/state/tasks.json (con campos layer, owner, test_files)
   - docs/state/agent-queues/ (directorio para colas)

🔜 **Siguiente fase**: PHASE 0.8 - Generación de Tests REALES (TDD)

¿Continuar? (yes/no)
```

---

### STEP 5: PHASE 0.8 - Real Test Generation (v4.4 CHANGE)

**Invoke qa-test-generator agent**

```python
Task(
    description="Generate REAL pytest files for TDD",
    prompt="""
    You are the qa-test-generator. Read .claude/agents/qa-test-generator.md for complete instructions.

    **v4.4 CRITICAL CHANGE**: You write REAL test files (.py), not just specs.

    **INPUT**:
    - docs/state/tasks.json ({total_tasks} tasks)

    **YOUR MISSION**:
    1. Read ALL tasks from tasks.json
    2. For EACH implementation task, write ACTUAL pytest files:
       - Domain tasks → tests/unit/domain/
       - Application tasks → tests/unit/application/
       - Infrastructure tasks → tests/integration/
    3. Use @pytest.mark.skipif(not IMPORTS_AVAILABLE, ...) pattern
    4. Update tasks.json with test_files array for each task
    5. Generate conftest.py with shared fixtures
    6. Write test-generation-report.json

    **OUTPUT FILES**:
    - tests/unit/domain/**/*.py (REAL pytest files)
    - tests/unit/application/**/*.py (REAL pytest files)
    - tests/integration/**/*.py (REAL pytest files)
    - tests/conftest.py
    - docs/state/test-generation-report.json

    **CRITICAL**: Tests will be in RED state (expected). Implementation agents make them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

**After qa-test-generator completes:**

```
✅ **PHASE 0.8 COMPLETADA: Generación de Tests Reales**

📊 Tests generados:
   - Domain tests: {domain_test_files} archivos
   - Application tests: {app_test_files} archivos
   - Integration tests: {integration_test_files} archivos

📁 Ubicación: tests/
📄 tasks.json actualizado con test_files para cada tarea

🔜 **Siguiente**: PHASE 2-3 - Implementación Híbrida
```

---

### STEP 6: PHASE 2-3 - Hybrid Execution (v4.4)

**v4.4 Hybrid Flow:**

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                          │
│                                                          │
│  For each layer (Domain → Application → Infrastructure): │
│                                                          │
│  1. PHASE A: Invoke agent for task selection            │
│     → Agent saves queue to agent-queues/{agent}.json    │
│     → Agent returns WITHOUT implementing                │
│                                                          │
│  2. PHASE B: For each task in queue:                    │
│     → Invoke agent with: "Implement THIS task: {id}"    │
│     → Agent implements ONE task                         │
│     → Agent runs tests, updates status                  │
│     → Repeat until queue empty                          │
│                                                          │
│  3. Proceed to next layer                               │
└─────────────────────────────────────────────────────────┘
```

#### STEP 6.1: DOMAIN LAYER (Hybrid)

**PHASE A: Task Selection + Validation**

```python
print("🔄 DOMAIN LAYER - PHASE A: Task Selection")

Task(
    description="Domain agent - Phase A: Task Selection",
    prompt="""
    You are the domain-agent. Read .claude/agents/domain-agent.md for complete instructions.

    **PHASE A: TASK SELECTION**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Identify YOUR tasks (layer = "domain", owner = null)
    3. VALIDATE each task - Is it REALLY a domain task? (Step 2.5 in your instructions)
    4. REJECT tasks that are NOT domain layer and re-classify them
    5. Save queue to: docs/state/agent-queues/domain-queue.json (includes rejected_tasks)
    6. Update tasks.json (set owner, status, rejection_history for rejected tasks)
    7. Return list of accepted + rejected tasks

    **DO NOT IMPLEMENT ANYTHING.**
    **ONLY select tasks, validate, and save queue.**

    OUTPUT:
    - docs/state/agent-queues/domain-queue.json (with rejected_tasks array)
    - docs/state/tasks.json (updated with ownership + rejections)
    - Report: accepted tasks + rejected tasks with suggested layers
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

**Read queue, handle rejections, and execute PHASE B:**

```python
# Read domain-agent's queue
Read: docs/state/agent-queues/domain-queue.json
domain_tasks = queue["queue"]
rejected = queue.get("rejected_tasks", [])

print(f"📋 Domain agent aceptó {len(domain_tasks)} tareas")
if rejected:
    print(f"⚠️ Rechazó {len(rejected)} tareas (re-clasificadas en tasks.json)")

# PHASE B: Execute each task one-by-one
for task in domain_tasks:
    task_id = task["task_id"]
    task_title = task["title"]

    print(f"🔄 Ejecutando: {task_id} - {task_title}")

    Task(
        description=f"Domain agent - Execute {task_id}",
        prompt=f"""
        You are the domain-agent. Read .claude/agents/domain-agent.md for instructions.

        **PHASE B: SINGLE TASK EXECUTION**

        Implement THIS task: {task_id} - {task_title}

        YOUR MISSION:
        1. Read test files for this task (from tasks.json → test_files)
        2. Understand what tests expect
        3. Implement domain code to make tests GREEN
        4. Run tests until ALL pass
        5. Update tasks.json (status = "completed")
        6. Update queue file (task status = "completed")

        **CRITICAL**:
        - Tests already exist (qa-test-generator wrote them)
        - You write CODE, not tests
        - Make tests GREEN
        - NO framework dependencies (pure Python only)
        """,
        subagent_type="domain-agent",
        model="sonnet"
    )

    print(f"✅ Completado: {task_id}")

print(f"✅ DOMAIN LAYER COMPLETE - {len(domain_tasks)} tasks")
```

#### STEP 6.2: APPLICATION LAYER (Hybrid)

**PHASE A: Task Selection + Validation**

```python
print("🔄 APPLICATION LAYER - PHASE A: Task Selection")

Task(
    description="Use-case agent - Phase A: Task Selection",
    prompt="""
    You are the use-case-agent. Read .claude/agents/use-case-agent.md for instructions.

    **PHASE A: TASK SELECTION**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Verify domain layer is complete (required dependency)
    3. Identify YOUR tasks (layer = "application", owner = null)
    4. VALIDATE each task - Is it REALLY an application task? (Step 2.5 in your instructions)
    5. REJECT tasks that are NOT application layer and re-classify them
    6. Save queue to: docs/state/agent-queues/application-queue.json (includes rejected_tasks)
    7. Update tasks.json (set owner, status, rejection_history for rejected tasks)

    **DO NOT IMPLEMENT ANYTHING.**
    **ONLY select tasks, validate, and save queue.**
    """,
    subagent_type="use-case-agent",
    model="sonnet"
)
```

**Read queue, handle rejections, and execute PHASE B:**

```python
Read: docs/state/agent-queues/application-queue.json
application_tasks = queue["queue"]
rejected = queue.get("rejected_tasks", [])

print(f"📋 Use-case agent aceptó {len(application_tasks)} tareas")
if rejected:
    print(f"⚠️ Rechazó {len(rejected)} tareas (re-clasificadas en tasks.json)")
```

**PHASE B: Execute each task** (same pattern as domain layer)

#### STEP 6.3: INFRASTRUCTURE BACKEND (Hybrid)

**PHASE A: Task Selection + Validation**

```python
print("🔄 INFRASTRUCTURE BACKEND - PHASE A: Task Selection")

Task(
    description="Infrastructure agent (backend) - Phase A: Task Selection",
    prompt="""
    You are the infrastructure-agent. Read .claude/agents/infrastructure-agent.md for instructions.

    **PHASE A: TASK SELECTION (Backend)**

    YOUR MISSION:
    1. Read ALL tasks from docs/state/tasks.json
    2. Verify domain AND application layers are complete
    3. Identify YOUR tasks (layer = "infrastructure_backend", owner = null)
    4. VALIDATE each task - Is it REALLY an infrastructure_backend task? (Step 3.5 in your instructions)
    5. REJECT tasks that are NOT infrastructure_backend and re-classify them
    6. Save queue to: docs/state/agent-queues/infrastructure-backend-queue.json (includes rejected_tasks)
    7. Update tasks.json (set owner, status, rejection_history for rejected tasks)

    **DO NOT IMPLEMENT ANYTHING.**
    **ONLY select tasks, validate, and save queue.**
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

**Read queue, handle rejections, and execute PHASE B:**

```python
Read: docs/state/agent-queues/infrastructure-backend-queue.json
backend_tasks = queue["queue"]
rejected = queue.get("rejected_tasks", [])

print(f"📋 Infrastructure agent (backend) aceptó {len(backend_tasks)} tareas")
if rejected:
    print(f"⚠️ Rechazó {len(rejected)} tareas (re-clasificadas en tasks.json)")
```

**PHASE B: Execute each task** (same pattern)

#### STEP 6.4: UI Design & Approval

```python
# 1. UI Design
Task(
    description="Design UI",
    prompt="Design UI for module using shadcn/ui components...",
    subagent_type="shadcn-ui-agent",
    model="sonnet"
)

# 2. UI Mockup
Task(
    description="Generate UI mockup",
    prompt="Generate HTML mockup for approval...",
    subagent_type="ui-approval-agent",
    model="sonnet"
)

# 3. Get user approval
AskUserQuestion(questions=[{
    "question": "Por favor revisa el mockup. ¿Qué opinas?",
    "header": "UI Approval",
    "options": [
        {"label": "APROBAR", "description": "Proceder con implementación"},
        {"label": "CAMBIOS", "description": "Modificar diseño"},
        {"label": "RECHAZAR", "description": "Rediseñar desde cero"}
    ]
}])
```

#### STEP 6.5: INFRASTRUCTURE FRONTEND (Hybrid)

**PHASE A: Task Selection + Validation**

```python
print("🔄 INFRASTRUCTURE FRONTEND - PHASE A: Task Selection")

Task(
    description="Infrastructure agent (frontend) - Phase A: Task Selection",
    prompt="""
    You are the infrastructure-agent. Read .claude/agents/infrastructure-agent.md for instructions.

    **PHASE A: TASK SELECTION (Frontend)**

    YOUR MISSION:
    1. Verify UI mockup is approved
    2. Verify backend infrastructure is complete
    3. Identify YOUR tasks (layer = "infrastructure_frontend", owner = null)
    4. VALIDATE each task - Is it REALLY an infrastructure_frontend task? (Step 3.5 in your instructions)
    5. REJECT tasks that are NOT infrastructure_frontend and re-classify them
    6. Save queue to: docs/state/agent-queues/infrastructure-frontend-queue.json (includes rejected_tasks)
    7. Update tasks.json (set owner, status, rejection_history for rejected tasks)

    **DO NOT IMPLEMENT ANYTHING.**
    **ONLY select tasks, validate, and save queue.**
    """,
    subagent_type="infrastructure-agent",
    model="sonnet"
)
```

**Read queue, handle rejections, and execute PHASE B:**

```python
Read: docs/state/agent-queues/infrastructure-frontend-queue.json
frontend_tasks = queue["queue"]
rejected = queue.get("rejected_tasks", [])

print(f"📋 Infrastructure agent (frontend) aceptó {len(frontend_tasks)} tareas")
if rejected:
    print(f"⚠️ Rechazó {len(rejected)} tareas (re-clasificadas en tasks.json)")
```

**PHASE B: Execute each task** (same pattern)

---

### STEP 7: PHASE 4.5 - Smoke Tests

```python
print("🚀 PHASE 4.5: Smoke Tests")

# Orchestrator executes directly (not an agent)
# Run 6 critical API tests with real payloads

# If pass_rate < 100%, fix before E2E
```

---

### STEP 8: PHASE 4 - E2E Tests

```python
print("🧪 PHASE 4: E2E Tests")

Task(
    description="Execute E2E tests",
    prompt="""
    You are the e2e-qa-agent. Execute E2E tests using Playwright MCP.
    Write report: docs/qa/e2e-report-{module}-iter-{n}.json
    """,
    subagent_type="e2e-qa-agent",
    model="sonnet"
)

# Max 3 iterations
# If pass_rate < 95% after 3 iterations, ask user for strategic decision
```

---

### STEP 9: Final Report

```
═══════════════════════════════════════════════════════════
✅ 🎉 MIGRACIÓN COMPLETADA (v4.4 Hybrid) 🎉
═══════════════════════════════════════════════════════════

📊 **Estadísticas**:
   - Total de tareas: {total_tasks}
   - Tareas completadas: {completed_tasks}
   - Tasa de éxito: {success_rate}%

📋 **Colas ejecutadas**:
   - domain-queue.json: {domain_count} tareas ✅
   - application-queue.json: {app_count} tareas ✅
   - infrastructure-backend-queue.json: {backend_count} tareas ✅
   - infrastructure-frontend-queue.json: {frontend_count} tareas ✅

🧪 **Tests**:
   - Tests generados: {test_files_count} archivos
   - Tests pasados: {tests_passed}/{tests_total}

📁 **Código generado en**: output/{project_name}/

🚀 **Para probar**:
   cd output/{project_name}
   docker-compose up
   # Backend: http://localhost:8000
   # Frontend: http://localhost:3000

✅ **v4.4 Benefits**:
   - Todos los agentes completaron TODAS sus tareas
   - Sin sobrecarga de contexto (1 tarea a la vez)
   - Trazabilidad absoluta via archivos de cola

═══════════════════════════════════════════════════════════
```

---

## CRITICAL RULES (v4.4)

1. **Hybrid execution is MANDATORY** - Phase A (selection) + Phase B (one-by-one execution)
2. **qa-test-generator writes REAL tests** - .py files, not just specs
3. **Implementation agents don't write tests** - They make existing tests GREEN
4. **Queue files track progress** - `docs/state/agent-queues/{agent}-queue.json`
5. **ONE task at a time during Phase B** - Never send multiple tasks
6. **tasks.json has layer field** - Required for agent task selection
7. **Sequential layer execution** - Domain → Application → Infrastructure (never reverse)
8. **Max 3 E2E iterations** - Strategic decision after 3 failures

---

## SESSION RECOVERY (v4.4)

```python
# Check queue files to determine progress
Read: docs/state/agent-queues/domain-queue.json
Read: docs/state/agent-queues/application-queue.json
Read: docs/state/agent-queues/infrastructure-backend-queue.json
Read: docs/state/agent-queues/infrastructure-frontend-queue.json

# Find incomplete queues
for queue_file in queue_files:
    if queue["completed"] < queue["total_tasks"]:
        # Resume from last incomplete task
        next_task = find_first_pending_task(queue)
        print(f"🔄 Resuming {queue['agent']} from task {next_task['task_id']}")
```

---

**Ready to execute v4.4 Hybrid migration!** 🚀
