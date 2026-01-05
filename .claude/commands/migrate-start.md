# 🚀 Migrate Start - Task-Driven Migration Framework v4.3

You are starting a **task-driven migration** using the Universal Migration Framework v4.3.

## Key Difference from Previous Version

**OLD (v4.2)**: User provides SDD → Framework analyzes → Generates tasks → Implements
**NEW (v4.3)**: User provides **pre-generated task list** → Framework validates → Enriches with tests → Agents implement

## Your Mission

Execute a migration based on a **pre-generated task list** (JSON file with 40, 90, or 200+ tasks).

**Stack objetivo**:
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js + React + TypeScript
- **Testing**: Pytest + Playwright (TDD approach)

---

## EXECUTION STEPS

### STEP 1: Greet User (Task-Driven Mode)

```
🤖 ¡Bienvenido al Universal Migration Framework v4.3 (Task-Driven Mode)!

Este framework ejecuta migraciones basadas en **listas de tareas pre-generadas**.

**Modo de operación**:
1. Tú me proporcionas un archivo JSON con la lista de tareas
2. Yo valido, enriquezco con tests (TDD) y ejecuto
3. Los agentes especializados implementan cada tarea siguiendo Clean Architecture

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

# 2. Parse JSON
import json
with open(task_file_path) as f:
    data = json.load(f)
    all_tasks = data['tasks']

# 3. Validar estructura
total_tasks = len(all_tasks)
print(f"📊 **Archivo de tareas cargado**")
print(f"   - Total de tareas: {total_tasks}")

# Validación 1: IDs secuenciales
task_ids = [t['id'] for t in all_tasks]
expected_ids = [f"TASK-{str(i).zfill(3)}" for i in range(1, total_tasks + 1)]
missing_ids = set(expected_ids) - set(task_ids)

if missing_ids:
    print(f"⚠️ ADVERTENCIA: Faltan tareas: {missing_ids}")
    # Preguntar al usuario si continuar

# Validación 2: Estructura de cada tarea
required_fields = ['id', 'title', 'description', 'dependencies', 'deliverables', 'acceptanceCriteria']
for task in all_tasks:
    for field in required_fields:
        if field not in task:
            print(f"❌ ERROR: La tarea {task.get('id', 'UNKNOWN')} no tiene el campo '{field}'")
            # Abortar migración

# Validación 3: Dependencias válidas
all_task_ids = set(task_ids)
for task in all_tasks:
    for dep in task['dependencies']:
        if dep not in all_task_ids:
            print(f"❌ ERROR: La tarea {task['id']} depende de {dep} que no existe")
            # Abortar migración

print(f"✅ Validaciones pasadas:")
print(f"   - {total_tasks} tareas presentes")
print(f"   - Todos los IDs son únicos")
print(f"   - Todas las tareas tienen estructura completa")
print(f"   - Todas las dependencias son válidas")

# 4. Calcular orden de ejecución (Topological Sort)
def topological_sort(tasks):
    # Construir grafo de dependencias
    graph = {t['id']: t['dependencies'] for t in tasks}

    # Calcular niveles
    levels = {}
    level = 0
    remaining = set(graph.keys())

    while remaining:
        # Tareas sin dependencias pendientes
        current_level = [
            task_id for task_id in remaining
            if all(dep not in remaining for dep in graph[task_id])
        ]

        if not current_level:
            # Dependencia circular detectada
            print(f"❌ ERROR: Dependencia circular detectada en tareas: {remaining}")
            break

        levels[level] = current_level
        remaining -= set(current_level)
        level += 1

    return levels

execution_levels = topological_sort(all_tasks)

print(f"\n📈 **Orden de ejecución calculado**:")
for level, task_ids in execution_levels.items():
    print(f"   Nivel {level}: {len(task_ids)} tareas")
    print(f"      {', '.join(task_ids[:5])}{'...' if len(task_ids) > 5 else ''}")

# 5. Preparar tasks.json con metadata del framework
framework_tasks = []

for task in all_tasks:
    # Agregar campos del framework
    framework_task = {
        **task,  # Mantener todos los campos originales
        # Metadata del framework
        "status": "pending",
        "owner": None,
        "started_at": None,
        "completed_at": None,
        "test_strategy": None,  # Se llenará en PHASE 0.8
        "framework_metadata": {
            "execution_level": None,  # Se calculará abajo
            "dependencies_met": False
        }
    }

    # Calcular nivel de ejecución
    for level, task_ids in execution_levels.items():
        if task['id'] in task_ids:
            framework_task['framework_metadata']['execution_level'] = level
            break

    framework_tasks.append(framework_task)

# 6. Guardar tasks.json
Write(
    file_path="docs/state/tasks.json",
    content=json.dumps({
        "project_name": data['project_info']['name'],
        "total_tasks": total_tasks,
        "execution_levels": execution_levels,
        "tasks": framework_tasks
    }, indent=2)
)

print(f"\n✅ **tasks.json generado**")
print(f"   - Ubicación: docs/state/tasks.json")
print(f"   - Tareas: {total_tasks}")
print(f"   - Niveles de ejecución: {len(execution_levels)}")

# 7. Generar execution plan (para el usuario)
Write(
    file_path="docs/state/execution-plan.md",
    content=f"""
# Execution Plan

## Statistics
- Total tasks: {total_tasks}
- Execution levels: {len(execution_levels)}

## Execution Order

{chr(10).join([
    f"### Level {level} ({len(task_ids)} tasks)\n" +
    chr(10).join([f"- {tid}" for tid in task_ids])
    for level, task_ids in execution_levels.items()
])}
    """
)

print(f"✅ **Plan de ejecución generado**")
print(f"   - Ubicación: docs/state/execution-plan.md")
```

