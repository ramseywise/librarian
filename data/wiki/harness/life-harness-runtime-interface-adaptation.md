---
title: LIFE-Harness Runtime Interface Adaptation
tags: [harness, pattern]
summary: Four runtime layers (environment contract, procedural skills, action realisation, trajectory regulation) are evolved by a stronger LLM around a frozen small solver, so the interface is adapted instead of the model.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xu-2026-adapting-interface-not-model.md
---

# LIFE-Harness Runtime Interface Adaptation

LIFE-Harness (Xu et al., an October 2026 preprint, Peking University) adapts the runtime interface around a frozen model instead of its weights. The authors diagnose 393 failed training episodes of a Qwen3-4B-Instruct solver and conclude that most failures are interface mismatches rather than reasoning errors, with the share varying by environment. The extraction notes the pie-chart label mapping is scrambled, so the per-category shares are not given here.

## Four layers

1. **Environment contract**, before interaction: makes tool rules, policy constraints and pitfalls explicit.
2. **Procedural skill**, applied when the task is set up: skills distilled from training trajectories are retrieved with BM25, and only the top-1 skill is inserted into the system prompt.
3. **Action realisation**, between model output and execution: the layer returns either execute or block-with-message, repairs interface errors that are unambiguous, and blocks calls certain to fail.
4. **Trajectory regulation**, after feedback: detects repetition, stagnation, invalid retries and budget exhaustion, then appends a recovery message.

An evolution LLM (GPT-5.5) receives the training trajectories together with the existing harness, and suggests edits. A candidate must clear replay and interface checks, with at most 3 repair attempts, and is accepted only if accuracy strictly improves on that same training batch.

## Results

All numbers are self-reported. Setup: frozen Qwen3-4B-Instruct, seven AgentBench and tau-bench environments, six evolution rounds, temperature 0; tau-bench results use 3 runs per task and AgentBench one; one evolution run per method.

- Mean Pass@1 on AgentBench goes from 27.9 to 59.5, and on the tau suites from 36.3 to 71.0.
- Against automated harness search on the same setup: +28.7 points over Meta-Harness and +7.5 over AHE, with 8.5% and 68.4% fewer evolution tokens respectively. AHE comes out ahead on ALFWorld (89.0 against 88.1) and on Telecom (95.0 against 90.0).
- One harness evolved on the 4B solver and reused unchanged improved 132 of 144 settings across 18 open-weight backbones; gains were small or slightly negative on the strongest ones.
- Three frontier models improved on average, by 2.8 points for GPT 5.5, 4.4 for Opus 4.8 and 3.4 for Gemini 3.1 Pro, with flat or negative cells.
- In leave-one-layer-out tests, relative accuracy falls as follows: dropping action realisation costs Airline 61.7% and OS 59.6%; removing trajectory regulation costs ALFWorld 86.5%. Which layer matters depends on the environment. Removal only, no confidence intervals.
- Two released interface baselines (ALIGN, AgentSquare) often scored below no harness, but they were evaluated as released rather than under the same evolution conditions.

## Limits

- Text and API environments only; nothing is shown for GUI tasks, nor for open-ended areas like coding or browsing.
- The harness is environment-specific and must be re-evolved per environment, and contains heavily environment-specific code, so how much gain is domain engineering is open.
- Small tau test sets (Airline 20, Retail 40, Telecom 40); no seeds or confidence intervals.
- Cost counts only evolution LLM tokens; failure labels were LLM-annotated with human checks but no agreement statistics.
- Figures 3, 5 and 7 are scrambled in the extraction. Evolution-batch accuracy in Table 12 is noisy because the batch changes each round.

## See Also

- [[Harness Anatomy]] — prerequisite-for
- [[Harness-R1 Learned Harness Editing]] — alternative-to (trains a small editor for hook-based patches)
- [[Meta-Harness End-to-End Optimization]] — alternative-to
- [[Agentic Harness Engineering]] — alternative-to
- [[Tool Design as Harness Surface]] — related
