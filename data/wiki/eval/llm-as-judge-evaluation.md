---
title: LLM-as-Judge Evaluation
tags: [eval, llm, pattern]
summary: A separate LLM scoring outputs against a rubric — the approach for subjective quality where exact matching fails, requiring calibration against human grades and recommended as a complement to golden-set grading rather than a replacement.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
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

## See Also
- [[Eval vs Test Distinction]] <!-- auto-linked -->
- [[Eval Ladder]] — part-of (rung 3)
- [[Golden Set Mechanics]] — complements (heuristic in CI, judge on demand)
- [[LLM Grader Calibration Insights]] — extends (calibration failure modes)
- [[Manual Review as Eval Bootstrap]] — prerequisite-for (human grades calibrate the judge)
- [[Eval Maturity Ladder]] — part-of (one of four layered grader types; source of the three judge biases)
- [[Online Eval Sampling]] — extends (the judge as layer 2 over production traces)
- [[Eval Harness Anatomy]] — part-of (one of the three grader types under the simplest-reliable rule)
