# Context7 MCP Server Setup Guide

This guide will help you install and configure the Context7 MCP server for use with Claude Code.

---

## What is Context7?

Context7 is an MCP (Model Context Protocol) server that provides:
- ✅ Official, up-to-date documentation from indexed repositories
- ✅ Real code examples from `llms.txt` files
- ✅ Current API references (avoiding outdated/hallucinated info)

**Supported Technologies**: React, Next.js, FastAPI, SQLAlchemy, Prisma, and many more.

---

## Installation Steps

### Step 1: Install Context7 MCP Server

**Option A: Via npx (recommended)**

Context7 can be run via npx without installation:

```bash
npx -y @upstash/context7-mcp@latest
```

**Option B: Install globally**

```bash
npm install -g @upstash/context7-mcp
```

---

### Step 2: Configure MCP in Claude Code

Claude Code uses MCP servers configured in `mcp_settings.json`.

**Location**: `~/.config/claude-code/mcp_settings.json`

Create or update this file:

```bash
mkdir -p ~/.config/claude-code
```

**Add Context7 configuration:**

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp@latest"
      ],
      "env": {}
    }
  }
}
```

**Alternative (if installed globally):**

```json
{
  "mcpServers": {
    "context7": {
      "command": "context7-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

---

### Step 3: Restart Claude Code

After configuring, restart Claude Code to load the MCP server.

---

### Step 4: Verify Installation

In Claude Code, try using a context7-agent prompt. If configured correctly, the agent will be able to query Context7 for documentation.

**Test query:**

```
Can you query Context7 for FastAPI dependency injection patterns?
```

---

## Manual Configuration (Full mcp_settings.json Example)

If you have other MCP servers, add context7 to the existing configuration:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yourusername/allowed-directory"
      ]
    },
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp@latest"
      ],
      "env": {}
    }
  }
}
```

---

## Using Context7 in the Framework

Once configured, the **context7-agent** will automatically use Context7 MCP when invoked by infrastructure-agent.

**Workflow:**

1. infrastructure-agent identifies a task (e.g., "Implement Customer database layer")
2. infrastructure-agent invokes context7-agent
3. context7-agent queries Context7 MCP for official documentation
4. context7-agent creates context document (e.g., `docs/tech-context/customer-database-context.md`)
5. infrastructure-agent reads context document and implements using official patterns

---

## Supported Technologies (via Context7)

Context7 indexes official documentation for:

**Frontend:**
- React (including React 19)
- Next.js 14, 15+
- Vue, Svelte
- Tailwind CSS
- shadcn/ui

**Backend:**
- FastAPI
- Node.js (Express, NestJS)
- Python (Django, Flask)

**ORMs & Databases:**
- SQLAlchemy 2.0
- Prisma
- Drizzle
- TypeORM
- Mongoose (MongoDB)

**Validation & Forms:**
- Zod
- React Hook Form
- Pydantic v2

**And many more...**

---

## Troubleshooting

### Issue: "context7 not found"

**Solution**: Make sure you're using `npx -y @upwithcj/context7-mcp` in the MCP config, not just `context7`.

### Issue: "MCP server not responding"

**Solution**:
1. Check that Node.js is installed: `node --version`
2. Restart Claude Code
3. Check Claude Code logs for errors

### Issue: "No documentation found for X technology"

**Solution**: Context7 indexes popular technologies. If a technology isn't indexed, the agent will fall back to WebSearch.

---

## Alternative: Use Without Context7

If you cannot configure Context7, the framework will still work:

- context7-agent will use **WebSearch** as fallback
- infrastructure-agent will still research patterns, but from general web sources
- Quality may be lower (risk of outdated patterns)

**Recommendation**: Configure Context7 for best results.

---

## Additional Resources

- **Context7 GitHub**: https://github.com/upwithcj/context7-mcp
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Claude Code MCP Docs**: https://docs.anthropic.com/claude/docs/model-context-protocol

---

## Quick Setup Commands

Copy and paste these commands to set up Context7:

```bash
# 1. Create config directory
mkdir -p ~/.config/claude-code

# 2. Create MCP settings file
cat > ~/.config/claude-code/mcp_settings.json << 'EOF'
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp@latest"
      ],
      "env": {}
    }
  }
}
EOF

# 3. Verify file was created
cat ~/.config/claude-code/mcp_settings.json

# 4. Restart Claude Code (manual step)
echo "✅ Configuration created. Please restart Claude Code."
```

---

**That's it!** Context7 MCP should now be configured and ready to use with the Migration Framework v4.2-CLEAN-ARCH.

**Questions?** Check the troubleshooting section above or refer to the official Context7 documentation.
