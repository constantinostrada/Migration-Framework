# Migration Checkpoints Command

You are managing checkpoint history for the migration project.

## Step 1: List Available Checkpoints

Run this command to get checkpoint history:

```bash
python3 << 'PYEOF'
import sys
import json
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager

sm = StateManager('.')
checkpoints = sm.list_checkpoints(limit=15)

if not checkpoints:
    print("NO_CHECKPOINTS")
else:
    print("CHECKPOINTS_FOUND")
    for i, cp in enumerate(checkpoints, 1):
        print(f"CP:{i}|{cp['checkpoint_id']}|{cp['phase']}|{cp['progress']}%|{cp['created_at']}|{cp['description']}")
PYEOF
```

## Step 2: Present Options

If no checkpoints found:
```
📍 HISTORIAL DE CHECKPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️ No hay checkpoints guardados para este proyecto.

Los checkpoints se crean:
- Automáticamente cada 15 minutos de trabajo
- Cuando se modifican 3+ archivos
- Al completar deliverables importantes
- Manualmente con /migration checkpoint

¿Deseas crear un checkpoint ahora? (sí/no)
```

If checkpoints found:
```
📍 HISTORIAL DE CHECKPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━

| # | ID | Fase | Progreso | Fecha | Descripción |
|---|-----|------|----------|-------|-------------|
| 1 | 20251229-143022 | DESIGN | 45% | 2025-12-29 14:30 | Checkpoint at DESIGN phase |
| 2 | 20251229-140015 | DESIGN | 35% | 2025-12-29 14:00 | API contracts completed |
| ... | ... | ... | ... | ... | ... |

¿Qué deseas hacer?

1. 🔄 RESTAURAR un checkpoint
   Volver a un estado anterior (crea backup automático)

2. 📍 CREAR nuevo checkpoint
   Guardar el estado actual

3. 🗑️ LIMPIAR checkpoints antiguos
   Mantener solo los últimos 10

4. ❌ CANCELAR
   No hacer nada
```

## Step 3: Execute Selected Option

### Option 1: RESTORE

Ask which checkpoint:
```
¿Qué checkpoint deseas restaurar?
Escribe el número (1-N) o el ID del checkpoint:
```

Then execute:
```bash
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager

sm = StateManager('.')
checkpoint_id = '[USER_INPUT]'

# If user entered a number, convert to ID
checkpoints = sm.list_checkpoints()
try:
    idx = int(checkpoint_id) - 1
    if 0 <= idx < len(checkpoints):
        checkpoint_id = checkpoints[idx]['checkpoint_id']
except ValueError:
    pass

success = sm.restore_checkpoint(checkpoint_id)
if success:
    print(f'RESTORED:{checkpoint_id}')
else:
    print('FAILED')
"
```

If successful:
```
✅ CHECKPOINT RESTAURADO
━━━━━━━━━━━━━━━━━━━━━━━

Se restauró el estado desde: [checkpoint_id]
Se creó backup automático del estado actual.

Estado actual:
- Fase: [phase from restored state]
- Progreso: [progress]%

⚠️ IMPORTANTE: Los archivos en src/ y docs/ NO fueron restaurados.
Solo se restauró el estado del orquestador.

Si necesitas restaurar archivos, considera usar git:
  git stash  # guardar cambios actuales
  git checkout [commit_hash]  # volver a versión anterior
```

### Option 2: CREATE

```bash
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager

sm = StateManager('.')
checkpoint_id = sm.save_checkpoint(description='Manual checkpoint', trigger='manual')
if checkpoint_id:
    print(f'CREATED:{checkpoint_id}')
else:
    print('FAILED')
"
```

If successful:
```
✅ CHECKPOINT CREADO
━━━━━━━━━━━━━━━━━━━

ID: [checkpoint_id]
Descripción: Manual checkpoint

El estado actual ha sido guardado.
Puedes restaurarlo en cualquier momento con /migration checkpoints
```

### Option 3: CLEANUP

```bash
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager

sm = StateManager('.')
sm.delete_old_checkpoints(keep_count=10)
print('CLEANED')
"
```

```
✅ LIMPIEZA COMPLETADA
━━━━━━━━━━━━━━━━━━━━━

Se mantuvieron los últimos 10 checkpoints.
Los más antiguos fueron eliminados.
```

### Option 4: CANCEL

```
👍 Operación cancelada.
```

## Important Notes

- Restaurar un checkpoint SOLO restaura el estado del orquestador
- Los archivos en src/ y docs/ NO se restauran automáticamente
- Se crea backup automático antes de cada restauración
- Los checkpoints se guardan en docs/state/projects/{id}/checkpoints/
- Máximo recomendado: 20 checkpoints por proyecto
