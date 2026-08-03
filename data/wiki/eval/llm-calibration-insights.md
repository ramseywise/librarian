---
title: LLM Grader Calibration Insights
tags: [eval, concept]
summary: Calibration evidence for LLM-as-judge graders in the project-g eval pipeline — custom v3 grader outperforms DeepEval defaults (+0.214 score delta vs +0.086), domain-shift is the main failure pattern, passage context is required for grounding accuracy. Grounding cross-check vs DeepEval shows near-zero agreement until article text is wired in.
updated: 2026-07-06
sources:
  - raw/claude-docs/playground/docs/evals/llm-calibration-insights.md
  - raw/notion/2026-06-26-va-hca-retrieval-executive-summary.md
  - raw/claude-docs/project-g/docs/evals/llm-calibration-insights.md
  - raw/claude-docs/project-g/docs/evals/grader_methodology.md
---

# LLM Grader Calibration Insights

Empirical findings from calibrating LLM-as-judge graders for the HC support agent eval pipeline. Evidence base: 200+ manually reviewed examples, cross-grader agreement analysis.

## Key Finding: Custom v3 Grader Outperforms DeepEval Defaults

| Grader | Agreement with human | False positive rate | Notes |
|---|---|---|---|
| DeepEval default | ~65% | High | Doesn't understand Danish domain |
| Custom v3 (calibrated) | ~85% | Low | Domain-adapted prompt, explicit rubric |

**Why:** DeepEval's default judges are trained on English-centric QA. HC support involves Danish financial terminology (SKAT, CVR, moms) that generic judges score incorrectly.

## Domain-Shift Pattern

The dominant failure mode is **domain shift**: graders trained or prompted on English general-purpose QA degrade significantly on Danish/Nordic financial support content.

Symptoms:
- False positive: grader accepts an English answer for a Danish question as "correct"
- False negative: grader rejects a valid Danish support response because it doesn't match English phrasing expectations
- Score inflation: graders give high scores to vague but fluent answers that don't actually resolve the user's issue

**Fix:** Add domain-context to grader prompt. Include 2–3 examples of domain-specific correct/incorrect pairs in the grader system message.

## Passage Context Requirement for Grounding Graders

`GroundingGrader.grade()` requires `context=[passage.text, ...]` not URL strings.

```python
# WRONG — produces score=0.5 (no context to grade against)
grader.grade(response=answer, context=["https://help.[product].dk/article/123"])

# CORRECT
grader.grade(response=answer, context=[passage.text for passage in retrieved_passages])
```

**Why it matters:** URL-only context → grader can't check factual grounding → scores default to 0.5 (neutral). This inflates grounding scores without actually measuring anything.

## Calibration Process

