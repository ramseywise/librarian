---
title: Contract-Anchored Findings Get Fixed
tags: [eval, pattern]
summary: Across 238 review findings, the ones citing a rule the repo had already written down were fixed 9 of 9 with no pushback. Other findings averaged 65%, and the dimension furthest from any written rule ran 44%. So every review dimension should be able to cite the change contract, not only the contracts reviewer.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/workflow-review/SKILL.md
---

# Contract-Anchored Findings Get Fixed

## The measurement

A multi-dimension code review wrote each finding to a JSONL ledger. Measured over **238
findings**:

- Findings anchored to an entry in the repo's change contract were fixed **9 of 9 (100%)**,
  with zero pushback.
- All other findings averaged **65%**.
- `intent`, the dimension furthest from any written rule, ran **44%** and had the highest
  argued-back rate in the corpus.

The ordering tracks one variable: **distance from a rule the repo already agreed to.** An
`important` finding from a reviewer is an opinion and gets negotiated. The same claim
carrying a contract reference is a rule the repo already signed, and it does not get
negotiated.

## The paradox and the fix

Contract-anchored findings were only **4%** of the corpus, so the highest-yield signal in
the pipeline was also its rarest. The cause was structural. Only the contracts dimension
was expected to cite the contract, so the other ten dimensions raised contract violations
as unanchored opinions.

The fix is a `contract_ref` field on **every** finding row, holding the heading text of
the contract entry the finding violates. It is omitted when no entry applies and never
invented to look rigorous. The contracts reviewer still owns its own finding class and the
layer taxonomy. The field only lets other dimensions *cite* the contract without claiming
its dimension.

## Implication

To raise the fix rate of automated review, grow and cite the written contract rather than
tuning reviewer tone. A recurring argued-back finding class is a candidate contract entry.

## See Also
- [[SANYI Change-Contract System]] — extends (the contract being cited)
- [[Merge Impact and Evidence State]] — extends (a third axis on each finding: what rule it rests on)
- [[Review Reporter Ground Rules]] — related
- [[Workflow Pipeline Telemetry Audit]] — related (the ledger hygiene that made the measurement possible)
- [[A Clean Contract Review Is Only as Wide as the Contract]] — related (the converse: a clean contracts verdict where no rule applied)
