---
title: PreAct
tags: [harness, pattern]
summary: "PreAct compiles a computer-using agent's first successful run into a state-machine program that later runs replay without per-step LLM calls, storing a program only if a re-run from a clean state passes the benchmark evaluator; warm replays ran 8.5 to 13 times faster on WebArena (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2026-preact.md
---

# PreAct

Li (Pine AI, sole author, preprint) targets computer-using agents that repeat tasks. After a first success, the run is compiled into a program: states hold screen predicates and transitions hold actions. Subsequent runs replay that program making almost no model calls. Each state's predicate is checked against the live screen before acting, and a mismatch falls back to the full agent.

## The verify-before-store gate

A freshly compiled program is stored only when the benchmark's evaluator passes it on a re-run from a reset environment. The paper reports programs that replayed every action (100% coverage) yet left the task undone, and that all 48 warm replays on WebArena with the gate off scored 0.

## Results (self-reported, paired cold and warm runs)

- Speed: warm replays were 8.5 to 13 times faster than a fresh agent solve on WebArena.
- One-time cost: the verify-replay step added 162% to wall time on Android (median solve 47 s, verify 76 s) and 217% on OSWorld (solve 65 s, verify 141 s), per stored program.
- Gate ablation, reporting the mean change in tasks solved between the cold and warm runs, with the gate on and then off. AndroidWorld with Gemini (n=5): +1.2 on, -1.4 off. OSWorld test_tiny used 6 tasks with Claude Sonnet 4.6 (n=5) and gave +0.2 on, -2.4 off. WebArena shopping_admin used 12 tasks (n=4+4) and gave -4.0 on, -5.75 off. The gated runs came out ahead in 13 of the 14 paired runs.
- On WebArena the gate turned away about 83% of compiled programs and warm success stayed at 2.0 of 12; letting a cache miss fall back to the agent lifted that to 6.25 of 12, indistinguishable from the Muscle-Mem baseline (p about 0.84).
- On 45 paraphrased queries a plain embedding retriever did at least as well as the LLM selector at finding the right program family (100% against 75.6%).
- Running the validation took about 50 container hours and roughly $30 to 35 of LLM spend.

## Limits

- Idempotency: because the gate runs the program again, it needs an environment that can be reset or tolerates repeats; the author says irreversible actions (sending email, submitting payment) need a side-effect-free check, left as future work.
- The evaluation subsets are very small (6, 15 and 12 tasks), with horizons of 10 to 30 actions, and the corpus holds 58 Android programs.
- Transfer outside the training distribution hurt: a corpus built from 6 tasks reached 55.6% on 30 unseen OSWorld tasks, against a single unpaired cold run of about 67%.
- The LLM compiler is lossy: about 28% of Android programs lack a navigate-back step.
- The extraction notes nothing on safety, permissions or adversarial UI, and no external replication.

## See Also
- [[Verification Loops]] — prerequisite-for
- [[Proposer-Reviewer and Sidecar Gating]] — related
- [[Skill Verification Levels and the Biconditional Check]] — related (both gate what enters a trusted store)