### STEP 4: Present Validation Summary to User

```
═══════════════════════════════════════════════════════════
📊 FASE 0 COMPLETADA: Importación y Validación de Tareas
═══════════════════════════════════════════════════════════

✅ **Validaciones exitosas**:
   - Tareas cargadas: {total_tasks}
   - IDs únicos y secuenciales: ✓
   - Estructura completa: ✓
   - Dependencias válidas: ✓

📈 **Orden de ejecución**:
   - Niveles calculados: {len(execution_levels)}
   - Nivel 0: {len(execution_levels[0])} tareas (sin dependencias)
   - Nivel 1: {len(execution_levels[1])} tareas
   ...

📁 **Archivos generados**:
   - docs/state/tasks.json (lista de tareas con metadata del framework)
   - docs/state/execution-plan.md (plan de ejecución legible)

🔜 **Siguiente fase**: PHASE 0.8 - Enriquecimiento de Test Specs (TDD)

¿Continuar? (yes/no)
```

**Wait for user confirmation**

---

### STEP 5: PHASE 0.8 - TDD Test Specification Enrichment

**Invoke qa-test-generator agent**

```python
Task(
    description="Enrich tasks with TDD test specifications",
    prompt="""Read .claude/agents/qa-test-generator.md for your instructions.

    **YOUR MISSION**: Enrich ALL tasks in tasks.json with comprehensive test specifications following TDD best practices.

    **INPUT**:
    - docs/state/tasks.json ({total_tasks} tasks)

    **YOUR TASK**:
    1. Read ALL {total_tasks} tasks from tasks.json
    2. For EACH task:
       a) Analyze acceptanceCriteria
       b) Analyze deliverables (files to be created)
       c) Generate test specifications:
          - Unit tests (test individual functions/classes)
          - Integration tests (test component interactions)
          - E2E tests (if applicable - frontend/API workflows)

    3. For each test specification, provide:
       - test_name: Descriptive test name
       - description: What does this test verify?
       - setup: What setup is needed? (test data, mocks, etc.)
       - action: What action to perform?
       - expected: What is the expected result?
       - assertions: Specific assertions to check

    4. Update tasks.json:
       - For each task, add field "test_strategy" with:
         {
           "unit_tests": [...],
           "integration_tests": [...],
           "e2e_tests": [...]  // if applicable
         }

    **CRITICAL RULES**:
    - Generate tests for ALL {total_tasks} tasks (no exceptions)
    - Follow TDD best practices (tests should guide implementation)
    - Tests should be comprehensive (cover all acceptance criteria)
    - Tests should be specific (clear assertions)
    - Update tasks.json directly (modify the existing file)

    **EXAMPLE OUTPUT** (for one task):
    ```json
    {
      "id": "TASK-004",
      "title": "Create SQLAlchemy Models",
      "test_strategy": {
        "unit_tests": [
          {
            "test_name": "test_customer_model_title_validation",
            "description": "Test Customer model validates title from allowed list",
            "setup": "Create Customer instance with invalid title",
            "action": "Attempt to save customer",
            "expected": "Raises ValueError with message 'Invalid title'",
            "assertions": [
              "Valid titles accepted (Mr, Mrs, Miss, Ms, Dr, etc.)",
              "Invalid title raises ValueError",
              "Error message contains invalid title value"
            ]
          },
          {
            "test_name": "test_customer_age_validation",
            "description": "Test Customer model validates age < 150 years",
            "setup": "Create Customer with date_of_birth = 1600-01-01",
            "action": "Calculate age",
            "expected": "Raises ValueError with message 'Age cannot exceed 150 years'",
            "assertions": [
              "Age > 150 raises ValueError",
              "Age = 150 is accepted",
              "Future birth date raises ValueError"
            ]
          }
        ],
        "integration_tests": [
          {
            "test_name": "test_customer_account_cascade_delete",
            "description": "Test deleting customer cascades to accounts",
            "setup": "Create customer with 3 accounts in database",
            "action": "Delete customer using db.session.delete(customer)",
            "expected": "All 3 accounts are deleted",
            "assertions": [
              "Customer deleted successfully",
              "All associated accounts deleted",
              "Database query for accounts returns 0 results"
            ]
          }
        ]
      }
    }
    ```

    **WHEN COMPLETE**: Report back with:
    - Total tasks enriched: {total_tasks}/{total_tasks}
    - Total unit tests generated: X
    - Total integration tests generated: Y
    - Total E2E tests generated: Z
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

**After qa-test-generator completes:**

```python
# Validate that tests were added
Read("docs/state/tasks.json")
tasks_with_tests = [t for t in tasks if t['test_strategy'] is not None]

