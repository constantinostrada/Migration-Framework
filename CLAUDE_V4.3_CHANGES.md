# Framework v4.3 - Critical Changes Summary

## 🔄 Major Changes

### **1. Auto-Assignment of Tasks (NO Orchestrator Assignment)**

**Before (v4.2)**:
- Orchestrator assigned tasks to agents via `assigned_to` field
- tasks.json specified: `"assigned_to": "domain-agent"`
- Agents were told exactly which tasks to do

**After (v4.3)**:
- ✅ **NO `assigned_to` field** - Replaced with `owner: null`
- ✅ Agents **read ALL tasks** and auto-identify their responsibilities
- ✅ Agents **claim ownership** by setting `owner: "agent-name"`
- ✅ Orchestrator invokes with **generic prompts** (no specific task assignment)

**Why**: Tests agents' intelligence - they must understand their role and identify their work.

---

### **2. Dual Tracking System**

**New Structure**:
```
docs/state/
├── tasks.json (master file, updated by all agents)
└── tracking/
    ├── domain-agent-progress.json
    ├── use-case-agent-progress.json
    └── infrastructure-agent-progress.json
```

**tasks.json** (shared, updated by agents):
```json
{
  "id": "TASK-CUSTOMER-PHASE2-001",
  "owner": "domain-agent",  // Agent claims ownership
  "status": "completed"      // Agent updates status
}
```

**agent-progress.json** (agent-specific details):
```json
{
  "agent_name": "domain-agent",
  "tasks": [
    {
      "task_id": "TASK-CUSTOMER-PHASE2-001",
      "owner": "domain-agent",
      "status": "completed",
      "files_generated": ["..."],
      "tests_passed": true,
      "notes": "Brief implementation summary"
    }
  ]
}
```

---

### **3. No FDD Approval (Fully Autonomous)**

**Before (v4.2)**:
- domain-agent generated full FDD document (10 sections)
- Workflow **paused** for user approval
- User had to review and approve before continuing

**After (v4.3)**:
- ✅ **NO FDD document** generation
- ✅ **NO pause** for user approval
- ✅ Agents update `progress.json` with brief notes (2-4 sentences)
- ✅ **Fully autonomous** workflow

**Decision Points Reduced**:
- **Before**: 5 decision points (including FDD approval)
- **After**: 4 decision points (FDD approval eliminated)

---

### **4. Agent Task Identification Logic**

**How Agents Know What Tasks Are Theirs**:

**domain-agent**:
- `implementation_layer: "domain"`
- Keywords: "entity", "value object", "domain service", "business rule"
- Must check: `owner: null` (not claimed yet)

**use-case-agent**:
- `implementation_layer: "application"` or `"use_case"`
- Keywords: "use case", "DTO", "repository interface", "orchestrate"
- Must verify: domain tasks completed first

**infrastructure-agent**:
- `implementation_layer: "infrastructure"`
- Keywords: "ORM", "API", "FastAPI", "frontend", "React", "repository implementation"
- Must verify: domain AND application tasks completed first

---

### **5. Conflict Prevention (Simplified)**

**How Agents Avoid Taking Same Task**:

1. Agent reads `tasks.json` **ONCE**
2. Filters: `owner: null` AND `status: "pending"` AND matches their layer
3. If `owner` is not null → **skip** (another agent already claimed it)
4. Claim ownership by updating `tasks.json`

**Key Simplification**:
- ❌ **NO** need to read other agents' progress files
- ✅ `tasks.json` is the **single source of truth** for ownership
- ✅ **One file read** instead of 3+
- ✅ **Simpler logic**, less prone to errors

---

### **6. Infrastructure Layer Separation** ✅

**Problem Solved**: infrastructure-agent being invoked twice (backend, then frontend) would cause task conflicts.

**Solution**: Split `infrastructure` layer into two:
- `infrastructure_backend` - ORM, repositories, API
- `infrastructure_frontend` - React, Next.js, UI components

**How it works**:
```python
# First invocation (backend)
my_tasks = [t for t in all_tasks if
    t["owner"] is None and
    t["implementation_layer"] == "infrastructure_backend"]

# Second invocation (frontend)
my_tasks = [t for t in all_tasks if
    t["owner"] is None and
    t["implementation_layer"] == "infrastructure_frontend"]
```

**Benefits**:
- ✅ No task conflicts
- ✅ Clear separation backend/frontend
- ✅ Same agent can be invoked twice safely
- ✅ Simple filtering logic

---

## 📁 Files Updated

### **Schemas (2 files)**:
1. ✅ `docs/schemas/tasks-schema.ts` - Replaced `assigned_to` with `owner`, split infrastructure layer
2. ✅ `docs/schemas/agent-progress-schema.ts` - **NEW** schema for progress files

### **Agent Instructions (3 files)**:
3. ✅ `.claude/agents/domain-agent.md` - Auto-assignment logic, no FDD, simplified conflict prevention
4. ✅ `.claude/agents/use-case-agent.md` - Auto-assignment logic, simplified conflict prevention
5. ✅ `.claude/agents/infrastructure-agent.md` - Auto-assignment logic, backend/frontend separation, simplified conflict prevention

### **Framework Documentation (3 files)**:
6. ✅ `CLAUDE.md` - Removed FDD approval, updated workflow, infrastructure layer split
7. ✅ `.claude/docs/migration-phases.md` - Generic prompts, no FDD pause, two infrastructure invocations
8. ✅ `.claude/docs/agent-invocation-guide.md` - v4.3 invocation patterns

---

## 🎯 Key Benefits

1. **Tests Agent Intelligence**: Agents must understand their role and self-assign
2. **Eliminates Bottlenecks**: No pause for FDD approval
3. **Better Tracking**: Separate progress files per agent (no conflicts)
4. **Simplified Conflict Prevention**: Single source of truth (tasks.json), 66% less I/O
5. **No Task Conflicts**: Infrastructure layer split prevents backend/frontend collision
6. **Fully Autonomous**: Workflow continues without user intervention (except 4 critical points)

---

## 🚀 Migration Impact

**For New Migrations**:
- ✅ tasks.json will have `owner: null` instead of `assigned_to`
- ✅ Agents will create their own progress files
- ✅ No FDD documents generated
- ✅ Faster workflow (no approval pause)

**Orchestrator Changes**:
- ✅ Generic prompts: "Read tasks.json and work on what corresponds to your role"
- ✅ No specific task assignment in prompts
- ✅ Agents report back after completing their work

---

## 📊 Decision Points (Reduced from 5 to 4)

**v4.2 (5 points)**:
1. PHASE 0: Unclear business rules
2. PHASE 0.5: Tech stack incompatibility
3. **PHASE 2: FDD approval** ← ELIMINATED
4. PHASE 3: UI mockup approval
5. PHASE 4: E2E strategic decision

**v4.3 (4 points)**:
1. PHASE 0: Unclear business rules
2. PHASE 0.5: Tech stack incompatibility
3. PHASE 3: UI mockup approval
4. PHASE 4: E2E strategic decision

---

**Version**: 4.3
**Date**: 2026-01-02
**Status**: ✅ Implemented
