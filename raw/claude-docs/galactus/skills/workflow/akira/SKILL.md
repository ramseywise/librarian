---
name: akira
description: Proactive codebase quality agent. Three modes — kiyoko (yin wanderer, mid-session questions), kaneda (yang scanner, 5 parallel domain subagents, findings doc), dao (道 the path, LLM triage per finding: auto-fix low-blast-radius changes, surface complex ones for review, discard false positives). Trigger on "akira", "quality check", "what did we miss", or any code quality request.
allowed-tools: Bash
---

# /akira

Delegates to `src/akira/` — a LangGraph agent with three subgraphs.

## Parse arguments

- `wander`, `kiyoko`, `?` → `make akira-kiyoko`
- no args, `scan`, `kaneda` → `make akira-kaneda`
- `dao`, `fix` → `make akira-dao`
- path glob (e.g. `src/support_agents/`) → `PYTHONPATH=src uv run python -m src.akira kaneda <path>`

## Run

```bash
make akira-kiyoko   # yin: reads delta, asks questions in chat
make akira-kaneda   # yang: 5 subagents, writes src/akira/findings/findings-{date}.md
make akira-dao      # 道: triages findings, auto-fixes, reverts on test failure, writes summary
```

Findings live at `src/akira/findings/findings-{date}.md` — review, then `make akira-dao`.
Dào applies everything, reverts what breaks tests, and writes a run summary at the top.
