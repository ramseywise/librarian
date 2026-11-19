---
title: PivotRL Pivot-Turn Agentic RL
tags: [llm, agent-training, pattern]
summary: "PivotRL profiles turns of expert trajectories, keeps only the turns where sampled actions disagree, and runs short local RL with a verifier that accepts any acceptable action; it beat same-data SFT on three of four agentic benchmarks and kept out-of-domain scores near base (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-yi-2026-pivotrl.md
---

# PivotRL Pivot-Turn Agentic RL

PivotRL (Yi, Mosk-Aoyama, Huang and colleagues, NVIDIA and UC Berkeley, arXiv March 2026) post-trains an agent from existing expert trajectories without running full end-to-end rollouts. Its motivation is a count: on tau2-bench and SWE-Bench, 71% of randomly chosen turns carry zero GRPO signal, since sampled actions all pass or all fail.

## Mechanism

1. **Profile offline.** Run K rollouts per turn under a frozen reference policy.
2. **Keep pivots.** A turn is kept when the reward variance is above 0 and the mean is below a difficulty threshold lambda_diff.
3. **Short local RL.** Run GRPO on one-turn rollouts from those states, using a functional reward that is 1 when the action lies in the set M(s) of acceptable actions, rather than exact string match.

The verifier differs by domain. The SWE verifier matches the tool-call name only, Terminal uses a schema check plus string similarity plus an LLM judge, and details for tau2 and BrowseComp are thin.

The paper's idealised theory (finite action space) says the natural-gradient norm along the KL path scales with the square root of the reward variance (divided by beta squared), which supports the variance filter, and that the functional reward moves probability mass to the acceptable set while preserving ratios inside it and inside its complement. The authors use the second result to explain out-of-domain retention; it assumes task-unrelated actions fall in the complement.

## Results (self-reported)

Setup: base model Qwen3-30B-A3B-Thinking-2507; four separate single-domain runs sharing prompts and expert trajectories; NeMo-RL with NeMo-Gym; SWE scored as mean@3 in OpenHands; seed count not given.

- tau2: base 44.35, SFT 58.44, PivotRL 63.81.
- SWE-Bench Verified: base 19.07, then SFT 37.40, and PivotRL 32.67.
- Terminal-Bench: base 5.42, SFT 13.75, PivotRL 20.00.
- BrowseComp: base 2.50, SFT 1.50, PivotRL 11.30.


- Average gain over base is +14.11 for PivotRL and +9.94 for SFT, and SFT wins on SWE-Bench Verified.
- On 8 non-agentic benchmarks, averaged over the four runs, SFT changes scores by −9.83 and PivotRL by +0.21, with no PivotRL benchmark worse than −3.12. The worst SFT case is after terminal training, where AIME25 falls from 86.04 to 21.56.
- Compute on SWE-Bench Verified, same model: both reach 32.67% with about 133K rollout turns for PivotRL (step 130, batch 64 prompts x 16 generations, one turn per sample) against about 542K for end-to-end RL (step about 72, batch 16 x 32, 12 to 25 turns per trajectory), around 4x fewer turns and 5.5x less wall-clock.
- Ablation on tau2 only: without pivot filtering 59.68; with a strict exact-match reward 57.34, below same-data SFT at 58.44.
- Production use in Nemotron-3-Super-120B-A12B: tau2 went from 48.00 to 64.00. On SWE-Bench Verified the score climbed from 12.87 up to 61.33, on Terminal-Bench 1.1 Core from 23.33 to 34.17, and on BrowseComp from 13.03 to 25.04. That RL stage also included other environments, so none of this is isolated to PivotRL.

## Limits

- No seeds or intervals are reported, and the paper has no limitations section. The ablation covers tau2 only.
- The end-to-end RL comparison is on SWE-Bench Verified with one 30B MoE, matched at one accuracy point; end-to-end RL's final accuracy and out-of-domain results are not reported. The cost of offline profiling is not counted in the 4x.
- The SFT arm is single-domain full training, and there is no mixed-data or replay-regularised SFT arm to show whether the out-of-domain loss could be avoided more cheaply.
- PivotRL needs a domain verifier (the SWE one is deliberately coarse), plus SFT trajectories. Some data is internal to NVIDIA (SWE trajectories from MiniMax-M2.5).
- The theory is idealised and the out-of-domain argument is an assumption.
- Internal inconsistency: the introduction gives the SFT out-of-domain change as −9.48 while Table 2 and the text say −9.83.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Kimi-Dev Agentless Skill Prior]] — related (a different SFT-versus-RL comparison on SWE tasks)
- [[Terminal-Bench]] — related (one of the four benchmarks scored)
