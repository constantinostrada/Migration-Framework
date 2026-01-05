#!/usr/bin/env python3
"""
Deliverable Checker - Validates required files exist before phase transitions.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# Phase deliverables manifest
PHASE_DELIVERABLES = {
    "ANALYSIS": {
        "required": [
            "docs/analysis/business-rules/extracted-rules.md",
            "docs/analysis/business-rules/rules.json",
            "docs/analysis/entities/entity-model.md",
            "docs/analysis/entities/entities.json",
            "docs/analysis/requirements/functional-requirements.md",
            "docs/analysis/requirements/requirements.json"
        ],
        "optional": [
            "docs/analysis/gaps/identified-gaps.md",
            "docs/analysis/technical-debt.md"
        ],
        "agents_required": [
            "business-rules-analyzer",
            "entity-analyzer",
            "requirements-analyzer"
        ]
    },
    "FEEDBACK": {
        "required": [
            "docs/analysis/feedback-checklist.md",
            "docs/analysis/flow-diagrams.md",
            "docs/state/decisions-log.md"
        ],
        "optional": [],
        "agents_required": []
    },
    "DESIGN": {
        "required": [
            "docs/design/backend/api-contracts.md",
            "docs/design/backend/api-contracts.json",
            "docs/design/backend/architecture.md",
            "docs/design/frontend/components.md",
            "docs/design/frontend/components.json",
            "docs/design/frontend/pages.md",
            "docs/design/database/schema.sql",
            "docs/design/database/schema.json",
            "docs/design/congruence/validation-matrix.md"
        ],
        "optional": [
            "docs/design/frontend/style-guide.md",
            "docs/design/backend/business-logic.md"
        ],
        "agents_required": [
            "backend-architect",
            "frontend-architect",
            "database-architect"
        ],
        "validation_required": True
    },
    "CONSTRUCTION": {
        "required": [
            "src/backend/main.py",
            "src/backend/app/models/__init__.py",
            "src/backend/app/schemas/__init__.py",
            "src/backend/app/api/v1/endpoints/__init__.py",
            "src/frontend/app/layout.tsx",
            "src/frontend/app/page.tsx"
        ],
        "optional": [
            "src/backend/alembic/versions/*.py",
            "src/backend/tests/"
        ],
        "agents_required": [],
        "validation_required": True
    },
    "TESTING": {
        "required": [
            "docs/qa/backend-report.md",
            "docs/qa/e2e-report.md"
        ],
        "optional": [
            "docs/qa/integration-report.md",
            "docs/qa/coverage-report.md"
        ],
        "agents_required": [
            "qa-validator",
            "e2e-tester"
        ],
        "minimum_pass_rate": 90
    }
}


class DeliverableChecker:
    """Checks if phase deliverables are complete."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.manifest_file = self.base_path / "docs" / "state" / "phase-deliverables.json"
        self._ensure_manifest()

    def _ensure_manifest(self):
        """Ensure the deliverables manifest file exists."""
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.manifest_file.exists():
            with open(self.manifest_file, 'w') as f:
                json.dump(PHASE_DELIVERABLES, f, indent=2)

    def get_deliverables(self, phase: str) -> Dict:
        """Get deliverables for a phase."""
        # First try to read from file (allows customization)
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r') as f:
                manifest = json.load(f)
                if phase in manifest:
                    return manifest[phase]

        # Fall back to built-in
        return PHASE_DELIVERABLES.get(phase, {"required": [], "optional": []})

    def check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists and is not empty."""
        full_path = self.base_path / file_path

        # Handle glob patterns
        if '*' in file_path:
            import glob
            matches = glob.glob(str(full_path))
            return len(matches) > 0

        if not full_path.exists():
            return False

        # Check if file is not empty (for files, not directories)
        if full_path.is_file():
            return full_path.stat().st_size > 10  # More than just whitespace

        return True

    def check_phase_deliverables(self, phase: str) -> Tuple[bool, List[str], List[str]]:
        """
        Check if all required deliverables for a phase are complete.

        Returns:
            Tuple of (all_complete, missing_required, missing_optional)
        """
        deliverables = self.get_deliverables(phase)
        required = deliverables.get("required", [])
        optional = deliverables.get("optional", [])

        missing_required = []
        missing_optional = []

        for file_path in required:
            if not self.check_file_exists(file_path):
                missing_required.append(file_path)

        for file_path in optional:
            if not self.check_file_exists(file_path):
                missing_optional.append(file_path)

        all_complete = len(missing_required) == 0
        return all_complete, missing_required, missing_optional

    def can_advance_phase(self, current_phase: str) -> Tuple[bool, str, Dict]:
        """
        Check if we can advance from the current phase.

        Returns:
            Tuple of (can_advance, reason, details)
        """
        all_complete, missing_required, missing_optional = self.check_phase_deliverables(current_phase)

        details = {
            "phase": current_phase,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "checked_at": datetime.now().isoformat()
        }

        if not all_complete:
            return False, f"Missing {len(missing_required)} required deliverables", details

        # Check if validation is required for this phase
        deliverables = self.get_deliverables(current_phase)
        if deliverables.get("validation_required", False):
            validation_ok, validation_msg = self._check_validation_passed(current_phase)
            if not validation_ok:
                details["validation_error"] = validation_msg
                return False, f"Validation not passed: {validation_msg}", details

        # Check minimum pass rate for testing phase
        if current_phase == "TESTING":
            min_rate = deliverables.get("minimum_pass_rate", 90)
            pass_rate, rate_msg = self._check_test_pass_rate()
            if pass_rate < min_rate:
                details["pass_rate"] = pass_rate
                details["minimum_required"] = min_rate
                return False, f"Test pass rate {pass_rate}% below minimum {min_rate}%", details

        return True, "All deliverables complete", details

    def _check_validation_passed(self, phase: str) -> Tuple[bool, str]:
        """Check if congruence validation passed for design/construction phases."""
        issues_file = self.base_path / "docs" / "design" / "congruence" / "issues.md"

        if not issues_file.exists():
            return False, "Validation not run - issues.md not found"

        with open(issues_file, 'r') as f:
            content = f.read()

        # Check for unresolved issues (unchecked boxes)
        unresolved = content.count("- [ ]")
        if unresolved > 0:
            return False, f"{unresolved} unresolved congruence issues"

        return True, "Validation passed"

    def _check_test_pass_rate(self) -> Tuple[int, str]:
        """Check the test pass rate from reports."""
        e2e_report = self.base_path / "docs" / "qa" / "e2e-report.md"

        if not e2e_report.exists():
            return 0, "E2E report not found"

        with open(e2e_report, 'r') as f:
            content = f.read()

        # Try to extract pass rate
        import re
        match = re.search(r'Pass Rate[:\s]+(\d+)%', content, re.IGNORECASE)
        if match:
            return int(match.group(1)), "Pass rate extracted from report"

        # Try to calculate from passed/total
        passed_match = re.search(r'Passed[:\s]+(\d+)', content, re.IGNORECASE)
        total_match = re.search(r'Total[:\s]+(\d+)', content, re.IGNORECASE)

        if passed_match and total_match:
            passed = int(passed_match.group(1))
            total = int(total_match.group(1))
            if total > 0:
                return int(passed / total * 100), "Calculated from passed/total"

        return 0, "Could not determine pass rate"

    def get_phase_status_report(self, phase: str) -> str:
        """Generate a status report for a phase's deliverables."""
        all_complete, missing_required, missing_optional = self.check_phase_deliverables(phase)
        deliverables = self.get_deliverables(phase)

        completed_required = [f for f in deliverables.get("required", []) if f not in missing_required]
        completed_optional = [f for f in deliverables.get("optional", []) if f not in missing_optional]

        report = f"""
## {phase} Phase Deliverables Status

### Required ({len(completed_required)}/{len(deliverables.get('required', []))})

"""
        for f in deliverables.get("required", []):
            status = "✅" if f not in missing_required else "❌"
            report += f"- {status} `{f}`\n"

        if deliverables.get("optional"):
            report += f"""
### Optional ({len(completed_optional)}/{len(deliverables.get('optional', []))})

"""
            for f in deliverables.get("optional", []):
                status = "✅" if f not in missing_optional else "⬜"
                report += f"- {status} `{f}`\n"

        if deliverables.get("agents_required"):
            report += f"""
### Required Agents

"""
            for agent in deliverables.get("agents_required", []):
                report += f"- {agent}\n"

        report += f"""
### Status

- **Complete**: {'✅ Yes' if all_complete else '❌ No'}
- **Missing Required**: {len(missing_required)}
- **Missing Optional**: {len(missing_optional)}
"""

        return report

    def record_deliverable_completion(self, file_path: str, project_id: Optional[str] = None):
        """Record that a deliverable was completed."""
        completion_log = self.base_path / "docs" / "state" / "deliverables-log.json"

        log = []
        if completion_log.exists():
            with open(completion_log, 'r') as f:
                log = json.load(f)

        log.append({
            "file": file_path,
            "completed_at": datetime.now().isoformat(),
            "project_id": project_id
        })

        with open(completion_log, 'w') as f:
            json.dump(log, f, indent=2)