if len(tasks_with_tests) != total_tasks:
    print(f"⚠️ WARNING: Only {len(tasks_with_tests)}/{total_tasks} tasks have test strategies")
    # Ask user if should retry

print(f"✅ **PHASE 0.8 COMPLETADA: Test Specification Enrichment**")
print(f"   - Tareas con test specs: {len(tasks_with_tests)}/{total_tasks}")
print(f"   - Total unit tests: {sum(len(t['test_strategy']['unit_tests']) for t in tasks_with_tests)}")
print(f"   - Total integration tests: {sum(len(t['test_strategy']['integration_tests']) for t in tasks_with_tests)}")
```

---

### STEP 6: PHASE 2-3 - Sequential Agent Execution

**Now invoke agents ONE BY ONE in sequence**

```python
# Agent invocation order (SEQUENTIAL, not parallel)
agent_sequence = [
    "domain-agent",
    "use-case-agent",
    "infrastructure-agent",  # Backend (ORM, API)
    "infrastructure-agent",  # Frontend (Next.js, components) - 2nd invocation
    "e2e-qa-agent"
]

for agent_name in agent_sequence:
    print(f"\n🔄 **Invocando: {agent_name}**")

    # Invoke agent
    Task(
        description=f"Execute tasks assigned to {agent_name}",
        prompt=f"""Read .claude/agents/{agent_name}.md for your complete instructions.

        **YOUR MISSION**: Implement tasks that correspond to your expertise.

        **INPUT**:
        - docs/state/tasks.json ({{total_tasks}} tasks)

        **YOUR PROCESS**:
        1. **Read ALL tasks** from docs/state/tasks.json

        2. **Identify YOUR tasks** based on your expertise:
           {get_agent_keywords(agent_name)}

        3. **Check ownership**:
           - If task has owner != null and owner != "{agent_name}":
             → SKIP (another agent already claimed it)
           - If task has owner == null:
             → YOU CAN CLAIM IT (if it matches your expertise)

        4. **For each task you claim**:
           a) Update tasks.json:
              - Set owner = "{agent_name}"
              - Set status = "claimed"
              - Set started_at = current_timestamp

           b) Create progress file:
              - docs/state/tracking/{agent_name}-progress.json
              - Track your tasks and implementation progress

           c) **READ THE TEST SPECS** for this task:
              - task["test_strategy"]["unit_tests"]
              - task["test_strategy"]["integration_tests"]
              - These tests were generated by qa-test-generator
              - **IMPLEMENT CODE TO PASS THESE TESTS** (TDD approach)

           d) Implement the task:
              - Follow task["description"] EXACTLY
              - Create ALL files in task["deliverables"]
              - Meet ALL task["acceptanceCriteria"]
              - Write tests FIRST (based on test_strategy)
              - Write code to pass tests

           e) Update task progress:
              - status = "in_progress" (while working)
              - status = "completed" (when all done)
              - completed_at = timestamp (when done)

           f) Update your progress file with:
              - Files created/modified
              - Tests implemented
              - Acceptance criteria met
              - Any issues or blockers

        5. **When ALL your tasks are completed**:
           - Report back to orchestrator with summary:
             * Total tasks claimed: X
             * Total tasks completed: X
             * Total files created: Y
             * Total tests passed: Z

        **CRITICAL RULES**:
        - NEVER take a task that already has an owner (unless owner == your name)
        - ALWAYS read test specs BEFORE implementing
        - ALWAYS write tests FIRST, then code (TDD)
        - ALWAYS update tasks.json after claiming and completing
        - ALWAYS create ALL deliverables listed
        - ALWAYS meet ALL acceptance criteria

        **WHEN COMPLETE**: Report:
        - Tasks claimed: X
        - Tasks completed: X/{agent_name}-tasks
        - Files created: Y
        - Tests passed: Z/Z (100%)
        - Ready for next agent: yes
        """,
        subagent_type="Explore",
        model="sonnet"
    )

    # Wait for agent to complete
    # Agent will report completion in its response

    print(f"✅ **{agent_name} completado**")

    # Validate agent completion
    Read("docs/state/tasks.json")
    agent_tasks = [t for t in tasks if t['owner'] == agent_name]
    completed_tasks = [t for t in agent_tasks if t['status'] == 'completed']

    if len(completed_tasks) < len(agent_tasks):
        print(f"⚠️ WARNING: {agent_name} completed {len(completed_tasks)}/{len(agent_tasks)} tasks")
        # Ask user if should retry or continue

    print(f"   - Tareas completadas: {len(completed_tasks)}/{len(agent_tasks)}")
