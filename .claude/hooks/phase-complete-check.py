#!/usr/bin/env python3
"""
Phase Complete Check Hook
Runs when Claude stops to check if a phase was completed
and update the state accordingly.
"""

import json
import os
from datetime import datetime

STATE_FILE = "docs/state/orchestrator-state.json"
RECOVERY_FILE = "docs/state/RECOVERY.md"


def load_state():
    """Load current orchestrator state."""
    if not os.path.exists(STATE_FILE):
        return None

    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def save_state(state):
    """Save orchestrator state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def check_phase_artifacts():
    """Check which phases have their required artifacts."""
    phases = {
        "ANALYSIS": [
            "docs/analysis/business-rules/extracted-rules.md",
            "docs/analysis/entities/entity-model.md"
        ],
        "FEEDBACK": [
            "docs/analysis/feedback-checklist.md"
        ],
        "DESIGN": [
            "docs/design/backend/api-contracts.md",
            "docs/design/frontend/components.md",
            "docs/design/database/schema.sql"
        ],
        "CONSTRUCTION": [
            "src/backend/app/__init__.py",
            "src/frontend/package.json"
        ],
        "TESTING": [
            "docs/qa/backend-report.md",
            "docs/qa/e2e-report.md"
        ]
    }

    completed = {}
    for phase, artifacts in phases.items():
        completed[phase] = all(os.path.exists(a) for a in artifacts)

    return completed


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

## Fases Completadas
{chr(10).join(['- ' + k + ': ' + ('✅' if v else '⏳') for k, v in state.get('phases_status', {}).items()])}

## Archivos Críticos a Leer (en orden)
1. `docs/state/orchestrator-state.json` - Estado exacto
2. `docs/analysis/feedback-checklist.md` - Decisiones del usuario
3. `docs/design/backend/api-contracts.md` - Contratos a implementar
4. `docs/design/congruence/validation-matrix.md` - Matriz de congruencia

## Decisiones Críticas
Ver: `docs/state/decisions-log.md`

## ⚠️ Próxima Acción
{state.get('next_action', 'Continuar con la fase actual')}
"""

    with open(RECOVERY_FILE, 'w') as f:
        f.write(content)


def main():
    state = load_state()
    if not state:
        return

    # Check completed phases
    completed = check_phase_artifacts()
    state["phases_status"] = completed

    # Calculate overall progress
    total_phases = 5
    completed_count = sum(1 for v in completed.values() if v)
    state["progress"] = int((completed_count / total_phases) * 100)

    # Update checkpoint
    state["last_checkpoint"] = datetime.now().isoformat()

    save_state(state)
    update_recovery_file(state)

    current_phase = state.get("current_phase", "IDLE")
    progress = state.get("progress", 0)

    if current_phase != "IDLE" and current_phase != "COMPLETED":
        print(f"\n📊 Estado: {current_phase} - {progress}% completado")


if __name__ == "__main__":
    main()
