# Agent Invocation Guide

**📖 Documentation Navigation:**
- **← Previous**: [migration-phases.md](./migration-phases.md) - Complete phase-by-phase workflow
- **→ Agent Files**: [../agents/](../agents/) - Individual agent instruction files

---

## 📚 AGENT INVOCATION REFERENCE

**Understanding Agent Architecture:**

The framework uses **11 specialized agents**, but only **2 are registered as dedicated `subagent_type`** in Claude Code:
- `context7-agent` (has Context7 MCP server)
- `e2e-qa-agent` (has Playwright MCP server)

**All other agents** (9 total) are invoked using `subagent_type="Explore"` and read their instructions from `.claude/agents/{agent-name}.md`.

**Why `/agents` command doesn't show all agents:**
- `/agents` shows registered `subagent_type` values, not markdown files
- Agent instruction files (`.claude/agents/*.md`) are documentation, not `subagent_type` registrations
- This is **by design** - keeps the framework flexible and extensible

**Complete Invocation Matrix:**

| Agent | File | Invocation Method |
|-------|------|-------------------|
| sdd-analyzer | `.claude/agents/sdd-analyzer.md` | `Task(..., subagent_type="Explore")` |
| tech-stack-validator | `.claude/agents/tech-stack-validator.md` | `Task(..., subagent_type="Explore")` |
| qa-test-generator | `.claude/agents/qa-test-generator.md` | `Task(..., subagent_type="Explore")` |
| domain-agent | `.claude/agents/domain-agent.md` | `Task(..., subagent_type="Explore")` |
| use-case-agent | `.claude/agents/use-case-agent.md` | `Task(..., subagent_type="Explore")` |
| infrastructure-agent | `.claude/agents/infrastructure-agent.md` | `Task(..., subagent_type="Explore")` |
| shadcn-ui-agent | `.claude/agents/shadcn-ui-agent.md` | `Task(..., subagent_type="Explore")` |
| ui-approval-agent | `.claude/agents/ui-approval-agent.md` | `Task(..., subagent_type="Explore")` |
| context7-agent | `.claude/agents/context7-agent.md` | `Task(..., subagent_type="context7-agent")` ⚠️ |
| smoke-test-agent | `.claude/agents/smoke-test-agent.md` | **Orchestrator executes directly** (no Task) |
| e2e-qa-agent | `.claude/agents/e2e-qa-agent.md` | `Task(..., subagent_type="e2e-qa-agent")` ⚠️ |

**⚠️ = Dedicated subagent_type (registered in Claude Code)**

**Standard Invocation Pattern (v4.3 - Auto-Assignment):**

```python
# For implementation agents (domain, use-case, infrastructure)
# v4.3: Generic prompts, NO specific task assignment
Task(
    description="{Agent} auto-implementation",
    prompt="""
    Read .claude/agents/{agent-name}.md for complete instructions.

    YOUR MISSION (v4.3 - Auto-Assignment):
    1. Read ALL tasks from docs/state/tasks.json
    2. Identify YOUR tasks based on your role (implementation_layer, keywords)
    3. Check for conflicts (read other progress files)
    4. Claim ownership (update tasks.json with owner = "{agent-name}")
    5. Initialize/update your progress file: docs/state/tracking/{agent-name}-progress.json
    6. For each task:
       - Implement according to your layer (domain/application/infrastructure)
       - Run tests until pass
       - Update progress.json with brief notes
       - Update tasks.json status = "completed"

    CRITICAL:
    - NO orchestrator tells you which tasks to do
    - YOU must identify your responsibilities
    - Work autonomously
    - Update both tasks.json and your progress.json
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

**For analysis agents (sdd-analyzer, qa-test-generator, etc.):**
```python
# These still get specific prompts (not auto-assignment)
Task(
    description="Execute {agent-name} workflow",
    prompt="""
    Read .claude/agents/{agent-name}.md for complete instructions.

    INPUT FILES:
    - {list input files}

    OUTPUT FILES:
    - {list expected output files}

    [Specific mission context]
    """,
    subagent_type="Explore",
    model="sonnet"
)
```

**Key Points (v4.3 Updates):**
- ✅ Agent instructions live in `.claude/agents/*.md` (11 files exist)
- ✅ Most agents share `subagent_type="Explore"` for efficiency
- ✅ **NEW**: Implementation agents auto-assign tasks (no orchestrator guidance)
- ✅ **NEW**: Agents update dual tracking (tasks.json + progress.json)
- ✅ **NEW**: No FDD approval, fully autonomous workflow
- ✅ Only 2 agents need dedicated `subagent_type` (MCP access)
- ✅ `smoke-test-agent` is executed by Orchestrator (Python script)

---

**Ready to migrate legacy systems with Clean Architecture!** 🚀