```

**Helper function for agent keywords:**

```python
def get_agent_keywords(agent_name):
    keywords_map = {
        "domain-agent": """
        - Keywords: 'business logic', 'domain rules', 'validation rules', 'entity'
        - Deliverables: Files in backend/app/domain/, business rule implementations
        - Focus: Pure business logic, no infrastructure dependencies
        """,

        "use-case-agent": """
        - Keywords: 'use case', 'DTO', 'schema', 'service coordinator', 'application logic'
        - Deliverables: Files in backend/app/schemas/, backend/app/services/
        - Focus: Application layer, DTOs, use case orchestration
        """,

        "infrastructure-agent": """
        - Keywords (Backend): 'ORM', 'database', 'API endpoint', 'SQLAlchemy', 'FastAPI', 'migration'
        - Keywords (Frontend): 'React', 'Next.js', 'component', 'UI', 'frontend'
        - Deliverables: backend/app/models/, backend/app/api/, frontend/src/
        - Focus: Infrastructure (DB, API, UI), framework-specific code
        - NOTE: This agent is invoked TWICE (once for backend, once for frontend)
        """,

        "e2e-qa-agent": """
        - Keywords: 'E2E test', 'integration test', 'Playwright', 'end-to-end'
        - Deliverables: Files in tests/e2e/, tests/performance/
        - Focus: End-to-end testing, performance testing
        """
    }
    return keywords_map.get(agent_name, "No keywords defined")
