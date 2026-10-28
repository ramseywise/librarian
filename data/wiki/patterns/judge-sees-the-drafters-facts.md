---
title: Judge Sees the Drafter's Facts
tags: [patterns, eval, pattern]
summary: "Give a groundedness judge the same derived facts the drafting agent was given, as reference facts the output must not contradict; otherwise the judge fails correct output for restating a given score or status as if it were invented."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-13-r18-eval-run-2-agents-evals-dashboard.md
---

# Judge Sees the Drafter's Facts

A drafting agent often receives facts that a deterministic step derived from the raw
input. Examples are a readiness score, an engagement status, or a signal level. If the
judge only gets the raw input, then a rationale that quotes "clarity 2/3" or calls a
record "completed" looks ungrounded to it. The judge then fails output that is correct.
In nonprofit-success-ai's second eval run, several of the routing-rationale and
narrative-draft failures turned out to be this artifact.

## Mechanism

- The judge's `expectedFacts()` calls **the same function the model path calls** (e.g.
  `scoreReadiness(input)`) and adds its output as a reference-fact block. It does not copy
  or re-derive the values.
- A **reference fact is something the output must not contradict.** Restating it counts as
  grounded. Contradicting it is a failure.
- Add each reference fact the agent saw: derived readiness for the routing judge, and
  `status` plus derived readiness for the narrative judge.
- If calibration shows the judge dropping below the trust bar after the change (0.8 in the
  source), revert that judge's rubric line. The change has to earn its place through
  calibration like any other rubric edit.

## Related failure: thin input forces restatement

The same run found a template that restated the objective because its input only had an
event count. The fix was on the input side: optional short event summaries (capped and
wrapped in the partner-data delimiter) that the template and the judge both read. Judge
the output against what the drafter could actually know.

## See Also
- [[LLM-as-Judge Evaluation]] — extends
- [[Demote Judge Findings to Keyless Gates]] — alternative-to
- [[Input-Starved Enrichment]] — extends
- [[Four-Source Provenance Contract]] — extends
