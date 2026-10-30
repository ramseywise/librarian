---
title: "Starved Tag Triage: Edge, Prompt, or Supply"
tags: [patterns, prompting, eval, pattern]
summary: When an enrichment tag is (nearly) never assigned, separate four causes before fixing anything — a missing scoring edge, a prompt that suppresses it (verbatim-quote grounding starves subjective atmosphere tags), a vocabulary gap, or a supply gap where the corpus simply doesn't carry it — and measure reach with the scorer's own tier function, not direct counts.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-25-dis392-s2-vibe-supply.md
  - data/raw/claude-docs/akira/docs/research/2026-09-25-dis392-s2-vibe-supply.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-25-dis392-s2-vibe-supply.md
  - data/raw/claude-docs/akira/docs/research/2026-09-25-dis392-s3-reasoning-vocabulary-remine.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-25-dis392-s3-reasoning-vocabulary-remine.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-25-dis392-s3-reasoning-vocabulary-remine.md
  - data/raw/claude-docs/akira/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis385-edge-registry.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis392-s2-vibe-supply.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis392-s2-vibe-supply.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis392-s2-vibe-supply.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis392-s2-vibe-supply.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis392-s2-vibe-supply.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis392-b130-s3.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis392-b130-s3.md
---

# Starved Tag Triage: Edge, Prompt, or Supply

From a series of research slices on why some venue "vibe" tags were starved in an
events-discovery product (repo akira, 2026-09). On a 200-row probe corpus, 24 tags made
376 assignments. `romantic` and `offbeat` had 0, `high_energy` had 3, and 128 of the 376
assignments sat on tags no mood reached directly. The issue proposed adding mood edges.
That would have fixed almost nothing.

## Measure reach with the scorer's own function

The issue's "eligible supply" was a **direct-tier** count. Replicating the scorer's
actual `tierFor()` showed the adjacency graph already reached 25 of 26 tags at some tier.
Only `outdoor` (17 assignments) was unreachable from any mood, and adding its edge moved
coverage by just 0.1–1.3%. Direct counts overstate starvation whenever scoring has
fallback tiers. Count with the code that consumes the tag, not with a simpler stand-in.

## The four causes

1. **Missing edge.** The tag is assigned but no consumer reaches it. Fix: the edge. (Rare
   here: one tag.)
2. **Prompt suppression.** The probe prompt required a verbatim `evidence_quote` for every
   vibe tag, and it explicitly told the model not to infer `romantic` from venue kind.
   Atmosphere words that venue copy rarely states literally were systematically
   under-produced. Easily quoted factual tags (`local`, `community_driven`,
   `traditional`) dominated. The sharpest case was `high_energy`: the corpus had real
   nightlife supply (12 `club`, 6 `techno`, 5 `nightclub`, 13 `party` descriptors), but
   the model chose the softer, quotable `lively`.
3. **Vocabulary gap.** The concept appears in the model's reasoning text, but no tag
   exists for it.
4. **Supply gap.** The tag exists, but the corpus doesn't carry the fact. No prompt or
   edge fixes that. It needs new sources (see [[One Facet Per Fact]] on discovery vs
   enrichment gaps).

## The fix for prompt suppression: a narrow carve-out

Don't drop quote grounding. That is the anti-hallucination contract
([[Evidence-Labelled Generation with Deterministic QC]]). Instead, add a **narrow
corroboration carve-out for named tags**: structured descriptor hints (genre and kind
keywords) may corroborate `high_energy` without a literal quote. Ship it with:

- a **weight-0 visibility flag**, so carve-out assignments are countable before they
  move any score;
- a **probe version bump**, so carve-out rows are distinguishable from quote-only rows.

## Mining reasoning text for vocabulary gaps: lower bounds only

A regex lexicon was hand-authored *before* the data was read and run over the probe's
reasoning text. Its counts are **lower bounds**: diagnostic, registered UNGATED, and
never a coverage metric (see [[UNGATED Metric Convention]]). Its job is only to tell
vocabulary gaps (the reasoning names it, no tag exists) apart from supply gaps (nothing
names it).

The same slice tested name matching between sources. A conservative loose matcher
recovered 2.1% more matches. A looser one produced about 630 false positives out of 664
on generic words. Matcher loosening has a steep precision cliff, so measure it before
trusting it.

## Rule lane vs model lane

The dataset review compared rule-derived tags against model tags. **Agreement is not
accuracy.** Kind- and column-based rules over-fired 2–7× with precision below 0.3, while
keyword rules reached 0.6–0.8 precision but under-fired. Neither lane can serve as the
other's ground truth. Labels are needed (see [[One-Sided Label Control]]).

## As built: the supply slice

- **Widen where, not whether.** The prompt carve-out widened which evidence blocks the
  model may quote from, but the quote must still be verbatim. The evidence bar did not
  move.
- **Join-haystack straddle.** Matching against `hints.join(' ')` lets a phrase match
  across the boundary of two unrelated blocks. Per-block `.some()` matching does not.
- **Key parity forces a weight-0 flag.** A new tag had to be registered in a keyed map
  that requires every key to have an entry, so it shipped with weight 0 rather than
  being omitted. The probe version was bumped v4 to v5 so old and new outputs stay
  distinguishable.
- **Measure the edge delta.** The outdoor edge moved +1.3% on one measure and +0.1% on
  another: small, and reported as small.
- **Check the real vocabulary before declaring a gap.** A lexicon claimed no
  vocabulary match for a noise/conversation signal, but `good_for_conversation`
  already existed.
- **Match the unit of the estimate.** Recovery was measured per distinct name (792) as
  well as per row (1,700), because the original estimate was in names.

## See Also
- [[Evidence-Labelled Generation with Deterministic QC]] — extends (the quote-grounding rule whose side effect this diagnoses)
- [[One Facet Per Fact]] — related (structural fix when a tag carries the wrong kind of fact)
- [[Graded-Uncertainty Enrichment Contract]] — related (abstention vs suppression)
- [[UNGATED Metric Convention]] — instance-of (the hand-authored lexicon counts)
- [[Kiez Project]] — instance-of
- [[Input-Starved Enrichment]] — extends (payload carried no evidence at all)
- [[Intake Option Separability via Reach Vectors]] — related (adjacency edges as the shared lever)
- [[Dead Modifier Trace]] — related (the same split for a modifier that reads 0)
- [[Edge Registry With a Completeness-Checked Manifest]] — related (consolidating the scoring edges this triage checks)
- [[The Eval Harness Has Its Own Adapter]] — related (the dead-modifier repair in the same series)
