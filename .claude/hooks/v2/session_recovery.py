#!/usr/bin/env python3
"""
Session Recovery Hook v2.0
Runs at session start to detect active migrations and BLOCK until context is confirmed.

Hook Type: UserPrompt (runs on every user message)
Output: JSON with result (allow/block) and context injection
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state_manager import StateManager, Phase
from core.logger import FrameworkLogger


def main():
    """Main hook execution."""
    base_path = os.getcwd()
    state_manager = StateManager(base_path)
    logger = FrameworkLogger(base_path)

    # Get active project
    project_id = state_manager.get_active_project_id()

    if not project_id:
        # No active migration - allow normal operation
        output = {
            "result": "allow",
            "message": "No active migration. Use /migration start to begin."
        }
        print(json.dumps(output))
        return

    # Get project state
    state = state_manager.get_project_state(project_id)

    if not state:
        output = {
            "result": "allow",
            "message": "No state found for active project."
        }
        print(json.dumps(output))
        return

    current_phase = state.get("current_phase", "IDLE")

    # Check if migration is completed or idle
    if current_phase in ["IDLE", "COMPLETED"]:
        output = {
            "result": "allow",
            "message": f"Migration status: {current_phase}"
        }
        print(json.dumps(output))
        return

    # Active migration in progress - inject recovery context
    progress = state.get("progress", 0)
    last_action = state.get("last_action", "N/A")
    last_checkpoint = state.get("last_checkpoint", "N/A")
    project_name = state.get("project_name", "Unknown")
    next_action = state.get("next_action", "Continue with current phase")
    blockers = state.get("blockers", [])

    # Build context injection message
    context_message = f"""
⚠️ MIGRACIÓN EN PROGRESO DETECTADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Proyecto: {project_name}
📍 Fase actual: {current_phase}
📊 Progreso: {progress}%
🔄 Última acción: {last_action}
💾 Último checkpoint: {last_checkpoint}

📖 ARCHIVOS DE CONTEXTO REQUERIDOS:
1. docs/state/RECOVERY.md
2. docs/state/projects/{project_id}/orchestrator-state.json

⏭️ PRÓXIMA ACCIÓN SUGERIDA:
{next_action}
"""

    if blockers:
        context_message += f"""
🚫 BLOCKERS ACTIVOS:
{chr(10).join(['- ' + b for b in blockers])}
"""

    # Log the recovery detection
    logger.log_hook_execution(
        hook_name="session_recovery",
        trigger="session_start",
        result="context_injected",
        details={
            "project_id": project_id,
            "phase": current_phase,
            "progress": progress
        }
    )

    output = {
        "result": "allow",  # Allow but inject context
        "message": context_message,
        "context": {
            "project_id": project_id,
            "project_name": project_name,
            "current_phase": current_phase,
            "progress": progress,
            "last_action": last_action,
            "next_action": next_action,
            "files_to_read": [
                "docs/state/RECOVERY.md",
                f"docs/state/projects/{project_id}/orchestrator-state.json"
            ],
            "blockers": blockers
        }
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
