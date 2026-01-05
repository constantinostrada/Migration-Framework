#!/usr/bin/env python3
"""
Auto-Commit Hook v2.0
Intelligent auto-commit during CONSTRUCTION phase.

Groups commits by entity and creates meaningful commit messages.
Only commits when a logical unit of work is complete.

Hook Type: PostToolUse (Write, Edit on src/ files)
Output: JSON with commit result
"""

import json
import sys
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state_manager import StateManager
from core.logger import FrameworkLogger

# Configuration
AUTO_COMMIT_ENABLED = True
COMMIT_THRESHOLD = 3  # Number of files to accumulate before committing
ENTITY_PATTERNS = {
    "customer": ["customer", "cust", "client"],
    "account": ["account", "acct"],
    "transaction": ["transaction", "txn", "transfer"],
    "user": ["user", "auth", "login"],
}


def get_git_status():
    """Get current git status."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []


def is_git_repo():
    """Check if we're in a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def detect_entity(file_path: str) -> str:
    """Detect which entity a file belongs to."""
    file_lower = file_path.lower()

    for entity, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            if pattern in file_lower:
                return entity

    return "general"


def detect_layer(file_path: str) -> str:
    """Detect which layer (backend/frontend/database) a file belongs to."""
    if "backend" in file_path:
        return "backend"
    elif "frontend" in file_path:
        return "frontend"
    elif "database" in file_path or "migration" in file_path:
        return "database"
    return "other"


def detect_file_type(file_path: str) -> str:
    """Detect the type of file for better commit messages."""
    file_lower = file_path.lower()

    if "model" in file_lower or "/models/" in file_lower:
        return "model"
    elif "schema" in file_lower or "/schemas/" in file_lower:
        return "schema"
    elif "endpoint" in file_lower or "/api/" in file_lower or "router" in file_lower:
        return "endpoint"
    elif "service" in file_lower or "/services/" in file_lower:
        return "service"
    elif "component" in file_lower or "/components/" in file_lower:
        return "component"
    elif "page" in file_lower or "/app/" in file_lower and ".tsx" in file_lower:
        return "page"
    elif "test" in file_lower or "/tests/" in file_lower:
        return "test"
    elif ".sql" in file_lower:
        return "migration"

    return "file"


def generate_commit_message(files: list, entity: str, layer: str) -> str:
    """Generate a descriptive commit message."""
    if not files:
        return "chore: update files"

    # Count file types
    file_types = {}
    for f in files:
        ft = detect_file_type(f)
        file_types[ft] = file_types.get(ft, 0) + 1

    # Build message
    if len(files) == 1:
        file_type = detect_file_type(files[0])
        filename = Path(files[0]).name
        return f"feat({layer}): add {entity} {file_type} - {filename}"

    # Multiple files
    type_summary = ", ".join([f"{count} {ft}(s)" for ft, count in file_types.items()])
    return f"feat({layer}): implement {entity} - {type_summary}"


def commit_files(files: list, message: str) -> bool:
    """Stage and commit files."""
    try:
        # Stage files
        for f in files:
            subprocess.run(["git", "add", f], check=True, capture_output=True)

        # Check if there are staged changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )

        if result.returncode == 0:
            # No changes to commit
            return False

        # Commit with message
        full_message = f"{message}\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"

        subprocess.run(
            ["git", "commit", "-m", full_message],
            check=True, capture_output=True
        )

        return True

    except subprocess.CalledProcessError as e:
        return False


def main():
    """Main hook execution."""
    if len(sys.argv) < 2:
        print(json.dumps({"result": "skip", "reason": "no_file_path"}))
        return

    file_path = sys.argv[1]

    # Skip if not a source file
    if not file_path or file_path == "undefined":
        print(json.dumps({"result": "skip", "reason": "invalid_path"}))
        return

    # Only process src/ files
    if "/src/" not in file_path and not file_path.startswith("src/"):
        print(json.dumps({"result": "skip", "reason": "not_src_file"}))
        return

    # Check if git repo exists
    if not is_git_repo():
        print(json.dumps({"result": "skip", "reason": "not_git_repo"}))
        return

    base_path = os.getcwd()
    state_manager = StateManager(base_path)
    logger = FrameworkLogger(base_path)

    # Get current state
    state = state_manager.get_project_state()
    if not state:
        print(json.dumps({"result": "skip", "reason": "no_project"}))
        return

    current_phase = state.get("current_phase", "IDLE")

    # Only auto-commit during CONSTRUCTION phase
    if current_phase != "CONSTRUCTION":
        print(json.dumps({
            "result": "skip",
            "reason": f"wrong_phase",
            "phase": current_phase
        }))
        return

    # Check if auto-commit is enabled
    if not AUTO_COMMIT_ENABLED:
        print(json.dumps({"result": "skip", "reason": "disabled"}))
        return

    # Track modified file
    modified_files = state.get("modified_files", [])
    if file_path not in modified_files:
        modified_files.append(file_path)
        state_manager.update_state({
            "modified_files": [file_path],
            "files_modified_since_checkpoint": state.get("files_modified_since_checkpoint", 0) + 1
        })

    # Get pending files from git status
    git_status = get_git_status()
    src_files = [
        line[3:] for line in git_status
        if line and (line.startswith(" M ") or line.startswith("?? ") or line.startswith("A  "))
        and "src/" in line
    ]

    if len(src_files) < COMMIT_THRESHOLD:
        print(json.dumps({
            "result": "pending",
            "files_count": len(src_files),
            "threshold": COMMIT_THRESHOLD,
            "message": f"Acumulando cambios ({len(src_files)}/{COMMIT_THRESHOLD})"
        }))
        return

    # Group files by entity and layer
    entity = detect_entity(file_path)
    layer = detect_layer(file_path)

    # Filter files for the same entity/layer
    entity_files = [f for f in src_files if detect_entity(f) == entity and detect_layer(f) == layer]

    if not entity_files:
        entity_files = src_files[:COMMIT_THRESHOLD]

    # Generate commit message
    commit_message = generate_commit_message(entity_files, entity, layer)

    # Commit
    success = commit_files(entity_files, commit_message)

    if success:
        logger.log_hook_execution(
            hook_name="auto_commit",
            trigger=f"file:{file_path}",
            result="committed",
            details={
                "files": entity_files,
                "entity": entity,
                "layer": layer,
                "message": commit_message
            }
        )

        print(json.dumps({
            "result": "committed",
            "files": entity_files,
            "message": commit_message,
            "display": f"🔄 Auto-commit: {commit_message}"
        }))
    else:
        print(json.dumps({
            "result": "no_changes",
            "reason": "nothing_to_commit"
        }))


if __name__ == "__main__":
    main()
