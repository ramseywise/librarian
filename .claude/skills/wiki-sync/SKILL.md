---
name: wiki-sync
description: "Audit wiki taxonomy drift. Compares the data/wiki/ directory structure (the canonical domain list) against the frontend colour map, the backend/MCP domain derivations, and any hardcoded domain list that has crept back in. Read-only by default; --fix applies mechanical changes."
allowed-tools: Read Bash Glob Grep Edit Write
---

You are auditing the Librarian wiki for structural drift between the wiki content and the code that references its domains. This is a **read-only** operation unless `--fix` is passed.

## How domains flow today (2026-10-30)

There is no hand-maintained domain list anywhere in the graph pipeline. The **directories under `data/wiki/` (minus `private/`) are the domain list**:

- `src/librarian/wiki/parser.py` — `_domain_tag_set()` derives the set from disk; `parse_wiki()` sends it to the UI as the payload's sorted `domains` field (graph_update over `/ws` and `GET /api/graph`). `tag_shared_edges()` uses it for `GET /api/graph?edges=all`.
- `src/librarian/retrieval/corpus.py` — `wiki_domains()`, same derivation, for MCP domain filters.
- `src/librarian/courses/catalog.py` — `_load_wiki()` takes each page's domain from its first path component (private and tombstoned pages skipped).
- `app/src/theme/domains.ts` — maps a domain **name to a colour only**. `KNOWN` holds fixed colours for established domains; any other domain gets a deterministic colour from `PALETTE` via `domainColor()`. Nodes, detail panel and minimap take their domain list from the payload and their colours from this module. The filter panel shows payload domains only until the curriculum loads; after that it follows `GET /api/graph/curriculum` (`src/librarian/courses/curriculum.py`), an overlay whose "Beyond the curriculum" group is still derived from directories, and pages a lesson links take `courseColor()` from `COURSE_COLORS`. Course colours are not domain drift.
- `app/src/utils/tagEdges.ts` — derives tag-shared edges client-side with the same rule as `tag_shared_edges()` in parser.py.

So a new wiki directory needs **no code change** to appear, be filterable and be coloured. What can still drift is listed in Step 3.

## Input

`$ARGUMENTS`:
- Empty → full audit, report only
- `--fix` → apply mechanical fixes (add KNOWN colours); never remove entries without asking

## Step 1 — Run the check

```bash
uv run librarian wiki sync-check          # --json for parsing; exit 1 on DRIFT
```

The verb lists the canonical domain list (directories under `data/wiki/` minus `private/`, with page counts) and prints one line per finding:

- `DRIFT`: `parser.py:_domain_tag_set`, `retrieval/corpus.py:wiki_domains` or `wiki/relinker.py:_domain_tag_set` holds a literal list or no longer reads `WIKI_DIR` and excludes `private/`; or a frontend file outside `theme/domains.ts` names three or more domains.
- `THIN` (< 3 pages) and `THICK` (> 20 pages): merge and split candidates. Most domains are past 20 now, so report only the ones that stand out, and suggest a target or the top themes (that part is yours).
- `NOTE`: a domain with no `KNOWN` colour (the palette colours it), or a ghost `KNOWN` colour with no directory.

Do not re-derive any of this by hand. What the verb cannot do is below.

## Step 2 — Read what the code holds (judgement only)

### `app/src/theme/domains.ts`
Only needed to pick a colour for `--fix` (Step 4): read the `KNOWN` values and the `PALETTE`. (`private` is a KNOWN key on purpose: private pages are shown locally with a badge, decision D1.)

### Derivations and the frontend list
`sync-check` already decided these (`parse_wiki()` must still return `domains`; read `parser.py` if a DRIFT line says why it is not enough). Open a flagged file and confirm the finding is a real list and not a test fixture or a one-off use before reporting it as DRIFT.

## Step 3 — Health checks

The verb's `NOTE` lines are the colour findings. A missing fixed colour is a **NOTE, not drift**: `domainColor()` already gives it a stable palette colour, so suggest a `KNOWN` entry only if the palette colour clashes with a neighbour or the domain is large. A ghost `KNOWN` colour is harmless; list it for cleanup.

Yours to add: for a `THIN` domain, a merge target; for a `THICK` one that stands out, the top themes. A `DRIFT` line you could not confirm in Step 2 is not reported as drift.

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
- Add `KNOWN` colours for missing domains in `app/src/theme/domains.ts` (optional; only where the report suggested it).

Do NOT auto-remove ghost entries or rewrite a reintroduced hardcoded list — list them and ask the user. Re-run Step 2 and confirm. Report what was fixed.

## Step 6 — Write plan file (if changes found and --fix not passed)

```
Found N issues. Run `/wiki-sync --fix` to apply mechanical fixes automatically,
or I can write a plan to `.claude/docs/plans/wiki-fe-sync-YYYY-MM-DD.md` for review.
```

If the user confirms, write the plan with the exact changes listed under "EXACT CHANGES NEEDED".