```

---

### STEP 7: PHASE 4 - Final E2E Testing

**After all implementation agents complete:**

```python
# Run final E2E tests
print(f"\n🧪 **PHASE 4: Final E2E Testing**")

# e2e-qa-agent already ran during sequential execution
# Validate all E2E tests passed

Read("docs/state/tasks.json")
e2e_tasks = [t for t in tasks if 'e2e' in t['title'].lower() or 'performance' in t['title'].lower()]

e2e_completed = [t for t in e2e_tasks if t['status'] == 'completed']

if len(e2e_completed) == len(e2e_tasks):
    print(f"✅ All E2E tests completed: {len(e2e_completed)}/{len(e2e_tasks)}")
else:
    print(f"⚠️ E2E tests incomplete: {len(e2e_completed)}/{len(e2e_tasks)}")
```

---

### STEP 8: PHASE 5 - Final Validation & Delivery

```python
print(f"\n✅ **PHASE 5: Final Validation**")

# 1. Verify ALL tasks completed
Read("docs/state/tasks.json")
completed_tasks = [t for t in tasks if t['status'] == 'completed']

print(f"📊 **Task Completion Report**:")
print(f"   - Total tasks: {total_tasks}")
print(f"   - Completed: {len(completed_tasks)}")
print(f"   - Success rate: {len(completed_tasks) / total_tasks * 100:.1f}%")

if len(completed_tasks) < total_tasks:
    incomplete = [t for t in tasks if t['status'] != 'completed']
    print(f"\n⚠️ **Tareas incompletas**: {len(incomplete)}")
    for task in incomplete:
        print(f"   - {task['id']}: {task['title']} (status: {task['status']})")

    # Ask user for decision
    # Option 1: Continue with incomplete migration
    # Option 2: Retry failed tasks
    # Option 3: Abort

# 2. Generate final report
final_report = {
    "migration_completed_at": current_timestamp,
    "total_tasks": total_tasks,
    "completed_tasks": len(completed_tasks),
    "success_rate": len(completed_tasks) / total_tasks,
    "tasks_by_agent": {
        "domain-agent": len([t for t in tasks if t['owner'] == 'domain-agent']),
        "use-case-agent": len([t for t in tasks if t['owner'] == 'use-case-agent']),
        "infrastructure-agent": len([t for t in tasks if t['owner'] == 'infrastructure-agent']),
        "e2e-qa-agent": len([t for t in tasks if t['owner'] == 'e2e-qa-agent'])
    },
    "deliverables_created": count_files_in_output_directory(),
    "tests_passed": count_tests_passed()
}

Write(
    file_path="docs/state/final-report.json",
    content=json.dumps(final_report, indent=2)
)
```

---

### STEP 9: Final Report to User

```
═══════════════════════════════════════════════════════════
✅ 🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE 🎉
═══════════════════════════════════════════════════════════

📊 **Estadísticas**:
   - Total de tareas: {total_tasks}
   - Tareas completadas: {completed_tasks}
   - Tasa de éxito: {success_rate}%
   - Archivos generados: {deliverables_created}
   - Tests pasados: {tests_passed}

