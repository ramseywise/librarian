# SANYI.md — change contract

project: librarian
version: 2
last-audit: 2026-07-20

<!-- v2 (2026-07-20): ratified in the owed init interview. Every v1 entry was
     verified against implementation before being rewritten; four of five were
     false as written. Entries marked TARGET describe intent the code does not
     yet meet — the gap is named inline and carried in ## Debt. Nothing here is
     "already true" unless it carries an evidence line.

     2026-07-20 (same day): all four BY-4 records cured — every Buyi entry now
     carries an evidence line backed by a test, and no TARGET markers remain. -->

## 不易 Buyi

### data/raw/ is immutable once written

<!-- v1 said "append-only", which nine ETL writers contradict by design. The
     enforceable invariant is no-mutate, not no-write: ingest creates files,
     nothing rewrites them. A blanket write-block would break every ingest. -->

- paths: data/raw/
- contract: ETL may CREATE new files under data/raw/. No tooling or agent may edit,
  overwrite, or delete an existing raw file. The wiki's provenance chain (every
  page's sources: list) resolves to raw files; mutating one silently invalidates
  every page citing it — a trust failure of the entire KB.
  Creation is explicitly permitted: core/ingest_notion.py, core/ingest_linear.py,
  core/ingest_pdf.py, and the four core/scrape_*.py
  scripts all write into data/raw/ as intended behaviour.
- evidence: .claude/hooks/raw-immutable.sh (PreToolUse, Write|Edit) blocks
  Edit/Write on an EXISTING data/raw/ path and permits creation; absolute and ../
  paths are normalised before the check. tests/hooks/test_raw_immutable_hook.py
  asserts both halves — mutation blocked, and creation permitted for all nine
  core/ ingest target dirs (cured 2026-07-20).

### data/wiki/private/ never leaves the machine

<!-- Two clauses, both now enforced and evidenced. Clause (b) was TARGET-only
     until 2026-07-20; app/ now filters private at every read path.

     2026-07-31: wiki/ moved to data/wiki/; the paths above and every consumer
     (6 absolute-path modules, the MCP server's relative root, wiki-lint.sh, the
     golden dataset) were repointed together. Invariant unchanged — only its
     location. Verified: 15 private-exclusion tests pass, git ls-files
     data/wiki/private returns 0. -->

- paths: data/wiki/private/, app/mcp_server/server.py, app/backend/agent.py
- contract: Pages under data/wiki/private/ (proprietary context, client names,
  internal project detail) are (a) never committed to git, and (b) never
  returned by any read path that can reach a user — MCP tool or chat agent
  tool call. Confidentiality failure if violated.
- evidence: clause (a) — .gitignore#L53 (verified 2026-07-31: git ls-files
  data/wiki/private returns 0). Clause (b) — server.py#_is_private gates
  build_index, _index_needs_rebuild, read_page, list_pages, and
  _resolve_domain_dir (which blocks list_domain + get_domain_briefing from
  addressing private as a domain); read_page returns the not-found message so a
  denial cannot confirm the page exists. tests/app/test_private_exclusion.py
  covers all six paths incl. ../ traversal; verified against the live wiki
  2026-07-20 — 130 pages indexed, 0 private, 5 private pages on disk.
  Chat agent — app/backend/agent.py#_is_private gates both wiki tools the Gemini
  agent can call: _search_wiki's walk and _read_page's ID lookup *and* its
  title-scan fallback (unfiltered, the fallback is a way around the ID check).
  The agent reached data/wiki/ by its own rglob, so the server's gating did not cover
  it; before the cure both tools served private pages into the SSE chat panel.
  Both callers share server.py#is_under_private for path resolution but pass
  their own private root: the server anchors on a relative Path("data/wiki"),
  which under `make api` (cwd=app/) resolves to a nonexistent app/data/wiki/private, so
  binding the agent to the server's own PRIVATE_DIR would read as correct and
  exclude nothing. tests/app/test_agent_private_exclusion.py covers both tools,
  the title fallback, and that cwd-independence as a regression test; its four
  leak cases fail against the pre-cure agent (cured 2026-07-20).

### Secrets never committed, never logged

- paths: .env, .env.example, core/, app/, tools/
- contract: API keys (Anthropic, Google, Notion, Linear) live only in .env
  (gitignored); .env.example carries names, never values; and no key value is
  ever passed to a log call, written to a wiki page, or embedded in data/raw/.
- evidence: commit clause — .gitignore#L2 (.env untracked, only .env.example
  tracked, verified 2026-07-20) + global secrets_scan hook (PostToolUse).
  Logging clause — shared/log_config.py#redact_secrets, a structlog processor that
  drops values for key/token/secret-named fields (walking nested dicts and
  sequences) and masks recognisable Anthropic/Notion/Linear/Google/GitHub key
  formats even under an innocuous field name; installed ahead of the renderer by
  configure_logging(). Called at every process entry point that logs, so the
  processor is installed before the first log call rather than only where the
  MCP server happens to run: app/mcp_server/server.py:42; app/backend/main.py at
  import (uvicorn imports the ASGI app and calls no main() of ours); the seven
  structlog-using core/ scripts (ingest_linear, ingest_notion, ingest_pdf,
  scrape_bookmarks, scrape_claude_docs, scrape_repos,
  scrape_sessions), first statement of each main(); and the tools/ CLIs
  (cartographer, codemap, presenter). tools/presenter/__main__.py previously
  configured structlog itself with no redact_secrets processor — a same-clause
  gap that reads as configured — and now calls the shared configure_logging().
  Entry points that only print() (core/relinker.py, core/lint_raw.py,
  core/manifest.py, core/screenshot.py) bind no logger and are out of scope.
  tests/shared/test_log_redaction.py asserts field-name, nested, value-shape, and
  end-to-end rendered-output cases (cured 2026-07-20).

