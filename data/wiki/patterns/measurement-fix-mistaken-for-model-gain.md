---
title: Measurement Fix Mistaken for Model Gain
tags: [patterns, eval, pattern]
summary: "When an agent's citations and the ground truth use different identifiers for the same document (a KB domain migration, URL titles standing in for passages), correct answers score as failures; fixing the scorer moves the headline number more than any model change, so report v1-strict and v2-calibrated side by side and treat historical baselines as lower bounds."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/project-g/docs/stakeholders/project-g-eval-framework.md
  - data/raw/repos/playground/docs--stakeholders--galactus-eval-framework.md
  - data/raw/claude-docs/project-g/docs/stakeholders/va-demo-may-2026.md
  - data/raw/claude-docs/project-g/docs/plans/VIR-212-gt-verification.md
  - data/raw/claude-docs/project-g/docs/rag/retrieval-improvements.md
---

# Measurement Fix Mistaken for Model Gain

Finding from the project-g support-agent eval. The headline result shown to decision-makers —
grounding pass rate jumping from **34% to 78%** — was almost entirely a scorer fix, not an
agent improvement. Nothing about the agent changed between the two numbers.

## The mechanism

The historical baseline's expected URLs pointed at the old KB domain; the new agent cited the
same articles on the new KB domain after a product migration. URL-overlap grading did literal
matching, so a response citing the **correct** article scored **zero**. Failure rates were
inflated across every grader that compared URLs, and the inflated "ungrounded response" bucket
looked like a model-quality problem worth investigating.

A sibling defect sat in the same pipeline: when an agent run carried no retrieved passages,
the grader context fell back to the expected URL *title strings*. RAGAS faithfulness was then
asked whether an answer was supported by "What is a fee? (https://…)" — and scored near zero.
A reported 55% liked-but-failed rate on faithfulness was largely that artifact. Same shape:
the scorer was measuring its own input problem. (Cf. [[Silent Fallthrough in String-Keyed Discovery]].)

## The fix

- **An alias layer, not agent logic.** A resolver maps old ↔ new URLs by title match, slug
  match, then TF-IDF fallback (182 of 268 mapped; humans verify the map). It is a stateless
  lookup table committed to the repo, matched on path only to dodge protocol/domain drift —
  KB migrations become a data operation, not a code redeploy, and agents stay KB-agnostic.
- **Passage enrichment.** Graders receive cached article text for expected URLs instead of
  URL strings, with explicit graceful degradation for uncached URLs.
- **Validate inputs before grading** — reject empty-passage rows rather than letting the
  grader silently degrade.

## How to report it

- **Two columns, always.** v1 = strict literal match (pre-normalisation); v2 = calibrated with
  aliasing. Showing both makes the measurement change visible instead of letting it read as a
  model gain.
- **Historical baselines become lower bounds.** The baseline suffered the same artifact (its
  grounding scored 0% because article text could not be fetched for old-domain URLs at scoring
  time), so baseline-vs-new comparisons understate the baseline.
- **Prefer relative over absolute.** Both systems handle the hardest, friction-heavy queries;
  absolute scores were low for both. The go-live decision rested on "at least as good as the
  baseline on calibrated metrics," with absolute scores treated cautiously.
- **Verify ground truth before calibrating graders.** Fixing grader bugs on top of unverified
  ground truth compounds noise; the order is GT audit (URL health, 404s, domain mix) → scorer
  fixes → calibration.

## Diagnostic

Before crediting a big jump to the agent, ask: *did the scorer, the ground truth, or the
grader's input change between the two runs?* A gap analysis of misses helps — in the same
project, 2 of 6 top-5 misses were documents never ingested (a coverage gap, not a ranking
error), and a later production comparison attributed a whole bucket of misses to the
URL-mapping gap.

## See Also
- [[LLM Grader Calibration Insights]] — extends
- [[project-g Eval Architecture]] — instance-of
- [[VA vs HCA Retrieval Evaluation]] — extends (URL-mapping gap as a miss category)
- [[RAG Eval Gate Contract]] — extends (alias-aware retrieval metrics)
- [[Silent Fallthrough in String-Keyed Discovery]] — extends
- [[Fallback Mistaken for the Design]] — alternative-to (the degraded path critiqued as the design; here it is scored as the model)
- [[Fixture Eval Blind to the Swapped Component]] — related (a model comparison whose gate never executes the model)