📦 **Distribución por agente**:
   - domain-agent: {domain_agent_tasks} tareas
   - use-case-agent: {use_case_agent_tasks} tareas
   - infrastructure-agent: {infrastructure_agent_tasks} tareas
   - e2e-qa-agent: {e2e_qa_agent_tasks} tareas

📁 **Código generado en**: output/{project_name}/

📂 **Estructura**:
   output/{project_name}/
   ├── backend/          (FastAPI + SQLAlchemy)
   │   ├── app/
   │   │   ├── domain/       (Business logic)
   │   │   ├── application/  (Use cases, DTOs)
   │   │   ├── infrastructure/ (ORM, API)
   │   │   └── tests/
   │   └── alembic/      (DB migrations)
   ├── frontend/         (Next.js + TypeScript)
   │   └── src/
   │       ├── app/
   │       ├── components/
   │       └── services/
   └── tests/
       ├── unit/
       ├── integration/
       └── e2e/

🚀 **Para probar localmente**:
   ```bash
   cd output/{project_name}
   docker-compose up
   # Backend: http://localhost:8000
   # Frontend: http://localhost:3000
   # API Docs: http://localhost:8000/docs
   ```

📖 **Documentación**:
   - Reporte final: docs/state/final-report.json
   - Plan de ejecución: docs/state/execution-plan.md
   - Tareas completadas: docs/state/tasks.json

═══════════════════════════════════════════════════════════

¿Necesitas algo más?
```

---

## CRITICAL RULES

1. **NO assigned_agent field** - Agents auto-select tasks based on keywords
2. **Sequential agent invocation** - One agent at a time, in order
3. **Agents check ownership** - Never take tasks already owned by others
4. **TDD mandatory** - Agents MUST read test_strategy before implementing
5. **tasks.json is single source of truth** - All agents read/write this file
6. **Scalability** - Framework works with 40, 90, 200+ tasks
7. **100% traceability** - Every task tracked from pending → completed

---

## ERROR HANDLING

### Agent fails to complete tasks

```python
if agent_completed_tasks < agent_total_tasks:
    # Option 1: Auto-retry (max 3 times)
    retry_count = 0
    while retry_count < 3 and agent_completed_tasks < agent_total_tasks:
        print(f"🔄 Retry {retry_count + 1}/3 for {agent_name}")
        re_invoke_agent(agent_name)
        retry_count += 1

    # Option 2: Ask user
    if agent_completed_tasks < agent_total_tasks:
        decision = AskUserQuestion({
            "question": f"{agent_name} completed {agent_completed_tasks}/{agent_total_tasks} tasks. ¿Qué hacer?",
            "options": [
                {"label": "Continuar", "description": "Continuar con el siguiente agente"},
                {"label": "Reintentar", "description": "Reintentar tareas fallidas"},
                {"label": "Abortar", "description": "Detener migración"}
            ]
        })
```

### Task dependency not met

```python
# This should not happen if topological sort is correct
# But if it does:
for task in tasks:
    if task['status'] == 'pending':
        deps_met = all(
            tasks[dep]['status'] == 'completed'
            for dep in task['dependencies']
        )
        if not deps_met:
            print(f"⚠️ WARNING: Task {task['id']} blocked by incomplete dependencies")
```

---

## SESSION RECOVERY

If session interrupted:

```python
Read("docs/state/tasks.json")

# Find last completed agent
agents_completed = set(t['owner'] for t in tasks if t['status'] == 'completed')

# Find next agent to invoke
agent_sequence = ["domain-agent", "use-case-agent", "infrastructure-agent", "e2e-qa-agent"]
next_agent_index = len(agents_completed)

if next_agent_index < len(agent_sequence):
    next_agent = agent_sequence[next_agent_index]
    print(f"🔄 Sesión recuperada. Siguiente agente: {next_agent}")
```

---

**Ready to execute task-driven migration!** 🚀
