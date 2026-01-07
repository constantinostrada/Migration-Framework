# State Management & Optimistic Locking - v4.4.1

## Overview

This document defines the **atomic state management** patterns for the Migration Framework v4.4.

**Problem Solved**: Race conditions when multiple agents access shared state files (tasks.json, queue files, rejection-tracker.json).

**v4.4.1 Change**: Replaced file-based locking with **Optimistic Locking** using version numbers (compatible with LLM execution via Claude Code tools).

---

## 1. Optimistic Locking Protocol (LLM-Native)

### 1.1 Why Optimistic Locking?

**File-based locks DON'T work** in LLM environments because:
- ❌ No `sleep()` function available in Claude Code
- ❌ Network latency between Read/Write operations
- ❌ Multiple agents (Task invocations) can run concurrently

**Optimistic locking DOES work** because:
- ✅ Uses version numbers to detect conflicts
- ✅ No loops or sleeps needed
- ✅ Retry on conflict using available tools
- ✅ Compatible with Read/Write/Bash tools

### 1.2 Version Number Convention

Every state file includes a `_version` field:

```json
{
  "_version": 42,
  "_last_modified": "2026-01-07T10:30:00Z",
  "_last_modified_by": "domain-agent",
  "tasks": [...]
}
```

**Rules**:
- Version starts at 0 when file is created
- Version increments by 1 on every write
- Version is checked before every write to detect conflicts

### 1.3 Optimistic Update Pattern

**INSTRUCTIONS FOR ORCHESTRATOR/AGENTS:**

When you need to update `tasks.json` (or any state file):

**Step 1: Read current state and note version**
```python
Read: docs/state/tasks.json

current_version = data.get("_version", 0)
print(f"📖 Read tasks.json version {current_version}")
```

**Step 2: Make your modifications**
```python
# Example: Mark task as completed
for task in data["tasks"]:
    if task["id"] == "TASK-001":
        task["status"] = "completed"
        task["completed_at"] = "2026-01-07T10:30:00Z"
```

**Step 3: IMMEDIATELY before Write, re-read to detect conflicts**
```python
# CRITICAL: Re-read to check if another agent modified the file
Read: docs/state/tasks.json

latest_version = latest_data.get("_version", 0)

if latest_version != current_version:
    # ⚠️ CONFLICT DETECTED
    print(f"🔴 CONFLICT: Expected version {current_version}, found {latest_version}")
    print(f"   Another agent modified the file. Retrying...")

    # RETRY: Re-apply your changes to the LATEST data
    return retry_update_with_conflict_resolution(attempt=1)
```

**Step 4: If no conflict, write with incremented version**
```python
# No conflict - safe to write
data["_version"] = current_version + 1
data["_last_modified"] = "2026-01-07T10:30:00Z"
data["_last_modified_by"] = "orchestrator"  # or agent name

Write: docs/state/tasks.json
print(f"✅ Updated tasks.json to version {current_version + 1}")
```

### 1.4 Conflict Resolution with Retry

