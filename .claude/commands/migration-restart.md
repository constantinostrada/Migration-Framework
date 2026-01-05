# Migration Restart Command

You are restarting or archiving the current migration. Follow these steps:

## Step 1: Check Current State

Read `docs/state/global-state.json` to understand current state.

**Also check for**:
- `output/` directory (contains generated code)
- `docs/analysis/` directory (SDD analysis)
- `docs/state/tasks.json` (task list)

If no active migration files found:
```
ℹ️ No hay ninguna migración activa para reiniciar.
Usa el framework para comenzar una nueva migración.
```

## Step 2: Present Options

If migration exists:

```
⚠️ REINICIO DE MIGRACIÓN
━━━━━━━━━━━━━━━━━━━━━━━

Proyecto actual: [project_name]
Fase: [current_phase]
Progreso: [progress]%

¿Qué deseas hacer?

1. 📦 ARCHIVAR
   Guardar todo el código y documentación en una carpeta
   y comenzar una nueva migración limpia.

2. 🗑️ ELIMINAR
   Borrar todo el código generado y comenzar de cero.
   ⚠️ Esta acción es irreversible.

3. 🔄 RESETEAR FASE
   Mantener el código pero volver a una fase específica
   para rehacer parte del proceso.

4. ❌ CANCELAR
   No hacer nada, continuar con la migración actual.

Escribe 1, 2, 3 o 4:
```

## Step 3: Execute Selected Option

### Option 1: ARCHIVE

1. Create archive directory:
   ```
   archived/migration-[YYYY-MM-DD-HH-MM]/
   ```

2. Move directories:
   - `output/` → `archived/.../output/`
   - `docs/analysis/` → `archived/.../docs/analysis/`
   - `docs/design/` → `archived/.../docs/design/`
   - `docs/qa/` → `archived/.../docs/qa/`
   - `docs/state/` → `archived/.../docs/state/`
   - `docs/tech-stack/` → `archived/.../docs/tech-stack/`
   - `docs/ui-design/` → `archived/.../docs/ui-design/`
   - `docs/ui-mockups/` → `archived/.../docs/ui-mockups/`
   - `docs/tech-context/` → `archived/.../docs/tech-context/`

3. Generate `migration-summary.md` in archive:
   ```markdown
   # Migration Archive Summary

   - **Project**: [name]
   - **Started**: [created_at]
   - **Archived**: [now]
   - **Final Phase**: [phase]
   - **Progress**: [progress]%

   ## Phase Status
   - ANALYSIS: [status]
   - FEEDBACK: [status]
   - DESIGN: [status]
   - CONSTRUCTION: [status]
   - TESTING: [status]

   ## Statistics
   - Entities: [count]
   - Endpoints: [count]
   - Components: [count]
   - Tests: [pass]/[total]

   ## Key Decisions
   [Copy from decisions-log.md]
   ```

4. Reset state to IDLE

5. Recreate empty structure

6. Confirm:
   ```
   ✅ Migración archivada en: archived/migration-[timestamp]/

   🆕 Proyecto limpio y listo.
   Usa `/migration start` para comenzar una nueva migración.
   ```

### Option 2: DELETE

1. Confirm deletion (dangerous):
   ```
   ⚠️ CONFIRMACIÓN REQUERIDA

   Esto eliminará PERMANENTEMENTE:
   - Todo el código en src/
   - Toda la documentación en docs/
   - Todos los reportes de QA

   Escribe "CONFIRMAR ELIMINACIÓN" para proceder:
   ```

2. If confirmed:
   - Delete `output/` directory (all generated code)
   - Delete `docs/analysis/`, `docs/design/`, `docs/qa/`, `docs/state/`
   - Delete `docs/tech-stack/`, `docs/ui-design/`, `docs/ui-mockups/`, `docs/tech-context/`
   - Keep `docs/input/` and `archived/`
   - Keep `.claude/` directory (framework files)

3. Confirm:
   ```
   ✅ Proyecto eliminado.
   Usa `/migration start` para comenzar una nueva migración.
   ```

### Option 3: RESET PHASE

1. Ask which phase:
   ```
   ¿A qué fase quieres volver?

   1. ANÁLISIS - Reiniciar todo el análisis
   2. FEEDBACK - Volver a validar con el usuario
   3. DISEÑO - Rediseñar la arquitectura
   4. CONSTRUCCIÓN - Reimplementar el código
   5. TESTING - Volver a ejecutar tests

   Escribe 1-5:
   ```

2. Clean appropriate directories based on selection:
   - ANALYSIS: Clean all `docs/` (except `docs/input/`) and `output/`
   - FEEDBACK: Clean `docs/design/`, `docs/qa/`, `output/`
   - DESIGN: Clean `docs/qa/`, `output/`
   - CONSTRUCTION: Clean `output/`, `docs/qa/`
   - TESTING: Clean `docs/qa/`

3. Update state to selected phase

4. Confirm:
   ```
   ✅ Migración reseteada a fase: [PHASE]
   Continuando desde esta fase...
   ```

### Option 4: CANCEL

```
👍 Operación cancelada.
Continuando con la migración actual en fase [PHASE].
```

## Important Notes

- ALWAYS create archive before destructive operations
- ALWAYS confirm dangerous actions twice
- NEVER delete `archived/` directory
- NEVER delete `.claude/` directory (framework files)
- Update state after every operation
- Check for `docs/state/global-state.json` (v4.3) not `orchestrator-state.json`
- Clean `output/` directory (contains all generated code)
- Clean v4.3 directories: `docs/tech-stack/`, `docs/ui-design/`, `docs/ui-mockups/`, `docs/tech-context/`

## Files to Clean in v4.3

**Framework v4.3 directories to clean**:
- `output/{project-name}/` - Generated code (backend, frontend, contracts)
- `docs/state/global-state.json` - Migration state
- `docs/state/tasks.json` - Task list
- `docs/analysis/` - SDD analysis (module-map, requirements, business-rules)
- `docs/design/` - FDD documents
- `docs/qa/` - Test reports (smoke tests, E2E reports)
- `docs/tech-stack/` - Tech stack validation reports (v4.3)
- `docs/ui-design/` - UI design documents (shadcn-ui-agent)
- `docs/ui-mockups/` - HTML mockups (ui-approval-agent v4.3)
- `docs/tech-context/` - Tech research documents (context7-agent)

**Framework files to KEEP**:
- `.claude/` - Framework configuration and agents
- `docs/input/` - Input documents (SDD, specifications)
- `archived/` - Previous migration archives
- `CLAUDE.md` - Framework instructions
