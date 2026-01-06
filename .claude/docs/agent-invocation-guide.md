# Agent Invocation Guide

**📖 Documentation Navigation:**
- **← Previous**: [migration-phases.md](./migration-phases.md) - Complete phase-by-phase workflow
- **→ Agent Files**: [../agents/](../agents/) - Individual agent instruction files

---

## 📚 AGENT INVOCATION REFERENCE

**Understanding Agent Architecture:**

The framework uses **11 specialized agents**. **10 are registered as dedicated subagents** in Claude Code with frontmatter:
- `sdd-analyzer`
- `tech-stack-validator`
- `qa-test-generator`
- `domain-agent`
- `use-case-agent`
- `infrastructure-agent`
- `context7-agent`
- `shadcn-ui-agent`
- `ui-approval-agent`
- `e2e-qa-agent`

**1 agent** is NOT a subagent:
- `smoke-test-agent` - orchestrator executes directly (Python/Bash scripts)

**Why `/agents` command shows these agents:**
- `/agents` shows registered `subagent_type` values (agents with proper frontmatter)
- 10 agents have `name:` frontmatter and are registered as dedicated subagents
- 1 agent is not a subagent (smoke-test-agent - direct execution)

**Complete Invocation Matrix:**

| Agent | File | Invocation Method |
|-------|------|-------------------|
| sdd-analyzer | `.claude/agents/sdd-analyzer.md` | `Task(..., subagent_type="sdd-analyzer")` ✅ |
| tech-stack-validator | `.claude/agents/tech-stack-validator.md` | `Task(..., subagent_type="tech-stack-validator")` ✅ |
| qa-test-generator | `.claude/agents/qa-test-generator.md` | `Task(..., subagent_type="qa-test-generator")` ✅ |
| domain-agent | `.claude/agents/domain-agent.md` | `Task(..., subagent_type="domain-agent")` ✅ |
| use-case-agent | `.claude/agents/use-case-agent.md` | `Task(..., subagent_type="use-case-agent")` ✅ |
| infrastructure-agent | `.claude/agents/infrastructure-agent.md` | `Task(..., subagent_type="infrastructure-agent")` ✅ |
| shadcn-ui-agent | `.claude/agents/shadcn-ui-agent.md` | `Task(..., subagent_type="shadcn-ui-agent")` ✅ |
| ui-approval-agent | `.claude/agents/ui-approval-agent.md` | `Task(..., subagent_type="ui-approval-agent")` ✅ |
| context7-agent | `.claude/agents/context7-agent.md` | `Task(..., subagent_type="context7-agent")` ✅ |
| smoke-test-agent | `.claude/agents/smoke-test-agent.md` | **Orchestrator executes directly** ⚠️ |
| e2e-qa-agent | `.claude/agents/e2e-qa-agent.md` | `Task(..., subagent_type="e2e-qa-agent")` ✅ |

**✅ = Registered as dedicated subagent (has frontmatter)**
**⚠️ = Not a subagent (orchestrator executes directly via Python/Bash)**

**Standard Invocation Pattern (v4.3 - All Registered Agents):**

```python
# For ALL REGISTERED agents (10 agents with dedicated subagent_type)
# Use agent-specific subagent_type
Task(
    description="{Agent-name} task",
    prompt="""
    [Context and mission specific to this invocation]

    You are the {agent-name}. Your instruction file contains your complete workflow.

    For implementation agents (domain, use-case, infrastructure):
    - Read ALL tasks from docs/state/tasks.json
    - Identify YOUR tasks based on your role and keywords
    - Claim ownership autonomously
    - Implement with TDD (test-first approach)
    - Update progress tracking

    For analysis/validation agents (sdd-analyzer, tech-stack-validator, qa-test-generator):
    - Follow your specific workflow in instruction file
    - Generate required output files
    - Validate completeness
    """,
    subagent_type="{agent-name}",  # Use the registered agent name
    model="sonnet"
)
```

**Example Invocations:**

```python
# 1. Invoking domain-agent
Task(
    description="Domain layer implementation",
    prompt="""
    Module: Customer
    Phase: Domain Layer (PHASE 2)

    Implement the domain layer for the Customer module. Read tasks from docs/state/tasks.json,
    identify your tasks (domain layer), and implement following TDD principles.
    """,
    subagent_type="domain-agent",
    model="sonnet"
)

# 2. Invoking tech-stack-validator
Task(
    description="Validate tech stack compatibility",
    prompt="""
    Module: Customer
    Phase: Tech Stack Validation (PHASE 0.5)

    Validate compatibility between Radix UI and Playwright for E2E testing.
    Research GitHub issues and official documentation.
    """,
    subagent_type="tech-stack-validator",
    model="sonnet"
)

# 3. Invoking ui-approval-agent
Task(
    description="Generate UI mockup for approval",
    prompt="""
    Module: Customer
    Phase: UI Approval (PHASE 2.5)

    Generate HTML mockup from shadcn-ui-agent design document.
    Output: docs/ui-mockups/customer-mockup.html
    """,
    subagent_type="ui-approval-agent",
    model="sonnet"
)
```

**Key Points (v4.3 Updates):**
- ✅ **10 agents are registered** as dedicated subagents (have frontmatter)
- ✅ **Always use agent-specific `subagent_type`** (NEVER use "Explore" for registered agents)
- ✅ Implementation agents auto-assign tasks (no orchestrator guidance)
- ✅ Agents update dual tracking (tasks.json + progress.json)
- ✅ Fully autonomous workflow (no FDD approval)
- ✅ Only 1 agent is not a subagent (smoke-test-agent - direct execution)
- ⚠️ `smoke-test-agent` is executed by Orchestrator (Python script, not Task invocation)

---

**Ready to migrate legacy systems with Clean Architecture!** 🚀