1. **Sample 50–100 examples** from the eval dataset
2. **Human-label each** with pass/fail + reason
3. **Run all graders** on the same examples
4. **Compute agreement** (Cohen's kappa or simple % match)
5. **Identify systematic disagreements** — these reveal domain-shift or prompt failures
6. **Tune grader prompt** with 2–3 few-shot examples from the disagreement set
7. **Re-run** and confirm agreement improves to target (≥80%)

## Grader Confidence vs Score

High grader scores (0.8+) don't mean high calibration. A grader can be confidently wrong in a systematic direction. Always check:
- **Score distribution:** if most scores cluster at 0.9+ or 0.1–, the grader may not be discriminating
- **Inter-grader agreement:** run two graders on the same examples; expect 15–25% disagreement is normal
- **Edge case coverage:** ensure your calibration set includes OOS, out-of-language, and borderline cases

## Pass Thresholds

Thresholds live in `evals/metrics/_constants.py` (`TIER_THRESHOLDS`). Tier policy in `evals/graders/registry.py`.

| Tier | Threshold | Use case |
|---|---|---|
| heuristic | Fixed (rule-based) | Citation checks, schema validation |
| fast | 0.6 | Rapid regression, large batches |
| voted | 0.7 | Majority-vote LLM, production threshold |
| calibrated | 0.75 | Calibrated against human labels |

## Grounding vs Faithfulness: Production Evidence

The VA vs HCA retrieval evaluation (n=754 Danish questions) surfaces a cross-system pattern worth tracking in calibration:

| Metric | VA | HCA | Interpretation |
|---|---|---|---|
| Grounding | 0.776 | 0.633 | Grounding measures whether claims are tied to *retrieved* sources — reflects retrieval quality |
| Faithfulness | 0.592 | 0.511 | Faithfulness measures whether the answer stays *within* retrieved content — reflects model extrapolation |

**The faithfulness gap:** Both systems show low faithfulness (~0.5–0.6) despite acceptable grounding on VA. The model adds unsupported detail even when it successfully retrieved relevant sources. This is not a retrieval failure — it is a model behavior pattern that grounding scores can mask.

**Calibration implication:** When tuning grounding graders, ensure your calibration set includes cases where grounding is high but faithfulness is low (model extrapolates beyond sources). These are easy to falsely pass if grounding is the only metric.

**Note:** Both metrics from the VA/HCA study are measured via LLM-as-judge (Grounding score = are claims tied to retrieved sources?; Faithfulness score = does answer stay within retrieved content?). Check your grader definition matches this distinction before comparing numbers across systems.

## Specific Calibration Numbers (BKH, 50 tasks, 25 liked / 25 disliked)

| Grader | Liked μ | Disliked μ | Δ | Cohen's d | Verdict |
|---|---|---|---|---|---|
| **Custom answer_relevancy v3** | 0.885 | 0.670 | **+0.214** | 0.75 | Strong |
| DeepEval answer_relevancy | 0.728 | 0.642 | +0.086 | 0.25 | Weak |
| Custom completeness | 0.750 | 0.720 | +0.030 | 0.07 | Marginal |
| DeepEval completeness | 0.681 | 0.723 | −0.042 | — | Inverted |
| Custom escalation | 0.800 | 0.800 | 0.000 | 0.00 | No signal |
| DeepEval escalation | 0.600 | 0.680 | −0.080 | — | Inverted |

**v3 prompt progression:** v2 Δ = −0.080 (inverted) → v3 Δ = +0.214 (+0.294 improvement per iteration)

**Score delta rule:** if `score_delta < 0.05`, the threshold is doing the work, not the score. The prompt needs iteration.

## Grader Selection Framework

1. **Check F1 leaderboard** sorted by F1 with cross-check r column alongside.
2. **Check score_delta** — Δ < 0.05 → prompt needs iteration.
3. **Pipeline gate vs. trace creation are different jobs:**
   - Gate: use highest-recall grader
   - Traces: use highest-precision grader
4. **Low cross-check r** — investigate root cause (context? threshold? prompt framing?) before switching judges.
5. **Grounding: hold judgement** until article text is wired. Current train split grounding calibration is under-powered due to `context_missing` exclusions.

## Grounding Cross-Check: The Context Problem

The grounding cross-check (DeepEval comparison) almost certainly shows low agreement because it runs against URL citation strings, not article body text. Our grader's context guard fires and returns 0.5, while faithfulness and G-Eval try to evaluate against URLs and produce unreliable results.

**To validate:** check how many sample records were `context_missing` and re-compute correlation for records that did have passage text.

Pass `context=[passage.text ...]` not URLs. The comparison is apples-to-oranges until `article_loader.py` is wired in.

## Domain-Shift Watch

Custom graders calibrated on BKH show strong Δ on BKH but near-zero Δ on VA staging data. Likely causes: VA disliked responses are disliked for reasons answer_relevancy doesn't capture (tone, escalation handling, multi-turn context loss) rather than irrelevance.

When re-running calibration on GT dataset, isolate by query type — accounting-specific queries vs nav/UI queries to see if Δ holds within domain before drawing cross-domain conclusions.

## See Also
- [[VA vs HCA Retrieval Evaluation]]
- [[project-g Eval Architecture]]
- [[VA Eval Harness]]
- [[RAG Evaluation]]
- [[HITL Annotation Pipeline]]
- [[Evaluation & Improvement Project (VIR)]]
- [[RAG Eval Gate Contract]]
- [[Grounding Claim Methodology]]
- [[LLM-as-Judge Evaluation]] — prerequisite-for (calibration is the setup cost of a usable judge)
