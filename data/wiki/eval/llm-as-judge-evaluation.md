---
title: LLM-as-Judge Evaluation
tags: [eval, llm, pattern]
summary: A separate LLM scoring outputs against a rubric — the approach for subjective quality where exact matching fails, requiring calibration against human grades and recommended as a complement to golden-set grading rather than a replacement.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-divergence-since-diskoe-mvp.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-divergence-since-diskoe-mvp.md
  - data/raw/claude-docs/akira/docs/technical-feasibility.md
  - data/raw/claude-docs/diskoe/docs/technical-feasibility.md
  - data/raw/claude-docs/playground/docs/technical-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/technical-feasibility.md
  - data/raw/claude-docs/akira/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--05-llm-as-judge.md
---

# LLM-as-Judge Evaluation

A separate LLM call evaluates output against criteria (relevance, accuracy, helpfulness,
tone), scoring on a scale or pass/fail. More flexible than heuristic grading, but more
expensive and more variable.

**Use when** output quality is subjective (summaries, drafts, recommendations); you need
to evaluate tone, completeness, or style; you want automated scoring but can't define
correctness by string match; you're evaluating *generation* rather than *retrieval*.

**Avoid when** correctness is objectively definable — use [[Golden Set Mechanics]] instead,
cheaper and more reliable; budget is tight; or you need deterministic results.

## Calibration is the setup cost

The step that distinguishes a working judge from a plausible one:

1. Write 3–5 quality criteria (*"Is the summary under 200 words? Does it include all
   action items? Is the tone professional?"*).
2. Create 5–10 sample inputs with human-graded "good" outputs.
3. Write a judge prompt scoring against the criteria.
4. **Run the judge on the sample set and calibrate until it agrees with human grades.**

Step 4 is what makes the scores mean anything. An uncalibrated judge produces numbers that
look like measurements but track the judge's priors — see
[[LLM Grader Calibration Insights]].

## Complexity

**Multi-sprint** — needs a rubric, a judge prompt, calibration samples, and eval-runner
integration.

## Scaffold mapping

| Parameter | Value | Rationale |
|---|---|---|
| `optional_features` | `[ragas]` | RAGAS provides LLM-judge grading infrastructure |
| `optional_features` | `[promptfoo]` | Promptfoo supports LLM-as-judge via config |

Both integrate *alongside* — not replacing — heuristic golden-set grading.

## Trade-offs

**Pro:** evaluates subjective quality; flexible criteria; catches subtle tone/style
regressions.
**Con:** costs money per run; non-deterministic (identical input may score differently);
requires calibration; **the judge can simply be wrong**.

**Recommendation:** *"Use as a complement to golden-set, not a replacement. Run heuristic
grading (free, fast) in CI; run LLM-judge on demand for quality audits."* The cost and
non-determinism make it a poor fit for a per-PR gate.

## The trust ceiling is human–human agreement

A decision log from an LLM-ranked consumer product (akira) states the limit precisely: a
judge's agreement with human raters cannot be trusted above the agreement measured *between*
those raters on the same instrument. If humans agree at kappa 0.6, a judge reporting 0.8
against one rater is measuring that rater, not the truth. Consequences adopted there:

- the judge is a **regression detector, never a launch gate** — it flags movement between
  prompt versions; humans decide whether the movement is real;
- items the judge cannot classify fail safe to `needs_human_review` rather than to a score;
- a fixed fraction (~25%) of judge critiques is sampled for human review on an ongoing basis,
  so the ceiling itself is re-measured rather than assumed.

The storage side of that measurement — keeping every human rating so agreement stays
computable — is [[Append-Only Human Labels]].

## Judge Choice Can Dominate the Number

In a venue-enrichment dataset review (repo akira, 2026-09-26), **the same 200 probe
outputs passed at 0.96 under one judge model and 0.25 under another**. The judge choice
moved the pass rate about four times more than swapping the probe model did. A third
judge run failed outright (1 of 200 rows ok), and cheaper probe models invented
attributes on 60–75% of rows under any judge. Consequence: **no judge threshold may be
written until one judge is calibrated against a human-anchored set** (see
[[Human Agreement Ceiling Protocol]]). Before then, judge pass rates across models are
not comparable, and quoting one as quality is meaningless.

## Calibration and bias (course synthesis, 2026-10)

The 06-eval course treats a judge as a classifier to be measured: 100–200 human labels split
train/dev/test, TPR and TNR on the held-out split, and a bias-corrected pass rate — see
[[Judge Calibration (TPR, TNR and Corrected Pass Rate)]]. Known judge biases (position, verbosity,
self-preference) and their mitigations are on [[LLM Judge Biases]]. Under that procedure a judge in the
`calibrated` state may gate a release at its calibrated threshold.

The two bars apply at different stages. The 5–10-sample calibration above is a
**discovery-stage smoke test** for a rubric, and a judge at that stage is a regression
detector only. Before a judge may gate a release it needs the full procedure: 100–200 human
labels, TPR/TNR on a held-out split, and a human inter-rater agreement measured high enough
that the judge's agreement means something ([[Human Agreement Ceiling Protocol]]). Where
that ceiling is low — as in the product above — the judge stays ungated whatever its
calibration says.

## See Also
- [[Eval vs Test Distinction]] <!-- auto-linked -->
- [[Eval Ladder]] — part-of (rung 3)
- [[Golden Set Mechanics]] — complements (heuristic in CI, judge on demand)
- [[LLM Grader Calibration Insights]] — extends (calibration failure modes)
- [[Manual Review as Eval Bootstrap]] — prerequisite-for (human grades calibrate the judge)
- [[Eval Maturity Ladder]] — part-of (one of four layered grader types; source of the three judge biases)
- [[Online Eval Sampling]] — extends (the judge as layer 2 over production traces)
- [[Eval Harness Anatomy]] — part-of (one of the three grader types under the simplest-reliable rule)
- [[Constitutional AI and RLAIF]] — instance-of (the same judge primitive used to generate training labels)
- [[Bradley-Terry Preference Model]] — complements (pairwise comparison formalized as a scalar)
- [[Append-Only Human Labels]] — prerequisite-for (human labels set the judge trust ceiling)
- [[Human Agreement Ceiling Protocol]] — prerequisite-for (κ_judge ≥ 0.8 × κ_HH, not an absolute target)
- [[Synthesize the Cheap Half]] — related (gold-set calibration, closed-loop and stratum-bias rules for synthesized labels)
- [[Confidence That Is Not a Probability]] — related (another score that needs independent labels before it can gate)
- [[Specialist Verdict Panel]] — extends (one judge split into single-dimension specialists with structured verdicts)
- [[Answer Criteria with Named Wrong Answers]] — extends (per-topic fail-if lists as the rubric)
- [[Positive-Only Judge Fixtures Measure Recall]] — extends (recall vs precision of a judge fixture set; one calibration pass)
- [[Closed Judge Vocabulary, Tolerant Parse]] — related (closing a judge's free-text issue list without brittle enum parsing)
- [[Demote Judge Findings to Keyless Gates]] — extends (regex-catchable findings leave the judge for a keyless 1.0 gate; missing-verdict re-ask; calibration floor)
- [[Judge Sees the Drafter's Facts]] — extends (reference facts so restating a given score is not scored ungrounded)
- [[Grader States (Heuristic, Calibrated, Experimental)]] — extends
- [[SOMA Judge Rubric]] — extends (specific, ordinal, multi-aspect rubric; never reveal self-grading)
