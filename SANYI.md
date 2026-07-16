# SANYI.md — change contract

project: librarian
version: 1
last-audit: 2026-07-17

<!-- Drafted 2026-07-17 from CLAUDE.md's directory contract and the wiki schema.
     Buyi entries below passed the consequence test on paper; the owner's init
     interview (confirm/extend Buyi, challenge budgets) is still owed. -->

## 不易 Buyi

### raw/ is append-only

- paths: raw/
- contract: Files in raw/ are immutable inputs — never edited or deleted by
  any tooling or agent. The wiki's provenance chain (every page's sources:
  list) breaks if raw files mutate; that is a trust failure of the entire KB.

### wiki/private/ never leaves the machine

- paths: wiki/private/
- contract: Pages holding proprietary context, client names, or internal
  project details are never committed to git or exposed via the public MCP
  tools. Legal/confidentiality failure if violated.
- evidence: .gitignore (wiki/private/ entry)

### Secrets never committed

- paths: .env, .env.example
- contract: API keys (Anthropic, Notion, Linear) live only in .env
  (gitignored); .env.example carries names, never values.
- evidence: global secrets_scan hook (PostToolUse)

## 简易 Jianyi

### Wiki page schema

- paths: wiki/, CLAUDE.md
- contract: Every page carries the required frontmatter (title, tags, summary,
  updated, sources) with at least one domain tag and exactly one type tag.
  The frontmatter shape is an interface consumed by the parser, MCP server,
  and graph UI — new required fields are schema growth.
- budget: 5 required frontmatter fields (+ optional confidence on raw
  sources); a new required field needs justification and a contract bump
- current: 5 required + 1 optional (2026-07-17)

### MCP tool surface

- paths: app/mcp_server/server.py
- contract: Wiki + codemap tools exposed to other agents are an external
  interface; signature changes are JY-3 drift.
- budget: tool additions need justification in the PR
- current: 5 tools (2026-07-17)

### Backend agent graph

- paths: app/backend/agent.py
- contract: Single chat agent with a wiki-search tool, streamed via SSE. New
  tools (e.g. a write-back tool) or multi-agent topology are control-flow
  growth needing justification — write access from the agent would also
  touch the raw/-immutability invariant above.
- budget: 1 agent, 1 tool; growth needs justification
- current: 1 agent / 1 tool (2026-07-17)

## 变易 Bianyi

### Scrape and ingest configuration

- paths: raw/repos/repos.txt
- contract: Which repos get scraped is config, editable without touching
  etl/scrape_repos.py.

### Model selection and thresholds

- paths: app/backend/
- contract: Model names and retrieval thresholds must come from env/config,
  never literals in handlers (BN-1 otherwise).

## Migrations

<!-- Empty at init. Format: - YYYY-MM-DD: <from> → <to> / <entry> — <rationale>. (author: <who>) -->

## Pending

<!-- Disputed assignments park here; enforced as Buyi until resolved. -->

## Debt

- [BY-4] raw/ append-only rule — declared invariant has docs-only enforcement
  (CLAUDE.md); no deterministic guard (a PreToolUse hook blocking Edit/Write
  on raw/ paths would cure this) (recorded 2026-07-17)
