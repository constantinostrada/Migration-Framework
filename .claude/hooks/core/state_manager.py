#!/usr/bin/env python3
"""
State Manager - Multi-project support with comprehensive state tracking.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum


class Phase(Enum):
    IDLE = "IDLE"
    ANALYSIS = "ANALYSIS"
    FEEDBACK = "FEEDBACK"
    DESIGN = "DESIGN"
    CONSTRUCTION = "CONSTRUCTION"
    TESTING = "TESTING"
    COMPLETED = "COMPLETED"


PHASE_ORDER = {
    Phase.IDLE: 0,
    Phase.ANALYSIS: 1,
    Phase.FEEDBACK: 2,
    Phase.DESIGN: 3,
    Phase.CONSTRUCTION: 4,
    Phase.TESTING: 5,
    Phase.COMPLETED: 6
}

PHASE_WEIGHTS = {
    Phase.ANALYSIS: 15,
    Phase.FEEDBACK: 10,
    Phase.DESIGN: 20,
    Phase.CONSTRUCTION: 40,
    Phase.TESTING: 15
}


class StateManager:
    """Manages migration state with multi-project support."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.projects_file = self.base_path / "docs" / "state" / "projects.json"
        self.active_project_file = self.base_path / "docs" / "state" / "active-project.json"

    def _ensure_dirs(self):
        """Ensure state directories exist."""
        (self.base_path / "docs" / "state").mkdir(parents=True, exist_ok=True)
        (self.base_path / "docs" / "state" / "phase-summaries").mkdir(parents=True, exist_ok=True)

    def get_projects(self) -> Dict[str, Any]:
        """Get all migration projects."""
        if not self.projects_file.exists():
            return {"projects": {}}
        with open(self.projects_file, 'r') as f:
            return json.load(f)

    def get_active_project_id(self) -> Optional[str]:
        """Get the currently active project ID."""
        if not self.active_project_file.exists():
            return None
        with open(self.active_project_file, 'r') as f:
            data = json.load(f)
            return data.get("active_project_id")

    def set_active_project(self, project_id: str):
        """Set the active project."""
        self._ensure_dirs()
        with open(self.active_project_file, 'w') as f:
            json.dump({
                "active_project_id": project_id,
                "activated_at": datetime.now().isoformat()
            }, f, indent=2)

    def get_project_state_file(self, project_id: str) -> Path:
        """Get the state file path for a project."""
        return self.base_path / "docs" / "state" / "projects" / project_id / "orchestrator-state.json"

    def get_project_state(self, project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get state for a specific project or active project."""
        if project_id is None:
            project_id = self.get_active_project_id()
        if project_id is None:
            return None

        state_file = self.get_project_state_file(project_id)
        if not state_file.exists():
            return None

        with open(state_file, 'r') as f:
            return json.load(f)

    def create_project(self, project_name: str, project_id: Optional[str] = None) -> str:
        """Create a new migration project."""
        self._ensure_dirs()

        if project_id is None:
            # Generate ID from name
            project_id = project_name.lower().replace(" ", "-").replace("_", "-")
            # Add timestamp to make unique
            project_id = f"{project_id}-{datetime.now().strftime('%Y%m%d')}"

        # Create project directory
        project_dir = self.base_path / "docs" / "state" / "projects" / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        for subdir in ["analysis", "design", "qa", "logs"]:
            (project_dir / subdir).mkdir(exist_ok=True)

        # Initialize state
        initial_state = {
            "project_id": project_id,
            "project_name": project_name,
            "current_phase": Phase.ANALYSIS.value,
            "progress": 0,
            "phases_status": {
                Phase.ANALYSIS.value: "in_progress",
                Phase.FEEDBACK.value: "pending",
                Phase.DESIGN.value: "pending",
                Phase.CONSTRUCTION.value: "pending",
                Phase.TESTING.value: "pending"
            },
            "phase_progress": {
                Phase.ANALYSIS.value: 0,
                Phase.FEEDBACK.value: 0,
                Phase.DESIGN.value: 0,
                Phase.CONSTRUCTION.value: 0,
                Phase.TESTING.value: 0
            },
            "last_action": "Project created",
            "next_action": "Begin analysis of provided documents",
            "last_checkpoint": datetime.now().isoformat(),
            "files_modified_since_checkpoint": 0,
            "modified_files": [],
            "deliverables_completed": [],
            "mcp_usage_log": [],
            "agent_invocations": [],
            "user_decisions": [],
            "blockers": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        state_file = self.get_project_state_file(project_id)
        state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(state_file, 'w') as f:
            json.dump(initial_state, f, indent=2)

        # Update projects list
        projects = self.get_projects()
        projects["projects"][project_id] = {
            "name": project_name,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }

        with open(self.projects_file, 'w') as f:
            json.dump(projects, f, indent=2)

        # Set as active project
        self.set_active_project(project_id)

        return project_id

    def update_state(self, updates: Dict[str, Any], project_id: Optional[str] = None):
        """Update project state."""
        if project_id is None:
            project_id = self.get_active_project_id()
        if project_id is None:
            raise ValueError("No active project")

        state = self.get_project_state(project_id)
        if state is None:
            raise ValueError(f"Project {project_id} not found")

        # Deep merge updates
        for key, value in updates.items():
            if isinstance(value, dict) and key in state and isinstance(state[key], dict):
                state[key].update(value)
            elif isinstance(value, list) and key in state and isinstance(state[key], list):
                if key in ["modified_files", "deliverables_completed", "mcp_usage_log",
                          "agent_invocations", "user_decisions", "blockers"]:
                    # Append to lists
                    state[key].extend(value)
                    # Keep limited history
                    if key == "modified_files":
                        state[key] = state[key][-50:]
                else:
                    state[key] = value
            else:
                state[key] = value

        state["updated_at"] = datetime.now().isoformat()

        state_file = self.get_project_state_file(project_id)
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        return state

    def advance_phase(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Advance to the next phase."""
        state = self.get_project_state(project_id)
        if state is None:
            raise ValueError("No project state found")

        current = Phase(state["current_phase"])
        current_order = PHASE_ORDER[current]

        # Find next phase
        next_phase = None
        for phase, order in PHASE_ORDER.items():
            if order == current_order + 1:
                next_phase = phase
                break

        if next_phase is None or next_phase == Phase.COMPLETED:
            # Mark as completed
            return self.update_state({
                "current_phase": Phase.COMPLETED.value,
                "progress": 100,
                "phases_status": {current.value: "completed"},
                "last_action": "Migration completed"
            }, project_id)

        return self.update_state({
            "current_phase": next_phase.value,
            "phases_status": {
                current.value: "completed",
                next_phase.value: "in_progress"
            },
            "last_action": f"Advanced to {next_phase.value} phase"
        }, project_id)

    def calculate_progress(self, project_id: Optional[str] = None) -> int:
        """Calculate overall progress percentage."""
        state = self.get_project_state(project_id)
        if state is None:
            return 0

        total_progress = 0
        for phase_name, weight in PHASE_WEIGHTS.items():
            phase_status = state["phases_status"].get(phase_name.value, "pending")
            phase_progress = state.get("phase_progress", {}).get(phase_name.value, 0)

            if phase_status == "completed":
                total_progress += weight
            elif phase_status == "in_progress":
                total_progress += int(weight * phase_progress / 100)

        return min(100, total_progress)

    def record_checkpoint(self, trigger: str = "manual", project_id: Optional[str] = None):
        """Record a checkpoint."""
        state = self.get_project_state(project_id)
        if state is None:
            return

        progress = self.calculate_progress(project_id)

        self.update_state({
            "last_checkpoint": datetime.now().isoformat(),
            "progress": progress,
            "files_modified_since_checkpoint": 0,
            "checkpoint_trigger": trigger
        }, project_id)

        # Update phase summary
        self._update_phase_summary(project_id)

        # Update recovery file
        self._update_recovery_file(project_id)

    def _update_phase_summary(self, project_id: Optional[str] = None):
        """Update the current phase summary file."""
        state = self.get_project_state(project_id)
        if state is None:
            return

        current_phase = state["current_phase"]
        phase_num = PHASE_ORDER.get(Phase(current_phase), 0)

        summary_file = self.base_path / "docs" / "state" / "phase-summaries" / f"{phase_num:02d}-{current_phase.lower()}-summary.md"
        summary_file.parent.mkdir(parents=True, exist_ok=True)

        # Count deliverables
        deliverables_for_phase = [d for d in state.get("deliverables_completed", []) if current_phase.lower() in d.lower()]

        content = f"""# {current_phase} Phase Summary

**Project**: {state.get('project_name', 'Unknown')}
**Status**: {state['phases_status'].get(current_phase, 'unknown').upper()}
**Progress**: {state.get('phase_progress', {}).get(current_phase, 0)}%
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Completed Tasks

{chr(10).join(['- ' + d for d in deliverables_for_phase]) if deliverables_for_phase else '*No deliverables completed yet*'}

## Files Modified This Phase

{chr(10).join(['- ' + f for f in state.get('modified_files', [])[-10:]]) if state.get('modified_files') else '*No files modified*'}

## Agent Invocations

{chr(10).join(['- ' + a.get('agent', 'unknown') + ': ' + a.get('status', 'unknown') for a in state.get('agent_invocations', []) if a.get('phase') == current_phase]) if state.get('agent_invocations') else '*No agents invoked*'}

## MCP Usage

{chr(10).join(['- ' + m.get('mcp', 'unknown') + ': ' + str(len(m.get('queries', []))) + ' queries' for m in state.get('mcp_usage_log', []) if m.get('phase') == current_phase]) if state.get('mcp_usage_log') else '*No MCPs used*'}

## Blockers

{chr(10).join(['- ' + b for b in state.get('blockers', [])]) if state.get('blockers') else '*No blockers*'}

## Next Actions

{state.get('next_action', 'Continue with current phase')}
"""

        with open(summary_file, 'w') as f:
            f.write(content)

    def _update_recovery_file(self, project_id: Optional[str] = None):
        """Update the recovery file for session continuity."""
        state = self.get_project_state(project_id)
        if state is None:
            return

        if project_id is None:
            project_id = self.get_active_project_id()

        recovery_file = self.base_path / "docs" / "state" / "RECOVERY.md"

        content = f"""# Recovery Context - {state.get('project_name', 'Migration')}

**Project ID**: {project_id}
**Last Updated**: {datetime.now().isoformat()}
**Current Phase**: {state['current_phase']}
**Progress**: {state.get('progress', 0)}%

---

## Quick Recovery Instructions

If this is a new session, Claude MUST read these files in order:

### 1. State Files
1. `docs/state/projects/{project_id}/orchestrator-state.json` - Current state
2. `docs/state/decisions-log.md` - User decisions made

### 2. Phase-Specific Context

{"#### ANALYSIS Phase" if state['current_phase'] == 'ANALYSIS' else ""}
{"- `docs/analysis/business-rules/extracted-rules.md`" if state['current_phase'] == 'ANALYSIS' else ""}
{"- `docs/analysis/entities/entity-model.md`" if state['current_phase'] == 'ANALYSIS' else ""}
{"- `docs/analysis/requirements/functional-requirements.md`" if state['current_phase'] == 'ANALYSIS' else ""}

{"#### FEEDBACK Phase" if state['current_phase'] == 'FEEDBACK' else ""}
{"- `docs/analysis/feedback-checklist.md`" if state['current_phase'] == 'FEEDBACK' else ""}
{"- `docs/analysis/flow-diagrams.md`" if state['current_phase'] == 'FEEDBACK' else ""}

{"#### DESIGN Phase" if state['current_phase'] == 'DESIGN' else ""}
{"- `docs/design/backend/api-contracts.md`" if state['current_phase'] == 'DESIGN' else ""}
{"- `docs/design/frontend/components.md`" if state['current_phase'] == 'DESIGN' else ""}
{"- `docs/design/database/schema.sql`" if state['current_phase'] == 'DESIGN' else ""}
{"- `docs/design/congruence/validation-matrix.md`" if state['current_phase'] == 'DESIGN' else ""}

{"#### CONSTRUCTION Phase" if state['current_phase'] == 'CONSTRUCTION' else ""}
{"- Read last modified files in `src/`" if state['current_phase'] == 'CONSTRUCTION' else ""}
{"- Check `docs/design/` for specifications to follow" if state['current_phase'] == 'CONSTRUCTION' else ""}

{"#### TESTING Phase" if state['current_phase'] == 'TESTING' else ""}
{"- `docs/qa/backend-report.md`" if state['current_phase'] == 'TESTING' else ""}
{"- `docs/qa/e2e-report.md`" if state['current_phase'] == 'TESTING' else ""}
{"- `docs/qa/integration-report.md`" if state['current_phase'] == 'TESTING' else ""}

---

## Last Actions

- **Last Action**: {state.get('last_action', 'N/A')}
- **Next Action**: {state.get('next_action', 'Continue with current phase')}
- **Last Checkpoint**: {state.get('last_checkpoint', 'N/A')}

## Recent Files Modified

{chr(10).join(['- ' + f for f in state.get('modified_files', [])[-5:]]) if state.get('modified_files') else '*None*'}

## Active Blockers

{chr(10).join(['- ' + b for b in state.get('blockers', [])]) if state.get('blockers') else '*None*'}

---

## Confirm Recovery

After reading this file, Claude should confirm with the user:

```
He recuperado el contexto del proyecto "{state.get('project_name', 'Migration')}".
- Fase actual: {state['current_phase']}
- Progreso: {state.get('progress', 0)}%
- Última acción: {state.get('last_action', 'N/A')}

¿Continúo desde donde quedamos?
```
"""

        with open(recovery_file, 'w') as f:
            f.write(content)

    def log_mcp_usage(self, mcp_name: str, queries: List[str], findings: str = "",
                      project_id: Optional[str] = None):
        """Log MCP usage for tracking."""
        state = self.get_project_state(project_id)
        if state is None:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": state["current_phase"],
            "mcp": mcp_name,
            "queries": queries,
            "findings_summary": findings
        }

        self.update_state({
            "mcp_usage_log": [log_entry]
        }, project_id)

    def log_agent_invocation(self, agent_name: str, task: str, status: str,
                             deliverables: List[str] = None, project_id: Optional[str] = None):
        """Log sub-agent invocation."""
        state = self.get_project_state(project_id)
        if state is None:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": state["current_phase"],
            "agent": agent_name,
            "task": task,
            "status": status,
            "deliverables": deliverables or []
        }

        self.update_state({
            "agent_invocations": [log_entry]
        }, project_id)

    def add_blocker(self, blocker: str, project_id: Optional[str] = None):
        """Add a blocker that needs resolution."""
        self.update_state({
            "blockers": [blocker]
        }, project_id)

    def remove_blocker(self, blocker: str, project_id: Optional[str] = None):
        """Remove a resolved blocker."""
        state = self.get_project_state(project_id)
        if state is None:
            return

        blockers = [b for b in state.get("blockers", []) if b != blocker]

        state_file = self.get_project_state_file(project_id or self.get_active_project_id())
        state["blockers"] = blockers
        state["updated_at"] = datetime.now().isoformat()

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    # ==================== Checkpoint History ====================

    def get_checkpoints_dir(self, project_id: Optional[str] = None) -> Path:
        """Get the checkpoints directory for a project."""
        if project_id is None:
            project_id = self.get_active_project_id()
        if project_id is None:
            return self.base_path / "docs" / "state" / "checkpoints"
        return self.base_path / "docs" / "state" / "projects" / project_id / "checkpoints"

    def save_checkpoint(self, description: str = "", trigger: str = "manual",
                        project_id: Optional[str] = None) -> Optional[str]:
        """
        Save a checkpoint with full state snapshot.

        Returns checkpoint_id if successful, None otherwise.
        """
        state = self.get_project_state(project_id)
        if state is None:
            return None

        if project_id is None:
            project_id = self.get_active_project_id()

        # Generate checkpoint ID
        timestamp = datetime.now()
        checkpoint_id = timestamp.strftime("%Y%m%d-%H%M%S")

        # Create checkpoint directory
        checkpoints_dir = self.get_checkpoints_dir(project_id)
        checkpoints_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_file = checkpoints_dir / f"{checkpoint_id}.json"

        # Build checkpoint data
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "created_at": timestamp.isoformat(),
            "trigger": trigger,
            "description": description or f"Checkpoint at {state.get('current_phase', 'UNKNOWN')} phase",
            "phase": state.get("current_phase"),
            "progress": state.get("progress", 0),
            "state_snapshot": state.copy()
        }

        # Save checkpoint
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        # Update current state with checkpoint reference
        self.update_state({
            "last_checkpoint": timestamp.isoformat(),
            "last_checkpoint_id": checkpoint_id,
            "files_modified_since_checkpoint": 0,
            "checkpoint_trigger": trigger
        }, project_id)

        # Update recovery file
        self._update_recovery_file(project_id)

        return checkpoint_id

    def list_checkpoints(self, project_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List available checkpoints for a project.

        Returns list of checkpoint metadata, sorted by most recent first.
        """
        checkpoints_dir = self.get_checkpoints_dir(project_id)

        if not checkpoints_dir.exists():
            return []

        checkpoints = []
        for checkpoint_file in sorted(checkpoints_dir.glob("*.json"), reverse=True):
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                    checkpoints.append({
                        "checkpoint_id": data.get("checkpoint_id"),
                        "created_at": data.get("created_at"),
                        "phase": data.get("phase"),
                        "progress": data.get("progress"),
                        "description": data.get("description"),
                        "trigger": data.get("trigger")
                    })
            except (json.JSONDecodeError, IOError):
                continue

            if len(checkpoints) >= limit:
                break

        return checkpoints

    def get_checkpoint(self, checkpoint_id: str, project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get full checkpoint data by ID."""
        checkpoints_dir = self.get_checkpoints_dir(project_id)
        checkpoint_file = checkpoints_dir / f"{checkpoint_id}.json"

        if not checkpoint_file.exists():
            return None

        try:
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def restore_checkpoint(self, checkpoint_id: str, project_id: Optional[str] = None) -> bool:
        """
        Restore state from a checkpoint.

        WARNING: This overwrites the current state with the checkpoint snapshot.
        Returns True if successful, False otherwise.
        """
        checkpoint = self.get_checkpoint(checkpoint_id, project_id)
        if checkpoint is None:
            return False

        if project_id is None:
            project_id = self.get_active_project_id()
        if project_id is None:
            return False

        state_snapshot = checkpoint.get("state_snapshot")
        if state_snapshot is None:
            return False

        # Save current state as a backup before restoring
        current_state = self.get_project_state(project_id)
        if current_state:
            self.save_checkpoint(
                description=f"Auto-backup before restore to {checkpoint_id}",
                trigger="pre_restore_backup",
                project_id=project_id
            )

        # Update snapshot with restore metadata
        state_snapshot["restored_from"] = checkpoint_id
        state_snapshot["restored_at"] = datetime.now().isoformat()
        state_snapshot["updated_at"] = datetime.now().isoformat()

        # Write restored state
        state_file = self.get_project_state_file(project_id)
        with open(state_file, 'w') as f:
            json.dump(state_snapshot, f, indent=2)

        # Update recovery file
        self._update_recovery_file(project_id)

        return True

    def delete_old_checkpoints(self, keep_count: int = 20, project_id: Optional[str] = None):
        """Delete old checkpoints, keeping only the most recent ones."""
        checkpoints_dir = self.get_checkpoints_dir(project_id)

        if not checkpoints_dir.exists():
            return

        checkpoint_files = sorted(checkpoints_dir.glob("*.json"), reverse=True)

        # Keep the most recent checkpoints
        for checkpoint_file in checkpoint_files[keep_count:]:
            try:
                checkpoint_file.unlink()
            except IOError:
                pass
