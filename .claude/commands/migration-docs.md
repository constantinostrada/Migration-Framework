# Migration Docs Command

You are querying Context7 MCP for up-to-date documentation on a specific technology.

## Purpose

Use this command to get current documentation before writing code.
This prevents using deprecated APIs or outdated patterns.

## Usage

```
/migration docs [technology]
```

Examples:
- `/migration docs fastapi` - Get FastAPI current patterns
- `/migration docs nextjs` - Get Next.js 14 App Router docs
- `/migration docs pydantic` - Get Pydantic v2 patterns
- `/migration docs sqlalchemy` - Get SQLAlchemy 2.0 async patterns
- `/migration docs react-hook-form` - Get React Hook Form with Zod
- `/migration docs tailwind` - Get Tailwind CSS patterns

## Supported Technologies

| Technology | Query Examples |
|------------|----------------|
| **Backend** | |
| fastapi | "FastAPI dependency injection", "FastAPI middleware" |
| pydantic | "Pydantic v2 validators", "Pydantic model_config" |
| sqlalchemy | "SQLAlchemy 2.0 async", "SQLAlchemy relationships" |
| alembic | "Alembic migrations", "Alembic autogenerate" |
| **Frontend** | |
| nextjs | "Next.js App Router", "Next.js server components" |
| react | "React hooks", "React context" |
| react-hook-form | "React Hook Form register", "RHF with Zod" |
| zod | "Zod schema validation", "Zod refinements" |
| tailwind | "Tailwind forms", "Tailwind components" |
| **Testing** | |
| pytest | "Pytest fixtures", "Pytest async tests" |
| playwright | "Playwright page objects", "Playwright assertions" |

## Step 1: Identify Technology

Parse the user's request to identify which technology documentation they need.

If no technology specified:
```
📚 DOCUMENTACIÓN DISPONIBLE
━━━━━━━━━━━━━━━━━━━━━━━━━━

Uso: /migration docs [tecnología]

Tecnologías soportadas:

Backend:
  • fastapi    - Endpoints, dependency injection, middleware
  • pydantic   - Schemas, validators, serialization
  • sqlalchemy - Models, async sessions, relationships
  • alembic    - Database migrations

Frontend:
  • nextjs     - App Router, server components, routing
  • react      - Hooks, context, patterns
  • react-hook-form - Form handling with validation
  • zod        - Schema validation
  • tailwind   - Styling, components

Testing:
  • pytest     - Unit tests, fixtures
  • playwright - E2E tests, browser automation

Ejemplo: /migration docs fastapi
```

## Step 2: Query Context7

Use the Context7 MCP to query documentation.

**IMPORTANT**: You (the orchestrator) have access to Context7 MCP.
Use it to fetch the relevant documentation.

Query patterns:
```
For fastapi:
  - "FastAPI 0.109 creating endpoints"
  - "FastAPI dependency injection patterns"
  - "FastAPI exception handlers"

For pydantic:
  - "Pydantic v2 BaseModel"
  - "Pydantic field validators"
  - "Pydantic model serialization"

For nextjs:
  - "Next.js 14 App Router"
  - "Next.js server components vs client"
  - "Next.js data fetching"

For sqlalchemy:
  - "SQLAlchemy 2.0 async session"
  - "SQLAlchemy mapped_column"
  - "SQLAlchemy relationships"
```

## Step 3: Present Results

Format the documentation in a useful way:

```
📚 DOCUMENTACIÓN: [TECHNOLOGY]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Versión Actual
[version info from Context7]

## Patrones Recomendados

### [Pattern 1 Name]
```code
[example code from docs]
```

### [Pattern 2 Name]
```code
[example code from docs]
```

## Cambios Importantes vs Versiones Anteriores
- [breaking change 1]
- [deprecated API 1]

## Links Útiles
- [Official docs URL]

💡 Usa esta información al implementar código en la fase CONSTRUCTION.
```

## Step 4: Save to Context (Optional)

If the user wants to save this for reference during construction:

```
¿Deseas guardar esta documentación para referencia?

1. Sí, guardar en docs/reference/[technology].md
2. No, solo mostrar
```

If yes, create the reference file for later use.

## Important Notes

- This command uses Context7 MCP (only available to orchestrator)
- Results are from live documentation, not training data
- Use before implementing each major component
- Particularly useful for: FastAPI, Pydantic v2, Next.js 14, SQLAlchemy 2.0
