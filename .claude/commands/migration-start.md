# Migration Start Command

You are starting a new migration project. Follow these steps:

## Step 1: Check for Existing Migration

First, check if there's already a migration in progress:
- Read `docs/state/orchestrator-state.json`
- If `current_phase` is not "IDLE" or "COMPLETED", warn the user:
  ```
  ⚠️ Ya hay una migración en progreso (Fase: [PHASE]).
  Usa `/migration restart` para archivarla o reiniciarla.
  ```

## Step 2: Welcome & Document Collection

If no active migration, greet the user and request documents:

```
🚀 INICIANDO NUEVA MIGRACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━

¡Bienvenido al Framework Universal de Migración!

Por favor, proporciona los siguientes documentos:

📄 REQUERIDOS:
1. SDD del sistema legacy (PDF, MD, TXT)
2. Reglas de negocio documentadas
3. Requerimientos funcionales

📄 OPCIONALES:
4. Diagramas de flujo existentes
5. Esquema de base de datos actual
6. Mockups o referencias de diseño

Puedes:
- Arrastrar los archivos aquí
- Indicar las rutas de los archivos
- Pegar el contenido directamente
```

## Step 3: Initialize State

Once documents are provided:

1. Create initial state in `docs/state/orchestrator-state.json`:
```json
{
  "project_name": "[Ask user for project name]",
  "current_phase": "ANALYSIS",
  "progress": 0,
  "phases_status": {
    "ANALYSIS": "in_progress",
    "FEEDBACK": "pending",
    "DESIGN": "pending",
    "CONSTRUCTION": "pending",
    "TESTING": "pending"
  },
  "last_action": "Migration started",
  "created_at": "[timestamp]"
}
```

2. Copy provided documents to `docs/input/`

3. Initialize git repository if not exists:
```bash
git init
git checkout -b migration/initial-setup
```

## Step 4: Begin Analysis Phase

Invoke the analysis sub-agents:

1. **business-rules-analyzer**: Extract business rules
2. **entity-analyzer**: Identify entities and relationships
3. **requirements-analyzer**: Extract functional/non-functional requirements

Each agent writes to their respective folders in `docs/analysis/`.

## Step 5: Transition to Feedback

After analysis completes:

1. Generate `docs/analysis/feedback-checklist.md`
2. Generate `docs/analysis/flow-diagrams.md` with Mermaid diagrams
3. Update state to `FEEDBACK` phase
4. Present findings to user and begin validation

## Important Notes

- NEVER skip document collection
- ALWAYS initialize state before analysis
- ALWAYS checkpoint after each step
- Communicate in Spanish unless user prefers otherwise
