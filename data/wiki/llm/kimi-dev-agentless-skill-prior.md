---
title: Kimi-Dev Agentless Skill Prior
tags: [llm, agent-training, pattern]
summary: "Kimi-Dev trains a 72B model on single-turn Agentless SWE tasks (mid-training, SFT, RL) and then adapts it to a multi-turn SWE-Agent with a few thousand trajectories; the RL-stage prior matched the base prior's best score with far fewer agent tokens (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-yang-2025-kimi-dev.md
---

# Kimi-Dev Agentless Skill Prior

Kimi-Dev (Yang, Wang and colleagues, Moonshot AI with THU and PKU; arXiv v3 December 2025) argues that training on the [[Agentless Localize-Repair-Validate]] workflow gives a better starting point for a multi-turn SWE agent. Four priors from Qwen2.5-72B-Base are compared: Base, MT (after mid-training), SFT (Agentless long-CoT SFT) and RL (after Agentless RL).

## Recipe

- **Mid-training:** roughly 150B tokens made of about 50B of diffs in Agentless form, 20B of PR commit packs and 20B of synthetic data repeated four times, followed by a 2,000-example SFT activation. BugFixer pass@1 improved monotonically at 50B, 100B and about 150B tokens.
- **RL:** A policy-gradient method taken from Kimi k1.5, baselined on the mean over rollouts, rewarded only by the test-execution result (0 or 1) with no format or process signal. Prompts that never reach a pass at 16 samples are dropped, then 500 hard ones are added back every 100 steps, and positive examples are reinforced late in training. Scale: 1,200 starting prompts, 10 rollouts for each of 1,024 problems, 64k context, and a Kubernetes sandbox running over 10,000 instances at once.
- **Test-time self-play:** BugFixer patches are scored by tests from a TestWriter. Performance rose from 48.0% to 60.4% as patch-test pairs grew from 1x1 to 40x40, and 3 patches x 3 tests already beat majority vote over 40 patches. The extraction records the selection score as a sum of two ratios, failing-test and passing-test counts for patch i over the corresponding totals (Eq. 1).
- **Agent adaptation:** fine-tune on nested subsets (100 to 2,000, up to 5,016) of SWE-smith Claude 3.7 Sonnet trajectories, training at 64K context and inference with up to 128K tokens and 100 turns.

## Results (self-reported)

Setup: SWE-bench Verified, pass@1 at temperature 0 unless stated.

- Agentless: 60.4% using self-play over 40 patches and 40 tests, the best workflow method listed. Comparators: SWE-SWISS 32B at 58.2, DeepSeek-R1-0528 671B at 57.6, MiniMax-M1 at 56.0.
- SWE-Agent after SFT on 5k public trajectories, no agentic RL: 48.6%. Table 2 lists far stronger agent systems: Qwen3-Coder at 69.6, Kimi-K2-0905 at 69.2, gpt-oss-20b at 60.7 and Devstral-Small at 53.6. Claude 3.5 Sonnet 241022 is at 49.0.
- The adapted agent's pass@10 (74.0%) is higher than the Agentless model's pass@30 (73.8%).
- **Adaptation efficiency:** the RL prior needs 2^23 agent-SFT tokens to reach the top pass@1 of the Base prior, which uses 1.5x2^28 (about 64x fewer, the extraction's arithmetic). The SFT prior drops sharply at 200 trajectories. The authors guess that those trajectories collapsed onto one data mode so the prior memorised them, whereas the RL prior transferred better. That is an explanation, not a tested mechanism, and SFT beat RL at zero-shot, possibly because the RL prior overfits the Agentless format.
- **Horizon:** with all 5,016 trajectories, the RL prior keeps improving past 70 turns (SFT diminishes near 70, MT near 60, Base near 50). The stage-3 cutoff resolves 484 cases for Base against 605 for RL, a reflection gain of +94 against +113 (counts over 3 runs, pass@3; stages annotated by kimi-k2-0711-preview).
- **End-to-end SWE-Agent RL** run for 300 steps at batch 256, begun after one agent-SFT gradient step of 2^21 tokens. There, the RL prior finishes a little higher than the SFT prior, while the MT prior collapses (pass@1 under 2% after 10 steps). Pass@1 averaged over 5 runs.
- **Out of distribution** (SWE-bench-Live and SWE-bench Multilingual, 300 tasks each): the SFT and RL priors lead Base chiefly when agent data is scarce, and more trajectories close the gap.

## Limits

- One model family (Qwen2.5-72B) for the prior comparison; 14B only for RL scaling. No seeds or intervals for the adaptation sweep.
- The RL here is on single-turn Agentless tasks rather than agent trajectories, and the contrast is mid-train plus SFT against mid-train plus SFT plus RL, so it is not a pure SFT-versus-RL test. The RL prior also receives extra data and compute. The difference is small in most settings, including end-to-end RL, and no significance test is given.
- The memorisation account rests on one sweep point.
- TestWriter produces false positives when test coverage is weak, and self-play remains under pass@N scored with ground-truth tests. The reflection and BugFixer skill measures are coarse, and the TestWriter prior was not isolated.
- The agent SFT trajectories are Claude 3.7 Sonnet runs in synthetic SWE-smith environments, so imitating a proprietary model may contaminate the prior effect. The parallel-scaling result is preliminary.
- Python-centric training environments; no claim outside SWE.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Agentless Localize-Repair-Validate]] — prerequisite-for
- [[PivotRL Pivot-Turn Agentic RL]] — related (another SFT-versus-RL comparison on agentic tasks)
- [[Repository-Level Coding Benchmarks]] — related
