---
title: Wiki Health Metrics
tags: [meta, reference]
summary: "The six deterministic numbers this wiki tracks and what each band means; every threshold is a local heuristic, some taken from second-brain-os's uncited docs and the rest chosen here, and average degree counts both ends of a link, so it reads double second-brain-os's figure."
updated: 2026-11-05
sources:
  - data/raw/web/2026-11-05-second-brain-os-graph-metrics.md
  - data/raw/web/2026-11-05-graph-health-comparators.md
  - data/raw/web/2026-11-05-citation-check-corrections.md
---

# Wiki Health Metrics

The definitions, the bands marked as this repo's, and every snapshot number on this page come from this repo's code and
telemetry (`data/telemetry/metrics.jsonl`), not from the raw sources listed above.

`core/wiki_telemetry.py` (`make wiki-stats`) computes these with no model calls. Private pages, tombstones
and underscore files are left out of every rate. Page count is printed, but it is not a health number. Rows
go to `data/telemetry/metrics.jsonl`, outside `data/wiki/`, so the index and graph never see them.

| Number | Definition | Healthy | Broken | Where the band comes from |
|---|---|---|---|---|
| Orphan rate | pages with no inbound wikilink ÷ pages | < 5% | > 15% | second-brain-os |
| Average degree | (inbound + outbound links) ÷ pages | 8–20 | < 4 | floor second-brain-os, doubled; band chosen here |
| Main component | pages in the largest connected component ÷ pages | ≥ 80% | < 60% | 80% second-brain-os; 60% this repo |
| Stale rate | pages with `updated` older than 60 days ÷ pages | report only | none | this repo; [[Evidence-Driven Wiki Compaction]] uses it as a candidate list |
| Typed-link rate | typed See Also entries ÷ See Also entries | ≥ 50% | none | this repo's lint rule; see [[Wiki Graph Engineering — Edge Quality Over Edge Count]] |
| Stub rate | pages under 200 body words ÷ pages | < 5% | none | this repo |

## These are heuristics

None of these thresholds is a research result, and no primary source was found for any orphan, degree or
component threshold.

[second-brain-os](https://github.com/undefined-ui/second-brain-os) (`docs/05-graphs/metrics.md`, commit 53aea82) gives
these as its own statements, with no citation or derivation: under 5% orphans healthy, over 15% broken, main component
about 80%, and degree in links per page, where below two is barely connected, three to eight is the working range, and
"much above ten" suggests decorative linking. They are kept here as a convention to watch against, nothing more.

Other numbers that sit beside them are not from that project:

- **Typed links:** the 50% line comes from this repo's lint rule. second-brain-os advises typing roughly one link in
  five, counted over all links, not See Also entries.
- **Component floor and stub rate:** the 60% floor and 5% stub line were chosen here. No such figures were found in
  that repo.
- **Stale:** 60 days is this repo's. second-brain-os uses ninety days, on concept pages only.

## Degree units

second-brain-os counts each link once. This wiki counts both ends, so its number reads double: the 2026-11-05 value of
13.93 is about 7 links per page, inside second-brain-os's range. An earlier version of this page said that range fitted
this wiki badly. That compared the two without converting, and it was wrong.

In second-brain-os's units the 8–20 band is 4–10, and the floor of 4 is its "below two". The band was picked by judgement
after seeing page degree with median 11 and p5–p95 of 5–34. Those are per-page figures and 8–20 is no percentile of them.

## Stub length

The 200-word line replaced a 120-word guess from this wiki's own plan. It was set from the same snapshot, where body
words had p1 of 191 and median 600. second-brain-os's stub lines are shorter, at about 40 and about 80 words. A band read
off one snapshot describes the wiki as it was, not what good looks like, so change it only on evidence from later snapshots.

## Comparators, not standards

Published figures give a sense of scale. None was designed as a health target for a personal wiki:

- **Karpathy's gist** includes a check for orphan pages and sets no threshold.
- **Wikipedia orphans:** roughly 15% of articles across all language editions (Arora, West, Gerlach, ICWSM 2024) and 4.7%
  on English Wikipedia (Wikimedia, last revised 2022), where about half of the 299k are disambiguation pages. The
  second-brain-os 5% and 15% sit close to these, but nothing shows they came from them.
- **Wikipedia's own rule** is per article: one relevant inbound link removes the orphan tag, and three or more help
  readers reach the page.
- **The web** in Broder et al. (Computer Networks, 2000): treated as undirected, a giant component of 186 million nodes,
  91% of the crawl, with a strongly connected core of about 28%.

## Baseline

At the 2026-11-05 snapshot, with 1,239 pages: orphan rate 0.6%, average degree 13.93, main component 100%, stale 1.9%,
typed links 89.4%, stub rate 1.3%. All sit in their healthy bands, which says little: some bands were set after seeing
this same data.

## Open questions

- Whether any of these numbers predicts a retrieval or answer-quality problem here. The second-brain-os claim that low
  component share makes answers quietly incomplete is untested on this wiki.

## See Also
- [[Wiki Graph Engineering — Edge Quality Over Edge Count]] — prerequisite-for (what the graph's edges are worth)
- [[Karpathy LLM Wiki Pattern]] — prerequisite-for (the lint stage these numbers make repeatable)
- [[Evidence-Driven Wiki Compaction]] — extends (acts on stale and orphan signals)
- [[Knowledge Base Recompile Stage]] — related (why a compiled wiki needs upkeep)
- [[Graph Topology Primitives]] — related
