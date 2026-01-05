# Problemas Encontrados en el Framework v4.1-CLEAN-ARCH

**Última actualización**: 2026-01-01 (Post-ejecución Customer module)

---

## 📊 RESUMEN EJECUTIVO

| # | Problema | Severidad | Estado |
|---|----------|-----------|--------|
| 1 | Orquestador entrega sin E2E tests | **CRÍTICO** | ⏳ Pendiente |
| 2 | e2e-qa-agent nunca se invoca | **CRÍTICO** | ⏳ Pendiente |
| 3 | No genera tasks.json (PHASE 0.7) | **CRÍTICO** | ⏳ Pendiente |
| 4 | No invoca qa-test-generator (PHASE 0.8 TDD) | **CRÍTICO** | ⏳ Pendiente |
| 5 | Imports incorrectos en backend | **ALTO** | ✅ Corregido |
| 6 | Dependencias faltantes | **MEDIO** | ✅ Corregido |
| 7 | Docker no disponible | **MEDIO** | ✅ Workaround |
| 8 | CORS incompleto | **BAJO** | ✅ Corregido |
| 9 | Next.js 15 async params | **BAJO** | ✅ Corregido |

**Nivel de confianza del framework**:
- **Antes de correcciones**: 40% (salta fases críticas)
- **Después de correcciones**: 95% (código validado + E2E pass)

---

## 🐛 Problema 1: Flujo del Orquestador Incorrecto

**Descripción**: El orquestador entrega el módulo al usuario ANTES de ejecutar y validar las pruebas E2E.

**Flujo Actual (Incorrecto)**:
```
Contratos → Domain → Application → Infrastructure → Frontend → UI Design → ✅ ENTREGA
                                                                           ❌ No E2E tests
```

**Flujo Correcto (Esperado)**:
```
Contratos → Domain → Application → Infrastructure → Frontend → UI Design →
→ E2E Tests (e2e-qa-agent) → ✅ Solo si pass rate >= 95% → ENTREGA
```

**Impacto**: **CRÍTICO**
- El usuario recibe código que NO ha sido validado end-to-end
- No hay garantía de que el frontend funcione con el backend
- No hay validación de user flows completos

**Solución Requerida**:
1. El orquestador debe invocar al **e2e-qa-agent** después de implementar el frontend
2. El e2e-qa-agent debe ejecutar pruebas Playwright contra backend + frontend corriendo
3. Solo si pass rate >= 95%, el orquestador entrega al usuario
4. Si pass rate < 95%, el orquestador debe:
   - Analizar fallos
   - Corregir código
   - Re-ejecutar tests
   - Máx 5 iteraciones

---

## 🐛 Problema 2: e2e-qa-agent Nunca Se Usa

**Descripción**: En ningún momento del flujo se invoca al agente **e2e-qa-agent** que está diseñado específicamente para ejecutar y validar pruebas E2E.

**Evidencia**:
- Se generó UI design
- Se implementó frontend
- Se entregó al usuario
- **NUNCA se ejecutó**: `Task(subagent_type="e2e-qa-agent")`

**Impacto**: **ALTO**
- El agente especializado en E2E no se utiliza
- No hay ejecución automatizada de Playwright
- No hay reporte de fallos E2E
- No hay iteraciones de corrección

**Solución Requerida**:
Después de implementar el frontend, el orquestador debe:

```python
# DESPUÉS de infrastructure-agent implementa frontend
Task(
    description="Execute E2E tests for Customer module",
    prompt="""
    Read .claude/agents/e2e-qa-agent.md for instructions.

    MODULE: Customer

    YOUR MISSION:
    1. Start backend: docker-compose up -d
    2. Start frontend: cd frontend && npm run dev
    3. Execute Playwright tests: npx playwright test
    4. Analyze failures with screenshots
    5. Categorize errors (frontend_rendering, backend_logic, etc.)
    6. Generate report: docs/qa/e2e-report-customer-iter-1.json
    7. Update global-state.json with pass_rate

    DELIVERABLES:
    - E2E test execution results
    - Screenshots of failures
    - Failure analysis with root cause
    - Suggested fixes per failure
    - Pass rate percentage
    """,
    subagent_type="e2e-qa-agent",
    model="sonnet"
)
```

