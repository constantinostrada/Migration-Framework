#!/usr/bin/env python3
"""
Session Recovery Hook
Runs at the start of each session to detect active migrations
and provide recovery information to Claude.
"""

import json
import os
from datetime import datetime

STATE_FILE = "docs/state/orchestrator-state.json"
RECOVERY_FILE = "docs/state/RECOVERY.md"


def check_recovery_needed():
    """Check if there's an active migration and return recovery info."""

    if not os.path.exists(STATE_FILE):
        return None

    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

    current_phase = state.get("current_phase")

    # No active migration
    if not current_phase or current_phase == "IDLE":
        return None

    # Migration completed
    if current_phase == "COMPLETED":
        return f"""
✅ MIGRACIÓN COMPLETADA
━━━━━━━━━━━━━━━━━━━━━━
La última migración fue completada exitosamente.
Usa `/migration restart` para comenzar una nueva migración.
"""

    # Active migration in progress
    progress = state.get("progress", 0)
    last_action = state.get("last_action", "N/A")
    last_checkpoint = state.get("last_checkpoint", "N/A")

    return f"""
⚠️ MIGRACIÓN EN PROGRESO DETECTADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Fase actual: {current_phase}
📊 Progreso: {progress}%
🔄 Última acción: {last_action}
💾 Último checkpoint: {last_checkpoint}

📖 IMPORTANTE: Lee docs/state/RECOVERY.md para contexto completo.

Archivos a leer antes de continuar:
1. docs/state/RECOVERY.md
2. docs/state/orchestrator-state.json
3. docs/state/decisions-log.md
"""


def main():
    message = check_recovery_needed()
    if message:
        print(message)


if __name__ == "__main__":
    main()
