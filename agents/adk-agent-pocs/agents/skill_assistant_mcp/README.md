# skill_assistant_mcp

Billy accounting assistant using ADK `SkillToolset` + `McpToolset`.

Identical to `skill_assistant` except all 14 domain tools are served by the
shared MCP server at `mcp_servers/billy/` instead of imported local functions.

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) installed (`brew install uv` on macOS)
- A `GOOGLE_API_KEY` (or Application Default Credentials) in your environment

---

## Setup

Install both the agent and MCP server dependencies once:

```bash
# Agent
cd agents/skill_assistant_mcp
uv sync

# MCP server (one-time install)
cd ../../mcp_servers/billy
uv sync
```

---

## Do I need to start the MCP server manually?

**No.** The MCP server is launched automatically.

`McpToolset` uses `StdioConnectionParams`, which spawns
`mcp_servers/billy` as a child process the moment the ADK agent
receives its first request. The server shuts down when the agent session ends.

You never run `uv run python -m app.main_noauth` yourself during normal use.

---

## Running the agent

### Interactive web UI (recommended for development)

```bash
cd agents/skill_assistant_mcp
adk web .
```

Open [http://localhost:8000](http://localhost:8000), pick **skill_assistant_mcp**,
and start chatting.

### CLI

```bash
cd agents/skill_assistant_mcp
adk run . "list my invoices"
```

---

## Debugging the MCP server separately

If you want to inspect the MCP server in isolation (e.g. run its test suite
or check tool schemas), start it manually in HTTP mode:

```bash
cd mcp_servers/billy
uv run python -m app.main_noauth --http
# → Listening on http://127.0.0.1:8765/mcp/
```

Run its tests:

```bash
cd mcp_servers/billy
uv run pytest
```

---

## Project layout

```
agents/skill_assistant_mcp/
├── agent.py          # Root agent — McpToolset + SkillToolset
├── app.py            # App wrapper (context compaction)
├── prompts/
│   ├── root_agent.txt
│   └── summarizer.txt
├── skills/           # 6 domain skills (invoice, customer, product, email, invite, support)
└── pyproject.toml

mcp_servers/billy/    # Shared MCP server (auto-started by the agent)
├── app/
│   ├── main_noauth.py
│   ├── common.py
│   └── tools/        # 14 Billy stub tools
├── tests/
└── pyproject.toml
```
