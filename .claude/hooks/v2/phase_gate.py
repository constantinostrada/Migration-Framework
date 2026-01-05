#!/usr/bin/env python3
"""
Phase Gate Hook v2.0
Validates deliverables and blocks phase transitions until requirements are met.

Hook Type: Stop (runs when Claude stops responding)
Output: JSON with phase completion status and blockers
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state_manager import StateManager, Phase, PHASE_ORDER
from core.deliverables import DeliverableChecker
from core.congruence import CongruenceValidator
from core.logger import FrameworkLogger


def main():
    """Main hook execution."""
    base_path = os.getcwd()
    state_manager = StateManager(base_path)
    deliverable_checker = DeliverableChecker(base_path)
    validator = CongruenceValidator(base_path)
    logger = FrameworkLogger(base_path)

    # Get current state
    state = state_manager.get_project_state()

    if not state:
        print(json.dumps({"result": "no_active_project"}))
        return

    current_phase = state.get("current_phase", "IDLE")

    if current_phase in ["IDLE", "COMPLETED"]:
        print(json.dumps({"result": "allow", "phase": current_phase}))
        return

    # Check deliverables for current phase
    can_advance, reason, details = deliverable_checker.can_advance_phase(current_phase)

    # Generate status report
    status_report = deliverable_checker.get_phase_status_report(current_phase)

    # Check for validation requirements (DESIGN, CONSTRUCTION phases)
    validation_required = current_phase in ["DESIGN", "CONSTRUCTION"]
    validation_passed = True
    validation_issues = []

    if validation_required:
        validation_issues = validator.get_blocking_issues()
        validation_passed = len(validation_issues) == 0 or "Validation not run" in validation_issues[0]

    # Determine overall gate status
    gate_passed = can_advance and (not validation_required or validation_passed)

    if not gate_passed:
        blockers = []

        if not can_advance:
            blockers.extend(details.get("missing_required", []))

        if not validation_passed:
            blockers.extend(validation_issues[:5])

        # Add blockers to state
        for blocker in blockers[:3]:  # Limit to 3 blockers
            state_manager.add_blocker(blocker)

        logger.log_hook_execution(
            hook_name="phase_gate",
            trigger=f"phase_check:{current_phase}",
            result="blocked",
            details={
                "missing_deliverables": len(details.get("missing_required", [])),
                "validation_issues": len(validation_issues)
            }
        )

        output = {
            "result": "blocked",
            "phase": current_phase,
            "message": f"""
⚠️ FASE {current_phase} - VERIFICACIÓN DE GATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{status_report}

{"## Validación de Congruencia" if validation_required else ""}
{"❌ " + str(len(validation_issues)) + " issues pendientes" if validation_issues and not validation_passed else ""}
{"✅ Sin issues de congruencia" if validation_passed and validation_required else ""}

## Estado del Gate

{"❌ NO PUEDE AVANZAR" if not gate_passed else "✅ PUEDE AVANZAR"}
Razón: {reason}

## Próximos Pasos

{chr(10).join(['- Completar: ' + b for b in blockers[:5]]) if blockers else '- Todos los deliverables completos'}
""",
            "can_advance": False,
            "blockers": blockers,
            "details": details
        }

        print(json.dumps(output))
        return

    # Gate passed - update progress and allow
    progress = state_manager.calculate_progress()

    # Update phase progress to 100% if all deliverables are complete
    state_manager.update_state({
        "phase_progress": {current_phase: 100},
        "progress": progress
    })

    logger.log_hook_execution(
        hook_name="phase_gate",
        trigger=f"phase_check:{current_phase}",
        result="passed",
        details={"progress": progress}
    )

    print(json.dumps({
        "result": "passed",
        "phase": current_phase,
        "message": f"""
✅ FASE {current_phase} - GATE VERIFICADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{status_report}

Todos los deliverables están completos.
{"Validación de congruencia pasada." if validation_required else ""}

Puede avanzar a la siguiente fase cuando esté listo.
""",
        "can_advance": True,
        "progress": progress
    }))


if __name__ == "__main__":
    main()
