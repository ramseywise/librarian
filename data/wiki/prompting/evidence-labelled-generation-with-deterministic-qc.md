---
title: Evidence-Labelled Generation with Deterministic QC
tags: [prompting, eval, pattern]
summary: Label every evidence item E1…En before the model sees it, require each claim to cite labels, keep the output schema as plain strings so out-of-vocabulary values reach QC instead of being coerced, then run a pure rule set whose worst outcome is the verdict — so every value shown can be traced to the record it rests on.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/kiez/docs/enrichment.md
  - data/raw/claude-docs/akira/docs/research/2026-09-23-pre-model-evidence-stage.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-23-pre-model-evidence-stage.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-23-pre-model-evidence-stage.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis372-pre-model-evidence-stage.md
---

# Evidence-Labelled Generation with Deterministic QC

The kiez enrichment graph asks a model for a 1–3 sentence venue summary and a list of
facet claims, written only from open-source evidence. The design makes the model's output
checkable by machine rather than trusted.

## Only checkable facets exist

A facet answers a question a map visitor asks (*can I sit outside, is it step-free, is
anything on tonight*). Every facet value must be checkable against a source a reader can
open — which rules out atmosphere and "who it suits": nothing in the sources can support
them, so a model asked for them would invent. The vocabulary is fixed in a versioned tag
list; the prose table is its summary, not the source of truth.

Each facet has an **origin** that says who may emit it:

| Origin | Who may emit | Merge rule |
|---|---|---|
| `rule` | the deterministic mapping from source tags only; a model claim is dropped | — |
| `model` | the model only, each value citing its item | — |
| `both` | the rule maps what the tags say, the model may add what the prose says | union; on a single-valued facet the rule wins and a contradicting model value is dropped |

## Shaping the input

Evidence items are deduped, ordered by how curated the source is, trimmed to a per-source
character budget (cut back to a sentence end), capped in total with later items losing
first, and then **labelled `E1…En`**. The rule facets already computed from tags are
attached so the model does not re-derive what is known. The model is asked to cite labels
for the summary and for every facet claim; a facet with no supporting item is left out.

## The schema is deliberately loose

Facet and value in the output schema are plain strings, not enums, *on purpose*: "an
out-of-vocabulary value must reach QC to be counted, not be silently coerced." A strict
schema would hide the model's errors inside a validation failure; a loose one lets QC
record them as named reasons.

## QC: pure rules, worst outcome wins

`qc.py` is pure; the verdict is the worst of `fail` > `review` > `pass`. Hard structural
failures (empty or over-long summary) fail. Vocabulary and citation problems drop the
value (`dropped:uncited`, `dropped:rule_conflict`). Plausibility checks send the row to
review: a label cited that was not in the input, a number or a capitalised mid-sentence
word that appears in no item, a promotional word, ≥ 12 consecutive words copied from one
item, more than one value on a single-valued facet. Rule facets are merged in afterwards
and never change the verdict. The name check is a known heuristic — it also flags a correct
English rendering of a name the items give only in German — which is why it is `review`,
not `fail`.

## Write so that every value is traceable

Beside the bare `facets` the web filters on, `facet_refs` maps each kept value to the
records it rests on (the source record for a rule value, the cited items — optionally a
`quote:<text>` — for a model value), and `facet_confidence` keeps the model's per-value
confidence when asked for. Writes are versioned: the current row is flipped to
`is_current = false`, a new row is inserted with model, prompt version, tag version, input
hash, the refs of every item the run saw, the evidence score, verdict and reasons.
History is never updated.

## Evals follow the document

Fixtures for the gate, the tag mapping and the QC verdict are hand-authored with expected
values written **from this document's rule text, not from running the code**, and sit
ungated until a threshold is measured ([[UNGATED Metric Convention]]).

## Recast Existing Flags Before Building a Pre-Model Stage

An audit for a "pre-model evidence stage" (facts derivable without a model, handed to the
prompt) found that **5 of 10 candidate items were already derived**, but as review flags
for humans rather than candidate labels for the model to adjudicate. The cheaper move was
to recast them, not build a new stage. Other findings:

- Put the stage beside the payload shaping it feeds (single consumer), not in a shared
  agents folder.
- Reuse a sibling pipeline's `evidence_quote` plus post-parse quote verification rather
  than inventing a new grounding mechanism.
- Genuinely absent: structured price parsing, venue coordinates in the payload, and a
  domain rule table.


## Persist Candidates Before the Model Adjudicates Them (akira, 2026-09-23)

The plan that followed the research above built the pre-model candidate stage itself, in
an order chosen to avoid co-fitting a metric to the prompt it measures:

- **Store first, wire later.** Deterministic candidate labels are written as a sibling key
  (`candidates`) beside the model payload inside the existing `raw_enrichment` jsonb column.
  No new table, and no prompt change in the first slice. A candidate / model / resolved
  agreement rate then builds up on real rows *before* the candidates are shown to the model
  and before any metric is registered on them. Showing the model the candidates first and
  measuring agreement afterwards would measure how well the model copies its input.
- **Candidates are untrusted source data in the prompt.** When they are wired in, they go in
  a marked block the model is told to verify, not instructions it is told to follow.
- **Reshaping the column moved a judge's prompt.** A QC stage serialized the whole column
  into its own prompt, so the reshape needed a read-side narrowing with a fallback for old
  rows ([[A Serialized Blob Is a Prompt Contract]]).
- **Reuse the quote verifier, do not fork it.** Per-candidate evidence quotes reuse the
  probe's post-parse check ([[Verbatim Evidence Quote Verification]]). Persisting quotes
  waits on the same store/render decision.

## See Also
- [[Grounding Claim Methodology]] — extends (claim-level grounding, enforced at generation time by labels rather than measured afterwards)
- [[Spend Gate Before the Model Call]] — prerequisite-for
- [[Structured Output]] — alternative-to (strict schemas; this page argues for loose-then-QC where the vocabulary is the thing under test)
- [[UNGATED Metric Convention]] — related
- [[Kiez Project]] — instance-of
- [[Sanitize Never Fails, Validate Never Mutates]] — extends (the sanitize/validate contract upstream of QC)
- [[Graded-Uncertainty Enrichment Contract]] — related (the output contract the deterministic QC reads)
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — extends (verbatim-quote grounding starves subjective tags; the narrow carve-out)
- [[One Facet Per Fact]] — extends (per-value provenance split by facet)
- [[Hide-Unknown Display Contract]] — related (teasers only from source-backed data; unknowns hidden downstream)
- [[Verbatim Evidence Quote Verification]] — related (the quote-level grounding check the candidate stage reuses)
- [[A Serialized Blob Is a Prompt Contract]] — related (the hidden QC reader the candidate storage reshape nearly broke)
- [[Shadow Signal Before Gate Change]] — related (accumulate the agreement rate before wiring the signal in)
