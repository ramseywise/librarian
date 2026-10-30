---
name: wiki-sync
description: "Audit wiki taxonomy drift. Compares the data/wiki/ directory structure (the canonical domain list) against the frontend colour map, the backend/MCP domain derivations, and any hardcoded domain list that has crept back in. Read-only by default; --fix applies mechanical changes."
allowed-tools: Read Bash Glob Grep Edit Write
---

You are auditing the Librarian wiki for structural drift between the wiki content and the code that references its domains. This is a **read-only** operation unless `--fix` is passed.

## How domains flow today (2026-10-30)

There is no hand-maintained domain list anywhere in the graph pipeline. The **directories under `data/wiki/` (minus `private/`) are the domain list**:

- `app/backend/wiki_parser.py` — `_domain_tag_set()` derives the set from disk; `parse_wiki()` sends it to the UI as the payload's sorted `domains` field (graph_update over `/ws` and `GET /api/graph`). `tag_shared_edges()` uses it for `GET /api/graph?edges=all`.
- `app/mcp_server/server.py` — `_domains()`, same derivation, for MCP domain filters.
- `app/backend/courses.py` — `_load_wiki()` takes each page's domain from its first path component (private and tombstoned pages skipped).
- `app/frontend/src/theme/domains.ts` — maps a domain **name to a colour only**. `KNOWN` holds fixed colours for established domains; any other domain gets a deterministic colour from `PALETTE` via `domainColor()`. The filter panel, nodes, detail panel and minimap all take their domain list from the payload and their colours from this module.
- `app/frontend/src/utils/tagEdges.ts` — derives tag-shared edges client-side with the same rule as `tag_shared_edges()` in wiki_parser.py.

So a new wiki directory needs **no code change** to appear, be filterable and be coloured. What can still drift is listed in Step 3.

## Input

`$ARGUMENTS`:
- Empty → full audit, report only
- `--fix` → apply mechanical fixes (add KNOWN colours); never remove entries without asking

## Step 1 — Discover actual wiki domains

```bash
ls -d data/wiki/*/ | xargs -n1 basename | grep -v '^private$'
for d in data/wiki/*/; do echo "$(find "$d" -name '*.md' | wc -l | tr -d ' ') $(basename $d)"; done | sort -rn
```

These names are the **canonical domain list**. Note any domain with **< 3 pages** (thin — merge candidate) or **> 20 pages** (thick — split candidate).

Confirm the backend agrees (it should, by construction):
```bash
uv run python -c "import sys; sys.path.insert(0, 'app'); from backend.wiki_parser import parse_wiki; print(parse_wiki()['domains'])"
```

## Step 2 — Read what the code holds

### `app/frontend/src/theme/domains.ts`
Extract the keys of `const KNOWN: Record<string, string> = {...}` and the `PALETTE` values. (`private` is a KNOWN key on purpose: private pages are shown locally with a badge, decision D1.)

### Derivation functions (confirm they still derive, not list)
- `app/backend/wiki_parser.py` — `_domain_tag_set()` must read `WIKI_DIR` at call time and exclude `private`; `parse_wiki()` must return `domains`.
- `app/mcp_server/server.py` — `_domains()`, same rule.
- If either has been replaced by a literal set/list, that is **DRIFT**.

### Remaining hardcoded lists
- `core/relinker.py` — `_domain_tag_set()` (discounts domain tags when scoring shared tags) must read `WIKI_DIR` at call time and exclude `private`, like the two above. A literal set here is **DRIFT**.
- Regression sweep — no other domain list should exist in the frontend:
  ```bash
  P='"(rag|langgraph|adk|infra|memory)"|^\s*(rag|langgraph|adk|infra|memory)\s*:'
  grep -cE "$P" app/frontend/src/theme/domains.ts   # positive control: must be > 0
  grep -rnE "$P" app/frontend/src --include='*.ts' --include='*.tsx' \
    | grep -v -e theme/domains.ts -e __tests__
  ```
  The pattern catches both quoted array entries and unquoted record keys. Any array or record naming three or more domains outside `theme/domains.ts` is **DRIFT** (a list was reintroduced).

## Step 3 — Health checks

For each actual wiki domain:
- **No fixed colour** — not a key in `KNOWN`. This is a **NOTE, not drift**: `domainColor()` already gives it a stable palette colour. Suggest adding a KNOWN entry only if the palette colour clashes with a neighbour or the domain is large.

For each name in code but with no `data/wiki/<name>/` directory:
- **Ghost KNOWN colour** — harmless (unused), NOTE; list for cleanup.

Structural:
- **DRIFT** — a derivation replaced by a literal, or a hardcoded domain list found by the regression sweep.
- **Thin domain** (< 3 pages) — merge candidate; suggest a target domain.
- **Thick domain** (> 20 pages) — split candidate; list the top themes.

## Step 4 — Colour for new KNOWN entries (if --fix)

Pick a colour visibly distinct from every existing `KNOWN` value and from `PALETTE` (the fallback for unlisted domains). Add it to `KNOWN` only — no other file holds domain colours.

## Step 5 — Output report

```
WIKI-SYNC REPORT — YYYY-MM-DD
==============================

DOMAIN INVENTORY
  data/wiki/ dirs (excl. private) : [list]
  parse_wiki() domains            : [list]  (must match)
  total pages                     : N

PAGE COUNT HEALTH
  [THIN]  voice/     — 1 page  (merge into adk?)
  [THICK] patterns/  — 63 pages (consider splitting)

DRIFT
  [DRIFT] TagFilterPanel.tsx:3 — hardcoded domain array reintroduced

NOTES
  [NOTE] harness — no fixed colour in theme/domains.ts KNOWN (fallback palette colours it)
  [NOTE] voice   — ghost KNOWN colour (no data/wiki/voice/)

EXACT CHANGES NEEDED
  (optional) theme/domains.ts KNOWN: add  harness: "#8D6E63",

VERDICT
  N drift findings, N warnings, N notes, N structural concerns
```

If everything is in sync:
```
WIKI-SYNC REPORT — YYYY-MM-DD
All clear — domains derive from disk everywhere; no drift.
```

### If --fix was passed

After the report, apply the mechanical fixes:
- Add `KNOWN` colours for missing domains in `app/frontend/src/theme/domains.ts` (optional; only where the report suggested it).

Do NOT auto-remove ghost entries or rewrite a reintroduced hardcoded list — list them and ask the user. Re-run Step 2 and confirm. Report what was fixed.

## Step 6 — Write plan file (if changes found and --fix not passed)

```
Found N issues. Run `/wiki-sync --fix` to apply mechanical fixes automatically,
or I can write a plan to `.claude/docs/plans/wiki-fe-sync-YYYY-MM-DD.md` for review.
```

If the user confirms, write the plan with the exact changes listed under "EXACT CHANGES NEEDED".