---

## 🐛 Problema 3: Imports Incorrectos en Backend

**Descripción**: El código generado en `backend/app/main.py` usa imports relativos que fallan al ejecutar.

**Código Generado (Incorrecto)**:
```python
from infrastructure.database.config import init_db, engine
from infrastructure.api.routes import customer_router
```

**Error al Ejecutar**:
```
ModuleNotFoundError: No module named 'infrastructure'
```

**Código Correcto**:
```python
from app.infrastructure.database.config import init_db, engine
from app.infrastructure.api.routes import customer_router
```

**Impacto**: **ALTO**
- El backend no inicia
- Usuario no puede probar la aplicación
- Requiere corrección manual

**Solución Requerida**:
- El infrastructure-agent debe usar SIEMPRE imports absolutos con prefijo `app.`
- Todos los archivos en `backend/app/` deben usar: `from app.xxx.yyy import zzz`
- Agregar validación: el orquestador debe verificar que el backend inicie antes de continuar

---

## 🐛 Problema 4: Dependencias Faltantes

**Descripción**: El `requirements.txt` generado no incluye todas las dependencias necesarias.

**Dependencias Faltantes**:
- `asyncpg` (para PostgreSQL async)
- `aiosqlite` (para SQLite async)
- Otras dependencias de dominio/application

**Error**:
```
ModuleNotFoundError: No module named 'asyncpg'
```

**Impacto**: **MEDIO**
- El backend no inicia hasta instalar manualmente
- El pip install falla

**Solución Requerida**:
El infrastructure-agent debe generar `requirements.txt` COMPLETO:

```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
asyncpg==0.31.0
aiosqlite==0.20.0
pydantic==2.10.3
pydantic-settings==2.6.1
python-multipart==0.0.20
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
httpx==0.28.1
```

---

## 🐛 Problema 5: Docker No Disponible

**Descripción**: El framework asume que Docker está corriendo, pero en el ambiente de prueba no lo está.

**Error**:
```
Cannot connect to the Docker daemon at unix:///Users/constantinostrada/.docker/run/docker.sock
```

**Impacto**: **MEDIO**
- docker-compose no funciona
- Necesita alternativa (SQLite local)

**Solución Implementada (Temporal)**:
- Script `start-local.sh` que usa SQLite en lugar de PostgreSQL
- No requiere Docker
- Funciona para demo/POC

**Solución Permanente Requerida**:
- El orquestador debe detectar si Docker está disponible
- Si Docker NO está: ofrecer alternativa con SQLite
- Si Docker SÍ está: usar docker-compose

---

## 📝 Correcciones Implementadas (Temporary Fixes)

1. ✅ Creado `start-local.sh` - Script para correr sin Docker
2. ✅ Corregido imports en `main.py` - Prefijo `app.`
3. ✅ Instalado `asyncpg` y `aiosqlite` manualmente
4. ⏳ Pendiente: Levantar backend + frontend
5. ⏳ Pendiente: Ejecutar E2E tests con e2e-qa-agent

---

## 🎯 Próximos Pasos Inmediatos

1. **Terminar de corregir el backend** para que inicie correctamente
2. **Levantar el frontend** (npm run dev)
3. **Verificar que ambos se comunican** (API calls funcionan)
4. **Ejecutar e2e-qa-agent** para validar user flows
5. **Solo entonces entregar al usuario**

---

## 📊 Impacto en el Framework

### Severidad de Problemas:
- **CRÍTICO**: Problema 1 (Flujo del orquestador)
- **CRÍTICO**: Problema 2 (e2e-qa-agent no se usa)
- **ALTO**: Problema 3 (Imports incorrectos)
- **MEDIO**: Problema 4 (Dependencias faltantes)
- **MEDIO**: Problema 5 (Docker no disponible)

