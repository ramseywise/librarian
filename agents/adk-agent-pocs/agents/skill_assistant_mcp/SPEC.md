# SPEC.md — skill_assistant_mcp

## Status: implemented

## Overview

`skill_assistant_mcp` is a reimplementation of `skill_assistant` where every
domain tool is served by the shared **Billy MCP server** at
`mcp_servers/billy/` instead of local Python functions.

Everything else is identical to `skill_assistant`:

- Single root agent with `SkillToolset` (5 active domain skills)
- Same model, instruction, and compaction config
- Same skill SKILL.md files (copied verbatim)

---

## Why MCP instead of local tools

| `skill_assistant` (local tools)     | `skill_assistant_mcp` (MCP tools)                     |
|-------------------------------------|-------------------------------------------------------|
| Tools are imported Python functions | Tools are served by a FastMCP process over stdio      |
| Agent package owns the mock data    | Mock data lives in `mcp_servers/billy/` (one place)   |
| `boto3` dependency for Bedrock KB   | No cloud dependency — MCP stub replaces Bedrock       |
| Each new agent copies tools again   | All agents share one server; update once, all benefit |

---

## Directory structure

```text
agents/skill_assistant_mcp/
├── SPEC.md                    # This file
├── README.md                  # Setup and run instructions
├── agent.py                   # Root agent — McpToolset + SkillToolset
├── app.py                     # App wrapper (context compaction, unchanged)
├── prompts/
│   ├── root_agent.txt         # System prompt (unchanged)
│   └── summarizer.txt
├── skills/                    # 5 active domain skills
│   ├── invoice-skill/SKILL.md
│   ├── customer-skill/SKILL.md
│   ├── product-skill/SKILL.md
│   ├── email-skill/SKILL.md
│   └── invitation-skill/SKILL.md
└── pyproject.toml

mcp_servers/billy/             # Shared MCP server (auto-started by the agent)
├── app/
│   ├── main_noauth.py         # STDIO + HTTP entry point
│   ├── common.py              # register_all(mcp)
│   └── tools/                 # 14 Billy stub tools
├── tests/                     # 59 passing unit tests
└── pyproject.toml
```

No `tools/` directory in this agent — all tools are provided by the MCP server.

---

## agent.py

```python
"""skill_assistant_mcp — Billy accounting agent using McpToolset + SkillToolset."""

import pathlib

import yaml
from google.adk import Agent
from google.adk.skills import Frontmatter, Skill
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types
from mcp import StdioServerParameters

_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"
_PROMPTS_DIR = pathlib.Path(__file__).parent / "prompts"
_BILLY_MCP_DIR = str(
    pathlib.Path(__file__).parent.parent.parent / "mcp_servers" / "billy"
)


def _load_skill_from_dir(skill_dir: pathlib.Path) -> Skill:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    _, fm_block, body = text.split("---", 2)
    fm = yaml.safe_load(fm_block)
    return Skill(frontmatter=Frontmatter(**fm), instructions=body.strip())


_skill_toolset = SkillToolset(
    skills=[
        _load_skill_from_dir(_SKILLS_DIR / "invoice-skill"),
        _load_skill_from_dir(_SKILLS_DIR / "customer-skill"),
        _load_skill_from_dir(_SKILLS_DIR / "product-skill"),
        _load_skill_from_dir(_SKILLS_DIR / "email-skill"),
        _load_skill_from_dir(_SKILLS_DIR / "invitation-skill"),
    ]
)

_billy_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=[
                "run",
                "--project",
                _BILLY_MCP_DIR,
                "python",
                "-m",
                "app.main_noauth",
            ],
        ),
    ),
)

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="skill_assistant_mcp",
    description="Billy accounting assistant (MCP tools edition)",
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(
            thinking_budget=8000, include_thoughts=False
        ),
    ),
    instruction=(_PROMPTS_DIR / "root_agent.txt").read_text(encoding="utf-8"),
    tools=[
        _billy_toolset,   # 14 Billy tool stubs via MCP (auto-started)
        _skill_toolset,   # 5 domain skills
    ],
)
```

**Differences from `skill_assistant/agent.py`:**

|             | `skill_assistant`            | `skill_assistant_mcp`                          |
|-------------|------------------------------|------------------------------------------------|
| Tool source | 14 imported Python functions | `McpToolset` (1 entry, auto-started via stdio) |
| Cloud deps  | `boto3` for Bedrock          | None                                           |
| Agent name  | `skill_assistant`            | `skill_assistant_mcp`                          |

---

## pyproject.toml

`boto3` removed (MCP stub replaces Bedrock knowledge base):

```toml
[project]
name = "skill_assistant_mcp"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "google-adk>=1.25.0",
    "google-genai>=1.47.0",
    "pyyaml>=6.0",
]
```

---

## MCP server startup

`McpToolset` with `StdioConnectionParams` spawns `mcp_servers/billy` as a child
process automatically on the first agent invocation — no manual startup needed.

To inspect the server independently:

```bash
cd mcp_servers/billy
uv run python -m app.main_noauth --http   # → http://127.0.0.1:8765/mcp/
uv run pytest                             # 59 tests
```

---

## Next steps

- Run evals: reuse `skill_assistant/eval/` evalset pointing at this agent
- Enable `support-skill` once `fetch_support_knowledge` stub is validated
- Consider HTTP transport (`SseConnectionParams`) for multi-agent deployments
