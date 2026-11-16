# Librarian Repo Feature Notes

> Repo documentation, formerly the wiki page `projects/librarian-repo-feature-notes.md`; moved here on 2026-11-10 when `projects/` went private.

These paragraphs used to sit under "What This Repo Is" in the repo's `CLAUDE.md`. They describe features and why they behave as they do. They are history and orientation, not contract: the rules that bind a session (never write back from the UI, the eval-gate rule, the private-page rule) stay in `CLAUDE.md` as one-line pointers. Each block carries the month it was written.

## Map filter panel (2026-11)

The graph UI's left panel follows the curriculum (`src/librarian/courses/curriculum.py`, `GET /api/graph/curriculum`); cards take their main course's colour. It is an overlay: `data/wiki/` directories remain the canonical domains for tags, MCP and `/lint`. Private pages never appear. An empty module means the wiki has no page on that topic.

Since 2026-11-10 the panel has a Domain / Wiki switch. **Domain** is a tree: course → module → wiki page, one row per course (the six pillars). A course is an area: `src/librarian/wiki/areas.py` maps each wiki directory to one area named after a course (programming, data-analytics, data-science and data-engineering → one area each; llm, rag, eval, memory, frameworks → Generative AI; prompting, context, harness, loop, graph, infra, mcp, multimodal → AI Engineering). Under a course sit its modules, each opening to the pages its lessons link (a page row opens that page on the map), and a "Not yet in a lesson" row: the pages of the area no lesson links (`gap:<area>`, or `beyond:<dir>` for a directory in no area), so a course's coverage gaps are one click away. The internal directories (patterns, meta, projects) and interview prep live under `private/` and are not on the map. A directory in no area is listed as its own row after the domains, so nothing is hidden and the table never needs a frontend change; `wiki sync-check` reports such a directory as a NOTE. A page's domain is its top-level directory, so `frameworks/adk/` and `frameworks/langgraph/` are one `frameworks` directory on the map. **Wiki** is three folding sections: the wiki directories, the glossary terms (a term lights the pages that mention it) and the topic tags; page-type tags are not offered as filters. The sidebar no longer carries a list view or the health strip. There is no "Not in a course" sector any more; the old `#/map/course/...` and `#/map/area/...` links open as `domain`, and an old `#/map/domain/<dir>` link now opens the domain atlas.

## Atlas and glossary (2026-11)

Above 1,000 pages the graph opens on an aggregate ring (`app/src/components/atlas/`, drawn on canvas); choosing a sector opens a capped React Flow view of it. The ring's sectors follow the panel's grouping (Domain: courses in domain order, then loose directories by size; Wiki: directories by size). Once the curriculum has loaded, a page no lesson links is drawn as a faint spike, and sector labels, tooltips and the list view carry a "k not yet in a lesson" count, so the gaps the panel lists are visible on the ring itself. `data/glossary.yaml` (hand-edited, served by `src/librarian/courses/glossary.py`) supplies the Wiki view's term filters, the map search's term hits and the hover definitions in lessons; terms are not drawn on the map. The map's health strip reads the latest telemetry row through `GET /api/wiki/health`.

## Verbs (2026-11)

The wiki skills are `/quiz`, `/gaps`, `/challenge`, `/wiki-weekly`, `/harness-audit`, `/evals-bootstrap`, `/wiki-graph` (hubs, bridges and consensus clusters, from `make wiki-graph`) and `/write` (a cited outline from the wiki; `/write-chapter` is for course chapters). The `ingest-reviewer` agent checks what an ingest wrote against its raw source. `/wiki-weekly` is the wiki's report; `/weekly` is the course's. All eight skip private pages. `/wiki-rename` (`librarian.wiki.rename`) renames a page and rewrites its links, in `private/` too, reporting those only as a count.

## Retrieval evals (2026-11)

`make eval-gate` runs four gated arms, and a ranking change must clear all of them:

- `sem`: hand-picked questions whose answers are mostly hub pages.
- `nofts`: the degraded path.
- `uniform`: questions on uniformly sampled wiki pages.
- `course`: lesson search.

Search blends BM25 and similarity equally. Backlinks are deliberately not a ranking signal; `sem` alone rewards them, so ranking must never be judged on it alone.

## Code index (2026-07)

`src/librarian/tools/codemap/` is a tree-sitter-based structural index (symbols, import edges) over source repos, separate from the wiki-compile pipeline. It is exposed through MCP tools (`find_symbol`, `repo_map`, `find_references`, and others) alongside the wiki tools. The design is in `.claude/docs/plans/codemap-code-index.md`.
