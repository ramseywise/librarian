---
title: Demote Judge Findings to Keyless Gates
tags: [patterns, eval, pattern]
summary: "When an LLM judge finds a defect that a regex or derivation check could catch, turn it into a keyless heuristic grader gated at 1.0 on the deterministic path; judges then measure only the model lane and prose quality, never the regression class itself."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-08-r17-eval-run-1-fixes.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-13-r18-eval-run-2-agents-evals-dashboard.md
---

# Demote Judge Findings to Keyless Gates

A judge run produces findings ("the charter lists a deliverable the assessment never
mentions", "the narrative claims outcomes the record does not state"). The tempting fix is
to keep the judge as the regression gate for that defect. That gate needs an API key, is
non-deterministic, and is uncalibrated until it has labels, so a repeat of the same defect
can slip through CI. In nonprofit-success-ai the rule became: **a judge finding that a regex
can detect becomes a heuristic grader gated at 1.0; the judge is not the regression gate
for it.**

## Mechanism

1. **Read the run before planning.** Every claim in the fix plan comes from the run's
   graded output and calibration file, not from memory of what the judge "usually" says.
2. **Groundedness lint = deny-list plus derivation check, not a second judge.** You get
   three kinds of check:
   - a shared list of phrases that may never appear in template output;
   - "every `outcomes[]` entry equals a supplied success criterion or objective";
   - "thin input ⇒ the narrative contains a provisional marker".
   Each check is a pure function with one passing and one failing unit test.
3. **Gate at 1.0 on the template (deterministic) path**, in `make gate` and in a keyless CI
   job. A new template phrase that invents a fact has to pass the deny-list.
4. **Conditional, not deleted.** When a finding is "criterion X is unsupported", make the
   criterion conditional on the deliverable that supports it rather than removing it.
   For example, a recurring-report criterion applies only when the deliverable is a
   pipeline or dashboard.
5. **Share rule text between the prompt and the heuristic.** The model prompt gets the
   heuristic's tiebreak rule verbatim. Drift between them then shows up as a model-lane
   disagreement. Do not change the heuristic to agree with the model; the model lane stays
   reported, never gated.

## Harness hardening that goes with it

- **Missing verdict ⇒ re-ask once, alone.** A verdict missing from a batched judge reply is
  re-asked as a batch of one before it is recorded `judge_missing_verdict`. Count the
  re-asks as calls.
- **Calibration floor before trust.** Each judge needs at least 10 labelled outputs, split
  roughly even between pass and fail. Every rubric dimension must be planted at least once
  as the *only* fault, so per-dimension agreement can be measured. Until a judge reaches the
  floor its key stays commented out of the targets file (see [[UNGATED Metric Convention]]).
  Judge outputs never set thresholds.
- **Model variance is measured, not gated.** `EVAL_MODEL_SAMPLES=n` runs the model lane n
  times per case and reports per-case agreement. The gated rate still reads sample 0
  only, so turning on variance cannot move a gate.
- **No fixture is rewritten to pass.** Expectations change only where the plan argues the
  expectation itself was wrong.
- **Bump every touched prompt version**, including the judge's, so the experiment log can
  attribute the change.

## Why it works

The judge's scarce, expensive signal goes to what only a judge can see: prose quality, the
model lane, and borderline groundedness. Everything mechanical moves to a gate that is
free, deterministic and runs on every PR. In the second run the lints held 10/10 at 1.0
with no key, and the judges were re-scoped to a smaller and better-calibrated surface.

## See Also
- [[LLM-as-Judge Evaluation]] — extends
- [[Build the Checker Before the Generator]] — extends
- [[Heuristic Pipeline Metrics]] — extends
- [[UNGATED Metric Convention]] — extends
- [[Judge Sees the Drafter's Facts]] — extends
- [[Human Agreement Ceiling Protocol]] — prerequisite-for