### Nivel de Confianza del Framework:
- **Antes de correcciones**: 60% (código generado pero no validado)
- **Después de correcciones**: 95% (código generado + validado + E2E pass)

---

## 🔧 Cambios Requeridos en CLAUDE.md

### 1. Actualizar PHASE 4 (Infrastructure Layer):

**AGREGAR después de implementar frontend**:

```markdown
### Step D.5: UI Design with shadcn-ui-agent (ANTES de implementar frontend)

Invoke shadcn-ui-agent:
- Research shadcn/ui components
- Design all pages
- Generate UI design document
- WAIT for design document
- THEN proceed to frontend implementation

### Step D.6: Frontend Implementation (DESPUÉS de UI design)

Implement frontend following UI design document:
- Install shadcn/ui components from design doc
- Implement pages/components
- Follow design EXACTLY

### Step D.7: **VALIDATE STARTUP** ⚠️ CRITICAL

BEFORE proceeding to E2E, validate that backend + frontend START:

\```python
# Validate backend starts
Bash: cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000
# Wait 5 seconds
Bash: curl http://localhost:8000/docs
# If fails: FIX imports and dependencies

# Validate frontend starts
Bash: cd frontend && npm run dev
# Wait 10 seconds
Bash: curl http://localhost:3000
# If fails: FIX dependencies

# Only if BOTH start successfully → Proceed to E2E
\```
```

### 2. Actualizar PHASE 5 (E2E QA):

**REEMPLAZAR completamente PHASE 5**:

```markdown
## PHASE 5: E2E QA with e2e-qa-agent ⚠️ MANDATORY

**Objective**: Execute E2E tests and validate user flows

**Agent**: e2e-qa-agent

**CRITICAL**: This phase is MANDATORY. Do NOT skip. Do NOT deliver to user without passing E2E tests.

\```python
iteration = 0
max_iterations = 5
pass_rate = 0

while iteration < max_iterations and pass_rate < 0.95:
    iteration += 1

    # Invoke e2e-qa-agent
    Task(
        description=f"Execute E2E tests for {module} (iteration {iteration})",
        prompt=f\"\"\"
        Read .claude/agents/e2e-qa-agent.md for instructions.

        MODULE: {module}
        ITERATION: {iteration}

        YOUR MISSION:
        1. Ensure backend is running: docker-compose up -d OR python backend
        2. Ensure frontend is running: npm run dev
        3. Execute Playwright: npx playwright test tests/e2e/{module}/
        4. Capture screenshots of failures
        5. Analyze each failure:
           - Category (frontend_rendering, backend_logic, api_contract, etc.)
           - Root cause
           - Affected file and line
           - Suggested fix
        6. Write report: docs/qa/e2e-report-{module}-iter-{iteration}.json
        7. Update global-state.json with pass_rate

        DELIVERABLES:
        - docs/qa/e2e-report-{module}-iter-{iteration}.json
        - Pass rate (0.0 - 1.0)
        - List of failures with analysis
        \"\"\",
        subagent_type="e2e-qa-agent",
        model="sonnet"
    )

    # Read report
    Read: docs/qa/e2e-report-{module}-iter-{iteration}.json
    pass_rate = report["pass_rate"]

    # Check if passed
    if pass_rate >= 0.95:
        print(f"✅ {module} E2E tests PASSED ({pass_rate*100}%)")
        break

    # Analyze and fix failures
    print(f"🔧 Fixing {len(report['failures'])} E2E failures...")

    for failure in report["failures"]:
        # Read affected file
        Read: {failure["affected_file"]}

        # Apply fix based on category
        if failure["category"] == "frontend_rendering":
            # Fix React component
            Edit: {failure["affected_file"]}
        elif failure["category"] == "backend_logic":
            # Fix use case or domain logic
            Edit: {failure["affected_file"]}
        elif failure["category"] == "api_contract":
            # Fix API endpoint
            Edit: {failure["affected_file"]}

        # Re-run related tests
        Bash: npx playwright test {failure["test_file"]}

# After loop
if pass_rate < 0.95:
    # Ask user if they want to continue or stop
    AskUserQuestion(
        questions=[{
            "question": f"E2E tests pass rate is {pass_rate*100}% (target: 95%). Continue fixing or deliver as-is?",
            "header": "E2E Tests",
            "multiSelect": false,
            "options": [
                {"label": "Continue fixing", "description": "Run more iterations to reach 95%"},
                {"label": "Deliver as-is", "description": "Accept current pass rate and deliver"}
            ]
        }]
    )
else:
    print(f"✅ E2E tests PASSED with {pass_rate*100}% pass rate")

# Update global state
modules[{module}]["e2e_tested"] = True
modules[{module}]["e2e_pass_rate"] = pass_rate
\```

**DO NOT PROCEED TO DELIVERY WITHOUT E2E VALIDATION**
```

