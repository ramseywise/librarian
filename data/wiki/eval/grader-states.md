---
title: Grader States (Heuristic, Calibrated, Experimental)
tags: [eval, llm, pattern]
summary: "Give every grader an explicit state — heuristic (deterministic code), calibrated (judge with human-agreement evidence), experimental (new or uncalibrated) — and let only the first two gate a release; behind it sits one grader interface with a requires field and a grader_version."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--04-graders.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--10-evals-in-ci.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--README.md
---

# Grader States (Heuristic, Calibrated, Experimental)

Not every grader is trustworthy enough to gate on. Make trust an explicit, recorded property
of the grader rather than an impression.

| State | Meaning | Can gate releases? |
|---|---|---|
| **Heuristic** | Deterministic code check | Yes |
| **Calibrated** | LLM judge with evidence it agrees with humans ([[Judge Calibration (TPR, TNR and Corrected Pass Rate)]]) | Yes, at the calibrated threshold |
| **Experimental** | New or uncalibrated judge | **No** — tracking and investigation only |

Two rules make it enforceable:

- **A threshold change without fresh calibration evidence moves the grader back to
  experimental.**
- **Release decisions name the state of every metric they cite.** In a gate ladder, a
  "grader calibration" gate fails when a gating judge is experimental or its calibration is
  stale ([[Run-Then-Assert Eval CI]]).

This is the grader-level counterpart of the [[UNGATED Metric Convention]], which withholds a
threshold until a pass rate has been measured.

## Code first, layered

Choose the simplest grader that can be trusted, and layer rather than choose:

| Layer | Scales | Cost | Role |
|---|---|---|---|
| Code | Fully | ~0 | First line; catches structural failures |
| Separated evaluator | Well | Medium | Operates the output (runs the app/code) — verdict rests on observed behavior ([[Verification Loops]]) |
| LLM judge | Fully | Medium | Subjective criteria at volume |
| Human sample | Poorly | High | **Calibrates** the judge — 5–10% of graded rows, not a review queue |

Run code graders first and **short-circuit**: an answer that fails the schema does not need a
judge. Teams reach for judges too early; checkable properties include format, tool name and
argument values, citation IDs in the retrieved set and verbatim quotes, final DB/file state,
compile/test pass, response language, forbidden-tool and turn limits, efficiency from the
trace, and exact facts within tolerance. For tool calls, check in order and stop at the first
failure: called a tool → right tool → valid arguments → right values.

Reference-based text metrics (BLEU, ROUGE, embedding similarity) correlate poorly with
quality on open-ended answers; use them for tightly constrained outputs or as a tracking
signal, never a gate.

## The grader interface

One contract makes graders swappable, composable and reportable the same way.

- **Input:** `task` (input, reference, labels), `output`, optional `trajectory`,
  `retrieved_context` (passage **text**, not IDs/URLs), `metadata` (model, prompt
  version, config, run ID).
- **Output:** `score` in [0,1], `passed`, `reasoning`, `dimensions`, `labels`
  ([[Eval Failure Taxonomy]]), `grader_version`.
- **`requires`:** the inputs the grader cannot work without. A grounding grader handed URLs
  instead of text returns can't-grade (`context_missing`), not a made-up score.

## Binary by default

Prefer pass/fail per dimension over 1–5 scales: graders disagree most in the middle of a
scale, pass/fail forces the bar to be defined, and binary rates have simple statistics
([[Eval Error Bars and Sample Size]]). Use a scale only when each level is described and the
extra resolution changes a decision.

## See Also
- [[Eval Harness Anatomy]] — extends (the grader noun, given a trust state)
- [[UNGATED Metric Convention]] — complements (metric-level counterpart)
- [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] — prerequisite-for (how a judge becomes calibrated)
- [[Veto Rubric Items]] — related (how graders combine into a task score)
- [[Demote Judge Findings to Keyless Gates]] — related (moving checks from judge to code)
