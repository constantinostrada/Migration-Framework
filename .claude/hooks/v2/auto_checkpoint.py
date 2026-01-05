#!/usr/bin/env python3
"""
Auto-Checkpoint Hook v2.0
Creates checkpoints based on time, events, and file modifications.
Updates ALL state files including phase summaries.

Hook Type: PostToolUse (Write, Edit)
Output: JSON with checkpoint status
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state_manager import StateManager
from core.deliverables import DeliverableChecker
from core.logger import FrameworkLogger


# Configuration
CHECKPOINT_TIME_MINUTES = 15  # Checkpoint every 15 minutes
CHECKPOINT_FILE_THRESHOLD = 3  # Checkpoint every 3 file modifications


def main():
    """Main hook execution."""
    if len(sys.argv) < 2:
        print(json.dumps({"result": "no_action", "message": "No file path provided"}))
        return

    file_path = sys.argv[1]

    if not file_path or file_path == "undefined":
        print(json.dumps({"result": "no_action"}))
        return

    base_path = os.getcwd()
    state_manager = StateManager(base_path)
    deliverable_checker = DeliverableChecker(base_path)
    logger = FrameworkLogger(base_path)

    # Get current state
    state = state_manager.get_project_state()

    if not state:
        print(json.dumps({"result": "no_active_project"}))
        return

    current_phase = state.get("current_phase", "IDLE")

    # Track file modification
    modified_files = state.get("modified_files", [])
    if file_path not in modified_files:
        modified_files.append(file_path)

    files_since_checkpoint = state.get("files_modified_since_checkpoint", 0) + 1

    # Update state with file modification
    state_manager.update_state({
        "modified_files": [file_path],  # Will be appended
        "files_modified_since_checkpoint": files_since_checkpoint,
        "last_modified_file": file_path,
        "last_action": f"Modified {os.path.basename(file_path)}"
    })

    # Determine if checkpoint is needed
    should_checkpoint = False
    checkpoint_trigger = None

    # Check 1: Time-based checkpoint
    last_checkpoint = state.get("last_checkpoint")
    if last_checkpoint:
        try:
            last_cp_time = datetime.fromisoformat(last_checkpoint.replace('Z', '+00:00'))
            time_diff = datetime.now(last_cp_time.tzinfo) - last_cp_time if last_cp_time.tzinfo else datetime.now() - datetime.fromisoformat(last_checkpoint)
            if time_diff > timedelta(minutes=CHECKPOINT_TIME_MINUTES):
                should_checkpoint = True
                checkpoint_trigger = f"time_elapsed_{CHECKPOINT_TIME_MINUTES}min"
        except (ValueError, TypeError):
            pass

    # Check 2: File count threshold
    if files_since_checkpoint >= CHECKPOINT_FILE_THRESHOLD:
        should_checkpoint = True
        checkpoint_trigger = f"file_count_{files_since_checkpoint}"

    # Check 3: Important file modified (always checkpoint)
    important_patterns = [
        "orchestrator-state.json",
        "RECOVERY.md",
        "decisions-log.md",
        "api-contracts.md",
        "schema.sql",
        "requirements.md"
    ]

    for pattern in important_patterns:
        if pattern in file_path:
            should_checkpoint = True
            checkpoint_trigger = f"important_file_{pattern}"
            break

    # Check 4: Deliverable completed
    deliverables = deliverable_checker.get_deliverables(current_phase)
    required = deliverables.get("required", [])
    for req_file in required:
        if req_file in file_path or file_path.endswith(req_file.split("/")[-1]):
            should_checkpoint = True
            checkpoint_trigger = f"deliverable_completed"

            # Record deliverable completion
            deliverable_checker.record_deliverable_completion(file_path)
            break

    if should_checkpoint:
        # Record checkpoint
        state_manager.record_checkpoint(trigger=checkpoint_trigger)

        logger.log_checkpoint(
            trigger=checkpoint_trigger,
            phase=current_phase,
            progress=state_manager.calculate_progress(),
            files_modified=files_since_checkpoint
        )

        print(json.dumps({
            "result": "checkpoint_created",
            "trigger": checkpoint_trigger,
            "phase": current_phase,
            "progress": state_manager.calculate_progress(),
            "message": f"📍 Checkpoint creado ({checkpoint_trigger})"
        }))
    else:
        print(json.dumps({
            "result": "file_tracked",
            "files_since_checkpoint": files_since_checkpoint,
            "next_checkpoint_at": CHECKPOINT_FILE_THRESHOLD
        }))


if __name__ == "__main__":
    main()
