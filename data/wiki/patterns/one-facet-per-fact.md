---
title: One Facet Per Fact
tags: [patterns, prompting, eval, pattern]
summary: An enrichment vocabulary where one tag carries several kinds of fact (type, time, companion, mood) cannot be measured or fixed; give each kind of fact its own facet, derive the facets a rule can compute instead of asking the model, stamp per-value provenance, and accept on per-facet precision before coverage.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-26-venue-tag-facets-proposal.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-26-venue-tag-facets-proposal.md
  - data/raw/claude-docs/akira/docs/research/2026-09-27-venue-enrichment-facet-map.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-27-venue-enrichment-facet-map.md
  - data/raw/claude-docs/akira/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/akira/docs/research/2026-09-27-venue-moment-coverage.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-27-venue-moment-coverage.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-27-venue-moment-coverage.md
---

# One Facet Per Fact

Found while reviewing a venue-enrichment dataset for an events-discovery product (repo
akira, 2026-09). The venue "vibe" vocabulary had grown into a single tag list that mixed
moods (`chill`, `lively`), venue types, times of day (`late_night`) and companions
(`date`, `families_with_kids`). Every quality question about it was unanswerable, because
a wrong tag could be wrong in four different ways.

## The rule

**A vibe adjective never encodes a type, a time or a companion.** Each kind of fact gets
its own facet with its own vocabulary, its own evidence rule and its own measurement:

| Facet | Holds | Written by |
|---|---|---|
| vibe | atmosphere only | model, quote-grounded |
| `audience_fit` | who it suits (companions) | model, needs audience-specific evidence |
| `time_fit` | when it works | **rule**, derived from `opening_hours` — never emitted |
| `offer` | what is on offer | model, controlled but growable vocabulary |

The decision record called this one facet per fact. Its consequences are concrete:

- **Derive what a rule can compute.** Across three prompt versions the model put a time
  tag on at most 6% of rows. Opening hours already carried the fact. `time_fit` is
  therefore derived by conservative rules (skip seasonal and public-holiday rules;
  `late_night` needs at least two day rules that qualify) and stamped
  `time_fit_source = {hours, rule_version}`.
- **Per-value provenance.** Every facet value carries `source` (`model` / `rule` /
  `osm`), so a precision number can be split by writer. This is the
  [[Data Clusters by Writer and Trust]] idea applied inside one column.
- **Controlled but growable.** `offer` values outside the vocabulary are dropped and
  counted, and a value is promoted by hand once it has been dropped at least 5 times.
  The vocabulary grows from evidence, not from the prompt author's guesses.
- **Read old rows through a map, never rewrite them.** v0 rows are translated by a
  v0→v1 map at the feed seam. The v0 vocabulary stays for parity, and only the version
  constant that actually stamps the changed prompt is bumped (the probe version, not the
  global enrichment version). See [[Frozen Version Stamps on Logged Results]].
- **Don't edit a GATED fixture corpus on speculation.** The facet split is a proposal
  until measured. The gated fixtures keep their current labels until then.

## Evidence rules that fell out of the split

- Format words ("bar", "club") are never neighbourhood evidence.
- "Since 1898" dates the business, not the building, so it is not heritage evidence.
- `families_with_kids` needs kids-specific evidence. A generic "welcoming" doesn't count.

## Acceptance: precision first, coverage second

The acceptance metric is **precision per facet on a labelled stratified sample**.
Coverage comes second, because on coverage alone "a system more willing to assert
things scores higher". The dataset review showed why this matters: rule lanes and model
lanes agreed with each other often, but agreement is not accuracy. Kind- and column-based
rules over-fired 2–7× with precision below 0.3, while keyword rules had precision
0.6–0.8 and under-fired. Cheaper probe models invented attributes on 60–75% of rows.

## Coverage is per moment edge, not per tag

A tag that is never emitted silently flattens a mood: a "romantic" search was scored as
"chill" through the adjacency map, and nothing failed. Count coverage per moment map
edge. Two more gaps showed up:

- **Discovery gap vs enrichment gap.** Some cells are empty because the venues were never
  discovered, and re-enriching can't add rows.
- **Moods that don't discriminate.** The same venues topped 4 of 6 mood cells.

No tag carried time at all (0 rows had `time_fit`), which is what pushed time into its
own derived facet. See [[Starved Tag Triage: Edge, Prompt, or Supply]] for diagnosing why
an individual tag is empty.

## See Also
- [[Graded-Uncertainty Enrichment Contract]] — extends (the output contract each facet value obeys)
- [[Evidence-Labelled Generation with Deterministic QC]] — extends (per-value traceability, here split by facet)
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — complements (diagnosing an empty value inside one facet)
- [[One-Sided Label Control]] — prerequisite-for (the per-facet precision labels this acceptance needs)
- [[Write-Only Fields and the Reader Map]] — related (`audience_fit` existed but no dimension read it)
- [[Kiez Project]] — instance-of
