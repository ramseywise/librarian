# Code layout and agent layer

Moved from CLAUDE.md. The code-layout contract: the three import layers are enforced by `make lint-imports`.

## Overview

**Visualization:** Obsidian native graph view (wikilinks = edges). Install the Graph
Analysis community plugin for cosine-similarity edges between pages. Do NOT use the
Streamlit visualizer — it was deprecated and the script has since been removed.

**Agent layer:** `src/librarian/agent/` — `tools.py` is the one registry of read-only tools (typed
params, schema, implementation) that both the chat agent and the MCP server build from, and `loop.py`
is the Anthropic-based chat agent (#96) tool loop, streamed via SSE (`POST /api/chat/stream`) to the React graph UI's chat panel. No
write-back route or tool exists; the UI is read-only over the wiki.

**Feature notes:** the map filter panel, the atlas and glossary, the skill verbs, the retrieval eval
gate and the code index (`src/librarian/tools/codemap/`, MCP `find_symbol`/`repo_map`) are described in the wiki page
[Librarian Repo Feature Notes](data/wiki/projects/librarian-repo-feature-notes.md). Rules that survive from them:

- The graph UI's map panel is an overlay: `data/wiki/` directories stay the canonical domains for tags, MCP and `/lint`. Private pages never appear in it.
- Every wiki verb/skill (`/quiz`, `/gaps`, `/challenge`, `/wiki-weekly`, `/harness-audit`, `/evals-bootstrap`, `/wiki-graph`, `/write`) skips private pages. `/wiki-weekly` is the wiki's report; `/weekly` is the course's. `/wiki-rename` (`librarian.wiki.rename`) rewrites links in `private/` too, reporting those only as a count.
- A ranking change must clear all six `make eval-gate` arms (`sem`, `nofts`, `uniform`, `course`, `graph`, `multihop`). Backlinks are deliberately not a ranking signal; never judge ranking on `sem` alone.

**Skills and unattended jobs:** skills live flat in `.claude/skills/<name>/SKILL.md` and are grouped by product in
`.claude/skills/README.md` (wiki, course, build). A skill keeps the judgement and the order; mechanical steps are
`librarian` verbs. Scheduled work runs headless with `librarian jobs run <name>` (Agent SDK, restricted tools, never
commits). See `.claude/skills/README.md`.

## Code Layout

- `src/librarian/` — the library, installed as the `librarian` package: `config.py` (every path and
  setting; `LIBRARIAN_ROOT` or a `pyproject.toml` above the package locates the repo), `log_config.py`,
  `cli.py`, `accounts/` (users, API keys; the API's `current_user` resolves them),
  `wiki/` (parser, health, telemetry, graph, rename, relinker, common), `retrieval/`
  (index, ranking, search/read API, embeddings), `courses/` (catalog, curriculum, leitner, glossary) and `ingest/`
  (scrapers, ingest gate, manifest, raw lint).
- Also inside the `librarian` package, in three layers (enforced by import-linter, `make lint-imports`):
  entry points `api/` (FastAPI, `librarian api`; routers in `api/routers/`, logic in the core) and `mcp/`
  (FastMCP, `librarian mcp`), independent of each other and using only the public names of
  `librarian.retrieval`; `agent/` (the tool registry and chat loop they share); `tools/` (`slides`, `presenter`, `codemap`, `cartographer`: what builds the media and content; they must not import api/mcp; `mcp`
  imports codemap's tools); and the core below (`courses`, `retrieval`, `wiki`, `ingest`, `accounts`, `db`), which imports none of them.
- `app/` — the React/Vite frontend only (`app/src/`, built to `app/dist/`, served by the API). The single
  `Dockerfile` at the repo root builds it and the API into one image.
- Cartographer (`src/librarian/tools/cartographer/`: session facts, dashboard, weekly sweep) runs as `uv run cartographer`.
