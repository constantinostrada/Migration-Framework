# 🚀 Migrate Start - Task-Driven Migration Framework v4.4 (Hybrid Execution)

You are starting a **task-driven migration** using the Universal Migration Framework v4.4.

## Key Changes in v4.4

**v4.3**: Agents received ALL tasks → Overwhelmed, implemented 1-2 then stopped
**v4.4**: Hybrid two-phase execution → Agents complete ALL assigned tasks

| Phase | What Happens |
|-------|--------------|
| **PHASE A** | Agent selects tasks, saves queue. **NO IMPLEMENTATION** |
| **PHASE B** | Orchestrator sends ONE task at a time. Agent implements, returns. **REPEAT** |

## ⚠️ CRITICAL: SEQUENTIAL EXECUTION RULE (v4.4.1)

**NEVER PARALLELIZE Phase B Task() calls.** Each agent invocation must complete before starting the next.

```
❌ WRONG (causes race conditions):
   Task("domain-001")  ─┬─→ running
   Task("domain-002")  ─┼─→ running  ← RACE CONDITION!
   Task("domain-003")  ─┼─→ running  ← STATE CORRUPTION!
   Task("domain-004")  ─┴─→ running

✅ CORRECT (sequential):
   Task("domain-001") → wait → complete
   Task("domain-002") → wait → complete
   Task("domain-003") → wait → complete
   Task("domain-004") → wait → complete
```

**Why**: Multiple agents writing to `tasks.json` or queue files simultaneously causes:
- Data loss (last writer wins)
- Optimistic locking failures
- Inconsistent state
- Wasted tokens (~30-60k per agent)

