# Orchestrator State Management Instructions - v4.4.1

**CRITICAL**: These instructions REPLACE the file locking pseudocode in migrate-start.md

---

## State Update Pattern (MANDATORY)

Every time you need to update `tasks.json` or any state file, follow this pattern:

### Pattern 1: Simple Update (Single Task)

```bash
# Update a single task's status with optimistic locking

python3 << 'PYEOF'
import json
from datetime import datetime, timezone
import os

TASK_ID = "TASK-001"
NEW_STATUS = "completed"
AGENT_NAME = "domain-agent"

# Read current state
with open('docs/state/tasks.json', 'r') as f:
    data = json.load(f)

original_version = data.get('_version', 0)

# Make changes
timestamp = datetime.now(timezone.utc).isoformat()
for task in data['tasks']:
    if task['id'] == TASK_ID:
        task['status'] = NEW_STATUS
        task['updated_at'] = timestamp
        if 'status_history' not in task:
            task['status_history'] = []
        task['status_history'].append({
            'status': NEW_STATUS,
            'timestamp': timestamp,
            'agent': AGENT_NAME
        })

# Increment version
data['_version'] = original_version + 1
data['_last_modified'] = timestamp
data['_last_modified_by'] = AGENT_NAME

# Write atomically (tmp + rename)
with open('docs/state/tasks.json.tmp', 'w') as f:
    json.dump(data, f, indent=2)

os.rename('docs/state/tasks.json.tmp', 'docs/state/tasks.json')

print(f'✅ Updated to version {original_version + 1}')
PYEOF

# Log to transaction log
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"orchestrator","operation":"complete_task","task_id":"'$TASK_ID'","after":{"status":"'$NEW_STATUS'"}}' >> docs/state/transaction-log.jsonl
```

### Pattern 2: Bulk Update (Multiple Tasks)

```bash
# Update multiple tasks at once (more efficient)

python3 << 'PYEOF'
import json
from datetime import datetime, timezone
import os

UPDATES = {
    "TASK-001": {"status": "completed"},
    "TASK-002": {"owner": "domain-agent", "status": "queued"},
    "TASK-003": {"layer": "application", "owner": None}
}

AGENT_NAME = "orchestrator"

# Read current state
with open('docs/state/tasks.json', 'r') as f:
    data = json.load(f)

original_version = data.get('_version', 0)
timestamp = datetime.now(timezone.utc).isoformat()

# Apply all updates
for task in data['tasks']:
    if task['id'] in UPDATES:
        changes = UPDATES[task['id']]
        for key, value in changes.items():
            task[key] = value
        task['updated_at'] = timestamp

# Increment version
data['_version'] = original_version + 1
data['_last_modified'] = timestamp
data['_last_modified_by'] = AGENT_NAME

# Write atomically
with open('docs/state/tasks.json.tmp', 'w') as f:
    json.dump(data, f, indent=2)

os.rename('docs/state/tasks.json.tmp', 'docs/state/tasks.json')

print(f'✅ Updated {len(UPDATES)} tasks to version {original_version + 1}')
PYEOF

# Log each update
for task_id in TASK-001 TASK-002 TASK-003; do
    echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"orchestrator","operation":"update_task","task_id":"'$task_id'"}' >> docs/state/transaction-log.jsonl
done
```

### Pattern 3: Task Rejection (with Re-classification)

```bash
# Reject a task and re-classify to different layer

TASK_ID="TASK-045"
REJECTING_AGENT="domain-agent"
NEW_LAYER="application"
REASON="DTO is application layer, not domain"

python3 << PYEOF
import json
from datetime import datetime, timezone
import os

TASK_ID = "$TASK_ID"
NEW_LAYER = "$NEW_LAYER"
REJECTING_AGENT = "$REJECTING_AGENT"
REASON = "$REASON"

# Read current state
with open('docs/state/tasks.json', 'r') as f:
    data = json.load(f)

original_version = data.get('_version', 0)
timestamp = datetime.now(timezone.utc).isoformat()

# Find and update task
for task in data['tasks']:
    if task['id'] == TASK_ID:
        old_layer = task.get('layer')

        # Update layer
        task['layer'] = NEW_LAYER
        task['owner'] = None
        task['status'] = 'pending'
        task['updated_at'] = timestamp

        # Add to rejection history
        if 'rejection_history' not in task:
            task['rejection_history'] = []

        task['rejection_history'].append({
            'rejected_by': REJECTING_AGENT,
            'original_layer': old_layer,
            'suggested_layer': NEW_LAYER,
            'reason': REASON,
            'timestamp': timestamp
        })

        print(f'✅ Rejected {TASK_ID}: {old_layer} → {NEW_LAYER}')

# Increment version
data['_version'] = original_version + 1
data['_last_modified'] = timestamp
data['_last_modified_by'] = REJECTING_AGENT

# Write atomically
with open('docs/state/tasks.json.tmp', 'w') as f:
    json.dump(data, f, indent=2)

os.rename('docs/state/tasks.json.tmp', 'docs/state/tasks.json')
PYEOF

# Log rejection
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"'$REJECTING_AGENT'","operation":"reject_task","task_id":"'$TASK_ID'","before":{"layer":"domain"},"after":{"layer":"'$NEW_LAYER'"},"reason":"'$REASON'"}' >> docs/state/transaction-log.jsonl
```

---

## Transaction Logging (MANDATORY)

**After EVERY state update, log to transaction-log.jsonl**

### Quick Reference

```bash
# Simple log entry (one-liner)
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"orchestrator","operation":"claim_task","task_id":"TASK-001"}' >> docs/state/transaction-log.jsonl

# With before/after
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"domain-agent","operation":"complete_task","task_id":"TASK-001","before":{"status":"in_progress"},"after":{"status":"completed"}}' >> docs/state/transaction-log.jsonl

# With reason
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"domain-agent","operation":"reject_task","task_id":"TASK-045","reason":"Not a domain task"}' >> docs/state/transaction-log.jsonl
```

