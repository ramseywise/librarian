---
title: Judge Calibration (TPR, TNR and Corrected Pass Rate)
tags: [eval, llm, pattern]
summary: "Calibrate an LLM judge against 100–200 human labels split train/dev/test, report TPR and TNR separately (TNR usually matters most), benchmark against human–human agreement, and correct the observed pass rate with (p̂ + TNR − 1) / (TPR + TNR − 1)."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--05-llm-as-judge.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--11-production-and-the-maturity-ladder.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--README.md
---

# Judge Calibration (TPR, TNR and Corrected Pass Rate)

A judge is a model making a measurement. **It is calibrated when you have measured how
often it agrees with humans on your data** — until then it is experimental and may not gate
a release ([[Grader States (Heuristic, Calibrated, Experimental)]]).

## The procedure

1. **Human labels.** 100–200 outputs labeled PASS/FAIL on the judge's single criterion by the
   domain expert who owns pass/fail ([[Error Analysis (Open and Axial Coding)]]). Both classes
   in reasonable numbers. Real user signal (👍/👎, escalation, resolution) can serve as the
   label.
2. **Split** into train (few-shot examples come from here), dev (iterate the prompt), test
   (measure once).
3. **Run on dev**, build the confusion matrix against human labels.
4. **Read every disagreement** — each is a judge-prompt problem (fix the prompt), a criteria
   problem (fix the criteria, re-label), or a hard case (add to few-shot).
5. **Iterate on dev** until good enough for the job.
6. **Measure on test once.** That is the reported number. Tuning against test makes it a
   dev set.
7. **Record** judge model, prompt version and test metrics; re-run when any changes.

## What to report

Accuracy hides the failure you care about. Report the two error rates separately:

| Metric | Meaning | Matters for |
|---|---|---|
| **TPR** (recall on PASS) | Of human-passed outputs, share the judge passed | Not blocking good releases |
| **TNR** (recall on FAIL) | Of human-failed outputs, share the judge failed | **Catching bad outputs** — usually the one that matters |
| **Precision on PASS** | Of judge-passed outputs, share humans passed | Using judge-passed outputs as golden labels |
| **Cohen's κ** | Chance-corrected agreement | Comparing with human–human agreement |
| **Score separation** | Mean score on human-PASS minus human-FAIL (and Cohen's *d*) | Whether a continuous judge discriminates at all |

Rules of thumb:

- **Different jobs, different metric.** A release gate needs high TNR; a golden-label builder
  needs high precision on PASS. If one judge cannot do both, use two.
- **Benchmark against human–human agreement.** If experts agree 85%, a judge at 83% is about
  as good as a second expert ([[Human Agreement Ceiling Protocol]]).
- **Separation under ~0.05 means the threshold is doing the work** — fix the prompt.
- **Inverted separation means it measures something else.** Off-the-shelf judges have been
  observed scoring *disliked* answers higher on completeness and escalation
  ([[LLM Grader Calibration Insights]]).

## Correcting the pass rate

A judge with known error rates gives a biased estimate of the true pass rate. With observed
judge pass rate p̂ and TPR/TNR from the test split:

```
true pass rate ≈ (p̂ + TNR − 1) / (TPR + TNR − 1)
```

Judge passes 80%, TPR 0.95, TNR 0.80 → 0.60 / 0.75 = **0.80**. With TNR 0.70 → 0.50 / 0.65 ≈
**0.77**. Small correction for a good judge, large for a lenient one; only valid when
TPR + TNR is well above 1.

## Keeping it calibrated

- **Re-calibrate on any change**: judge model, judge prompt, the system under test (new
  failure types), the user population.
- **Calibration is per domain.** The same judges separated well on one product's traffic and
  near-zero on another, where users disliked answers for different reasons (tone,
  escalation, multi-turn context).
- **Keep a human sample flowing** (5–10% in production) — the human layer of
  [[Online Eval Sampling]] is what reveals judge drift.
- **Pin the judge model version**; never mix judges across runs you intend to compare.
- **Cross-checking against another judge** (RAGAS, DeepEval, G-Eval) shows correlation, not
  correctness — only human labels settle which is right.

## See Also
- [[LLM-as-Judge Evaluation]] — extends (the calibration step, specified)
- [[LLM Judge Biases]] — complements (bias mitigations applied before calibrating)
- [[Human Agreement Ceiling Protocol]] — prerequisite-for (the ceiling the judge is compared to)
- [[Positive-Only Judge Fixtures Measure Recall]] — related (a fixture set that can only measure TPR)
- [[Human Verdicts as Judge Fixtures]] — related (human labels exported as fixtures)
- [[LLM Grader Calibration Insights]] — instance-of (calibration results from one pipeline)
