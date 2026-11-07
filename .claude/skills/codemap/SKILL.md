---
name: codemap
description: "Reindex and query the live code-structure index. No args = reindex all configured repos + report symbol/file counts. 'query <term>' = find_symbol lookup. 'map <repo>' = repo_map overview for orientation before working in an unfamiliar repo."
allowed-tools: Read Bash
---

You are maintaining the live structural code index — distinct from the wiki compiler,
this tracks symbols (functions/classes/methods) and file import edges parsed directly
from source with tree-sitter, not LLM-synthesized prose. Never write to `data/wiki/` from
this skill.

## Input

`$ARGUMENTS`:
- Empty → reindex all configured repos (see Step 1)
- `query <term>` → look up a symbol by name via the `find_symbol` MCP tool
- `map <repo>` → structural overview of one repo via the `repo_map` MCP tool
- `callers <symbol>` → who calls a given symbol, via the `find_callers` MCP tool
- `semantic <query>` → fuzzy/conceptual symbol search via `semantic_find_symbol`
  (only works if the Codemap API was started with `sentence-transformers` installed)

Change tracking lives only in the DB: a file is skipped when its hash equals `files.content_hash`.
There is no manifest file to keep or delete; to force a full reparse, rebuild the index DB.

## Step 1 — Check configuration (reindex mode)

The repo list is `src/librarian/tools/codemap/repos.local.txt` (gitignored, the user's own repos)
if it exists, else the tracked `repos.txt` (this checkout only); `$CODEMAP_REPOS_FILE` overrides both.
Paths may use `~` or be relative to the librarian checkout. Confirm the list has at least one
uncommented repo path. If it's empty, tell the user to add one to `repos.local.txt` and stop —
do not invent a repo to index.

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

Unattended reindexing is `uv run librarian jobs run codemap` (it replaces the old
`codemap-cron.sh`). It is **not registered anywhere**: scheduling is an environment/hosting
decision, not something to do silently from a skill run. The crontab line and launchd plist
are in `.claude/skills/README.md`; write and load them by hand.
