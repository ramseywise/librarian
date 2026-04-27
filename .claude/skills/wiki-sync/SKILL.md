---
name: wiki-sync
description: "Audit wiki taxonomy drift and generate an FE sync report. Compares actual wiki/ directory structure against hardcoded domain lists in the frontend and backend. Read-only by default; --fix applies mechanical changes."
allowed-tools: Read Bash Glob Grep Edit Write
---

You are auditing the Librarian wiki for structural drift between the wiki content and the frontend/backend code that references it. This is a **read-only** operation unless `--fix` is passed.

## Input

`$ARGUMENTS`:
- Empty → full audit, report only
- `--fix` → apply mechanical fixes (add missing entries with defaults); never remove entries without asking

## Step 1 — Discover actual wiki domains

Run:
```bash
ls wiki/
```

Collect all subdirectory names that do NOT start with `_`. These are the **canonical domain list**. Also count pages per domain:
```bash
for d in wiki/*/; do echo "$(ls "$d"*.md 2>/dev/null | wc -l | tr -d ' ') $(basename $d)"; done | sort -rn
```

Note any domain with **< 3 pages** (thin — merge candidate) or **> 20 pages** (thick — split candidate).

## Step 2 — Extract hardcoded domain lists from code

Read each file and extract its domain/color list:

### `app/ui/src/components/TagFilterPanel.tsx`
Find `const DOMAIN_TAGS = [...]`. Extract the array values.

### `app/ui/src/components/WikiNode.tsx`
Find `const DOMAIN_COLORS: Record<string, string> = {...}`. Extract keys.

### `app/ui/src/components/NodeDetailPanel.tsx`
Find `const TAG_COLORS: Record<string, string> = {...}`. Extract domain-tag keys (skip type tags: concept, pattern, decision, project, comparison, reference, conflict).

### `app/ui/src/components/WikiGraph.tsx`
Find the `miniMapColor` callback's inline `colors` record. Extract keys.

### `app/backend/wiki_parser.py`
Find `DOMAIN_TAG_SET = {...}`. Extract values.

## Step 3 — Taxonomy health checks

For each actual wiki domain:

- **Missing from TagFilterPanel** — domain not in DOMAIN_TAGS array
- **Missing from WikiNode** — domain not in DOMAIN_COLORS
- **Missing from NodeDetailPanel** — domain not in TAG_COLORS (domain section)
- **Missing from WikiGraph miniMapColor** — domain not in inline colors record
- **Missing from wiki_parser.py** — domain not in DOMAIN_TAG_SET

For each hardcoded domain NOT found in `wiki/`:

- **Ghost entry** — domain in code but no corresponding `wiki/<domain>/` directory (may be stale)

Structural concerns:
- **Thin domain** — < 3 pages: flag as merge candidate, suggest which domain to fold into
- **Thick domain** — > 20 pages: flag as split candidate, list top-level themes in pages

## Step 4 — Generate color for missing domains (if --fix)

If a domain is missing from a color map and `--fix` is passed, assign a color from this unused-color palette (pick one not already in use):

```
#FF5722, #8BC34A, #00ACC1, #7E57C2, #FFA726, #26A69A, #EC407A, #78909C
```

Pick by visual distinctiveness from the existing palette. Use the same color across all 4 FE color maps for consistency.

## Step 5 — Output report

### Format

```
WIKI-SYNC REPORT — YYYY-MM-DD
==============================

DOMAIN INVENTORY
  actual wiki/ dirs : [list]
  total pages       : N

PAGE COUNT HEALTH
  [THIN]  voice/     — 1 page  (merge into adk?)
  [THICK] langgraph/ — 23 pages (consider splitting)

FE DRIFT
  [MISSING] patterns — not in TagFilterPanel DOMAIN_TAGS
  [MISSING] patterns — not in WikiNode DOMAIN_COLORS
  [GHOST]   llm      — in wiki_parser.py DOMAIN_TAG_SET but no wiki/llm/ directory

EXACT CHANGES NEEDED
  TagFilterPanel.tsx line ~2: add "patterns" to DOMAIN_TAGS array
  WikiNode.tsx: add  patterns: "#E91E63",  to DOMAIN_COLORS
  NodeDetailPanel.tsx: add  patterns: "#E91E63",  to TAG_COLORS
  WikiGraph.tsx miniMapColor: add  patterns: "#E91E63",
  wiki_parser.py DOMAIN_TAG_SET: add "patterns"

VERDICT
  N missing entries across M files
  N ghost entries (stale — verify before removing)
  N structural concerns
```

If everything is in sync:
```
WIKI-SYNC REPORT — YYYY-MM-DD
All clear — wiki structure matches FE code. No changes needed.
```

### If --fix was passed

After printing the report, apply each MISSING entry automatically:
- Add domain to `DOMAIN_TAGS` array in TagFilterPanel.tsx
- Add `domain: "#COLOR"` to DOMAIN_COLORS in WikiNode.tsx
- Add `domain: "#COLOR"` to TAG_COLORS (after the domain section comment) in NodeDetailPanel.tsx
- Add `domain: "#COLOR"` to miniMapColor inline record in WikiGraph.tsx
- Add `"domain"` to DOMAIN_TAG_SET in wiki_parser.py

Do NOT auto-remove GHOST entries — list them and ask the user to confirm before removing.

After applying fixes, re-run Step 2 mentally and confirm all entries are present. Report what was fixed.

## Step 6 — Write plan file (if changes found and --fix not passed)

If there are missing entries and `--fix` was NOT passed, offer to write a plan:

```
Found N issues. Run `/wiki-sync --fix` to apply mechanical fixes automatically,
or I can write a plan to `.claude/docs/plans/wiki-fe-sync-YYYY-MM-DD.md` for review.
```

If the user confirms, write the plan with the exact changes listed under "EXACT CHANGES NEEDED".
