# Migration Status Command

You are showing the current migration status. Follow these steps:

## Step 1: Load State

Read the orchestrator state:
- Read `docs/state/orchestrator-state.json`

If file doesn't exist or state is IDLE:
```
ℹ️ No hay ninguna migración activa.
Usa `/migration start` para comenzar una nueva migración.
```

## Step 2: Generate Status Report

If migration is active, generate a comprehensive status:

```
📊 ESTADO DE MIGRACIÓN
━━━━━━━━━━━━━━━━━━━━━━
📁 Proyecto: [project_name]
📍 Fase actual: [current_phase]
📈 Progreso general: [progress]%

FASES:
[For each phase, show status with emoji]
✅ ANÁLISIS: Completado
✅ FEEDBACK: Completado
🔄 DISEÑO: En progreso (65%)
⏳ CONSTRUCCIÓN: Pendiente
⏳ TESTING: Pendiente

DETALLES DE FASE ACTUAL:
[Show specific details based on current phase]

📝 Última acción: [last_action]
💾 Último checkpoint: [last_checkpoint]
```

## Step 3: Phase-Specific Details

### If ANALYSIS:
- Show number of documents processed
- Show extraction progress

### If FEEDBACK:
- Show checklist completion percentage
- Show pending validations

### If DESIGN:
- Show designed components
- Show congruence validation status

### If CONSTRUCTION:
- Show entities implemented
- Show files created
- Show git commit count

### If TESTING:
- Show test results summary
- Show coverage percentage

## Step 4: Show Next Actions

```
📋 PRÓXIMAS ACCIONES:
1. [Based on current state]
2. [Next logical steps]

💡 SUGERENCIAS:
- [Context-aware suggestions]
```

## Step 5: Show Quick Commands

```
🔧 COMANDOS DISPONIBLES:
/migration validate  - Validar congruencia
/migration checkpoint - Crear checkpoint manual
/migration restart   - Archivar/reiniciar
/migration help      - Ver ayuda completa
```
