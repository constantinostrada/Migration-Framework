#!/usr/bin/env python3
"""
Auto-Checkpoint Hook
Runs after Write/Edit operations to automatically update state.
Creates checkpoint after every N file modifications.
"""

import json
import os
import sys
from datetime import datetime

STATE_FILE = "docs/state/orchestrator-state.json"
RECOVERY_FILE = "docs/state/RECOVERY.md"
CHECKPOINT_THRESHOLD = 5  # Checkpoint every 5 file modifications


def load_state():
    """Load current orchestrator state."""
    if not os.path.exists(STATE_FILE):
        return {
            "current_phase": "IDLE",
            "progress": 0,
            "last_action": None,
            "last_checkpoint": None,
            "files_modified_since_checkpoint": 0,
            "modified_files": []
        }

    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {
            "current_phase": "IDLE",
            "progress": 0,
            "last_action": None,
            "last_checkpoint": None,
            "files_modified_since_checkpoint": 0,
            "modified_files": []
        }


def save_state(state):
    """Save orchestrator state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def update_recovery_file(state):
    """Update the recovery file with current state."""
    os.makedirs(os.path.dirname(RECOVERY_FILE), exist_ok=True)

    content = f"""# 🔄 RECOVERY FILE - Migration Framework
> Este archivo se lee AL INICIO de cada sesión de Claude
> Última actualización: {datetime.now().isoformat()}

## Estado Actual
- **Fase**: {state.get('current_phase', 'IDLE')}
- **Progreso**: {state.get('progress', 0)}%
- **Última acción**: {state.get('last_action', 'N/A')}
- **Último checkpoint**: {state.get('last_checkpoint', 'N/A')}

## Archivos Críticos a Leer (en orden)
1. `docs/state/orchestrator-state.json` - Estado exacto
2. `docs/analysis/feedback-checklist.md` - Decisiones del usuario
3. `docs/design/backend/api-contracts.md` - Contratos a implementar
4. `docs/design/congruence/validation-matrix.md` - Matriz de congruencia

## Últimos Archivos Modificados
{chr(10).join(['- ' + f for f in state.get('modified_files', [])[-5:]])}

## Decisiones Críticas
Ver: `docs/state/decisions-log.md`

## ⚠️ Próxima Acción
{state.get('next_action', 'Continuar con la fase actual')}
"""

    with open(RECOVERY_FILE, 'w') as f:
        f.write(content)


def update_checkpoint(file_path):
    """Update checkpoint with new file modification."""
    state = load_state()

    # Update state
    state["last_modified_file"] = file_path
    state["last_action"] = f"Modified {os.path.basename(file_path)}"

    # Track modified files
    modified_files = state.get("modified_files", [])
    if file_path not in modified_files:
        modified_files.append(file_path)
    state["modified_files"] = modified_files[-20:]  # Keep last 20

    # Increment counter
    files_modified = state.get("files_modified_since_checkpoint", 0) + 1
    state["files_modified_since_checkpoint"] = files_modified

    # Auto-checkpoint every N files
    if files_modified >= CHECKPOINT_THRESHOLD:
        state["last_checkpoint"] = datetime.now().isoformat()
        state["files_modified_since_checkpoint"] = 0
        update_recovery_file(state)
        print(f"📍 Auto-checkpoint created ({files_modified} files modified)")

    save_state(state)


def main():
    if len(sys.argv) < 2:
        return

    file_path = sys.argv[1]

    # Skip if not a valid path
    if not file_path or file_path == "undefined":
        return

    update_checkpoint(file_path)


if __name__ == "__main__":
    main()
