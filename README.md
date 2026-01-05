# Universal Migration Framework

A comprehensive framework for migrating legacy systems to modern architectures using AI-assisted development with Claude Code.

## Overview

This framework implements best practices from context engineering research to guide you through migrating legacy systems (COBOL, VB6, legacy Java, etc.) to modern tech stacks.

### Key Features

- **5-Phase Migration Process**: Analysis → Feedback → Design → Construction → Testing
- **Context Preservation**: Hooks and checkpoints prevent context loss during long sessions
- **Congruence Validation**: Automatic detection of inconsistencies between frontend, backend, and database
- **Sub-Agent Architecture**: Specialized agents for analysis, design, and testing
- **MCP Integration**: Context7, Playwright, PostgreSQL, and GitHub MCPs for enhanced capabilities

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python + FastAPI + SQLAlchemy |
| Frontend | Next.js 14+ + TypeScript + Tailwind CSS |
| Database | PostgreSQL |
| Testing | Pytest + Playwright |

## Quick Start

### Prerequisites

- Claude Code CLI installed
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### Installation

1. Clone or navigate to this framework directory
2. Configure MCPs in `.claude/settings.json`:
   - Add your GitHub token
   - Configure PostgreSQL connection string

3. Start a migration:
```bash
claude
```

Then run:
```
/migration start
```

## Commands

| Command | Description |
|---------|-------------|
| `/migration start` | Begin a new migration project |
| `/migration status` | View current progress |
| `/migration restart` | Archive or reset migration |
| `/migration validate` | Check congruence between layers |
| `/migration checkpoint` | Create manual checkpoint |
| `/migration help` | Show help information |

## Migration Phases

### Phase 1: Analysis

Sub-agents extract information from your legacy documentation:
- **business-rules-analyzer**: Extracts business rules (BR-XXX)
- **entity-analyzer**: Identifies data entities and relationships
- **requirements-analyzer**: Extracts functional/non-functional requirements

### Phase 2: Feedback

Interactive validation with the user:
- Checklist for entities, rules, and requirements
- Flow diagrams in Mermaid format
- Suggestions for undocumented features

### Phase 3: Design

Architecture planning with MCP support:
- **backend-architect**: API contracts, architecture (uses Context7)
- **frontend-architect**: Components, pages (uses Context7 + design reference)
- **database-architect**: SQL schema, migrations (uses Postgres MCP)

### Phase 4: Construction

Implementation by the orchestrator (only Claude writes code):
- Clean Architecture + DDD for backend
- App Router + Server Components for frontend
- Automatic git commits during development

### Phase 5: Testing

Comprehensive testing with detailed reports:
- **qa-validator**: API and unit tests
- **integration-tester**: Cross-layer validation
- **e2e-tester**: User flow testing with Playwright

## Project Structure

```
Migration-Framework/
├── CLAUDE.md                    # Orchestrator instructions
├── README.md                    # This file
├── .claude/
│   ├── settings.json            # MCP configuration
│   ├── settings.local.json      # Hooks configuration
│   ├── hooks/                   # Automation scripts
│   │   ├── session-recovery.py
│   │   ├── auto-checkpoint.py
│   │   ├── auto-commit.sh
│   │   ├── pre-write-validation.py
│   │   └── phase-complete-check.py
│   ├── commands/                # Slash commands
│   │   ├── migration-start.md
│   │   ├── migration-status.md
│   │   ├── migration-restart.md
│   │   ├── migration-validate.md
│   │   ├── migration-checkpoint.md
│   │   └── migration-help.md
│   └── agents/                  # Sub-agent definitions
│       ├── business-rules-analyzer.md
│       ├── entity-analyzer.md
│       ├── requirements-analyzer.md
│       ├── backend-architect.md
│       ├── frontend-architect.md
│       ├── database-architect.md
│       ├── qa-validator.md
│       ├── integration-tester.md
│       └── e2e-tester.md
├── docs/
│   ├── input/                   # User-provided documents
│   ├── analysis/                # Analysis phase output
│   │   ├── business-rules/
│   │   ├── entities/
│   │   ├── requirements/
│   │   └── gaps/
│   ├── design/                  # Design phase output
│   │   ├── backend/
│   │   ├── frontend/
│   │   ├── database/
│   │   └── congruence/
│   ├── qa/                      # Testing reports
│   └── state/                   # State management
│       ├── orchestrator-state.json
│       ├── RECOVERY.md
│       ├── decisions-log.md
│       └── phase-summaries/
├── src/                         # Generated code
│   ├── backend/
│   ├── frontend/
│   └── database/
└── archived/                    # Archived migrations
```

## Context Preservation

This framework implements several mechanisms to prevent context loss:

### Hooks

- **session-recovery**: Detects active migrations at session start
- **auto-checkpoint**: Updates state after file modifications
- **auto-commit**: Commits code changes automatically
- **pre-write-validation**: Warns of congruence issues before writing
- **phase-complete-check**: Updates progress when Claude stops

### Recovery System

- `RECOVERY.md`: Human-readable recovery file
- `orchestrator-state.json`: Machine-readable state
- `phase-summaries/`: Detailed summaries per phase
- `decisions-log.md`: Record of user decisions

### Checkpoint Protocol

Checkpoints are created:
- After completing each phase
- After completing an entity/module
- After critical user decisions
- Every 5 file modifications (automatic)
- On manual request (`/migration checkpoint`)

## Congruence Validation

The framework validates consistency between layers:

| Validation | Description |
|------------|-------------|
| Frontend ↔ Backend | Form fields match API schemas |
| Backend ↔ Database | API schemas match table columns |
| Business Rules | Rules implemented in correct layers |
| Data Types | Consistent types across all layers |

Run validation manually:
```
/migration validate
```

## MCP Configuration

### Required MCPs

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-playwright"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:password@localhost:5432/db"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
      }
    }
  }
}
```

## Best Practices

1. **Provide complete documentation**: The better your legacy docs, the better the migration
2. **Validate during feedback**: Don't skip the feedback phase
3. **Use checkpoints**: Create manual checkpoints before complex work
4. **Review congruence**: Run validation before and after construction
5. **Archive before restart**: Always archive before starting a new migration

## Troubleshooting

### Lost Context
1. Check `docs/state/RECOVERY.md`
2. Run `/migration status`
3. Claude will automatically recover from last checkpoint

### Congruence Issues
1. Run `/migration validate`
2. Review `docs/design/congruence/issues.md`
3. Fix issues before continuing

### Hook Errors
1. Check hook scripts in `.claude/hooks/`
2. Ensure Python 3 is available
3. Check file permissions

## Contributing

This framework is designed to be extended. Key extension points:
- Add new sub-agents in `.claude/agents/`
- Add new commands in `.claude/commands/`
- Add new hooks in `.claude/hooks/`

## License

MIT License