**Additional v4.4 Changes:**
- `qa-test-generator` writes REAL pytest files (not just specs)
- Implementation agents just make tests GREEN (don't write tests)
- Queue files track progress: `docs/state/agent-queues/`
- **File locking** prevents race conditions on shared state files
- **Schema validation** ensures state file integrity
- **Transaction logging** enables rollback on failures

---

## 🔒 STATE MANAGEMENT (v4.4 - Critical)

**Read**: `.claude/docs/state-management.md` for complete state management protocol.

### File Locking Functions

```python
def acquire_lock(file_path: str, timeout_seconds: int = 30) -> bool:
    """Acquire exclusive lock on a state file."""
    lock_path = f"{file_path}.lock"
    start_time = current_timestamp()

    while True:
        if not file_exists(lock_path):
            # Create lock file
            Write(lock_path, {
                "locked_by": get_agent_id(),
                "locked_at": current_timestamp()
            })
            return True

        # Check for stale lock (> 60 seconds)
        lock_info = Read(lock_path)
        if current_timestamp() - lock_info["locked_at"] > 60:
            delete_file(lock_path)
            continue

        # Timeout check
        if current_timestamp() - start_time > timeout_seconds:
            return False

        sleep(0.5)

def release_lock(file_path: str):
    """Release exclusive lock."""
    lock_path = f"{file_path}.lock"
    if file_exists(lock_path):
        delete_file(lock_path)

def safe_update_tasks(update_fn: callable):
    """Safely update tasks.json with locking."""
    file_path = "docs/state/tasks.json"

    if not acquire_lock(file_path):
        raise Exception("Could not acquire lock on tasks.json")

    try:
        current = Read(file_path)
        updated = update_fn(current)
        validate_tasks_schema(updated)

        # Atomic write: temp file + rename
        Write(f"{file_path}.tmp", updated)
        rename_file(f"{file_path}.tmp", file_path)

        # Log transaction
        log_transaction("update_tasks", updated)
    finally:
        release_lock(file_path)
```

### Validation on Startup

```python
def validate_state_on_startup():
    """Run at the start of every migration session."""
    print("🔍 Validating state files...")

    all_errors = []
    all_warnings = []
    all_auto_fixed = []

    # 1. Remove stale locks
    for lock_file in glob("docs/state/**/*.lock"):
        try:
            lock_info = Read(lock_file)
            if current_timestamp() - lock_info.get("locked_at", 0) > 60:
                print(f"   ⚠️ Removing stale lock: {lock_file}")
                delete_file(lock_file)
        except:
            # Corrupted lock file - remove it
            delete_file(lock_file)

    # 2. Validate tasks.json
    print("\n   📄 Validating tasks.json...")
    try:
        tasks_state = Read("docs/state/tasks.json")
        tasks_result = validate_state_schema("tasks.json", tasks_state)

        if tasks_result["errors"]:
            print(f"      🔴 Errors: {len(tasks_result['errors'])}")
            all_errors.extend(tasks_result["errors"])
        if tasks_result["warnings"]:
            print(f"      ⚠️ Warnings: {len(tasks_result['warnings'])}")
            all_warnings.extend(tasks_result["warnings"])
        if tasks_result["auto_fixed"]:
            print(f"      🔧 Auto-fixed: {len(tasks_result['auto_fixed'])}")
            all_auto_fixed.extend(tasks_result["auto_fixed"])
            # Write back auto-fixed state
            Write("docs/state/tasks.json", tasks_state)

        if tasks_result["valid"]:
            print(f"      ✅ tasks.json is valid")
    except Exception as e:
        all_errors.append(f"tasks.json: Failed to read - {e}")
        print(f"      🔴 Failed to read tasks.json: {e}")

    # 3. Validate all queue files
    queue_files = glob("docs/state/agent-queues/*.json")
    for queue_file in queue_files:
        print(f"\n   📄 Validating {queue_file}...")
        try:
            queue_state = Read(queue_file)
            queue_result = validate_state_schema(queue_file, queue_state)

            if queue_result["errors"]:
                print(f"      🔴 Errors: {len(queue_result['errors'])}")
                for err in queue_result["errors"]:
                    print(f"         - {err}")
                all_errors.extend(queue_result["errors"])

            if queue_result["warnings"]:
                all_warnings.extend(queue_result["warnings"])

            if queue_result["auto_fixed"]:
                print(f"      🔧 Auto-fixed: {queue_result['auto_fixed']}")
                all_auto_fixed.extend(queue_result["auto_fixed"])
                # Write back auto-fixed state
                Write(queue_file, queue_state)

            if queue_result["valid"]:
                print(f"      ✅ {queue_file} is valid")

        except Exception as e:
            all_errors.append(f"{queue_file}: Failed to read - {e}")
            print(f"      🔴 Failed to read: {e}")

    # 4. Validate rejection-tracker.json if exists
    try:
        tracker = Read("docs/state/rejection-tracker.json")
        print(f"\n   📄 Validating rejection-tracker.json...")
        tracker_result = validate_state_schema("rejection-tracker.json", tracker)
        if tracker_result["errors"]:
            all_errors.extend(tracker_result["errors"])
        if tracker_result["valid"]:
            print(f"      ✅ rejection-tracker.json is valid")
    except:
        pass  # File may not exist yet

    # 5. Check cross-file consistency
    print("\n   🔗 Checking cross-file consistency...")
    consistency_errors = verify_state_consistency()
    if consistency_errors:
        print(f"      🔴 Consistency errors: {len(consistency_errors)}")
        for err in consistency_errors:
            print(f"         - {err}")
        all_errors.extend(consistency_errors)
    else:
        print(f"      ✅ State consistency verified")

    # Summary
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    print(f"   Errors: {len(all_errors)}")
    print(f"   Warnings: {len(all_warnings)}")
    print(f"   Auto-fixed: {len(all_auto_fixed)}")

    if all_errors:
        print(f"\n🔴 State validation FAILED - {len(all_errors)} blocking errors")
        return False

    if all_auto_fixed:
        print(f"\n🔧 State auto-repairs applied - re-validate recommended")

    print(f"\n✅ State validation PASSED")
    return True
```

### Layer Completeness Verification (v4.4 - Critical)

```python
def verify_layer_completeness(layer: str) -> dict:
    """
    Verify that ALL tasks in a layer are completed before proceeding to next layer.

    Args:
        layer: One of "domain", "application", "infrastructure_backend", "infrastructure_frontend"

    Returns:
        {
            "is_complete": bool,
            "is_complete_strict": bool,  # True only if ALL tasks completed (no escalated)
            "has_escalated": bool,  # Warning: some tasks were skipped
            "total": int,
            "completed": int,
            "blocked": int,
            "in_progress": int,
            "pending": int,
            "escalated": int,
            "blocked_tasks": list,
            "escalated_tasks": list,  # Tasks that were skipped (not implemented!)
            "incomplete_tasks": list
        }
    """
    tasks_data = Read("docs/state/tasks.json")
    all_tasks = tasks_data.get("tasks", [])

    # Filter tasks for this layer
    layer_tasks = [t for t in all_tasks if t.get("layer") == layer]

    # Count by status
    completed = [t for t in layer_tasks if t.get("status") == "completed"]
    blocked = [t for t in layer_tasks if t.get("status") == "blocked"]
    in_progress = [t for t in layer_tasks if t.get("status") == "in_progress"]
    pending = [t for t in layer_tasks if t.get("status") in ["pending", "queued", None]]
    escalated = [t for t in layer_tasks if t.get("status") == "escalated"]

    # STRICT: Layer is complete ONLY if ALL tasks are completed (no escalated)
    is_complete_strict = len(completed) == len(layer_tasks) and len(layer_tasks) > 0

    # LENIENT: Layer is "complete" if all tasks are either completed or escalated
    # But this is RISKY - escalated tasks were NOT implemented!
    non_terminal = len(layer_tasks) - len(completed) - len(escalated)
    is_complete_lenient = non_terminal == 0 and len(layer_tasks) > 0

    # Use STRICT by default - safer for Clean Architecture
    is_complete = is_complete_strict

    # If no tasks for this layer, it's considered complete (nothing to do)
    if len(layer_tasks) == 0:
        is_complete = True
        is_complete_strict = True

    # Warning flag if there are escalated tasks
    has_escalated = len(escalated) > 0

    return {
        "is_complete": is_complete,
        "is_complete_strict": is_complete_strict,
        "is_complete_lenient": is_complete_lenient,  # For user to choose PROCEED
        "has_escalated": has_escalated,
        "total": len(layer_tasks),
        "completed": len(completed),
        "blocked": len(blocked),
        "in_progress": len(in_progress),
        "pending": len(pending),
        "escalated": len(escalated),
        "blocked_tasks": [
            {
                "id": t["id"],
                "title": t.get("title", "Unknown"),
                "blocker_info": t.get("blocker_info", {"reason": "Unknown"})
            }
            for t in blocked
        ],
        "escalated_tasks": [
            {
                "id": t["id"],
                "title": t.get("title", "Unknown"),
                "escalation_info": t.get("escalation_info", {"reason": "Unknown"})
            }
            for t in escalated
        ],
        "incomplete_tasks": [
            {
                "id": t["id"],
                "title": t.get("title", "Unknown"),
                "status": t.get("status", "unknown")
            }
            for t in layer_tasks if t.get("status") != "completed"
        ]
    }


def verify_all_prerequisites(target_layer: str) -> dict:
    """
    Verify all prerequisite layers are complete before starting a layer.

    Args:
        target_layer: The layer we want to start

    Returns:
        {
            "can_proceed": bool,
            "blocking_layers": list,  # Layers that are not complete
            "details": dict  # Status of each prerequisite layer
        }
    """
    # Define layer dependencies
    prerequisites = {
        "domain": [],  # Domain has no prerequisites
        "application": ["domain"],
        "infrastructure_backend": ["domain", "application"],
        "infrastructure_frontend": ["domain", "application", "infrastructure_backend"]
    }

    required = prerequisites.get(target_layer, [])
    blocking = []
    details = {}

    for layer in required:
        status = verify_layer_completeness(layer)
        details[layer] = status

        if not status["is_complete"]:
            blocking.append(layer)

    return {
        "can_proceed": len(blocking) == 0,
        "blocking_layers": blocking,
        "details": details
    }

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

🔜 **Siguiente fase**: Implementación por capas con TDD Per-Layer (v4.5)

¿Continuar? (yes/no)
```

---

### STEP 5: TDD Per-Layer Execution (v4.5 CHANGE)

**🆕 v4.5 CAMBIO IMPORTANTE**: QA ya NO genera todos los tests upfront.
Ahora genera tests DESPUÉS de cada Phase A, solo para las tareas aceptadas/creadas.

**Nuevo Flujo por Capa:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Para cada capa (Domain → Application → Infrastructure):        │
│                                                                 │
│  1. PHASE A: Agent selecciona/extrae tareas → Guarda queue     │
│  2. PHASE QA: qa-test-generator genera tests SOLO para queue   │
│  3. PHASE B: Agent implementa tareas → Hace tests GREEN        │
│                                                                 │
│  ✅ TDD Real: Tests escritos para lo que el agente encontró    │
└─────────────────────────────────────────────────────────────────┘
```

**Beneficios v4.5:**
- Tests específicos para tareas aceptadas (no tests desperdiciados)
- Para domain-agent v5.0: tests basados en conceptos EXTRAÍDOS
- Verdadero TDD: test → implement → refactor por capa

---

### STEP 6: Domain Layer (TDD Per-Layer)

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

#### STEP 6.1: DOMAIN LAYER (Hybrid) - v5.0 DOMAIN EXTRACTOR

**🆕 v5.0 PARADIGM**: Domain agent is a **DOMAIN EXTRACTOR**, not a task validator.
It reads ALL tasks (even infrastructure) and EXTRACTS implicit domain concepts to CREATE its own domain tasks.

**PHASE A: Domain Extraction**

```python
print("🔄 DOMAIN LAYER - PHASE A: Domain Extraction (v5.0)")

Task(
    description="Domain agent - Phase A: Domain Extraction",
    prompt="""
    # DOMAIN AGENT v5.0 - DOMAIN EXTRACTOR MODE

    ⚠️ CRITICAL PARADIGM: You are a DOMAIN EXTRACTOR, NOT a task validator.
    ⚠️ DO NOT filter tasks by layer. DO NOT reject tasks. DO NOT return 0 tasks.
    ⚠️ Your job is to EXTRACT domain concepts from ALL tasks and CREATE new domain tasks.

    ## YOUR MISSION (PHASE A - EXTRACTION ONLY)

    1. **Read ALL 110 tasks** from docs/state/tasks.json (infrastructure, frontend, backend - ALL of them)

    2. **For EACH task, extract these domain concepts:**
       - ENTITIES: Customer, Account, Transaction, User, etc.
       - VALUE OBJECTS: Money, Email, CreditScore, AccountNumber, etc.
       - BUSINESS RULES: "MORTGAGE cannot use PAYMENT", "daily limit $10,000", "age >= 18"
       - DOMAIN SERVICES: Validation services, calculation services
       - ENUMS: AccountType, TransactionType, Status enums

    3. **CREATE YOUR OWN domain tasks** (DOMAIN-001, DOMAIN-002, etc.):
       Example:
       {
         "task_id": "DOMAIN-001",
         "title": "Create Customer Entity with Business Rules",
         "description": "Implement Customer entity with age validation (>=18), email VO, credit score VO",
         "derived_from": ["TASK-016", "TASK-057"],
         "deliverables": ["backend/app/domain/entities/customer.py"]
       }

    4. **Save to docs/state/domain-extracted-tasks.json:**
       {
         "agent": "domain-agent",
         "approach": "domain-extraction-v5",
         "extraction_summary": {
           "entities_found": ["Customer", "Account", "Transaction"],
           "value_objects_found": ["Money", "Email", "CreditScore"],
           "business_rules_found": ["BR-CUST-001: Age >= 18", "BR-ACC-001: Balance >= 0"]
         },
         "extracted_domain_tasks": [...]
       }

    5. **Save queue to docs/state/agent-queues/domain-queue.json** with your DOMAIN-XXX tasks

    ## WHAT TO LOOK FOR IN TASKS (extract these patterns):
    - "cannot", "must not", "restricted" → Business rules
    - "valid", "invalid", "required" → Validations
    - "$X,XXX", "limit", "maximum" → Constraints
    - Entity names: Customer, Account, Transaction, User
    - Value patterns: email, phone, amount, score, date

    ## EXPECTED OUTPUT:
    - AT LEAST 5-15 domain tasks (DOMAIN-001 through DOMAIN-015)
    - entities: ~5-8 (Customer, Account, Transaction, etc.)
    - value_objects: ~10-15 (Money, Email, CreditScore, etc.)
    - business_rules: ~10-20 (BR-XXX codes)

    ## FORBIDDEN ACTIONS:
    ❌ DO NOT reject tasks
    ❌ DO NOT return "0 domain tasks"
    ❌ DO NOT filter by layer field
    ❌ DO NOT use the old validation approach
    ❌ DO NOT implement code yet

    **DO NOT IMPLEMENT ANYTHING. ONLY EXTRACT AND CREATE DOMAIN TASKS.**
    """,
    subagent_type="domain-agent",
    model="sonnet"
)
```

**Read extraction results:**

```python
# 🆕 v5.0: Read domain-agent's EXTRACTION results (not rejections)
Read: docs/state/domain-extracted-tasks.json
extraction_summary = data.get("extraction_summary", {})
domain_tasks = data.get("extracted_domain_tasks", [])

print(f"📦 Domain Extraction Complete:")
print(f"   📦 Entities found: {len(extraction_summary.get('entities_found', []))}")
print(f"   💎 Value Objects: {len(extraction_summary.get('value_objects_found', []))}")
print(f"   📜 Business Rules: {len(extraction_summary.get('business_rules_found', []))}")
print(f"   📋 Domain Tasks Created: {len(domain_tasks)}")

# Also read queue for compatibility
Read: docs/state/agent-queues/domain-queue.json
queue_tasks = queue.get("queue", [])

if not domain_tasks and not queue_tasks:
    print("⚠️ No domain tasks extracted - domain-agent may not have understood v5.0 mode")
    print("   Check if domain-extracted-tasks.json was created correctly")
```

**🆕 PHASE QA: Generate Domain Tests (TDD per-layer v4.5)**

```python
print("🧪 DOMAIN LAYER - PHASE QA: Generating Tests")

# Convert domain_tasks to JSON for prompt
import json
domain_tasks_json = json.dumps(domain_tasks, indent=2)

Task(
    description="QA - Generate tests for domain layer",
    prompt=f"""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **🆕 TDD PER-LAYER MODE (v4.5): Generate tests for DOMAIN layer ONLY**

    Tasks to generate tests for (from domain-agent Phase A):
    {domain_tasks_json}

    YOUR MISSION:
    1. Read docs/state/domain-extracted-tasks.json for full task details
    2. For EACH domain task in the list above, write pytest files in tests/unit/domain/
    3. Tests should verify:
       - Entity creation and validation
       - Value object immutability and validation
       - Business rule enforcement (BR-XXX codes)
       - Domain service behavior
    4. Update domain-extracted-tasks.json with test_files array for each task
    5. Generate tests/unit/domain/conftest.py with domain fixtures

    OUTPUT:
    - tests/unit/domain/entities/test_*.py
    - tests/unit/domain/value_objects/test_*.py
    - tests/unit/domain/services/test_*.py
    - tests/unit/domain/conftest.py
    - Update domain-extracted-tasks.json with test_files

    **CRITICAL**:
    - Generate tests ONLY for tasks listed above (not all tasks)
    - Tests will be RED. Domain agent Phase B makes them GREEN.
    - Use @pytest.mark.skipif pattern for imports
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)

print("✅ Domain tests generated - ready for Phase B implementation")
```

**PHASE B: Execute each DOMAIN task (make tests GREEN)**

⚠️ **CRITICAL: SEQUENTIAL EXECUTION REQUIRED**
- Execute ONE task at a time
- WAIT for each Task() to complete before starting the next
- NEVER launch multiple Task() calls in parallel during Phase B
- This prevents race conditions on shared state files

```python
# PHASE B: Execute each DOMAIN task SEQUENTIALLY (ONE AT A TIME)
# ⚠️ DO NOT PARALLELIZE - Each task must complete before starting next
for task in domain_tasks:
    task_id = task["task_id"]  # DOMAIN-001, DOMAIN-002, etc.
    task_title = task["title"]

    print(f"🔄 Ejecutando: {task_id} - {task_title}")

    Task(
        description=f"Domain agent - Execute {task_id}",
        prompt=f"""
        You are the domain-agent. Read .claude/agents/domain-agent.md for instructions.

        **PHASE B: SINGLE TASK EXECUTION**

        Implement THIS domain task: {task_id} - {task_title}

        YOUR MISSION:
        1. Read your task from docs/state/domain-extracted-tasks.json
        2. Check if tests exist in tests/unit/domain/
        3. Implement PURE domain code (entities, value objects, domain services)
        4. Run tests if they exist
        5. Update domain-extracted-tasks.json (status = "completed")
        6. Update queue file (task status = "completed")

        **CRITICAL**:
        - NO framework dependencies (pure Python only)
        - Use dataclasses, typing, enum, abc
        - Implement business rules from task description
        """,
        subagent_type="domain-agent",
        model="sonnet"
    )

    print(f"✅ Completado: {task_id}")

print(f"✅ DOMAIN LAYER COMPLETE - {len(domain_tasks)} tasks")

# Check for blocked tasks and handle them
handle_blocked_tasks("domain-agent", "domain-queue.json")

# 🆕 Check for orphaned tasks in domain layer
check_layer_orphans("domain")
```

#### STEP 6.2: APPLICATION LAYER (Hybrid)

**PRE-CHECK: Verify Domain Layer Completeness (MANDATORY)**

```python
print("🔍 PRE-CHECK: Verifying domain layer completeness...")

# Real validation of domain layer completion
domain_status = verify_layer_completeness("domain")

if not domain_status["is_complete"]:
    print(f"🔴 BLOCKED: Domain layer is NOT complete")
    print(f"   - Total domain tasks: {domain_status['total']}")
    print(f"   - Completed: {domain_status['completed']}")
    print(f"   - Blocked: {domain_status['blocked']}")
    print(f"   - Escalated (skipped): {domain_status['escalated']}")
    print(f"   - In Progress: {domain_status['in_progress']}")

    if domain_status["blocked"] > 0:
        print(f"\n   ⚠️ Blocked tasks preventing completion:")
        for task in domain_status["blocked_tasks"]:
            print(f"      - {task['id']}: {task['blocker_info']['reason']}")

    if domain_status["has_escalated"]:
        print(f"\n   🔴 ESCALATED (NOT IMPLEMENTED) tasks:")
        for task in domain_status["escalated_tasks"]:
            print(f"      - {task['id']}: {task['title']}")
        print(f"   ⚠️ WARNING: Escalated tasks were SKIPPED - dependent code may fail!")

    # Ask user how to proceed
    response = AskUserQuestion(questions=[{
        "question": f"Domain layer incomplete ({domain_status['completed']}/{domain_status['total']}). ¿Cómo proceder?",
        "header": "Layer Dependency",
        "options": [
            {"label": "WAIT", "description": "Resolver tareas bloqueadas primero"},
            {"label": "PROCEED", "description": "Continuar de todos modos (riesgo)"},
            {"label": "ABORT", "description": "Detener migración"}
        ],
        "multiSelect": False
    }])

    user_choice = response.get("answer", "ABORT")

    if user_choice == "WAIT":
        print("🔄 Intentando resolver tareas bloqueadas del domain layer...")

        # Retry blocked tasks
        handle_blocked_tasks("domain-agent", "domain-queue.json")

        # Re-check completeness
        domain_status = verify_layer_completeness("domain")

        if not domain_status["is_complete"]:
            print(f"❌ Domain layer aún incompleto después de recovery")
            print(f"   Completadas: {domain_status['completed']}/{domain_status['total']}")

            # Offer to proceed anyway or abort
            retry_response = AskUserQuestion(questions=[{
                "question": "Recovery no resolvió todos los bloqueos. ¿Continuar de todos modos?",
                "header": "Recovery Failed",
                "options": [
                    {"label": "PROCEED", "description": "Continuar con riesgo"},
                    {"label": "ABORT", "description": "Detener migración"}
                ],
                "multiSelect": False
            }])

            if retry_response.get("answer") == "ABORT":
                abort_migration("Domain layer incomplete after recovery attempt")
            else:
                print("⚠️ WARNING: Continuando con domain layer incompleto")
        else:
            print(f"✅ Domain layer ahora completo después de recovery")

    elif user_choice == "PROCEED":
        print("⚠️ WARNING: Continuando con domain layer incompleto - pueden ocurrir errores")

        # Log warning for traceability
        log_warning_to_state({
            "type": "incomplete_layer_proceed",
            "layer": "domain",
            "completed": domain_status["completed"],
            "total": domain_status["total"],
            "blocked": domain_status["blocked"],
            "timestamp": current_timestamp()
        })

    elif user_choice == "ABORT":
        abort_migration(f"User aborted: domain layer incomplete ({domain_status['completed']}/{domain_status['total']})")

else:
    print(f"✅ Domain layer complete: {domain_status['completed']}/{domain_status['total']} tasks")
```

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

# 🆕 v4.4.1: IMMEDIATE REJECTION PROCESSING
if rejected:
    print(f"⚠️ Rechazó {len(rejected)} tareas - procesando INMEDIATAMENTE")

    for rejection in rejected:
        task_id = rejection["task_id"]
        new_layer = rejection["suggested_layer"]
        reason = rejection.get("reason", "No reason provided")

        print(f"   🔄 Re-clasificando {task_id}: application → {new_layer}")

        # Update tasks.json with new layer
        Bash: python3 << PYEOF
import json
from datetime import datetime, timezone
import os

TASK_ID = "$task_id"
NEW_LAYER = "$new_layer"
REASON = "$reason"

with open('docs/state/tasks.json', 'r') as f:
    data = json.load(f)

original_version = data.get('_version', 0)
timestamp = datetime.now(timezone.utc).isoformat()

for task in data['tasks']:
    if task['id'] == TASK_ID:
        old_layer = task.get('layer')
        task['layer'] = NEW_LAYER
        task['owner'] = None
        task['status'] = 'pending'
        task['updated_at'] = timestamp

        if 'rejection_history' not in task:
            task['rejection_history'] = []

        task['rejection_history'].append({
            'rejected_by': 'use-case-agent',
            'original_layer': old_layer,
            'suggested_layer': NEW_LAYER,
            'reason': REASON,
            'timestamp': timestamp
        })

        print(f'   ✅ Updated {TASK_ID}: {old_layer} → {NEW_LAYER}')

data['_version'] = original_version + 1
data['_last_modified'] = timestamp
data['_last_modified_by'] = 'use-case-agent'

with open('docs/state/tasks.json.tmp', 'w') as f:
    json.dump(data, f, indent=2)

os.rename('docs/state/tasks.json.tmp', 'docs/state/tasks.json')
PYEOF

        # Log rejection to transaction log
        Bash: echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"use-case-agent","operation":"reject_task","task_id":"'$task_id'","before":{"layer":"application"},"after":{"layer":"'$new_layer'"},"reason":"'$reason'"}' >> docs/state/transaction-log.jsonl

    print(f"✅ Todas las rejections procesadas - tasks.json actualizado")

# 🆕 Handle escalated tasks
escalated = queue.get("escalated_tasks", [])
if escalated:
    print(f"🔴 {len(escalated)} tareas ESCALADAS requieren clasificación manual")
    handle_escalated_tasks("use-case-agent", escalated)
```

**🆕 PHASE QA: Generate Application Tests (TDD per-layer v4.5)**

```python
print("🧪 APPLICATION LAYER - PHASE QA: Generating Tests")

import json
application_tasks_json = json.dumps(application_tasks, indent=2)

Task(
    description="QA - Generate tests for application layer",
    prompt=f"""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **🆕 TDD PER-LAYER MODE (v4.5): Generate tests for APPLICATION layer ONLY**

    Tasks to generate tests for (from use-case-agent Phase A):
    {application_tasks_json}

    YOUR MISSION:
    1. Read docs/state/tasks.json for full task details of tasks listed above
    2. For EACH application task, write pytest files in tests/unit/application/
    3. Tests should verify:
       - Use case execution flow
       - DTO validation and serialization
       - Repository interface contracts (mock implementations)
       - Application exceptions
    4. Update tasks.json with test_files array for these tasks
    5. Generate tests/unit/application/conftest.py with fixtures

    OUTPUT:
    - tests/unit/application/use_cases/test_*.py
    - tests/unit/application/dtos/test_*.py
    - tests/unit/application/conftest.py

    **CRITICAL**:
    - Generate tests ONLY for tasks listed above (not all tasks)
    - Tests will be RED. Use-case agent Phase B makes them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)

print("✅ Application tests generated - ready for Phase B implementation")
```

**PHASE B: Execute each task** (same pattern as domain layer)

⚠️ **CRITICAL: SEQUENTIAL EXECUTION REQUIRED**
- Execute ONE task at a time
- WAIT for each Task() to complete before starting the next
- NEVER launch multiple Task() calls in parallel during Phase B

```python
# PHASE B: Execute each APPLICATION task SEQUENTIALLY (ONE AT A TIME)
# ⚠️ DO NOT PARALLELIZE - Each task must complete before starting next
for task in application_tasks:
    Task(
        description=f"Use-case agent - Execute {task['task_id']}",
        prompt=f"...(implementation prompt)...",
        subagent_type="use-case-agent",
        model="sonnet"
    )
    # WAIT for completion before next iteration

# After completing PHASE B
print(f"✅ APPLICATION LAYER COMPLETE")

# Check for blocked tasks and handle them
handle_blocked_tasks("use-case-agent", "application-queue.json")

# 🆕 Check for orphaned tasks in application layer
check_layer_orphans("application")
```

#### STEP 6.3: INFRASTRUCTURE BACKEND (Hybrid)

**PRE-CHECK: Verify Domain + Application Layer Completeness (MANDATORY)**

```python
print("🔍 PRE-CHECK: Verifying domain + application layer completeness...")

# Verify both prerequisite layers
all_prereqs_complete = True

for layer in ["domain", "application"]:
    status = verify_layer_completeness(layer)

    if not status["is_complete"]:
        all_prereqs_complete = False
        print(f"🔴 BLOCKED: {layer.upper()} layer is NOT complete")
        print(f"   - Total: {status['total']} | Completed: {status['completed']} | Blocked: {status['blocked']}")

        if status["blocked_tasks"]:
            print(f"   ⚠️ Blocked tasks:")
            for task in status["blocked_tasks"][:3]:  # Show max 3
                print(f"      - {task['id']}: {task.get('blocker_info', {}).get('reason', 'Unknown')}")

        response = AskUserQuestion(questions=[{
            "question": f"{layer.capitalize()} layer incomplete. ¿Cómo proceder?",
            "header": "Layer Dependency",
            "options": [
                {"label": "WAIT", "description": "Resolver tareas bloqueadas primero"},
                {"label": "PROCEED", "description": "Continuar (riesgo de errores)"},
                {"label": "ABORT", "description": "Detener migración"}
            ],
            "multiSelect": False
        }])

        user_choice = response.get("answer", "ABORT")

        if user_choice == "WAIT":
            print(f"🔄 Intentando resolver tareas bloqueadas del {layer} layer...")
            queue_file = "domain-queue.json" if layer == "domain" else "application-queue.json"
            agent_name = "domain-agent" if layer == "domain" else "use-case-agent"
            handle_blocked_tasks(agent_name, queue_file)

            # Re-check
            status = verify_layer_completeness(layer)
            if status["is_complete"]:
                print(f"✅ {layer.capitalize()} layer ahora completo")
            else:
                print(f"⚠️ {layer.capitalize()} layer aún incompleto - continuando con riesgo")

        elif user_choice == "PROCEED":
            print(f"⚠️ WARNING: Continuando con {layer} layer incompleto")
            log_warning_to_state({
                "type": "incomplete_layer_proceed",
                "layer": layer,
                "completed": status["completed"],
                "total": status["total"],
                "timestamp": current_timestamp()
            })

        elif user_choice == "ABORT":
            abort_migration(f"User aborted: {layer} layer incomplete")

    else:
        print(f"✅ {layer.capitalize()} layer complete: {status['completed']}/{status['total']} tasks")

if all_prereqs_complete:
    print("✅ All prerequisite layers complete - proceeding to infrastructure backend")
```

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

# 🆕 v4.4.1: IMMEDIATE REJECTION PROCESSING
if rejected:
    print(f"⚠️ Rechazó {len(rejected)} tareas - procesando INMEDIATAMENTE")

    for rejection in rejected:
        task_id = rejection["task_id"]
        new_layer = rejection["suggested_layer"]
        reason = rejection.get("reason", "No reason provided")

        print(f"   🔄 Re-clasificando {task_id}: infrastructure_backend → {new_layer}")

        # Update tasks.json with new layer
        Bash: python3 << PYEOF
import json
from datetime import datetime, timezone
import os

TASK_ID = "$task_id"
NEW_LAYER = "$new_layer"
REASON = "$reason"

with open('docs/state/tasks.json', 'r') as f:
    data = json.load(f)

original_version = data.get('_version', 0)
timestamp = datetime.now(timezone.utc).isoformat()

for task in data['tasks']:
    if task['id'] == TASK_ID:
        old_layer = task.get('layer')
        task['layer'] = NEW_LAYER
        task['owner'] = None
        task['status'] = 'pending'
        task['updated_at'] = timestamp

        if 'rejection_history' not in task:
            task['rejection_history'] = []

        task['rejection_history'].append({
            'rejected_by': 'infrastructure-agent-backend',
            'original_layer': old_layer,
            'suggested_layer': NEW_LAYER,
            'reason': REASON,
            'timestamp': timestamp
        })

        print(f'   ✅ Updated {TASK_ID}: {old_layer} → {NEW_LAYER}')

data['_version'] = original_version + 1
data['_last_modified'] = timestamp
data['_last_modified_by'] = 'infrastructure-agent-backend'

with open('docs/state/tasks.json.tmp', 'w') as f:
    json.dump(data, f, indent=2)

os.rename('docs/state/tasks.json.tmp', 'docs/state/tasks.json')
PYEOF

        # Log rejection to transaction log
        Bash: echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"infrastructure-agent-backend","operation":"reject_task","task_id":"'$task_id'","before":{"layer":"infrastructure_backend"},"after":{"layer":"'$new_layer'"},"reason":"'$reason'"}' >> docs/state/transaction-log.jsonl

    print(f"✅ Todas las rejections procesadas - tasks.json actualizado")

# 🆕 Handle escalated tasks
escalated = queue.get("escalated_tasks", [])
if escalated:
    print(f"🔴 {len(escalated)} tareas ESCALADAS requieren clasificación manual")
    handle_escalated_tasks("infrastructure-agent-backend", escalated)
```

**🆕 PHASE QA: Generate Backend Integration Tests (TDD per-layer v4.5)**

```python
print("🧪 INFRASTRUCTURE BACKEND - PHASE QA: Generating Tests")

import json
backend_tasks_json = json.dumps(backend_tasks, indent=2)

Task(
    description="QA - Generate tests for infrastructure backend",
    prompt=f"""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **🆕 TDD PER-LAYER MODE (v4.5): Generate tests for INFRASTRUCTURE BACKEND ONLY**

    Tasks to generate tests for (from infrastructure-agent Phase A):
    {backend_tasks_json}

    YOUR MISSION:
    1. Read docs/state/tasks.json for full task details of tasks listed above
    2. For EACH backend task, write pytest files in tests/integration/
    3. Tests should verify:
       - Repository implementations (with test DB fixtures)
       - API endpoint responses and status codes
       - ORM model mappings
       - Database operations
    4. Update tasks.json with test_files array for these tasks
    5. Generate tests/integration/conftest.py with DB fixtures

    OUTPUT:
    - tests/integration/repositories/test_*.py
    - tests/integration/api/test_*.py
    - tests/integration/conftest.py

    **CRITICAL**:
    - Generate tests ONLY for tasks listed above (not all tasks)
    - Tests will be RED. Infrastructure agent Phase B makes them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)

print("✅ Backend integration tests generated - ready for Phase B implementation")
```

**PHASE B: Execute each task** (same pattern)

⚠️ **CRITICAL: SEQUENTIAL EXECUTION REQUIRED**
- Execute ONE task at a time
- WAIT for each Task() to complete before starting the next
- NEVER launch multiple Task() calls in parallel during Phase B

```python
# PHASE B: Execute each BACKEND task SEQUENTIALLY (ONE AT A TIME)
# ⚠️ DO NOT PARALLELIZE - Each task must complete before starting next
for task in backend_tasks:
    Task(
        description=f"Infrastructure agent - Execute {task['task_id']}",
        prompt=f"...(implementation prompt)...",
        subagent_type="infrastructure-agent",
        model="sonnet"
    )
    # WAIT for completion before next iteration

# After completing PHASE B
print(f"✅ INFRASTRUCTURE BACKEND COMPLETE")

# Check for blocked tasks and handle them
handle_blocked_tasks("infrastructure-agent-backend", "infrastructure-backend-queue.json")

# 🆕 Check for orphaned tasks in infrastructure_backend layer
check_layer_orphans("infrastructure_backend")
```

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

**PRE-CHECK: Verify All Backend Layers Complete (MANDATORY)**

```python
print("🔍 PRE-CHECK: Verifying all backend layers completeness...")

# Use the comprehensive prerequisite check
prereq_status = verify_all_prerequisites("infrastructure_frontend")

if not prereq_status["can_proceed"]:
    print(f"🔴 BLOCKED: Cannot start frontend - prerequisite layers incomplete")

    for blocking_layer in prereq_status["blocking_layers"]:
        status = prereq_status["details"][blocking_layer]
        print(f"\n   ❌ {blocking_layer.upper()} layer:")
        print(f"      - Total: {status['total']} | Completed: {status['completed']}")
        print(f"      - Blocked: {status['blocked']} | In Progress: {status['in_progress']}")

        if status["blocked_tasks"]:
            print(f"      ⚠️ Blocked tasks:")
            for task in status["blocked_tasks"][:3]:
                reason = task.get("blocker_info", {}).get("reason", "Unknown")
                print(f"         - {task['id']}: {reason}")

    response = AskUserQuestion(questions=[{
        "question": f"Frontend blocked by {len(prereq_status['blocking_layers'])} incomplete layer(s). ¿Cómo proceder?",
        "header": "Layer Dependency",
        "options": [
            {"label": "WAIT", "description": "Resolver tareas bloqueadas primero"},
            {"label": "PROCEED", "description": "Continuar de todos modos (riesgo alto)"},
            {"label": "ABORT", "description": "Detener migración"}
        ],
        "multiSelect": False
    }])

    user_choice = response.get("answer", "ABORT")

    if user_choice == "WAIT":
        print("🔄 Intentando resolver tareas bloqueadas de layers prerequisitos...")

        # Try to recover each blocking layer
        for blocking_layer in prereq_status["blocking_layers"]:
            queue_map = {
                "domain": ("domain-agent", "domain-queue.json"),
                "application": ("use-case-agent", "application-queue.json"),
                "infrastructure_backend": ("infrastructure-agent", "infrastructure-backend-queue.json")
            }
            if blocking_layer in queue_map:
                agent, queue_file = queue_map[blocking_layer]
                handle_blocked_tasks(agent, queue_file)

        # Re-check prerequisites
        prereq_status = verify_all_prerequisites("infrastructure_frontend")
        if prereq_status["can_proceed"]:
            print("✅ Todos los prerequisitos ahora completos")
        else:
            print(f"⚠️ Aún hay {len(prereq_status['blocking_layers'])} layers incompletos - continuando con riesgo")

    elif user_choice == "PROCEED":
        print("⚠️ WARNING: Continuando con prerequisitos incompletos - ALTO RIESGO de errores")
        log_warning_to_state({
            "type": "incomplete_prereqs_proceed",
            "target_layer": "infrastructure_frontend",
            "blocking_layers": prereq_status["blocking_layers"],
            "timestamp": current_timestamp()
        })

    elif user_choice == "ABORT":
        abort_migration(f"User aborted: frontend prerequisites incomplete ({prereq_status['blocking_layers']})")

else:
    print(f"✅ All prerequisite layers complete:")
    for layer, status in prereq_status["details"].items():
        print(f"   - {layer}: {status['completed']}/{status['total']} tasks")
```

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

# 🆕 v4.4.1: IMMEDIATE REJECTION PROCESSING
if rejected:
    print(f"⚠️ Rechazó {len(rejected)} tareas - procesando INMEDIATAMENTE")

    for rejection in rejected:
        task_id = rejection["task_id"]
        new_layer = rejection["suggested_layer"]
        reason = rejection.get("reason", "No reason provided")

        print(f"   🔄 Re-clasificando {task_id}: infrastructure_frontend → {new_layer}")

        # Update tasks.json with new layer
        Bash: python3 << PYEOF
import json
from datetime import datetime, timezone
import os

TASK_ID = "$task_id"
NEW_LAYER = "$new_layer"
REASON = "$reason"

with open('docs/state/tasks.json', 'r') as f:
    data = json.load(f)

original_version = data.get('_version', 0)
timestamp = datetime.now(timezone.utc).isoformat()

for task in data['tasks']:
    if task['id'] == TASK_ID:
        old_layer = task.get('layer')
        task['layer'] = NEW_LAYER
        task['owner'] = None
        task['status'] = 'pending'
        task['updated_at'] = timestamp

        if 'rejection_history' not in task:
            task['rejection_history'] = []

        task['rejection_history'].append({
            'rejected_by': 'infrastructure-agent-frontend',
            'original_layer': old_layer,
            'suggested_layer': NEW_LAYER,
            'reason': REASON,
            'timestamp': timestamp
        })

        print(f'   ✅ Updated {TASK_ID}: {old_layer} → {NEW_LAYER}')

data['_version'] = original_version + 1
data['_last_modified'] = timestamp
data['_last_modified_by'] = 'infrastructure-agent-frontend'

with open('docs/state/tasks.json.tmp', 'w') as f:
    json.dump(data, f, indent=2)

os.rename('docs/state/tasks.json.tmp', 'docs/state/tasks.json')
PYEOF

        # Log rejection to transaction log
        Bash: echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"infrastructure-agent-frontend","operation":"reject_task","task_id":"'$task_id'","before":{"layer":"infrastructure_frontend"},"after":{"layer":"'$new_layer'"},"reason":"'$reason'"}' >> docs/state/transaction-log.jsonl

    print(f"✅ Todas las rejections procesadas - tasks.json actualizado")