### Operations to Log

| Operation | When | Required Fields |
|-----------|------|-----------------|
| `claim_task` | Task assigned to agent | `task_id`, `after.owner` |
| `reject_task` | Task rejected & re-classified | `task_id`, `before.layer`, `after.layer`, `reason` |
| `complete_task` | Task marked completed | `task_id`, `after.status` |
| `block_task` | Task marked blocked | `task_id`, `reason` |
| `escalate_task` | Task escalated to user | `task_id`, `reason` |
| `create_queue` | Queue file created | `agent`, `queue_file`, `total_tasks` |
| `agent_invocation_start` | Before Task() call | `agent`, `phase`, `task_id` (if PHASE B) |
| `agent_invocation_end` | After Task() returns | `agent`, `phase`, `success`, `duration_seconds` |

---

## Agent Invocation Logging

**Before every `Task()` invocation**:

```bash
# Log invocation start
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","event":"agent_invocation_start","agent":"domain-agent","phase":"A","module":"Customer"}' >> docs/state/agent-invocations.jsonl
```

**After `Task()` returns**:

```bash
# Log invocation end (success)
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","event":"agent_invocation_end","agent":"domain-agent","phase":"A","success":true,"duration_seconds":45}' >> docs/state/agent-invocations.jsonl

# Log invocation end (failure)
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","event":"agent_invocation_end","agent":"domain-agent","phase":"B","task_id":"TASK-001","success":false,"error":"Tests failed"}' >> docs/state/agent-invocations.jsonl
```

---

## Validation Pattern

**After critical operations, validate state**:

```bash
# Verify tasks.json is valid JSON
python3 -c "import json; data = json.load(open('docs/state/tasks.json')); print(f'✅ Valid JSON, {len(data[\"tasks\"])} tasks, version {data.get(\"_version\", 0)}')"

# Verify transaction log is appendable
if [ -f docs/state/transaction-log.jsonl ]; then
    echo '{"test":"true"}' >> docs/state/transaction-log.jsonl && tail -1 docs/state/transaction-log.jsonl | grep -q test && echo "✅ Transaction log OK"
fi

# Check for orphaned tasks
python3 << 'PYEOF'
import json

with open('docs/state/tasks.json') as f:
    data = json.load(f)

orphans = [t for t in data['tasks']
           if t.get('status') not in ['completed', 'escalated']
           and t.get('owner') is None]

if orphans:
    print(f"⚠️ Found {len(orphans)} orphaned tasks:")
    for task in orphans[:5]:
        print(f"   - {task['id']}: {task.get('title', 'No title')}")
else:
    print("✅ No orphaned tasks")
PYEOF
```

---

## Checkpoint Pattern

**After each layer completes, create checkpoint**:

```bash
# Create checkpoint after Domain layer completes

LAYER="domain"
CHECKPOINT_NAME="checkpoint-${LAYER}-complete"

mkdir -p docs/state/checkpoints

# Copy state files
cp docs/state/tasks.json docs/state/checkpoints/${CHECKPOINT_NAME}.json
cp docs/state/agent-queues/domain-queue.json docs/state/checkpoints/${CHECKPOINT_NAME}-queue.json 2>/dev/null || true

# Create metadata
python3 << PYEOF
import json
from datetime import datetime, timezone

tasks = json.load(open('docs/state/tasks.json'))
total = len(tasks['tasks'])
completed = len([t for t in tasks['tasks'] if t.get('status') == 'completed'])

metadata = {
    'checkpoint_name': '$CHECKPOINT_NAME',
    'layer': '$LAYER',
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'total_tasks': total,
    'completed_tasks': completed,
    'progress_percent': round(completed / total * 100, 1) if total > 0 else 0
}

with open('docs/state/checkpoints/${CHECKPOINT_NAME}-meta.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Checkpoint created: ${CHECKPOINT_NAME} ({metadata['progress_percent']}% complete)")
PYEOF

# Log checkpoint creation
echo '{"tx_id":"TX-'$(date +%s)'","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","event":"checkpoint_created","checkpoint":"'$CHECKPOINT_NAME'","layer":"'$LAYER'"}' >> docs/state/transaction-log.jsonl
```

---

## Session Recovery Detection

**At the start of migrate-start.md (STEP 0)**:

```bash
# Check if previous session exists

if [ -f "docs/state/tasks.json" ]; then
    echo "🔍 Previous migration session detected"

    # Calculate progress
    python3 << 'PYEOF'
import json

data = json.load(open('docs/state/tasks.json'))
total = len(data['tasks'])
completed = len([t for t in data['tasks'] if t.get('status') == 'completed'])
in_progress = len([t for t in data['tasks'] if t.get('status') == 'in_progress'])
blocked = len([t for t in data['tasks'] if t.get('status') == 'blocked'])

progress = round(completed / total * 100, 1) if total > 0 else 0

print(f"📊 Session State:")
print(f"   Total tasks: {total}")
print(f"   Completed: {completed} ({progress}%)")
print(f"   In progress: {in_progress}")
print(f"   Blocked: {blocked}")
print(f"   Version: {data.get('_version', 0)}")
PYEOF

    # Ask user
    # Use AskUserQuestion here
    echo "   Options: RESUME | RESTART | INSPECT"

    # If RESUME: Find last completed layer, continue from next
    # If RESTART: Backup old state, start fresh
    # If INSPECT: Show queue files, let user investigate
fi
```

---

**Use these patterns in migrate-start.md to replace the old file locking code.**