### 3. Actualizar PHASE 6 (Final Validation):

**AGREGAR validación obligatoria**:

```markdown
## PHASE 6: Final Validation & Delivery

**Objective**: Validate everything works and generate documentation

**MANDATORY CHECKS** ⚠️:

\```python
# 1. Verify E2E tests passed
assert modules[{module}]["e2e_tested"] == True
assert modules[{module}]["e2e_pass_rate"] >= 0.95

# 2. Verify backend + frontend start
assert backend_starts_successfully()
assert frontend_starts_successfully()

# 3. Verify all tests pass
assert unit_tests_pass_rate == 1.0
assert integration_tests_pass_rate == 1.0

# 4. Only then generate delivery
\```

If ANY check fails:
- ❌ DO NOT DELIVER
- 🔧 FIX issues
- 🔄 RE-RUN checks

Only when ALL checks pass:
- ✅ Generate final report
- ✅ Generate README
- ✅ Deliver to user
```

---

## 📌 Resumen de Correcciones Necesarias

| Problema | Severidad | Corrección | Estado |
|----------|-----------|------------|--------|
| Flujo sin E2E | CRÍTICO | Agregar PHASE 5 obligatoria | ⏳ Pendiente |
| e2e-qa-agent no se usa | CRÍTICO | Invocar después de frontend | ⏳ Pendiente |
| No genera tasks.json | CRÍTICO | Implementar PHASE 0.7 | ⏳ Pendiente |
| No invoca qa-test-generator | CRÍTICO | Implementar PHASE 0.8 TDD | ⏳ Pendiente |
| Imports incorrectos | ALTO | Usar `from app.` | ✅ Corregido |
| Dependencias faltantes | MEDIO | requirements.txt completo | ✅ Corregido |
| Docker no disponible | MEDIO | Alternativa con SQLite | ✅ Implementado |
| CORS incompleto | BAJO | Agregar localhost:3001 | ✅ Corregido |
| Next.js 15 async params | BAJO | Usar React.use() | ✅ Corregido |

---

## 🐛 Problema 3: No Genera tasks.json (PHASE 0.7)

**Descripción**: El orquestador **NO ejecuta PHASE 0.7** (Task Generation) que debe convertir requirements en tareas atómicas.

**Evidencia**:
```bash
$ find . -name "tasks.json"
# (vacío - archivo no existe)
```

**Impacto**: **CRÍTICO**
- ❌ No hay trazabilidad: FR/NFR → Tasks → Code → Tests
- ❌ No hay división granular de trabajo
- ❌ Imposible trackear progreso por tarea
- ❌ Agentes no saben qué tareas tienen asignadas
- ❌ No hay test_strategy por tarea (TDD)