**INSTRUCTIONS: If conflict detected (versions don't match):**

```
**Retry with exponential backoff** (max 3 attempts):

Attempt 1:
1. Re-read latest state
2. Re-apply YOUR specific changes only (don't overwrite others' changes)
3. Check version again before write
4. If still conflict → Attempt 2

Attempt 2:
1. Wait 2 seconds: Bash: sleep 2
2. Re-read latest state
3. Re-apply your changes
4. Check version, attempt write
5. If still conflict → Attempt 3

Attempt 3:
1. Wait 4 seconds: Bash: sleep 4
2. Re-read latest state
3. Re-apply your changes
4. Check version, attempt write
5. If still conflict → ESCALATE to user

If all 3 attempts fail:
⚠️ Print error: "Failed to update tasks.json after 3 attempts due to conflicts"
⚠️ Log to transaction log
⚠️ Ask user whether to:
   - Retry manually
   - Skip this update (risky)
   - Abort migration
```

### 1.5 Bash Implementation Pattern

**For Orchestrator executing via Bash tool:**

```bash
# Update tasks.json with optimistic locking via Python one-liner

python3 << 'PYEOF'
import json
from datetime import datetime, timezone

MAX_ATTEMPTS = 3

def update_task_status(task_id, new_status, attempt=1):
    # Read current state
    with open('docs/state/tasks.json', 'r') as f:
        data = json.load(f)

    current_version = data.get('_version', 0)

    # Re-read immediately before write to detect conflicts
    with open('docs/state/tasks.json', 'r') as f:
        latest_data = json.load(f)

    latest_version = latest_data.get('_version', 0)

    # Check for conflict
    if latest_version != current_version:
        print(f"⚠️ Conflict detected: expected v{current_version}, found v{latest_version}")

        if attempt < MAX_ATTEMPTS:
            print(f"🔄 Retrying (attempt {attempt + 1}/{MAX_ATTEMPTS})...")
            import time
            time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s
            return update_task_status(task_id, new_status, attempt + 1)
        else:
            print(f"🔴 FAILED after {MAX_ATTEMPTS} attempts")
            return False

    # No conflict - apply changes to latest_data
    for task in latest_data['tasks']:
        if task['id'] == task_id:
            task['status'] = new_status
            task['updated_at'] = datetime.now(timezone.utc).isoformat()

    # Increment version
    latest_data['_version'] = latest_version + 1
    latest_data['_last_modified'] = datetime.now(timezone.utc).isoformat()
    latest_data['_last_modified_by'] = 'orchestrator'

    # Write atomically (tmp file + rename)
    with open('docs/state/tasks.json.tmp', 'w') as f:
        json.dump(latest_data, f, indent=2)

    import os
    os.rename('docs/state/tasks.json.tmp', 'docs/state/tasks.json')

    print(f"✅ Updated to version {latest_version + 1}")
    return True

# Execute update
success = update_task_status('TASK-001', 'completed')
exit(0 if success else 1)
PYEOF
```

### 1.6 Simplified Pattern for Agents

**INSTRUCTIONS FOR AGENTS (in agent .md files):**

When updating tasks.json, use this Bash command:

```bash
# Update task with optimistic locking
python3 -c "
import json
from datetime import datetime, timezone

# Read current state
with open('docs/state/tasks.json', 'r') as f:
    data = json.load(f)

original_version = data.get('_version', 0)

# Make changes
for task in data['tasks']:
    if task['id'] == 'TASK-001':
        task['status'] = 'completed'
        task['completed_at'] = datetime.now(timezone.utc).isoformat()

# Increment version
data['_version'] = original_version + 1
data['_last_modified'] = datetime.now(timezone.utc).isoformat()
data['_last_modified_by'] = 'domain-agent'

# Write atomically
with open('docs/state/tasks.json.tmp', 'w') as f:
    json.dump(data, f, indent=2)

import os
os.rename('docs/state/tasks.json.tmp', 'docs/state/tasks.json')

print(f'✅ Updated to version {original_version + 1}')
"

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Task updated successfully"
else
    echo "🔴 Failed to update task"
fi
```

---

## 2. Transaction Log (MANDATORY - Active Logging)

### 2.1 Transaction Log Structure

All state modifications MUST be logged to `docs/state/transaction-log.jsonl`:

```jsonl
{"tx_id": "TX-1736253600", "timestamp": "2026-01-07T10:00:00Z", "agent": "orchestrator", "operation": "claim_task", "file": "tasks.json", "task_id": "TASK-001", "before": {"owner": null}, "after": {"owner": "domain-agent"}}
{"tx_id": "TX-1736253661", "timestamp": "2026-01-07T10:01:01Z", "agent": "domain-agent", "operation": "reject_task", "file": "tasks.json", "task_id": "TASK-045", "before": {"layer": "domain"}, "after": {"layer": "application"}}
{"tx_id": "TX-1736253722", "timestamp": "2026-01-07T10:02:02Z", "agent": "domain-agent", "operation": "complete_task", "file": "tasks.json", "task_id": "TASK-001", "before": {"status": "in_progress"}, "after": {"status": "completed"}}
```

**Format**: JSONL (JSON Lines) - one JSON object per line, append-only

### 2.2 How to Log Transactions (INSTRUCTIONS FOR ORCHESTRATOR/AGENTS)

**CRITICAL**: After EVERY state modification, log to transaction-log.jsonl

**Using Bash (Orchestrator)**:

```bash
# Generate TX ID (unix timestamp)
TX_ID="TX-$(date +%s)"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Log entry
echo "{\"tx_id\":\"$TX_ID\",\"timestamp\":\"$TIMESTAMP\",\"agent\":\"orchestrator\",\"operation\":\"claim_task\",\"file\":\"tasks.json\",\"task_id\":\"TASK-001\",\"before\":{\"owner\":null},\"after\":{\"owner\":\"domain-agent\"}}" >> docs/state/transaction-log.jsonl

# Verify written
echo "✅ Logged transaction $TX_ID"
```

**Using Python one-liner**:

```bash
python3 -c "
import json
from datetime import datetime, timezone
import time

entry = {
    'tx_id': f'TX-{int(time.time())}',
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'agent': 'orchestrator',
    'operation': 'claim_task',
    'file': 'tasks.json',
    'task_id': 'TASK-001',
    'before': {'owner': None},
    'after': {'owner': 'domain-agent'}
}

with open('docs/state/transaction-log.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')

print(f'✅ Logged {entry[\"tx_id\"]}')
"
```

### 2.3 When to Log (MANDATORY)

**Log EVERY one of these operations:**

| Operation | When | Example |
|-----------|------|---------|
| `claim_task` | Orchestrator assigns task to agent | Agent takes ownership |
| `reject_task` | Agent rejects task during PHASE A | Re-classification |
| `complete_task` | Agent marks task as completed | After tests pass |
| `block_task` | Agent marks task as blocked | Tests fail, dependency missing |
| `escalate_task` | Task escalated to user | Circular rejection, too many failures |
| `update_layer` | Task layer changed | Manual re-classification |
| `create_queue` | Agent queue file created | PHASE A completes |
| `update_queue` | Queue file modified | Task status updated |

**Example workflow with logging:**

```bash
# 1. Orchestrator assigns task to domain-agent
python3 -c "..." # Update tasks.json
# IMMEDIATELY log:
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"orchestrator","operation":"claim_task","task_id":"TASK-001","after":{"owner":"domain-agent"}}' >> docs/state/transaction-log.jsonl

# 2. Domain agent completes task
python3 -c "..." # Update tasks.json status=completed
# IMMEDIATELY log:
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"domain-agent","operation":"complete_task","task_id":"TASK-001","after":{"status":"completed"}}' >> docs/state/transaction-log.jsonl

# 3. Domain agent rejects TASK-045
python3 -c "..." # Update tasks.json layer=application
# IMMEDIATELY log:
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"domain-agent","operation":"reject_task","task_id":"TASK-045","before":{"layer":"domain"},"after":{"layer":"application"},"reason":"DTO is application layer"}' >> docs/state/transaction-log.jsonl
```

### 2.3 Rollback Capability

```python
def rollback_to_transaction(tx_id: str):
    """
    Rollback all state changes after the specified transaction.
    """
    log = read_transaction_log()

    # Find transactions to rollback (in reverse order)
    to_rollback = []
    found = False
    for entry in reversed(log):
        if entry["tx_id"] == tx_id:
            found = True
            break
        to_rollback.append(entry)

    if not found:
        raise TransactionNotFoundError(tx_id)

    # Apply rollbacks in reverse order
    for entry in to_rollback:
        file_path = f"docs/state/{entry['file']}"

        # Restore "before" state
        safe_update_state_file(file_path, lambda state:
            apply_rollback(state, entry)
        )

        print(f"⏪ Rolled back: {entry['operation']} on {entry['task_id']}")
```

---

## 3. State File Schemas

### 3.1 tasks.json Schema

```python
TASKS_SCHEMA = {
    "type": "object",
    "required": ["framework_version", "tasks"],
    "properties": {
        "framework_version": {"type": "string", "pattern": "^4\\.4"},
        "imported_from": {"type": "string"},
        "total_tasks": {"type": "integer", "minimum": 0},
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "layer", "status"],
                "properties": {
                    "id": {"type": "string", "pattern": "^TASK-"},
                    "title": {"type": "string", "minLength": 1},
                    "layer": {"enum": ["domain", "application", "infrastructure_backend", "infrastructure_frontend", null]},
                    "status": {"enum": ["pending", "queued", "in_progress", "completed", "blocked", "escalated"]},
                    "owner": {"type": ["string", "null"]},
                    "test_files": {"type": "array", "items": {"type": "string"}},
                    "rejection_history": {"type": "array"},
                    "blocker_info": {"type": "object"},
                    "escalation_info": {"type": "object"}
                }
            }
        }
    }
}
```

### 3.2 Queue File Schema

```python
QUEUE_SCHEMA = {
    "type": "object",
    "required": ["agent", "created_at", "total_tasks", "completed", "queue"],
    "properties": {
        "agent": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "total_tasks": {"type": "integer", "minimum": 0},
        "completed": {"type": "integer", "minimum": 0},
        "rejected_tasks": {"type": "array"},
        "escalated_tasks": {"type": "array"},
        "blocked_tasks": {"type": "array"},
        "queue": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["position", "task_id", "title", "status"],
                "properties": {
                    "position": {"type": "integer", "minimum": 1},
                    "task_id": {"type": "string"},
                    "title": {"type": "string"},
                    "module": {"type": "string"},
                    "status": {"enum": ["pending", "in_progress", "completed", "blocked"]},
                    "test_files": {"type": "array"}
                }
            }
        }
    },
    "additionalProperties": false
}
```

### 3.3 Rejection Tracker Schema

```python
REJECTION_TRACKER_SCHEMA = {
    "type": "object",
    "required": ["rejections", "processed"],
    "properties": {
        "rejections": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["task_id", "rejected_by", "original_layer", "suggested_layer", "timestamp"],
                "properties": {
                    "task_id": {"type": "string", "pattern": "^TASK-"},
                    "title": {"type": "string"},
                    "rejected_by": {"type": "string"},
                    "original_layer": {"enum": ["domain", "application", "infrastructure_backend", "infrastructure_frontend", None]},
                    "suggested_layer": {"enum": ["domain", "application", "infrastructure_backend", "infrastructure_frontend"]},
                    "reason": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "processed": {"type": "boolean"}
                }
            }
        },
        "processed": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}
```

### 3.4 Validation Function (Complete Implementation)

```python
def validate_state_schema(file_path: str, state: dict) -> dict:
    """
    Validate state against its schema with detailed error reporting.

    Returns:
        {
            "valid": bool,
            "errors": list,  # List of error messages
            "warnings": list,  # Non-blocking issues
            "auto_fixed": list  # Issues that were auto-repaired
        }
    """
    result = {"valid": True, "errors": [], "warnings": [], "auto_fixed": []}

    # Determine schema
    if "tasks.json" in file_path:
        schema = TASKS_SCHEMA
        result = validate_tasks_file(state, result)
    elif "queue.json" in file_path:
        schema = QUEUE_SCHEMA
        result = validate_queue_file(state, result)
    elif "rejection-tracker.json" in file_path:
        schema = REJECTION_TRACKER_SCHEMA
        result = validate_rejection_tracker(state, result)
    else:
        return result  # No schema for unknown files

    result["valid"] = len(result["errors"]) == 0
    return result


def validate_tasks_file(state: dict, result: dict) -> dict:
    """Validate tasks.json with business rules."""

    # Required fields
    if "tasks" not in state:
        result["errors"].append("Missing required field: tasks")
        return result

    tasks = state.get("tasks", [])

    # Check for duplicate IDs
    task_ids = [t.get("id") for t in tasks]
    duplicates = [id for id in task_ids if task_ids.count(id) > 1]
    if duplicates:
        result["errors"].append(f"Duplicate task IDs found: {set(duplicates)}")

    # Validate each task
    for i, task in enumerate(tasks):
        task_id = task.get("id", f"[index {i}]")

        # Required fields
        if not task.get("id"):
            result["errors"].append(f"Task at index {i} missing 'id'")
        if not task.get("title"):
            result["warnings"].append(f"Task {task_id} missing 'title'")

        # Layer validation
        valid_layers = ["domain", "application", "infrastructure_backend", "infrastructure_frontend", None]
        if task.get("layer") not in valid_layers:
            result["errors"].append(f"Task {task_id} has invalid layer: {task.get('layer')}")

        # Status validation
        valid_statuses = ["pending", "queued", "in_progress", "completed", "blocked", "escalated"]
        if task.get("status") not in valid_statuses:
            result["errors"].append(f"Task {task_id} has invalid status: {task.get('status')}")

        # Owner consistency
        if task.get("status") == "in_progress" and not task.get("owner"):
            result["warnings"].append(f"Task {task_id} is in_progress but has no owner")

        # Blocked tasks must have blocker_info
        if task.get("status") == "blocked" and not task.get("blocker_info"):
            result["warnings"].append(f"Task {task_id} is blocked but has no blocker_info")

        # Escalated tasks should have escalation_info
        if task.get("status") == "escalated" and not task.get("escalation_info"):
            result["warnings"].append(f"Task {task_id} is escalated but has no escalation_info")

    return result


def validate_queue_file(state: dict, result: dict) -> dict:
    """Validate queue file with business rules."""

    # Required fields
    required = ["agent", "created_at", "total_tasks", "completed", "queue"]
    for field in required:
        if field not in state:
            result["errors"].append(f"Missing required field: {field}")

    if "queue" not in state:
        return result

    queue = state.get("queue", [])
    agent = state.get("agent", "unknown")

    # Validate completed count
    actual_completed = sum(1 for item in queue if item.get("status") == "completed")
    declared_completed = state.get("completed", 0)
    if actual_completed != declared_completed:
        result["warnings"].append(
            f"Completed count mismatch: declared {declared_completed}, actual {actual_completed}"
        )
        # Auto-fix
        state["completed"] = actual_completed
        result["auto_fixed"].append(f"Fixed completed count: {declared_completed} → {actual_completed}")

    # Validate total_tasks
    if state.get("total_tasks", 0) != len(queue):
        result["warnings"].append(
            f"total_tasks mismatch: declared {state.get('total_tasks')}, actual {len(queue)}"
        )
        state["total_tasks"] = len(queue)
        result["auto_fixed"].append(f"Fixed total_tasks count")

    # Check position sequence
    positions = [item.get("position", 0) for item in queue]
    expected_positions = list(range(1, len(queue) + 1))
    if sorted(positions) != expected_positions:
        result["warnings"].append(f"Position sequence is not continuous")

    # Validate each queue item
    for i, item in enumerate(queue):
        task_id = item.get("task_id", f"[position {i}]")

        # Required fields
        if not item.get("task_id"):
            result["errors"].append(f"Queue item at position {i} missing 'task_id'")
        if not item.get("title"):
            result["warnings"].append(f"Queue item {task_id} missing 'title'")

        # Status validation
        valid_statuses = ["pending", "in_progress", "completed", "blocked"]
        if item.get("status") not in valid_statuses:
            result["errors"].append(f"Queue item {task_id} has invalid status: {item.get('status')}")

    # Validate rejected_tasks if present
    for rejected in state.get("rejected_tasks", []):
        if not rejected.get("task_id"):
            result["errors"].append("Rejected task entry missing task_id")
        if not rejected.get("suggested_layer"):
            result["errors"].append(f"Rejected task {rejected.get('task_id')} missing suggested_layer")

    # Validate escalated_tasks if present
    for escalated in state.get("escalated_tasks", []):
        if not escalated.get("task_id"):
            result["errors"].append("Escalated task entry missing task_id")
        if not escalated.get("reason"):
            result["warnings"].append(f"Escalated task {escalated.get('task_id')} missing reason")

    return result


def validate_rejection_tracker(state: dict, result: dict) -> dict:
    """Validate rejection-tracker.json."""

    # Required fields
    if "rejections" not in state:
        result["errors"].append("Missing required field: rejections")
        return result

    # Validate each rejection entry
    for i, rejection in enumerate(state.get("rejections", [])):
        if not rejection.get("task_id"):
            result["errors"].append(f"Rejection entry at index {i} missing task_id")
        if not rejection.get("suggested_layer"):
            result["errors"].append(f"Rejection entry {rejection.get('task_id')} missing suggested_layer")

        # Validate suggested_layer value
        valid_layers = ["domain", "application", "infrastructure_backend", "infrastructure_frontend"]
        if rejection.get("suggested_layer") and rejection["suggested_layer"] not in valid_layers:
            result["errors"].append(
                f"Rejection entry {rejection.get('task_id')} has invalid suggested_layer: {rejection['suggested_layer']}"
            )

    return result
```

---

## 4. Consistency Checks

### 4.1 Cross-File Consistency

```python
def verify_state_consistency():
    """
    Verify consistency across all state files.

    Checks:
    1. All tasks in queue files exist in tasks.json
    2. Task ownership matches between tasks.json and queues
    3. Completed counts are accurate
    4. No orphaned tasks
    """
    tasks = Read("docs/state/tasks.json")["tasks"]
    task_ids = {t["id"] for t in tasks}

    errors = []

    # Check each queue file
    for queue_file in glob("docs/state/agent-queues/*.json"):
        queue = Read(queue_file)

        for item in queue["queue"]:
            # Check task exists
            if item["task_id"] not in task_ids:
                errors.append(f"Queue {queue_file} references non-existent task {item['task_id']}")

            # Check ownership matches
            task = next((t for t in tasks if t["id"] == item["task_id"]), None)
            if task and task.get("owner") != queue["agent"]:
                errors.append(f"Ownership mismatch: {item['task_id']} owned by {task.get('owner')} but in {queue['agent']}'s queue")

        # Check completed count
        actual_completed = sum(1 for item in queue["queue"] if item["status"] == "completed")
        if actual_completed != queue["completed"]:
            errors.append(f"Completed count mismatch in {queue_file}: {queue['completed']} vs {actual_completed}")

    # Check for orphaned tasks
    owned_tasks = set()
    for queue_file in glob("docs/state/agent-queues/*.json"):
        queue = Read(queue_file)
        for item in queue["queue"]:
            owned_tasks.add(item["task_id"])

    for task in tasks:
        if task["status"] not in ["completed", "escalated"] and task["id"] not in owned_tasks:
            if task.get("owner") is None:
                errors.append(f"Orphaned task: {task['id']} has no owner and is not in any queue")

    return errors
```

### 4.2 Repair Functions

```python
def repair_completed_count(queue_file: str):
    """Repair completed count in queue file."""
    def update(queue):
        actual = sum(1 for item in queue["queue"] if item["status"] == "completed")
        queue["completed"] = actual
        return queue

    safe_update_state_file(queue_file, update)


def repair_orphaned_task(task_id: str, target_layer: str):
    """Assign orphaned task to appropriate layer."""
    def update(tasks_data):
        for task in tasks_data["tasks"]:
            if task["id"] == task_id:
                task["layer"] = target_layer
                task["owner"] = None  # Will be picked up in next PHASE A
                task["status"] = "pending"
        return tasks_data

    safe_update_state_file("docs/state/tasks.json", update)
```

---

## 5. Recovery Protocol

### 5.1 Startup Validation

```python
def validate_state_on_startup():
    """
    Run all validations when framework starts.
    """
    print("🔍 Validating state files...")

    # 1. Check for stale locks
    for lock_file in glob("docs/state/**/*.lock"):
        lock_info = Read(lock_file)
        age = current_timestamp() - lock_info["locked_at"]
        if age > 60:
            print(f"   ⚠️ Removing stale lock: {lock_file}")
            delete_file(lock_file)

    # 2. Validate schemas
    for state_file in ["docs/state/tasks.json", *glob("docs/state/agent-queues/*.json")]:
        try:
            state = Read(state_file)
            validate_state_schema(state_file, state)
            print(f"   ✅ {state_file} - valid")
        except SchemaValidationError as e:
            print(f"   🔴 {state_file} - INVALID: {e}")

    # 3. Check consistency
    errors = verify_state_consistency()
    if errors:
        print(f"   🔴 Consistency errors found:")
        for error in errors:
            print(f"      - {error}")
    else:
        print(f"   ✅ State consistency verified")

    return len(errors) == 0
```

### 5.2 Corruption Recovery

```python
def recover_from_corruption(file_path: str):
    """
    Attempt to recover a corrupted state file.
    """
    print(f"🔧 Attempting recovery of {file_path}")

    # Try to read transaction log
    log = read_transaction_log()

    # Find last known good state for this file
    last_good_state = None
    for entry in reversed(log):
        if entry["file"] == file_path and entry.get("after"):
            last_good_state = entry["after"]
            break

    if last_good_state:
        print(f"   ✅ Found last good state from TX {entry['tx_id']}")
        Write(file_path, last_good_state)
        return True
    else:
        print(f"   🔴 No recovery data available")
        return False
```

---

## 6. Usage in Agents

### 6.1 Claiming Task Ownership (Safe Pattern)

```python
def claim_task_ownership(task_id: str, agent: str):
    """
    Safely claim ownership of a task with locking.
    """
    def update(tasks_data):
        for task in tasks_data["tasks"]:
            if task["id"] == task_id:
                # Check if already owned
                if task.get("owner") is not None and task["owner"] != agent:
                    raise TaskAlreadyOwnedError(f"Task {task_id} owned by {task['owner']}")

                task["owner"] = agent
                task["status"] = "queued"
        return tasks_data

    safe_update_state_file("docs/state/tasks.json", update)

    # Log transaction
    log_transaction("claim_task", "tasks.json", {
        "task_id": task_id,
        "before": {"owner": None},
        "after": {"owner": agent}
    })
```

### 6.2 Rejecting Task (Safe Pattern)

```python
def reject_task(task_id: str, rejecting_agent: str, suggested_layer: str, reason: str):
    """
    Safely reject and re-classify a task with locking.
    """
    def update(tasks_data):
        for task in tasks_data["tasks"]:
            if task["id"] == task_id:
                old_layer = task.get("layer")

                # Update layer
                task["layer"] = suggested_layer
                task["owner"] = None
                task["status"] = "pending"

                # Add to rejection history
                if "rejection_history" not in task:
                    task["rejection_history"] = []

                task["rejection_history"].append({
                    "rejected_by": rejecting_agent,
                    "original_layer": old_layer,
                    "suggested_layer": suggested_layer,
                    "reason": reason,
                    "timestamp": current_timestamp()
                })
        return tasks_data

    safe_update_state_file("docs/state/tasks.json", update)

    # Log transaction
    log_transaction("reject_task", "tasks.json", {
        "task_id": task_id,
        "before": {"layer": old_layer},
        "after": {"layer": suggested_layer}
    })
```

---

## 7. Integration with migrate-start.md

All state file operations in migrate-start.md should use these patterns:

```python
# BEFORE (unsafe):
tasks = Read("docs/state/tasks.json")
tasks["tasks"][0]["owner"] = "domain-agent"
Write("docs/state/tasks.json", tasks)

# AFTER (safe):
claim_task_ownership("TASK-001", "domain-agent")
```

---

**Document Version**: 1.0
**Last Updated**: 2026-01-06
