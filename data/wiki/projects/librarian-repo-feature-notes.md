---
title: Librarian Repo Feature Notes
tags: [rag, infra, project]
summary: Dated notes on how the librarian repo's UI panels, skill verbs, retrieval eval gate and code index work and why they are built that way, moved out of CLAUDE.md so it loads lighter each session.
updated: 2026-11-07
sources:
  - CLAUDE.md
  - src/librarian/courses/curriculum.py
  - src/librarian/courses/glossary.py
  - src/librarian/wiki/rename.py
  - src/librarian/tools/codemap/
---

# Librarian Repo Feature Notes

These paragraphs used to sit under "What This Repo Is" in the repo's `CLAUDE.md`. They describe features and why they behave as they do. They are history and orientation, not contract: the rules that bind a session (never write back from the UI, the eval-gate rule, the private-page rule) stay in `CLAUDE.md` as one-line pointers. Each block carries the month it was written.

## Map filter panel (2026-11)

The graph UI's left panel follows the curriculum (`src/librarian/courses/curriculum.py`, `GET /api/graph/curriculum`); cards take their main course's colour. It is an overlay: `data/wiki/` directories remain the canonical domains for tags, MCP and `/lint`. Pages no lesson links appear under "Beyond the curriculum" by directory. Private pages never appear. An empty module means the wiki has no page on that topic.

## Atlas and glossary (2026-11)

Above 1,000 pages the graph opens on an aggregate ring (`app/src/components/atlas/`, drawn on canvas); choosing a sector opens a capped React Flow view of it. `data/glossary.yaml` (hand-edited, served by `src/librarian/courses/glossary.py`) supplies a toggleable layer of term nodes and the hover definitions in lessons. The map's health strip reads the latest telemetry row through `GET /api/wiki/health`. See [[Librarian Graph Explorer]] for the explorer these panels belong to.

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

## See Also
- [[Librarian Graph Explorer]] — extends (the UI the panels and atlas belong to)
- [[Librarian Project]] — related
- [[Wiki Health Metrics]] — related (the telemetry behind the health strip)
