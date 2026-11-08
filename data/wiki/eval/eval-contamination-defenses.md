---
title: Eval Contamination Defenses
tags: [eval, llm, pattern]
summary: "If eval rows reach a model's training data, prompts or index, the score measures memory — public benchmarks fight it with unique multi-source answers, parameterized task templates refilled every run, temporal freshness and canary GUIDs, and each tactic transfers to a private suite."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--03-eval-datasets.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--12-failure-modes.md
  - data/raw/papers/2026-11-05-chen-2024-scienceagentbench.md
  - data/raw/papers/2026-11-05-chan-2024-mle-bench.md
  - data/raw/papers/2026-11-05-borji-2023-categorical-archive-chatgpt-failures.md
---

# Eval Contamination Defenses

If eval rows end up in what the model has seen, the score measures memory, not ability.

## Four tactics from public benchmarks

| Tactic | Benchmark | How |
|---|---|---|
| **Unique answers** | GAIA | Answers combine several sources, some from attachments (PDFs, audio, images) not on the web |
| **Parameterized templates** | AndroidWorld, τ²-bench | The task is a template ("change `[CONTACT_NAME]`'s number to `[NEW_PHONE]`") filled with fresh values every run, so a memorized action sequence won't replay. Fixing some parameters while varying others gives controlled experiments |
| **Temporal freshness** | SWE-bench-Live | Keep adding tasks created after the model's training cutoff |
| **Canaries** | Terminal-Bench | Embed a unique GUID; if a model can produce it, the set leaked |

Each works for a private set too.

## Your own leaks

- Eval rows pasted into few-shot examples.
- Fine-tuning data built from logs that include eval rows.
- Eval rows sitting in the retrieval index, or visible to the agent at runtime.

**Detection:** performance far above similar unseen tasks; the model completes a task's text
verbatim; scores drop on paraphrased versions.

## Related hygiene

- **Dev / held-out split.** Iterate on dev; look at held-out rarely (per release). Divergence
  between them means you overfit — freshen dev from production. Small suites overfit faster:
  on 50 tasks one lucky flip is 2 points. Judge calibration uses the same split discipline
  ([[Judge Calibration (TPR, TNR and Corrected Pass Rate)]]).
- **Version the dataset** and record the version on every result; v3 and v4 scores are not
  comparable. If labels came from a grader, record that grader's version too.
- **Reset state per trial** so one trial's side effects don't look like the next one's
  failure.
- **Hide the answers from an agent that can read files.** ScienceAgentBench replaces test
  labels with dummy values (e.g. −1) in the files the agent is given, and drops a few test
  points so a memorised output cannot match exactly ([[ScienceAgentBench]]).
- **Reword and compare.** MLE-bench reworded competition descriptions and saw no drop, and
  checked submissions against public notebooks for copying (self-reported, one model tested;
  [[MLE-bench]]). An archive of chatbot failures found that rewording a question could flip a
  correct answer, which is also why a single phrasing is a weak test.
- **Keep a private held-out set** that never appears online; a public benchmark's examples
  can enter the next model's training.
- **Generate synthetic rows with a different model family** from the candidate under test,
  or the candidate finds its own phrasing easy.

## Benchmark QC lessons (Li, *AI Agents in Depth*, ch. 6)

- **Budget for rejection.** SWE-bench Verified: 93 developers reviewed 1,699 of 2,294 tasks;
  only 500 survived (29%). OSWorld-Verified surfaced 300+ issues in 15 months.
- **Check "fixed it" and "broke nothing" separately** — SWE-bench's FAIL_TO_PASS tests
  prove the fix, PASS_TO_PASS tests prove no regression.
- **Difficulty levels as a diagnostic** — GAIA L1 (1–2 tools) / L2 (multi-step) / L3 (long
  combinations) failures point to prompts/tools, planning, and architecture respectively.
- **Tighten success conditions** until a superficial fix can't pass.
- **Start some tasks mid-stream**, and accept more than one valid end state (OSWorld).

## See Also
- [[Hashed Fingerprint Contamination Gate]] — instance-of (a mechanical leak check)
- [[Golden Set Mechanics]] — extends (curation and versioning of the rows themselves)
- [[Eval Suite Maintenance]] — related (overfitting and saturation)
- [[Simulated User Evaluation]] — related (τ²-bench fresh parameters)
- [[Eval Non-Determinism]] — alternative-to
- [[Parameterised Benchmark Instances]] — instance-of
- [[ScienceAgentBench]] — related (dummy test labels and dropped test points)
- [[MLE-bench]] — related (familiarity, rewording and plagiarism checks)
