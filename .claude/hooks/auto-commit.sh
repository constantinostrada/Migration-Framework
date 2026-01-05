#!/bin/bash
# Auto-Commit Hook
# Runs after Write/Edit operations on src/ files to auto-commit changes.

FILE_PATH="$1"
STATE_FILE="docs/state/orchestrator-state.json"

# Exit if no file path provided
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Exit if not in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    exit 0
fi

# Get current phase from state
PHASE="UNKNOWN"
if [ -f "$STATE_FILE" ]; then
    PHASE=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('current_phase', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
fi

# Only auto-commit during CONSTRUCTION phase
if [ "$PHASE" != "CONSTRUCTION" ]; then
    exit 0
fi

# Determine commit type based on file path
TYPE="chore"
if [[ "$FILE_PATH" == *"backend"* ]]; then
    TYPE="backend"
elif [[ "$FILE_PATH" == *"frontend"* ]]; then
    TYPE="frontend"
elif [[ "$FILE_PATH" == *"database"* ]]; then
    TYPE="database"
fi

# Get filename
FILENAME=$(basename "$FILE_PATH")

# Stage the file
git add "$FILE_PATH" 2>/dev/null

# Check if there are staged changes
if git diff --cached --quiet 2>/dev/null; then
    exit 0
fi

# Create commit (silent, no hooks to avoid recursion)
git commit -m "wip($TYPE): update $FILENAME [auto-commit]" --no-verify 2>/dev/null || true

echo "🔄 Auto-commit: $FILENAME"
