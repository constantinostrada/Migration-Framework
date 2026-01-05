#!/usr/bin/env python3
"""
Pre-Write Validation Hook
Runs before Write operations on src/ files to validate congruence.
Warns Claude if there are unresolved congruence issues.
"""

import os
import sys

ISSUES_FILE = "docs/design/congruence/issues.md"
STATE_FILE = "docs/state/orchestrator-state.json"


def check_congruence_issues(file_path):
    """Check if there are unresolved congruence issues for the target layer."""

    if not os.path.exists(ISSUES_FILE):
        return None

    # Determine which layer we're writing to
    layer = None
    if "backend" in file_path:
        layer = "backend"
    elif "frontend" in file_path:
        layer = "frontend"
    elif "database" in file_path:
        layer = "database"

    if not layer:
        return None

    # Read issues file
    try:
        with open(ISSUES_FILE, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return None

    # Check for unresolved issues (lines starting with - [ ])
    lines = content.split('\n')
    unresolved = []

    in_section = False
    for line in lines:
        # Check if we're in the relevant layer section
        if f"## {layer.upper()}" in line.upper() or f"## {layer.capitalize()}" in line:
            in_section = True
            continue
        elif line.startswith("## "):
            in_section = False

        # If in relevant section, check for unresolved issues
        if in_section and line.strip().startswith("- [ ]"):
            unresolved.append(line.strip())

    if unresolved:
        return f"""
⚠️ ADVERTENCIA: Inconsistencias de congruencia detectadas para {layer}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issues pendientes:
{chr(10).join(unresolved[:5])}

Revisa: docs/design/congruence/issues.md

Considera resolver estos issues antes de continuar.
"""

    return None


def main():
    if len(sys.argv) < 2:
        return

    file_path = sys.argv[1]

    if not file_path or file_path == "undefined":
        return

    warning = check_congruence_issues(file_path)
    if warning:
        print(warning)


if __name__ == "__main__":
    main()