# 🆕 Handle escalated tasks
escalated = queue.get("escalated_tasks", [])
if escalated:
    print(f"🔴 {len(escalated)} tareas ESCALADAS requieren clasificación manual")
    handle_escalated_tasks("infrastructure-agent-frontend", escalated)
```

**🆕 PHASE QA: Generate Frontend Tests (TDD per-layer v4.5)**

```python
print("🧪 INFRASTRUCTURE FRONTEND - PHASE QA: Generating Tests")

import json
frontend_tasks_json = json.dumps(frontend_tasks, indent=2)

Task(
    description="QA - Generate tests for infrastructure frontend",
    prompt=f"""
    You are qa-test-generator. Read .claude/agents/qa-test-generator.md for instructions.

    **🆕 TDD PER-LAYER MODE (v4.5): Generate tests for INFRASTRUCTURE FRONTEND ONLY**

    Tasks to generate tests for (from infrastructure-agent Phase A):
    {frontend_tasks_json}

    YOUR MISSION:
    1. Read docs/state/tasks.json for full task details of tasks listed above
    2. For EACH frontend task, write test files (Jest/Vitest/React Testing Library)
    3. Tests should verify:
       - Component rendering
       - Form validation and submission
       - API client calls (mocked)
       - User interactions
       - State management
    4. Update tasks.json with test_files array for these tasks

    OUTPUT:
    - Frontend test files appropriate for the framework (Jest/Vitest)
    - Component tests with React Testing Library patterns

    **CRITICAL**:
    - Generate tests ONLY for tasks listed above (not all tasks)
    - Tests will be RED. Infrastructure agent Phase B makes them GREEN.
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)

print("✅ Frontend tests generated - ready for Phase B implementation")
```

**PHASE B: Execute each task** (same pattern)

⚠️ **CRITICAL: SEQUENTIAL EXECUTION REQUIRED**
- Execute ONE task at a time
- WAIT for each Task() to complete before starting the next
- NEVER launch multiple Task() calls in parallel during Phase B

```python
# PHASE B: Execute each FRONTEND task SEQUENTIALLY (ONE AT A TIME)
# ⚠️ DO NOT PARALLELIZE - Each task must complete before starting next
for task in frontend_tasks:
    Task(
        description=f"Infrastructure agent - Execute {task['task_id']}",
        prompt=f"...(implementation prompt)...",
        subagent_type="infrastructure-agent",
        model="sonnet"
    )
    # WAIT for completion before next iteration

# After completing PHASE B
print(f"✅ INFRASTRUCTURE FRONTEND COMPLETE")

# Check for blocked tasks and handle them
handle_blocked_tasks("infrastructure-agent-frontend", "infrastructure-frontend-queue.json")

# 🆕 Check for orphaned tasks in infrastructure_frontend layer
check_layer_orphans("infrastructure_frontend")
```

---

### STEP 6.6: REJECTION RECOVERY ~~(DEPRECATED in v4.4.1)~~

**⚠️ DEPRECATED**: This step is NO LONGER NEEDED in v4.4.1.

**Why**: Rejections are now processed IMMEDIATELY after each PHASE A (see v4.4.1 sections in STEPs 6.1-6.5).

**Old behavior (v4.4)**: Rejected tasks were tracked and re-classified at the END (this step).

**New behavior (v4.4.1)**: Rejected tasks are re-classified IMMEDIATELY after each PHASE A completes.

**If you're using v4.4.1, SKIP this entire step.**

---

~~**After all 4 layers complete their PHASE A + B, process any rejected tasks that were re-classified.**~~

```python
print("🔄 REJECTION RECOVERY: Processing re-classified tasks")

# Read rejection tracking file
Read: docs/state/rejection-tracker.json

# Group rejected tasks by their NEW suggested_layer
rejections_by_layer = group_rejections_by_suggested_layer(rejection_tracker)

# For each layer that has pending re-classified tasks
for layer, rejected_tasks in rejections_by_layer.items():
    if not rejected_tasks:
        continue

    print(f"📋 Processing {len(rejected_tasks)} tasks re-classified to {layer}")

    # Check if these tasks are still unprocessed (owner = null or status != completed)
    unprocessed = filter_unprocessed_tasks(rejected_tasks)

    if not unprocessed:
        print(f"   ✅ All {layer} re-classified tasks already processed")
        continue

    print(f"   ⚠️ {len(unprocessed)} tasks need processing")

    # Re-invoke the appropriate agent's PHASE A to pick up these tasks
    if layer == "domain":
        # Domain agent should have processed these - check why not
        print(f"   🔴 ERROR: Domain tasks found after domain phase complete!")
        # These might be late arrivals from infrastructure rejection - flag for manual review

    elif layer == "application":
        print(f"   🔄 Re-invoking use-case-agent PHASE A for {len(unprocessed)} tasks")
        Task(
            description="Use-case agent - Phase A: Pick up re-classified tasks",
            prompt=f"""
            You are the use-case-agent. Read .claude/agents/use-case-agent.md.

            **PHASE A: PICK UP RE-CLASSIFIED TASKS**

            {len(unprocessed)} tasks were re-classified to application layer by other agents.
            Task IDs: {[t['task_id'] for t in unprocessed]}

            YOUR MISSION:
            1. Read docs/state/tasks.json
            2. Find these specific tasks (they should now have layer="application")
            3. Add them to your existing queue file
            4. Return for PHASE B execution

            **DO NOT IMPLEMENT. Just add to queue.**
            """,
            subagent_type="use-case-agent",
            model="sonnet"
        )
        # Then execute PHASE B for new tasks
        execute_phase_b_for_tasks("use-case-agent", unprocessed)

    elif layer == "infrastructure_backend":
        print(f"   🔄 Re-invoking infrastructure-agent (backend) PHASE A for {len(unprocessed)} tasks")
        Task(
            description="Infrastructure agent (backend) - Pick up re-classified tasks",
            prompt=f"""
            You are the infrastructure-agent. Read .claude/agents/infrastructure-agent.md.

            **PHASE A: PICK UP RE-CLASSIFIED TASKS (Backend)**

            {len(unprocessed)} tasks were re-classified to infrastructure_backend by other agents.
            Task IDs: {[t['task_id'] for t in unprocessed]}

            YOUR MISSION:
            1. Read docs/state/tasks.json
            2. Find these specific tasks
            3. Add them to infrastructure-backend-queue.json
            4. Return for PHASE B execution

            **DO NOT IMPLEMENT. Just add to queue.**
            """,
            subagent_type="infrastructure-agent",
            model="sonnet"
        )
        execute_phase_b_for_tasks("infrastructure-agent-backend", unprocessed)

    elif layer == "infrastructure_frontend":
        print(f"   🔄 Re-invoking infrastructure-agent (frontend) PHASE A for {len(unprocessed)} tasks")
        Task(
            description="Infrastructure agent (frontend) - Pick up re-classified tasks",
            prompt=f"""
            You are the infrastructure-agent. Read .claude/agents/infrastructure-agent.md.

            **PHASE A: PICK UP RE-CLASSIFIED TASKS (Frontend)**

            {len(unprocessed)} tasks were re-classified to infrastructure_frontend by other agents.
            Task IDs: {[t['task_id'] for t in unprocessed]}

            YOUR MISSION:
            1. Read docs/state/tasks.json
            2. Find these specific tasks
            3. Add them to infrastructure-frontend-queue.json
            4. Return for PHASE B execution

            **DO NOT IMPLEMENT. Just add to queue.**
            """,
            subagent_type="infrastructure-agent",
            model="sonnet"
        )
        execute_phase_b_for_tasks("infrastructure-agent-frontend", unprocessed)

print("✅ REJECTION RECOVERY COMPLETE")

# Final validation: Check no tasks are orphaned
orphaned = find_orphaned_tasks()  # Tasks with owner=null and status!=completed
if orphaned:
    print(f"🔴 Found {len(orphaned)} orphaned tasks - initiating recovery")
    recover_orphaned_tasks(orphaned)
else:
    print("✅ All tasks have been processed or assigned")
```

**Helper Function: find_orphaned_tasks**

```python
def find_orphaned_tasks() -> list:
    """
    Find tasks that are orphaned (no owner, not completed, not in any queue).

    Returns:
        List of orphaned task dicts
    """
    tasks_data = Read("docs/state/tasks.json")
    all_tasks = tasks_data.get("tasks", [])

    # Build set of task IDs that are in queue files
    queued_task_ids = set()
    queue_files = [
        "domain-queue.json",
        "application-queue.json",
        "infrastructure-backend-queue.json",
        "infrastructure-frontend-queue.json"
    ]

    for queue_file in queue_files:
        try:
            queue = Read(f"docs/state/agent-queues/{queue_file}")
            for item in queue.get("queue", []):
                queued_task_ids.add(item.get("task_id"))
        except:
            pass  # Queue file doesn't exist yet

    # Find orphaned tasks
    orphaned = []
    terminal_statuses = ["completed", "escalated"]

    for task in all_tasks:
        task_id = task.get("id")
        status = task.get("status")
        owner = task.get("owner")

        # Skip terminal tasks
        if status in terminal_statuses:
            continue

        # Orphaned if: no owner AND not in any queue
        if owner is None and task_id not in queued_task_ids:
            orphaned.append(task)

    return orphaned


def recover_orphaned_tasks(orphaned_tasks: list):
    """
    Recover orphaned tasks by:
    1. Analyzing why they're orphaned
    2. Offering recovery options to user
    3. Re-assigning to appropriate queues
    """
    print(f"\n{'='*60}")
    print(f"🔄 ORPHANED TASK RECOVERY")
    print(f"{'='*60}")
    print(f"Found {len(orphaned_tasks)} orphaned tasks")

    # Categorize orphans by their layer
    by_layer = {
        "domain": [],
        "application": [],
        "infrastructure_backend": [],
        "infrastructure_frontend": [],
        "unknown": []
    }

    for task in orphaned_tasks:
        layer = task.get("layer")
        if layer in by_layer:
            by_layer[layer].append(task)
        else:
            by_layer["unknown"].append(task)

    # Report
    print(f"\n📊 Orphans by layer:")
    for layer, tasks in by_layer.items():
        if tasks:
            print(f"   {layer}: {len(tasks)} tasks")

    # Ask user how to proceed
    response = AskUserQuestion(questions=[{
        "question": f"¿Cómo quieres manejar los {len(orphaned_tasks)} huérfanos?",
        "header": "Orphan Recovery",
        "options": [
            {"label": "AUTO_RECOVER", "description": "Asignar automáticamente a sus layers"},
            {"label": "CLASSIFY", "description": "Clasificar manualmente los 'unknown'"},
            {"label": "SKIP", "description": "Marcar como escalated y continuar"},
            {"label": "ABORT", "description": "Detener para revisión manual"}
        ],
        "multiSelect": False
    }])

    choice = response.get("answer", "SKIP")

    if choice == "AUTO_RECOVER":
        auto_recover_orphans(by_layer)
    elif choice == "CLASSIFY":
        # Only classify unknowns, auto-recover the rest
        if by_layer["unknown"]:
            classified = classify_unknown_orphans(by_layer["unknown"])
            # Merge classified into by_layer
            for layer, tasks in classified.items():
                by_layer[layer].extend(tasks)
            by_layer["unknown"] = []
        auto_recover_orphans(by_layer)
    elif choice == "SKIP":
        skip_orphaned_tasks(orphaned_tasks)
    elif choice == "ABORT":
        abort_migration("User aborted due to orphaned tasks")


def auto_recover_orphans(by_layer: dict):
    """
    Automatically recover orphaned tasks by adding them to appropriate queues.
    """
    print(f"\n🔄 Auto-recovering orphans...")

    queue_map = {
        "domain": "domain-queue.json",
        "application": "application-queue.json",
        "infrastructure_backend": "infrastructure-backend-queue.json",
        "infrastructure_frontend": "infrastructure-frontend-queue.json"
    }

    recovered = 0
    failed = []

    for layer, tasks in by_layer.items():
        if not tasks or layer == "unknown":
            continue

        queue_file = queue_map.get(layer)
        if not queue_file:
            failed.extend(tasks)
            continue

        queue_path = f"docs/state/agent-queues/{queue_file}"

        # Read or create queue
        try:
            queue = Read(queue_path)
        except:
            queue = {
                "agent": layer.replace("_", "-") + "-agent",
                "created_at": current_timestamp(),
                "total_tasks": 0,
                "completed": 0,
                "queue": [],
                "rejected_tasks": [],
                "escalated_tasks": [],
                "blocked_tasks": []
            }

        # Add orphans to queue
        next_position = len(queue["queue"]) + 1
        for task in tasks:
            # Check if already in queue (avoid duplicates)
            if any(q.get("task_id") == task["id"] for q in queue["queue"]):
                print(f"   ⏭️ {task['id']} already in queue - skipping")
                continue

            queue["queue"].append({
                "position": next_position,
                "task_id": task["id"],
                "title": task.get("title", "Unknown"),
                "status": "pending",
                "test_files": task.get("test_files", []),
                "recovered_from": "orphan_recovery"
            })
            next_position += 1
            recovered += 1

            # Update task in tasks.json
            update_task_for_recovery(task["id"], layer)

        queue["total_tasks"] = len(queue["queue"])
        Write(queue_path, queue)
        print(f"   ✅ Added {len(tasks)} tasks to {queue_file}")

    # Handle unknown layer tasks
    if by_layer.get("unknown"):
        print(f"\n   ⚠️ {len(by_layer['unknown'])} tasks with unknown layer - marking as escalated")
        for task in by_layer["unknown"]:
            mark_task_as_skipped(task["id"])
            failed.append(task)

    # Summary
    print(f"\n📊 Recovery Summary:")
    print(f"   Recovered: {recovered}")
    print(f"   Failed/Unknown: {len(failed)}")

    if failed:
        print(f"\n   Failed tasks:")
        for task in failed[:5]:  # Show max 5
            print(f"      - {task['id']}: {task.get('title', 'Unknown')}")
        if len(failed) > 5:
            print(f"      ... and {len(failed) - 5} more")


def update_task_for_recovery(task_id: str, layer: str):
    """Update a task's status after recovery."""
    def update(tasks_data):
        for task in tasks_data["tasks"]:
            if task["id"] == task_id:
                task["status"] = "queued"
                task["layer"] = layer

                # Add recovery note
                if "recovery_history" not in task:
                    task["recovery_history"] = []

                task["recovery_history"].append({
                    "recovered_from": "orphan",
                    "recovered_to": layer,
                    "timestamp": current_timestamp()
                })

        return tasks_data

    safe_update_state_file("docs/state/tasks.json", update)


def classify_unknown_orphans(unknown_tasks: list) -> dict:
    """
    Interactively classify orphaned tasks with unknown layer.
    """
    classified = {
        "domain": [],
        "application": [],
        "infrastructure_backend": [],
        "infrastructure_frontend": []
    }

    print(f"\n📋 Classifying {len(unknown_tasks)} orphans with unknown layer...")

    for task in unknown_tasks:
        task_id = task["id"]
        title = task.get("title", "Unknown")

        print(f"\n   Task: {task_id}")
        print(f"   Title: {title}")

        response = AskUserQuestion(questions=[{
            "question": f"¿A qué layer pertenece '{title}'?",
            "header": "Classify Orphan",
            "options": [
                {"label": "domain", "description": "Entities, value objects, business rules"},
                {"label": "application", "description": "Use cases, DTOs, interfaces"},
                {"label": "infrastructure_backend", "description": "ORM, API, database"},
                {"label": "infrastructure_frontend", "description": "React, pages, UI"},
                {"label": "SKIP", "description": "Mark as escalated"}
            ],
            "multiSelect": False
        }])

        choice = response.get("answer", "SKIP")

        if choice == "SKIP":
            mark_task_as_skipped(task_id)
        elif choice in classified:
            classified[choice].append(task)
            # Update task layer in tasks.json
            update_task_classification(task_id, choice)

    return classified


def skip_orphaned_tasks(orphaned_tasks: list):
    """Mark all orphaned tasks as escalated/skipped."""
    print(f"\n⏭️ Marking {len(orphaned_tasks)} orphans as skipped...")

    for task in orphaned_tasks:
        def update(tasks_data):
            for t in tasks_data["tasks"]:
                if t["id"] == task["id"]:
                    t["status"] = "escalated"
                    t["escalation_info"] = {
                        "reason": "orphan_skipped",
                        "timestamp": current_timestamp(),
                        "note": "Task was orphaned and user chose to skip"
                    }
            return tasks_data

        safe_update_state_file("docs/state/tasks.json", update)
        print(f"   - {task['id']}: marked as skipped")

    print(f"✅ All orphans marked as skipped")
```

**Helper Function: handle_escalated_tasks**

```python
def handle_escalated_tasks(agent: str, escalated_tasks: list):
    """
    Handle tasks that have exceeded max rejections or have circular rejection patterns.
    These tasks require manual classification by the user.
    """
    if not escalated_tasks:
        return

    print(f"\n🔴 ESCALATED TASKS from {agent}:")
    print(f"   These tasks could not be automatically classified.\n")

    for task in escalated_tasks:
        task_id = task["task_id"]
        title = task["title"]
        reason = task["reason"]
        circular = task.get("circular_detected", False)

        print(f"   📋 {task_id}: {title}")
        print(f"      Reason: {reason}")

        if circular:
            print(f"      ⚠️ CIRCULAR REJECTION DETECTED")
            history = task.get("rejection_history", [])
            if history:
                path = " → ".join([h.get("suggested_layer", "?") for h in history])
                print(f"      Path: {path}")

    # Ask user how to handle escalated tasks
    response = AskUserQuestion(questions=[{
        "question": f"Hay {len(escalated_tasks)} tareas que no pudieron clasificarse automáticamente. ¿Cómo proceder?",
        "header": "Escalated Tasks",
        "options": [
            {"label": "CLASSIFY", "description": "Déjame clasificarlas manualmente"},
            {"label": "SKIP", "description": "Omitir estas tareas y continuar"},
            {"label": "ABORT", "description": "Detener migración para revisión"}
        ],
        "multiSelect": False
    }])

    # Handle user response
    user_choice = response.get("answer", "SKIP")

    if user_choice == "CLASSIFY":
        process_manual_classification(escalated_tasks)
    elif user_choice == "SKIP":
        mark_tasks_as_skipped(escalated_tasks)
    elif user_choice == "ABORT":
        abort_migration("User aborted due to escalated tasks")
```

**Helper Function: process_manual_classification**

```python
def process_manual_classification(escalated_tasks: list):
    """
    Interactively classify escalated tasks with user input.
    """
    print(f"\n📋 MANUAL CLASSIFICATION - {len(escalated_tasks)} tasks")

    classified_tasks = {
        "domain": [],
        "application": [],
        "infrastructure_backend": [],
        "infrastructure_frontend": []
    }

    for task in escalated_tasks:
        task_id = task["task_id"]
        title = task["title"]
        reason = task.get("reason", "No reason provided")

        print(f"\n{'='*60}")
        print(f"📋 Task: {task_id}")
        print(f"   Title: {title}")
        print(f"   Escalation reason: {reason}")

        # Show rejection history if available
        history = task.get("rejection_history", [])
        if history:
            print(f"\n   📜 Rejection history:")
            for i, h in enumerate(history, 1):
                print(f"      {i}. {h.get('rejected_by', '?')} → suggested: {h.get('suggested_layer', '?')}")
                print(f"         Reason: {h.get('reason', 'No reason')}")

        # Ask user for classification
        response = AskUserQuestion(questions=[{
            "question": f"¿A qué layer pertenece '{title}'?",
            "header": "Classification",
            "options": [
                {"label": "domain", "description": "Entities, value objects, business rules (pure logic)"},
                {"label": "application", "description": "Use cases, DTOs, repository interfaces"},
                {"label": "infrastructure_backend", "description": "ORM, API endpoints, database"},
                {"label": "infrastructure_frontend", "description": "React components, pages, UI"},
                {"label": "SKIP", "description": "Skip this task (mark as escalated)"}
            ],
            "multiSelect": False
        }])

        chosen_layer = response.get("answer", "SKIP")

        if chosen_layer == "SKIP":
            print(f"   ⏭️ Skipping {task_id}")
            mark_task_as_skipped(task_id)
        else:
            print(f"   ✅ Classified as: {chosen_layer}")
            classified_tasks[chosen_layer].append(task_id)

            # Update tasks.json
            update_task_classification(task_id, chosen_layer)

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 CLASSIFICATION SUMMARY")
    print(f"{'='*60}")
    for layer, task_ids in classified_tasks.items():
        if task_ids:
            print(f"   {layer}: {len(task_ids)} tasks")
            for tid in task_ids:
                print(f"      - {tid}")

    # Re-queue classified tasks for appropriate agents
    requeue_classified_tasks(classified_tasks)


def update_task_classification(task_id: str, new_layer: str):
    """
    Update a task's layer classification in tasks.json.
    Uses safe locking pattern.
    """
    def update(tasks_data):
        for task in tasks_data["tasks"]:
            if task["id"] == task_id:
                old_layer = task.get("layer")

                # Update task
                task["layer"] = new_layer
                task["owner"] = None  # Clear owner so new agent can pick it up
                task["status"] = "pending"

                # Add manual classification to history
                if "classification_history" not in task:
                    task["classification_history"] = []

                task["classification_history"].append({
                    "classified_by": "user_manual",
                    "from_layer": old_layer,
                    "to_layer": new_layer,
                    "timestamp": current_timestamp(),
                    "was_escalated": True
                })

                # Clear escalation status
                if "escalation_info" in task:
                    del task["escalation_info"]

        return tasks_data

    safe_update_state_file("docs/state/tasks.json", update)
    print(f"   📝 Updated {task_id} → layer={new_layer}")


def mark_task_as_skipped(task_id: str):
    """Mark a task as skipped/escalated in tasks.json."""
    def update(tasks_data):
        for task in tasks_data["tasks"]:
            if task["id"] == task_id:
                task["status"] = "escalated"
                task["escalation_info"] = {
                    "reason": "user_skipped",
                    "timestamp": current_timestamp(),
                    "note": "User chose to skip this task during manual classification"
                }
        return tasks_data

    safe_update_state_file("docs/state/tasks.json", update)


def log_warning_to_state(warning: dict):
    """Log a warning to global state for traceability."""
    try:
        global_state = Read("docs/state/global-state.json")
    except:
        global_state = {"warnings": [], "errors": []}

    if "warnings" not in global_state:
        global_state["warnings"] = []

    global_state["warnings"].append(warning)
    Write("docs/state/global-state.json", global_state)
    print(f"   📝 Warning logged: {warning.get('type', 'unknown')}")


def check_layer_orphans(layer: str):
    """
    Check for orphaned tasks in a specific layer after Phase B completes.
    Orphans = tasks with layer=X, owner=null, status not terminal.
    """
    print(f"\n🔍 Checking for orphans in {layer} layer...")

    tasks_data = Read("docs/state/tasks.json")
    all_tasks = tasks_data.get("tasks", [])

    # Find orphans in this layer
    terminal_statuses = ["completed", "escalated"]
    layer_orphans = [
        t for t in all_tasks
        if t.get("layer") == layer
        and t.get("owner") is None
        and t.get("status") not in terminal_statuses
    ]

    if not layer_orphans:
        print(f"   ✅ No orphans in {layer} layer")
        return

    print(f"   ⚠️ Found {len(layer_orphans)} orphans in {layer} layer:")
    for task in layer_orphans:
        print(f"      - {task['id']}: {task.get('title', 'Unknown')} (status={task.get('status')})")

    # Auto-recover: add to appropriate queue
    queue_map = {
        "domain": "domain-queue.json",
        "application": "application-queue.json",
        "infrastructure_backend": "infrastructure-backend-queue.json",
        "infrastructure_frontend": "infrastructure-frontend-queue.json"
    }

    queue_file = queue_map.get(layer)
    if not queue_file:
        print(f"   🔴 Unknown layer: {layer}")
        return

    queue_path = f"docs/state/agent-queues/{queue_file}"

    # Read existing queue
    try:
        queue = Read(queue_path)
    except:
        print(f"   🔴 Queue file not found: {queue_path}")
        return

    # Add orphans to queue
    added = 0
    for task in layer_orphans:
        # Check not already in queue
        if any(q.get("task_id") == task["id"] for q in queue.get("queue", [])):
            continue

        queue["queue"].append({
            "position": len(queue["queue"]) + 1,
            "task_id": task["id"],
            "title": task.get("title", "Unknown"),
            "status": "pending",
            "test_files": task.get("test_files", []),
            "recovered_from": "layer_orphan_check"
        })
        added += 1

    if added > 0:
        queue["total_tasks"] = len(queue["queue"])
        Write(queue_path, queue)
        print(f"   🔄 Added {added} orphans to {queue_file} for re-processing")

        # Log for traceability
        log_warning_to_state({
            "type": "layer_orphans_recovered",
            "layer": layer,
            "count": added,
            "task_ids": [t["id"] for t in layer_orphans],
            "timestamp": current_timestamp()
        })


def group_rejections_by_suggested_layer(rejection_tracker: dict) -> dict:
    """
    Group rejected tasks by their suggested_layer.
    Returns dict: {layer: [tasks]}
    """
    result = {
        "domain": [],
        "application": [],
        "infrastructure_backend": [],
        "infrastructure_frontend": []
    }

    for rejection in rejection_tracker.get("rejections", []):
        if rejection.get("processed"):
            continue  # Skip already processed

        suggested = rejection.get("suggested_layer")
        if suggested in result:
            result[suggested].append(rejection)

    return result


def mark_tasks_as_skipped(escalated_tasks: list):
    """Mark multiple tasks as skipped."""
    print(f"\n⏭️ Marking {len(escalated_tasks)} tasks as skipped...")

    for task in escalated_tasks:
        mark_task_as_skipped(task["task_id"])
        print(f"   - {task['task_id']}: marked as skipped")

    print(f"✅ All escalated tasks marked as skipped")


def requeue_classified_tasks(classified_tasks: dict):
    """
    Add classified tasks to the appropriate agent queues.
    These will be processed in the next layer execution.
    """
    for layer, task_ids in classified_tasks.items():
        if not task_ids:
            continue

        # Determine queue file based on layer
        queue_map = {
            "domain": "domain-queue.json",
            "application": "application-queue.json",
            "infrastructure_backend": "infrastructure-backend-queue.json",
            "infrastructure_frontend": "infrastructure-frontend-queue.json"
        }

        queue_file = queue_map.get(layer)
        if not queue_file:
            continue

        queue_path = f"docs/state/agent-queues/{queue_file}"

        # Read existing queue or create new
        try:
            queue = Read(queue_path)
        except:
            queue = {
                "agent": layer.replace("_", "-"),
                "created_at": current_timestamp(),
                "total_tasks": 0,
                "completed": 0,
                "queue": [],
                "rejected_tasks": [],
                "escalated_tasks": [],
                "blocked_tasks": []
            }

        # Get task details from tasks.json
        tasks_data = Read("docs/state/tasks.json")
        all_tasks = {t["id"]: t for t in tasks_data.get("tasks", [])}

        # Add tasks to queue
        next_position = len(queue["queue"]) + 1
        for task_id in task_ids:
            task = all_tasks.get(task_id)
            if task:
                queue["queue"].append({
                    "position": next_position,
                    "task_id": task_id,
                    "title": task.get("title", "Unknown"),
                    "status": "pending",
                    "test_files": task.get("test_files", []),
                    "from_manual_classification": True
                })
                next_position += 1

        queue["total_tasks"] = len(queue["queue"])

        # Write queue
        Write(queue_path, queue)
        print(f"   📝 Added {len(task_ids)} tasks to {queue_file}")


def abort_migration(reason: str):
    """
    Abort the migration process cleanly.
    Saves current state and reports reason.
    """
    print(f"\n🛑 MIGRATION ABORTED")
    print(f"   Reason: {reason}")

    # Update global state
    try:
        global_state = Read("docs/state/global-state.json")
        global_state["status"] = "aborted"
        global_state["abort_reason"] = reason
        global_state["abort_timestamp"] = current_timestamp()
        Write("docs/state/global-state.json", global_state)
    except:
        pass

    # Log the abort
    log_transaction("migration_abort", "global-state.json", {
        "reason": reason,
        "timestamp": current_timestamp()
    })

    print(f"\n   State saved. You can review and resume later.")
    print(f"   To resume: run /migrate-start and follow recovery prompts")

    raise MigrationAbortedException(reason)

---

**Helper Function: track_rejected_tasks**

```python
def track_rejected_tasks(rejecting_agent: str, rejected_tasks: list):
    """
    Track rejected tasks in a central file for later processing.
    Called after each agent's PHASE A completes.
    """
    tracker_path = "docs/state/rejection-tracker.json"

    # Read existing tracker or create new
    try:
        tracker = Read(tracker_path)
    except:
        tracker = {"rejections": [], "processed": []}

    # Add new rejections
    for task in rejected_tasks:
        tracker["rejections"].append({
            "task_id": task["task_id"],
            "title": task["title"],
            "rejected_by": rejecting_agent,
            "original_layer": task["original_layer"],
            "suggested_layer": task["suggested_layer"],
            "reason": task["reason"],
            "timestamp": current_timestamp(),
            "processed": False
        })

    Write(tracker_path, tracker)
    print(f"   📝 Tracked {len(rejected_tasks)} rejections in rejection-tracker.json")
```

---

### STEP 6.7: BLOCKED TASK RECOVERY (v4.4 - Critical)

**After all layers complete, process any blocked tasks that may now be unblocked.**

```python
print("🔄 BLOCKED TASK RECOVERY: Processing blocked tasks")

# Collect all blocked tasks from all queues
all_blocked = []
queue_files = [
    "domain-queue.json",
    "application-queue.json",
    "infrastructure-backend-queue.json",
    "infrastructure-frontend-queue.json"
]

for queue_file in queue_files:
    try:
        queue = Read(f"docs/state/agent-queues/{queue_file}")
        blocked = queue.get("blocked_tasks", [])
        if blocked:
            all_blocked.extend([{**b, "queue_file": queue_file} for b in blocked])
    except:
        pass

if not all_blocked:
    print("✅ No blocked tasks to process")
else:
    print(f"⚠️ Found {len(all_blocked)} blocked tasks")

    # Analyze each blocked task
    for blocked_task in all_blocked:
        task_id = blocked_task["task_id"]
        reason = blocked_task["reason"]

        print(f"\n📋 Analyzing blocked task: {task_id}")
        print(f"   Reason: {reason}")

        # Check if the blocker has been resolved
        analysis = analyze_if_blocker_resolved(blocked_task)

        print(f"   Analysis: {analysis['reason']}")
        print(f"   Confidence: {analysis['confidence']*100:.0f}%")

        if analysis["can_retry"] and analysis["confidence"] >= 0.5:
            print(f"   ✅ Blocker appears resolved - scheduling retry")

            # Determine which agent should retry
            agent = determine_agent_from_queue(blocked_task["queue_file"])

            Task(
                description=f"{agent} - Retry blocked task {task_id}",
                prompt=f"""
                You are {agent}. Read .claude/agents/{agent}.md for instructions.

                **RETRY BLOCKED TASK**

                Task {task_id} was previously blocked with reason: {reason}
                The blocker appears to be resolved now.

                YOUR MISSION:
                1. Re-attempt implementing this task
                2. Run tests
                3. If successful: mark as completed
                4. If still blocked: mark as blocked with updated reason

                Context from previous attempt:
                {blocked_task.get("details", "No details available")}
                """,
                subagent_type=get_subagent_type(agent),
                model="sonnet"
            )
        else:
            print(f"   🔴 Blocker NOT resolved - escalating to user")

            # Add to escalation list
            escalations.append({
                "task_id": task_id,
                "reason": reason,
                "details": blocked_task.get("details", "")
            })

# If there are escalations, ask user
if escalations:
    print(f"\n🔴 {len(escalations)} tasks require user attention:")
    for esc in escalations:
        print(f"   - {esc['task_id']}: {esc['reason']}")

    AskUserQuestion(questions=[{
        "question": f"Hay {len(escalations)} tareas bloqueadas que requieren tu atención. ¿Qué hacer?",
        "header": "Blocked Tasks",
        "options": [
            {"label": "SKIP", "description": "Continuar sin estas tareas"},
            {"label": "INVESTIGATE", "description": "Dame más detalles para investigar"},
            {"label": "ABORT", "description": "Detener migración para revisión manual"}
        ],
        "multiSelect": False
    }])
```

**Helper Function: handle_blocked_tasks**

```python
def handle_blocked_tasks(agent: str, queue_file: str):
    """
    Handle blocked tasks after an agent completes its queue.
    Called after each layer's PHASE B completes.
    """
    queue = Read(f"docs/state/agent-queues/{queue_file}")
    blocked = queue.get("blocked_tasks", [])

    if not blocked:
        print(f"   ✅ No blocked tasks in {queue_file}")
        return

    print(f"   ⚠️ {len(blocked)} blocked tasks in {queue_file}")

    for task in blocked:
        print(f"      - {task['task_id']}: {task['reason']}")

    # These will be processed in STEP 6.7 (BLOCKED TASK RECOVERY)
    # For now, just report them
```

**Helper Function: analyze_if_blocker_resolved**

```python
def analyze_if_blocker_resolved(blocked_task: dict) -> dict:
    """
    Analyze if the blocker for a task has been resolved.

    Returns:
        {
            "can_retry": bool,
            "reason": str,
            "confidence": float,  # 0.0 - 1.0
            "details": str
        }
    """
    reason = blocked_task.get("reason", "unknown")
    task_id = blocked_task["task_id"]
    blocker_info = blocked_task.get("blocker_info", {})
    details = blocked_task.get("details", "")

    result = {
        "can_retry": False,
        "reason": "Unable to determine",
        "confidence": 0.0,
        "details": ""
    }

    # Read current tasks.json to check dependencies
    tasks_data = Read("docs/state/tasks.json")
    tasks = tasks_data.get("tasks", [])
    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        result["reason"] = f"Task {task_id} not found in tasks.json"
        return result

    # ===============================
    # REASON: missing_dependency
    # ===============================
    if reason == "missing_dependency":
        # Extract dependency info
        # Expected format in details: "Requires TASK-XXX to be completed" or "depends_on: [TASK-001, TASK-002]"
        dependency_ids = extract_dependency_ids(details, blocker_info)

        if not dependency_ids:
            result["reason"] = "Could not identify dependency from blocker details"
            result["details"] = f"Raw details: {details}"
            return result

        # Check status of each dependency
        all_resolved = True
        unresolved = []
        for dep_id in dependency_ids:
            dep_task = next((t for t in tasks if t["id"] == dep_id), None)
            if not dep_task:
                unresolved.append(f"{dep_id} (not found)")
                all_resolved = False
            elif dep_task.get("status") != "completed":
                unresolved.append(f"{dep_id} (status: {dep_task.get('status')})")
                all_resolved = False

        if all_resolved:
            result["can_retry"] = True
            result["reason"] = f"All dependencies resolved: {dependency_ids}"
            result["confidence"] = 0.9
        else:
            result["reason"] = f"Dependencies still unresolved: {unresolved}"
            result["details"] = f"Required: {dependency_ids}"

        return result

    # ===============================
    # REASON: domain_entity_missing
    # ===============================
    elif reason == "domain_entity_missing":
        # Check if ALL domain tasks are completed (not just most)
        domain_tasks = [t for t in tasks if t.get("layer") == "domain"]

        if not domain_tasks:
            result["reason"] = "No domain tasks found"
            return result

        completed = [t for t in domain_tasks if t.get("status") == "completed"]
        blocked = [t for t in domain_tasks if t.get("status") == "blocked"]

        completion_rate = len(completed) / len(domain_tasks)

        # Extract specific entity name if mentioned
        entity_name = extract_entity_name(details, blocker_info)

        if entity_name:
            # Check if specific entity task is completed
            entity_task = next((t for t in domain_tasks if entity_name.lower() in t.get("title", "").lower()), None)
            if entity_task and entity_task.get("status") == "completed":
                result["can_retry"] = True
                result["reason"] = f"Entity '{entity_name}' task is now completed"
                result["confidence"] = 0.95
                return result
            elif entity_task:
                result["reason"] = f"Entity '{entity_name}' task status: {entity_task.get('status')}"
                return result

        # Fallback: check if domain layer is sufficiently complete
        if completion_rate >= 0.9 and len(blocked) == 0:
            result["can_retry"] = True
            result["reason"] = f"Domain layer {completion_rate*100:.0f}% complete"
            result["confidence"] = 0.7
        else:
            result["reason"] = f"Domain layer only {completion_rate*100:.0f}% complete, {len(blocked)} blocked"

        return result

    # ===============================
    # REASON: use_case_missing
    # ===============================
    elif reason == "use_case_missing":
        app_tasks = [t for t in tasks if t.get("layer") == "application"]

        if not app_tasks:
            result["reason"] = "No application tasks found"
            return result

        completed = [t for t in app_tasks if t.get("status") == "completed"]
        blocked = [t for t in app_tasks if t.get("status") == "blocked"]

        completion_rate = len(completed) / len(app_tasks)

        # Extract specific use case name if mentioned
        use_case_name = extract_use_case_name(details, blocker_info)

        if use_case_name:
            use_case_task = next((t for t in app_tasks if use_case_name.lower() in t.get("title", "").lower()), None)
            if use_case_task and use_case_task.get("status") == "completed":
                result["can_retry"] = True
                result["reason"] = f"Use case '{use_case_name}' is now completed"
                result["confidence"] = 0.95
                return result
            elif use_case_task:
                result["reason"] = f"Use case '{use_case_name}' status: {use_case_task.get('status')}"
                return result

        if completion_rate >= 0.9 and len(blocked) == 0:
            result["can_retry"] = True
            result["reason"] = f"Application layer {completion_rate*100:.0f}% complete"
            result["confidence"] = 0.7
        else:
            result["reason"] = f"Application layer only {completion_rate*100:.0f}% complete"

        return result

    # ===============================
    # REASON: repository_interface_mismatch
    # ===============================
    elif reason == "repository_interface_mismatch":
        # This typically requires the interface to be regenerated
        # Check if there's been any update to the relevant interface file
        interface_file = blocker_info.get("file", "")
        if interface_file:
            # Check if file was modified recently (would need file timestamps)
            # For now, recommend retry if domain is complete
            domain_status = verify_layer_completeness("domain")
            if domain_status["is_complete"]:
                result["can_retry"] = True
                result["reason"] = "Domain layer complete - interface should be stable"
                result["confidence"] = 0.6
            else:
                result["reason"] = "Domain layer incomplete - interface may change"
        return result

    # ===============================
    # REASON: import_error / type_error / syntax_error
    # ===============================
    elif reason in ["import_error", "type_error", "syntax_error"]:
        # These errors might be resolved if dependent files were fixed
        # Check if the dependent layer is now complete
        task_layer = task.get("layer", "")

        if task_layer == "application":
            prereq = verify_layer_completeness("domain")
        elif task_layer in ["infrastructure_backend", "infrastructure_frontend"]:
            prereq = verify_all_prerequisites(task_layer)
        else:
            prereq = {"is_complete": True}  # Domain has no prereqs

        # For import/type errors, we should retry once dependencies are met
        if prereq.get("is_complete") or prereq.get("can_proceed", False):
            result["can_retry"] = True
            result["reason"] = f"Prerequisites met - worth retrying {reason}"
            result["confidence"] = 0.5  # Medium confidence, might fail again
        else:
            result["reason"] = f"Prerequisites not met for {task_layer}"

        return result

    # ===============================
    # REASON: circular_dependency
    # ===============================
    elif reason == "circular_dependency":
        # Circular dependencies require manual intervention
        result["can_retry"] = False
        result["reason"] = "Circular dependencies require manual task restructuring"
        result["confidence"] = 0.0
        return result

    # ===============================
    # REASON: business_rule_unclear
    # ===============================
    elif reason == "business_rule_unclear":
        # Check if there's been a clarification added to the task
        clarification = task.get("clarification", task.get("notes", ""))
        if clarification:
            result["can_retry"] = True
            result["reason"] = "Clarification was added to task"
            result["confidence"] = 0.8
        else:
            result["reason"] = "No clarification found - requires user input"
        return result

    # ===============================
    # REASON: test_setup_error
    # ===============================
    elif reason == "test_setup_error":
        # Check if conftest.py exists and pytest is available
        result["can_retry"] = True
        result["reason"] = "Test setup errors may be transient - worth retrying"
        result["confidence"] = 0.4
        return result

    # ===============================
    # REASON: unknown / other
    # ===============================
    else:
        # For unknown reasons, check if enough time/tasks have passed
        result["can_retry"] = True
        result["reason"] = f"Unknown reason '{reason}' - attempting retry"
        result["confidence"] = 0.3
        return result


def extract_dependency_ids(details: str, blocker_info: dict) -> list:
    """Extract task IDs from dependency info."""
    import re

    task_ids = []

    # Check blocker_info first
    if blocker_info.get("depends_on"):
        return blocker_info["depends_on"]

    if blocker_info.get("dependency_id"):
        return [blocker_info["dependency_id"]]

    # Parse from details string
    # Pattern: TASK-XXX
    matches = re.findall(r'TASK-\d+', str(details))
    if matches:
        return list(set(matches))

    return task_ids


def extract_entity_name(details: str, blocker_info: dict) -> str:
    """Extract entity name from blocker details."""
    if blocker_info.get("entity"):
        return blocker_info["entity"]

    # Try to parse from details
    # Pattern: "Entity 'CustomerEntity' not found" or "Missing Customer entity"
    import re
    match = re.search(r"[Ee]ntity\s+['\"]?(\w+)['\"]?", str(details))
    if match:
        return match.group(1)

    return ""


def extract_use_case_name(details: str, blocker_info: dict) -> str:
    """Extract use case name from blocker details."""
    if blocker_info.get("use_case"):
        return blocker_info["use_case"]

    # Try to parse from details
    import re
    match = re.search(r"[Uu]se\s*[Cc]ase\s+['\"]?(\w+)['\"]?", str(details))
    if match:
        return match.group(1)

    return ""
```

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
