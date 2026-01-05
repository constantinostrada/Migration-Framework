# Migration Checkpoint Command

You are creating a manual checkpoint with full state snapshot.

## Step 1: Check Active Project

```bash
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager

sm = StateManager('.')
project_id = sm.get_active_project_id()
if project_id:
    state = sm.get_project_state()
    print(f'PROJECT:{project_id}')
    print(f'PHASE:{state.get(\"current_phase\", \"UNKNOWN\")}')
    print(f'PROGRESS:{state.get(\"progress\", 0)}')
else:
    print('NO_PROJECT')
"
```

If no project active:
```
ℹ️ No hay ningún proyecto de migración activo.
Usa /migration start para comenzar una nueva migración.
```

## Step 2: Create Checkpoint with Snapshot

Execute the checkpoint save:

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager

sm = StateManager('.')
checkpoint_id = sm.save_checkpoint(
    description="Manual checkpoint",
    trigger="manual"
)

if checkpoint_id:
    state = sm.get_project_state()
    print(f"SUCCESS:{checkpoint_id}")
    print(f"PHASE:{state.get('current_phase', 'UNKNOWN')}")
    print(f"PROGRESS:{state.get('progress', 0)}")

    # Count existing checkpoints
    checkpoints = sm.list_checkpoints()
    print(f"TOTAL_CHECKPOINTS:{len(checkpoints)}")
else:
    print("FAILED")
PYEOF
```

## Step 3: Update Supporting Files

After checkpoint is saved, also update:

1. **Recovery file** - Already done by save_checkpoint()

2. **Phase summary** - Update current phase summary:
```bash
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager

sm = StateManager('.')
sm._update_phase_summary()
print('SUMMARY_UPDATED')
"
```

## Step 4: Confirm to User

```
📍 CHECKPOINT CREADO
━━━━━━━━━━━━━━━━━━━

✅ ID: [checkpoint_id]
✅ Estado guardado con snapshot completo
✅ Recovery actualizado

📊 Estado actual:
- Fase: [current_phase]
- Progreso: [progress]%

📁 Archivos actualizados:
- docs/state/projects/{project_id}/checkpoints/[checkpoint_id].json
- docs/state/projects/{project_id}/orchestrator-state.json
- docs/state/RECOVERY.md

💡 Checkpoints guardados: [total_checkpoints]
   Usa /migration checkpoints para ver historial o restaurar.
```

## Step 5: Cleanup Old Checkpoints (if needed)

If total checkpoints > 25, suggest cleanup:
```
⚠️ Tienes [N] checkpoints guardados.
¿Deseas limpiar los más antiguos? (mantener últimos 15)
Usa /migration checkpoints para gestionar.
```

## When to Create Manual Checkpoints

Suggest manual checkpoints when:
- About to start complex implementation
- After important user decisions
- Before ending a work session
- After completing a significant feature
- When context feels "heavy"
- Before making risky changes

## Difference from Auto-Checkpoints

| Tipo | Trigger | Descripción |
|------|---------|-------------|
| Manual | `/migration checkpoint` | Snapshot completo con descripción |
| Auto | 15 min / 3+ archivos | Automático por hooks |
| Pre-restore | Antes de restaurar | Backup de seguridad |
