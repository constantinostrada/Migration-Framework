# Migration Framework Documentation

This directory contains modular documentation for the Migration Framework v4.3.

## 📚 Documentation Structure

The framework documentation is split into modular files for optimal performance:

### Main Documentation
- **[../../CLAUDE.md](../../CLAUDE.md)** (23k chars)
  - Framework overview and principles
  - Architecture and agent summary
  - Quick references with navigation links

### Detailed Guides
1. **[migration-phases.md](./migration-phases.md)** (47k chars)
   - Complete PHASE 0-5 workflows
   - Step-by-step instructions with code examples
   - All validation and verification steps

2. **[agent-invocation-guide.md](./agent-invocation-guide.md)** (3k chars)
   - How to invoke each of the 11 specialized agents
   - Complete invocation matrix
   - Special cases and patterns

## 🧭 Navigation Flow

```
CLAUDE.md
    ↓
    → When executing migration: Read migration-phases.md
    ↓
    → When invoking agents: Read agent-invocation-guide.md
    ↓
    → When implementing: Read specific agent file in ../agents/
```

## 📊 Performance Benefits

**Before modularization:**
- Single CLAUDE.md: 69,206 chars (173% over 40k limit)
- Performance warning: ⚠️ Large file impacts performance

**After modularization:**
- CLAUDE.md: 23,964 chars (60% of limit)
- Details loaded on-demand
- No performance warnings ✅

## 🔍 What's In Each File

### CLAUDE.md
- Overview & What's New in v4.3
- Core Principles
- Orchestrator Autonomy Rules (when to interact with user)
- Architecture Overview (11 agents)
- File Structure
- Migration Workflow → Quick reference
- FDD Document
- Critical Rules
- Success Metrics
- Tools Reference
- Agent Invocation → Quick reference
- Documentation Map (navigation guide)

### migration-phases.md
- PHASE 0: SDD Analysis
- PHASE 0.5: Tech Stack Validation (v4.3 - NEW)
- PHASE 0.7: Task Generation
- PHASE 0.8: Test Specification (TDD)
- PHASE 1: Contract Generation
- PHASE 2-3: Implementation (Domain → Application → Infrastructure)
- PHASE 4.5: Smoke Tests (v4.3 - NEW)
- PHASE 4: E2E QA with Strategic Decisions
- PHASE 5: Final Validation & Delivery
- Complete example flows

### agent-invocation-guide.md
- Agent architecture explanation
- Complete invocation matrix (11 agents)
- Standard invocation patterns
- Special cases (context7-agent, e2e-qa-agent, smoke-test-agent)
- Why `/agents` command doesn't show all agents

## 🚀 For Developers

When adding new content:
- **Architecture/principles** → Add to CLAUDE.md
- **New phases/workflows** → Add to migration-phases.md
- **New agents** → Add to agent-invocation-guide.md + create agent file in ../agents/
- Keep CLAUDE.md under 40k chars for optimal performance

## 📖 Related Files

- **Agent Instructions**: `../agents/*.md` (11 files)
- **Slash Commands**: `../commands/*.md`
- **Schemas**: `../../docs/schemas/*.ts`
