# Wiki health: telemetry, lint checks, health numbers

Moved from CLAUDE.md. Lint output order stays BLOCKER, then WARN, then NOTE.

## Telemetry (`data/telemetry/`)

Written by `librarian.wiki.telemetry`, never by hand. Outside `data/wiki/`, so the MCP index, relinker and graph don't see it.

- **Tracked:** `metrics.jsonl` (one row per day, at most 36, from `make wiki-snapshot`) and `operations.jsonl` (`log <op> "<detail>"`: last ~30 entries in full, older ones one row per month). This repo is public: `log` refuses text that names a private page.
- **Gitignored (query history):** `asked.jsonl` (`ask "<topic>"`) and `gaps.md` (`make wiki-gaps`).

## Lint checks

Run lint to find health issues. Check each of the following:

- **Orphan pages** — pages with no backlinks from any other wiki page
- **Missing frontmatter** — pages missing required frontmatter fields
- **Stale pages** — `updated` date older than 60 days (flag for review, don't auto-update; these flags feed `/compact-wiki` as retire/merge candidates)
- **Unresolved conflicts** — pages tagged `conflict` that haven't been resolved
- **Dead wikilinks** — `[[Page]]` references that don't correspond to an existing file
- **Missing summaries** — `summary:` field is empty or generic
- **Orphan raw files** — files in `data/raw/` with no corresponding wiki coverage
- **Untyped links** — `## See Also` entries without a `— type` annotation (>50% untyped = WARN)
- **Unrecognized link types** — typed-syntax annotations whose type is not canonical (WARN)
- **Ontology** — `librarian wiki check` WARNs (never the exit code) on `prerequisite-for` cycles (`ONT001`), `instance-of` declared both ways (`ONT002`) or with a `project` page as the general side (`ONT003`), and near-duplicate pages by title+summary token overlap (`ONT004`, threshold 0.35); public non-tombstone pages only
- **Bridge gaps** — domain pairs with >5 pages each but <3 cross-domain links (NOTE)
- **Stale suggestions** — `data/wiki/_relink_suggestions.md` entries older than 14 days unreviewed
- **Private leak** — a page outside `private/` has a wikilink resolving into `private/` (`make wiki-check`, exit 1; a 3+ word private title in public text is a WARN). A lesson outside `data/courses/private/` that links, embeds or lists a lesson id into it, or names a private wiki page (`[[...]]` or `wiki:`), also blocks, and so does a git-tracked file under either `private/` tree (pre-commit runs `wiki check --tracked-only`). Reports name the public file and line, never the private page

Output a prioritised list: BLOCKER (conflicts, dead links, private leak) → WARN (orphans, stale, untyped) → NOTE (missing coverage, bridge gaps, stale suggestions).

## Health numbers (`make wiki-stats`)

Deterministic. Private pages, tombstones and underscore files are out of every rate; page count is printed but is not a health number. Between the bands reads `watch`. The bands are local heuristics, not research results: see [Wiki Health Metrics](data/wiki/meta/wiki-health-metrics.md) for where each comes from. Average degree counts both ends of a link, so it reads double a links-per-page figure.

| Number | Definition | Healthy | Broken |
|---|---|---|---|
| Orphan rate | pages with no inbound wikilink ÷ pages | < 5% | > 15% |
| Average degree | (inbound + outbound links) ÷ pages | 8–20 | < 4 |
| Main component | pages in the largest connected component ÷ pages | ≥ 80% | < 60% |
| Stale rate | pages with `updated` older than 60 days ÷ pages | report only | none |
| Typed-link rate | typed See Also entries ÷ See Also entries | ≥ 50% | none |
| Stub rate | pages under 200 body words ÷ pages | < 5% | none |

---
