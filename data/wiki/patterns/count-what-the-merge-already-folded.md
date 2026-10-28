---
title: Count What the Merge Already Folded
tags: [patterns, eval, pattern]
summary: "A cross-source corroboration signal does not need a new pairwise matcher when ingestion already merges sources on a natural key. Count the distinct sources the merge folded into each row, approximate 'independent source' by host and say so, store the count as versioned rows, and treat the floor value as neutral, never as a penalty."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-18-dis249-cross-source-corroboration.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-18-dis249-cross-source-corroboration.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-18-dis249-cross-source-corroboration.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-18-dis249-cross-source-corroboration.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-18-dis249-cross-source-corroboration.md
---

# Count What the Merge Already Folded

In akira (2026-09), a planned "internal quality signal" was blocked because none of its
behavioural inputs had data yet. The triage carved out one piece that needed no traffic: a
deterministic count of how many independent sources list each event. The obvious build was
a pairwise duplicate scan across events. Research showed that scan was unnecessary.

## The load-bearing finding

Ingestion already collapsed sources. An incoming event matched an existing row on a natural
key (venue plus normalised title, see [[Natural Key Without a Discriminator Collapses Rows]]).
A match recorded one occurrence row per distinct `source_url` under the same parent (see
[[Event–Occurrence Split, Added Behind the Old Column]]). So by the time an event existed,
every other source that listed it had already been folded into the occurrences table. The
corroboration signal was already recorded. It just was not being counted anywhere.

The work became arithmetic over what the merge had already done. The matching logic was
already written: the merge and the pairwise classifier
([[Three-Level Duplicate Classification]]) shared one title-normalisation rule.

**Generalisation:** before you build a matcher to detect agreement between sources, check
whether some upstream merge already groups them. If it does, the signal is a `count(distinct)`
over that group, and it inherits the merge's identity rule rather than introducing a second
one that can disagree with it.

## Design decisions that carry over

| Decision | Choice | Why |
|---|---|---|
| What counts as "independent" | Distinct **registrable host** (lowercased, `www.` stripped), not distinct URL | A listing page and a detail page on one site are not two sources. There was no source-registry FK on the occurrence row, so the host was a no-schema proxy. It was **named as an approximation everywhere**: the doc comment, the metric description and the checklist all say "distinct source host", so no downstream reader takes it as more precise than it is |
| Nulls | Filter null and blank URLs before counting | SQL `count(distinct)` silently drops NULLs, but a naive TypeScript mirror (`.trim()` on each element) throws on them. Both sides were specified to filter, so a null-only set still hits the floor of 1 |
| Shape | Raw integer, not a boolean or tier | A tier can be derived later without a schema change, and the raw count holds more information |
| Storage | New versioned table (`is_current` plus a partial unique index), not a column on the parent | A column forces in-place updates. Versioned rows make the sweep idempotent and replayable from scratch |
| Writer trust | Grouped with QC and sampling evidence, service-role only | The table holds evidence about a row's trustworthiness, and nothing displays it yet ([[Data Clusters by Writer and Trust]]) |
| Ranking | **Explicit non-change**: a grep proves no scoring path reads it | No ranking weight is added until the metric has a measured pass rate. The eval is registered UNGATED ([[One Check Shape for Quality Verdicts]]) |

## Floor, not penalty

A count of 1 means "one source recorded so far". It does not mean low quality. A venue's own
official page is often the only correct source for its programme. The written policy for any
future ranking use: the count is a **boost above the floor (2+), never a penalty at the floor**.
Backfilled rows carry a real recorded URL, so their `1` means exactly what a fresh row's `1`
means, and no "unknown provenance" sentinel is needed.

## Ship evidence ahead of its traffic

When this shipped, the catalogue had five published events, and possibly none of them had a
second source. The plan said up front that the metric might measure nothing for a while.
That was correct by design: this is layer-1 evidence, which needs no model, labels or
traffic. The gate on learned layers applies only when the count becomes a ranking weight.
Places were scoped out explicitly. They upserted on source URL and had no natural-key merge,
so there was no cheap group to count. That extension is recorded as a named follow-up, not
silently dropped.

## See Also
- [[Natural Key Without a Discriminator Collapses Rows]] — prerequisite-for (the merge whose groups this counts)
- [[Event–Occurrence Split, Added Behind the Old Column]] — prerequisite-for (the occurrence table being counted)
- [[Three-Level Duplicate Classification]] — alternative-to (the pairwise matcher this avoided re-running)
- [[Relevance Is the Score, Enrichability Is the Gate]] — extends (its corroboration component pointed at an empty column)
- [[Migration Done Means Pushed and Probed]] — instance-of (closed with drift plus a structural schema diff, not just a column probe)
