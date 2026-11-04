---
title: "Similar vs Interchangeable in Matching"
tags: [foundations, pattern]
summary: "Text similarity rewards both same-part and look-alike pairs, so a matcher's score should propose while extracted attributes decide (clash rejects, all read and agreeing accepts, unread goes to a person); the label chosen is itself a design decision."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--04-entity-matching-and-learning-to-rank.md
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--05-learning-a-similarity-function.md
---

# Similar vs Interchangeable in Matching

Two records can describe the same part, two makers' parts meeting one spec, or two parts of one size differing in material. Only the first two are **interchangeable** (safe to swap); the third is **similar**, and swapping it is the unsafe mistake. Text similarity rewards all three. Most specs in the generated catalogue have a sibling differing in one critical attribute.

## The label is a decision

Thresholds set for 90% recall of interchangeable pairs, new catalogue:

| Method | Recall | Precision | Unsafe share | Flagged |
|---|---:|---:|---:|---:|
| Cosine on character n-gram TF-IDF | 0.944 | 0.145 | 0.086 | 12,509 |
| Taught "same shape" | 0.903 | 0.756 | 0.222 | 2,279.8 |
| Taught interchangeable | 0.902 | 0.793 | 0.180 | 2,172.0 |

Cosine's low 8.6% is not safety: it flags nearly everything, about 1,080 unsafe pairs against 391 for the interchangeable model. Teaching the right target moved the unsafe share of proposals from 22.2% to 18.0% in four of five catalogues, still too high to act on, because when a record omits its material no score sees the clash.

## Propose, then decide on facts

A rule reads dimensions and critical attributes from both records: any clash rejects, all read and agreeing accepts, anything unread goes to a person. Mean pairs per new catalogue: accept 936.6 (914.2 interchangeable, 22.4 unsafe); review 1,201.0 (780.2 and 371.6); reject 34.4 (23.8 and 1.6); not proposed 11,665.4. Unsafe pairs in the accept pile fall to 2.4%, at the price of a review queue larger than that pile.

- Accepted unsafe pairs come from the data: 2% of stated attributes carry the wrong value, so the rule alone accepts about 23 unsafe pairs per catalogue at that rate and none at 0%. A rule cannot see through a wrong value; sample the accept pile too.
- Vetoes were mostly wrong: 24 of 34 rejected proposals were interchangeable, as the model already had clashes as features and the vetoes mostly caught mistyped records. A hard rule stays for explainability and no drift, but measure its cost.
- Sparse records: as the missing-attribute rate rose 0%, 15%, 30%, accepted pairs fell 1430.6, 960.0, 596.8 and the queue grew; the unsafe share of the pile stayed about 2.8%, 2.4%, 2.6%. Even at 0% missing about 700 pairs go to review (spellings the extractor does not know, typos).
- Costs are asymmetric: a wrongly swapped seal can stop a plant, a missed swap costs a duplicate stock line. Price the routes ([[Calibrated Score, Deterministic Decision Rule]]).

All numbers come from one generator with chosen 2% mistype and 15% missing rates, untested on a real catalogue.

## Four stages together

A capstone chains: read attributes with rules, retrieve candidates, score pairs, decide merges. With assumed prices (wrong merge 200, review 3, missed pair 5 euros), about 1,766 records and 3,784 true pairs per catalogue, means of 5 seeds: full pipeline k=10 offered 0.505 of true pairs, 546 merged, 0.4 wrong, 1,187 reviews, 8.44 euros per record. No review band: 8.4 wrong merges, 17.2 after closure, 9.77 euros. Hiding the rules from model and gate: 9.22. Thresholds tuned on 200 specs rather than 800: 5.4 wrong merges, 8.95. Retrieve k=3 offered 0.329, k=30 0.681: retrieval sets the ceiling, and a pair scorer cannot recover pairs never offered (closure can partly, since a chain of offered pairs can reach a missing one). Set thresholds on a catalogue of production size.

## See Also
- [[Entity-Disjoint Splits and Group Scores for Pair Matchers]] — prerequisite-for
- [[Match Errors Are Not Classification Errors]] — related
- [[Three-Level Duplicate Classification]] — related
- [[Calibrated Score, Deterministic Decision Rule]] — related
