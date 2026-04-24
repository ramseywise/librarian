---
name: Project profile
description: Architecture decisions, repo constraints, and platform facts for the agents monorepo
type: project
---

## Architecture

Agents are **independent processes**, not integrated via a shared layer. Each agent is a standalone CLI tool triggered manually or via cron.

**Why:** Separate entities with different triggers and lifecycles — not nodes in an orchestration graph.

**How to apply:** No LangGraph, no shared state machine, no inter-agent communication. Shared infra limited to: Claude client, config loading, logging, paths. Each agent owns its own models, prompts, and orchestration logic.

Key facts:
- Obsidian vault = curated corpus (output of research agent)
- Raw PDFs (~1GB) in Dropbox, accessed via `.env` path
- Deployment: CLI tools + cron — no web server or API gateway
- Future agents: possibly RAG search, websearch — keep shared core extensible but lightweight
- GitHub repo is private/free-tier constrained; local hooks and pre-commit carry most enforcement
- LangChain is only used in the librarian agent; the rest of the repo uses the bare anthropic SDK

## Repo

- `ramseywise/playground` — private repo on GitHub Free
- Branch protection rulesets require GitHub Pro ($4/mo) or making repo public — not available on current plan
- Claude Code hooks + pre-commit provide local enforcement in the meantime
