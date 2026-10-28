---
title: Closed-Vocabulary Parser Silently Drops Invented Types
tags: [patterns, meta, pattern]
summary: "A parser regex that lists the allowed annotation types makes every other type invisible to downstream tooling. The dropped annotation still renders exactly like a parsed one, so authors keep inventing types. In librarian, 481 typed links (40% of all typed annotations) used non-canonical types and were dropped without warning."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-05-typed-graph-retrieval.md
  - data/raw/repos/librarian/.claude--docs--prompts--2026-08-05-typed-graph-retrieval.md
---

# Closed-Vocabulary Parser Silently Drops Invented Types

librarian's wiki types its edges inline (`- [[Page]] — extends`). The canonical
`TYPED_LINK_RE` lists the six allowed types by name. Anything else does not match, so it
never becomes an edge, never reaches lint, and never feeds graph expansion.

The typed-graph research pass (2026-08-05) counted the same syntax again with an open type
capture. It found **481 non-canonical annotations**, against 735 canonical ones:

| Invented type | Count |
|---|---|
| `complements` | 189 |
| `part-of` | 104 |
| `depends-on` | 57 |
| `implements` | 36 |
| `related` | 35 |
| `constrains` | 13 |
| tail (`upgrade-path`, `mitigates`, `feeds`, `used-by`, …) | ~47 |

`complements` alone appeared more often than the canonical `prerequisite-for`.

## Why it stays silent

- **The authoring surface does not show the difference.** In Obsidian a dropped annotation
  looks the same as a parsed one. The author gets no feedback.
- **The writer is an LLM.** During ingest, Claude coins a relation that sounds right
  whenever the six canonical types do not fit well. Nothing pushes back, so the
  vocabulary drifts with every ingest.
- **The counts look healthy.** Edge totals are computed with the same closed regex, so
  the graph is smaller than its authors believe and no metric shows it.

This is schema entropy: the declared schema and the data actually written drift apart,
and the check that should catch it shares the schema's blind spot. Contract systems like
[[SANYI Change-Contract System]] exist to catch exactly this.

## Fix shape

1. **Count with an open capture next to the closed one.** Lint should report
   "annotation-shaped, type not recognised" as a WARN. Never drop it silently.
2. **Decide what each invented type means.** Map frequent synonyms to canonical types,
   or adopt them as recognised-but-inactive. The type exists for lint and display, but
   no traversal consumes it. Same move as [[Closed Judge Vocabulary, Tolerant Parse]]:
   close the vocabulary, but parse leniently through a synonym table.
3. **Separate "recognised" from "retrieval-active."** Only types with a consumer should
   affect behaviour. In the same audit, only 2 of 6 canonical types had a traversal
   consumer. `supersedes` and `contradicts` had 1 and 2 edges, so the typed layer was
   mostly scaffolding.

## See Also
- [[Wiki Graph Engineering — Edge Quality Over Edge Count]] — extends (the edge layer these annotations feed)
- [[Closed Judge Vocabulary, Tolerant Parse]] — extends (the same close-but-parse-leniently fix for an LLM writer)
- [[Typed-Graph Retrieval Ablation]] — prerequisite-for (the census that surfaced the drop)
- [[Silent Failure Catalogue]] — instance-of
