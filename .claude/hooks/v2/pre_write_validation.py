#!/usr/bin/env python3
"""
Pre-Write Validation Hook v2.0
Validates congruence BEFORE allowing writes to src/ files.
BLOCKS writes if there are unresolved congruence issues.

Hook Type: PreToolUse (Write, Edit)
Output: JSON with result (allow/block) and validation details
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.congruence import CongruenceValidator
from core.state_manager import StateManager
from core.logger import FrameworkLogger


def main():
    """Main hook execution."""
    if len(sys.argv) < 2:
        print(json.dumps({"result": "allow", "message": "No file path provided"}))
        return

    file_path = sys.argv[1]

    # Skip if not a source file
    if not file_path or file_path == "undefined":
        print(json.dumps({"result": "allow"}))
        return

    # Only validate src/ files
    if "/src/" not in file_path and not file_path.startswith("src/"):
        print(json.dumps({"result": "allow", "message": "Not a source file"}))
        return

    base_path = os.getcwd()
    validator = CongruenceValidator(base_path)
    state_manager = StateManager(base_path)
    logger = FrameworkLogger(base_path)

    # Get current phase
    state = state_manager.get_project_state()
    current_phase = state.get("current_phase", "IDLE") if state else "IDLE"

    # Only enforce validation during CONSTRUCTION phase
    if current_phase != "CONSTRUCTION":
        print(json.dumps({
            "result": "allow",
            "message": f"Validation not enforced in {current_phase} phase"
        }))
        return

    # Check for blocking issues
    blocking_issues = validator.get_blocking_issues()

    # Determine if this file is affected by any issues
    is_frontend = "frontend" in file_path
    is_backend = "backend" in file_path

    relevant_issues = []
    for issue in blocking_issues:
        issue_lower = issue.lower()
        if is_frontend and ("frontend" in issue_lower or "missing_in_frontend" in issue_lower or "name_mismatch" in issue_lower):
            relevant_issues.append(issue)
        elif is_backend and ("backend" in issue_lower or "missing_in_backend" in issue_lower):
            relevant_issues.append(issue)

    if relevant_issues:
        logger.log_hook_execution(
            hook_name="pre_write_validation",
            trigger=f"write:{file_path}",
            result="block",
            details={
                "issues_count": len(relevant_issues),
                "issues": relevant_issues[:5]  # Limit for logging
            }
        )

        output = {
            "result": "block",
            "reason": "CONGRUENCE_ISSUES",
            "message": f"""
⛔ ESCRITURA BLOQUEADA - ISSUES DE CONGRUENCIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivo: {file_path}

Hay {len(relevant_issues)} issue(s) de congruencia sin resolver que afectan este archivo:

{chr(10).join(['❌ ' + issue for issue in relevant_issues[:5]])}

ACCIONES REQUERIDAS:
1. Revisar docs/design/congruence/issues.md
2. Corregir los issues listados
3. Marcar como resueltos cambiando [ ] a [x]
4. Ejecutar /migration validate para verificar

⚠️ No se permite modificar código hasta resolver estos issues.
""",
            "issues": relevant_issues,
            "file_path": file_path
        }

        print(json.dumps(output))
        sys.exit(1)  # Block the write

    # No blocking issues - allow write
    logger.log_hook_execution(
        hook_name="pre_write_validation",
        trigger=f"write:{file_path}",
        result="allow",
        details={"file_path": file_path}
    )

    print(json.dumps({
        "result": "allow",
        "message": "No blocking congruence issues"
    }))


if __name__ == "__main__":
    main()
