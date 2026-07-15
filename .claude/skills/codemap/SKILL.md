---
name: codemap
description: "Reindex and query the live code-structure index. No args = reindex all configured repos + report symbol/file counts. 'query <term>' = find_symbol lookup. 'map <repo>' = repo_map overview for orientation before working in an unfamiliar repo."
allowed-tools: Read Bash
---

You are maintaining the live structural code index — distinct from the wiki compiler,
this tracks symbols (functions/classes/methods) and file import edges parsed directly
from source with tree-sitter, not LLM-synthesized prose. Never write to `wiki/` from
this skill.

## Input

`$ARGUMENTS`:
- Empty → reindex all repos in `tools/codemap/repos.txt`
- `query <term>` → look up a symbol by name via the `find_symbol` MCP tool
- `map <repo>` → structural overview of one repo via the `repo_map` MCP tool
- `callers <symbol>` → who calls a given symbol, via the `find_callers` MCP tool
- `semantic <query>` → fuzzy/conceptual symbol search via `semantic_find_symbol`
  (only works if the Codemap API was started with `sentence-transformers` installed)

## Step 1 — Check configuration (reindex mode)

Confirm `tools/codemap/repos.txt` has at least one uncommented repo path. If it's
empty, tell the user to add a repo path and stop — do not invent a repo to index.

## Step 2 — Reindex

```bash
make codemap-reindex
```

Report the per-repo counts printed (`parsed`, `skipped`, `removed`, `errors`). If
`errors > 0`, list which files failed to parse (visible in the command's structlog
output) — these are usually syntax errors or non-Python files matched by mistake.

## Step 3 — Query modes

For any query mode, do not shell out — call the MCP tools directly (`find_symbol`,
`repo_map`, `find_references`, `find_callers`, `semantic_find_symbol`,
`get_file_symbols`, `list_repos`). If a tool call fails with an "API unreachable"
message, tell the user to run `make codemap-api` in another terminal first — the query
layer is a separate process from the indexer by design (indexing is meant to run
centrally; querying happens through the API, never by opening the DB file directly).

If `semantic_find_symbol` returns "Semantic search is not available," that means the
running Codemap API doesn't have `sentence-transformers` installed — fall back to
`find_symbol` and tell the user semantic search needs `uv sync --extra api --extra
codemap` (both extras — semantic search piggybacks on the wiki side's existing
`sentence-transformers` dependency rather than declaring its own).

## Output Format

Reindex mode:
```
Indexed <repo>: parsed=<N> skipped=<N> removed=<N> errors=<N>
```

Query mode: relay the MCP tool's formatted output directly — it's already structured
for readability (symbol name, kind, signature, file:line, docstring).

## Centralized indexing (manual setup, not installed by this skill)

`tools/codemap/codemap-cron.sh` exists for unattended reindexing but is **not
registered anywhere** — same reasoning as `tools/cartographer/cartographer-cron.sh`:
scheduling is an environment/hosting decision, not something to do silently from a
skill run. To actually enable it:

**Crontab** (any machine):
```bash
crontab -e
# add:
*/30 * * * * /absolute/path/to/repo/tools/codemap/codemap-cron.sh
```

**launchd** (macOS alternative): write a
`~/Library/LaunchAgents/com.librarian.codemap.plist` with `ProgramArguments` pointing
at the script's absolute path and a `StartInterval` (seconds), then
`launchctl load ~/Library/LaunchAgents/com.librarian.codemap.plist`. Not created by
this skill — write and load it by hand.

**Pointing a querier at a centrally-hosted index**: on the host running the indexer +
API, set `CODEMAP_API_HOST`/`CODEMAP_API_PORT` if binding beyond `127.0.0.1` (e.g.
`CODEMAP_API_HOST=0.0.0.0 make codemap-api`, or `uv run python -m tools.codemap.api`
which reads the same env vars). On every machine that only queries, set
`CODEMAP_API_URL=http://<host>:<port>` before starting Claude Code / the MCP server —
no other config changes needed, since `codemap_tools.py`'s MCP tools are already thin
HTTP clients with no direct DB access.