**Flujo Esperado (PHASE 0.7)**:
```python
# Después de requirements.json
for module in modules:
    tasks = []

    # A) Contract task
    tasks.append({
        "id": f"TASK-{module}-001-CONTRACTS",
        "type": "contracts",
        "deliverables": ["openapi.yaml", "types.ts", "schema.sql"]
    })

    # B) Domain task
    tasks.append({
        "id": f"TASK-{module}-002-DOMAIN",
        "type": "implementation",
        "layer": "domain",
        "assigned_to": "domain-agent",
        "related_requirements": ["FR-001", "FR-002"]
    })

    # C) Use case task
    # D) Infrastructure tasks
    # E) E2E task

Write: docs/state/tasks.json
```

**Solución Requerida**:
1. Orquestador debe implementar PHASE 0.7 completa
2. Generar tasks.json con todas las tareas antes de implementar
3. Cada tarea debe tener: id, type, layer, assigned_to, dependencies, deliverables

---

## 🐛 Problema 4: No Invoca qa-test-generator (PHASE 0.8 TDD)

**Descripción**: El orquestador **NO ejecuta PHASE 0.8** que debe enriquecer tasks.json con especificaciones de tests (TDD).

**Evidencia**:
- tasks.json no existe (problema #3)
- Nunca se invocó: `Task(subagent_type="qa-test-generator")`
- Los agentes implementaron sin test_strategy predefinido

**Impacto**: **CRÍTICO**
- ❌ No hay TDD (Test-Driven Development)
- ❌ Tests escritos DESPUÉS del código (no antes)
- ❌ No hay especificación de qué tests escribir
- ❌ Cada agente decide arbitrariamente qué testear

**Flujo Esperado (PHASE 0.8)**:
```python
# Después de generar tasks.json
Task(
    description="Enrich tasks with TDD test specifications",
    prompt="""
    Read .claude/agents/qa-test-generator.md for instructions.

    INPUT: docs/state/tasks.json (sin test_strategy)
    OUTPUT: docs/state/tasks.json (CON test_strategy)

    Para cada task de implementación, agregar:
    {
      "test_strategy": {
        "unit_tests": [
          {
            "name": "test_customer_creation_valid",
            "scenario": "Happy path - valid customer",
            "arrange": "Create customer with valid data",
            "act": "Call Customer() constructor",
            "assert": "Customer created successfully",
            "mocks_required": []
          }
        ],
        "integration_tests": [...],
        "e2e_tests": [...]
      }
    }
    """,
    subagent_type="qa-test-generator",
    model="sonnet"
)
```

**Solución Requerida**:
1. Orquestador debe invocar qa-test-generator DESPUÉS de generar tasks.json
2. qa-test-generator debe enriquecer TODAS las tareas con test_strategy
3. Agentes de implementación deben LEER test_strategy y escribir tests ANTES de código

---

## 🐛 Problema 8: CORS Incompleto

**Descripción**: Backend configurado para `localhost:3000` pero frontend corrió en `localhost:3001`.

**Error**:
```
OPTIONS /api/v1/customers HTTP/1.1" 400 Bad Request
Network Error (frontend)
```

**Solución Aplicada**: ✅
```python
# backend/app/main.py
allow_origins=[
    "http://localhost:3000",
    "http://localhost:3001",  # ← AGREGADO
    ...
]
```

---

## 🐛 Problema 9: Next.js 15 Async Params

**Descripción**: infrastructure-agent generó código con Next.js 14 syntax, pero el proyecto tiene Next.js 16.1.1.

**Error**:
```
A param property was accessed directly with `params.id`.
`params` is a Promise and must be unwrapped with `React.use()`
```

**Archivos afectados**:
- `frontend/app/customers/[id]/page.tsx`
- `frontend/app/customers/[id]/edit/page.tsx`

**Solución Aplicada**: ✅
```typescript
// ANTES (incorrecto)
export default function Page({ params }: { params: { id: string } }) {
  const customer = useCustomer(params.id);
}

// DESPUÉS (correcto)
import { use } from 'react';
export default function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const customer = useCustomer(id);
}
```

---

**Generado**: 2026-01-01
**Autor**: Análisis post-implementación módulo Customer
**Framework**: v4.1-CLEAN-ARCH (requiere v4.2 con correcciones)