### Wiki provenance is traceable

<!-- Ratified 2026-07-20. This is the invariant data/raw/-immutability exists to
     protect, and it is the one frontmatter field nothing currently checks. -->

- paths: data/wiki/, .claude/hooks/wiki-lint.sh
- contract: Every wiki page carries a non-empty sources: list, and every entry
  in it resolves to a real data/raw/ file or an external URL. A page asserting
  invented or unresolvable provenance is a trust failure of the KB.
- evidence: .claude/hooks/wiki-lint.sh — sources: is in the required-field loop
  (L23), and each entry is resolved against the filesystem (URLs exempt), with
  empty/inline-empty lists flagged. tests/hooks/test_wiki_lint_sources.py covers
  missing field, unresolvable path, URL, resolvable path, and empty list.
  The same pass fixed a latent `grep -oP` failure that, under `set -e`, aborted
  the hook (exit 2) before the orphan check ran on BSD grep — the environment
  hooks actually get on macOS (cured 2026-07-20).

## 简易 Jianyi

### Wiki page schema

- paths: data/wiki/, .claude/hooks/wiki-lint.sh, CLAUDE.md
- contract: Every page carries the required frontmatter (title, tags, summary,
  updated, sources) with at least one domain tag and exactly one type tag. The
  frontmatter shape is an interface consumed by the parser, MCP server, and
  graph UI — new required fields are schema growth.
- budget: 5 required frontmatter fields (+ optional confidence on raw sources);
  a new required field needs justification and a contract bump
- current: 5 declared / 5 enforced (2026-07-20) — sources: enforced by
  wiki-lint.sh as of the BY-4 cure; see Buyi "Wiki provenance"

### MCP tool surface

<!-- v1 measured server.py alone and recorded 5. codemap_tools.py registers 7
     more via register_codemap_tools(mcp) at server.py:614 — the true surface
     was already 12, i.e. 140% of an unnoticed budget. -->

- paths: app/mcp_server/server.py, app/mcp_server/codemap_tools.py
- contract: Wiki + codemap tools exposed to other agents are an external
  interface; signature changes and additions are drift needing justification.
- budget: 12 tools; additions need justification in the PR
- current: 12 — 5 wiki + 7 codemap (2026-07-20)

### Backend agent graph

- paths: app/backend/agent.py
- contract: Single chat agent with read-only wiki tools, streamed via SSE. New
  tools or multi-agent topology is control-flow growth needing justification. A
  write-back tool would additionally touch the data/raw/-immutability and
  wiki-provenance invariants above and is a Buyi-level change.
- budget: 1 agent, 2 tools; growth needs justification
- current: 1 agent / 2 tools — _search_wiki, _read_page (2026-07-20)

## 变易 Bianyi

### Scrape and ingest configuration

- paths: data/raw/repos/repos.txt
- contract: Which repos get scraped is config, editable without touching
  core/scrape_repos.py.
- evidence: core/scrape_repos.py#load_repos + --repos-file CLI override
  (verified 2026-07-20)

### Model selection and thresholds

- paths: app/backend/
- contract: Model names and retrieval thresholds must come from env/config,
  never literals in handlers (BN-1 otherwise).
- current: MODEL is env-driven (agent.py:14); one live BN-1 at main.py:86
  (2026-07-20) — see Debt

## Migrations

- 2026-07-20: Buyi → Buyi (rescoped) / data/raw/ immutability — v1 declared
  "append-only", which nine ETL writers contradict by design; narrowed to
  "immutable once written" so the enforceable invariant (no mutation of
  existing files) is separated from permitted behaviour (creating new ones).
  (author: ramsey)
- 2026-07-20: all four BY-4 debt records cured — each Buyi entry moved from
  TARGET to an evidence line backed by a test: data/raw/ immutability
  (PreToolUse hook), data/wiki/private/ MCP exclusion (_is_private gate),
  wiki provenance (wiki-lint sources: check), and log redaction
  (structlog processor). Two latent bugs surfaced in the process: the
  MCP server was serving 5 real private pages, and wiki-lint's orphan
  check had been dead on macOS via an unsupported `grep -oP`.
  (author: ramsey)

## Pending

<!-- Empty. All v1 disputes were resolved by verification, not deferral. -->

## Debt

- [BN-1] app/backend/main.py:86 — threshold: float = 0.65 is a literal in a
  handler signature; the Bianyi entry requires env/config sourcing (recorded
  2026-07-20)
- [UN-1] tools/ (presenter, codemap, cartographer) and core/researcher/ have no
  contract entries — ~30 modules unassigned. Deliberate for v2: this interview
  scoped to the wiki/KB core. Revisit if tools/ grows a safety surface
  (recorded 2026-07-20)
