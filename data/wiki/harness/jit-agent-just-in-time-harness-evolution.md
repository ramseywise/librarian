---
title: JIT-Agent Just-in-Time Harness Evolution
tags: [harness, pattern]
summary: A trained 27B generator writes a task-specific harness (memory, planning, capability and action modules) for each instance at inference time, with training rewarding quality, latency and cost together.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhang-2026-jit-agent.md
---

# JIT-Agent Just-in-Time Harness Evolution

JIT-Agent (Zhang et al., a September 2026 preprint) generates a harness per task instead of searching for one in advance. A trained generator (Qwen3.6-27B base) emits a harness for each incoming task at inference time; the generator is frozen at deployment. In static inference it produces N candidate harnesses and runs only the selected one. In streaming mode, a bank of harnesses is revised using execution feedback, with the weights left untouched.

## Four-module decomposition

The paper splits a harness into four modules, each with a fixed schema: memory (compressing history into a view), planning (forming a local directive), capability orchestration (choosing the active tools and skills) and action (updating controller state and emitting the next action). The runtime dependency order is memory, planning, capability, action. Existing systems are mapped into this protocol; for instance ReAct is full-history memory with no planner and a full tool registry, while Codex and OpenCode combine compact memory with todo planning.

## Training

- Stage I: SFT followed by DPO on validated harnesses that a teacher model generated. A preferred harness must earn more reward and not regress on latency or cost.
- Stage II: repair, trained on those failures that can be made executable inside two rounds.
- Stage III: Evo-GDPO, normalising reward, latency and cost advantages separately, and efficiency counts only when the incumbent's reward is kept. A candidate stays in the bank only when it matches the frontier and strictly improves along one dimension.

The bank starts with 13 seed harnesses, among them ReAct, Plan-and-Execute and ReSum.

## Results

All numbers are self-reported by the authors.

- Nine benchmarks, four task types: replacing each vanilla model's default scaffold with a JIT harness improved all 18 backbone-benchmark pairs; the average moved from 74.1 to 81.8 for GLM-5.2, and from 66.7 to 75.5 for DeepSeek-V4-Flash.
- With the backbone fixed (DeepSeek-V4-Flash and Qwen3.6-Flash on DeepSearchQA, xBench-DS and AgentIF), JIT harnesses were best in 4 of 6 settings against Claude Code, Codex, OpenCode, Hermes and NanoBot, and reduced cost by between 14.9 and 54.1% relative to the cheapest fixed harness, averaging 36.0%. In the remaining two settings they scored lower, by 3.1 and 3.9 points.
- One cited case: on V4-Flash xBench-DS against NanoBot, tokens fell from 527K to 212K, cost from $0.075 to $0.039 and the score rose from 78.0 to 82.0.
- Six backbones, four benchmarks (50 to 100 examples each): JIT beat a fixed ReAct harness in 24 of 24 comparisons, +7.6 on average.
- The largest gains were on long-horizon planning, such as DeepPlanning-Shopping (59.1 to 83.9 on V4-Flash).

Appendix case studies describe task-shaped harnesses, for example a final-answer tool withheld until a completeness check passes, a bounded research sub-agent with a fact-graph memory, and a step retry limited to two attempts. These are qualitative.

## Limits

- The three training stages are not ablated, and no per-module analysis shows which of the four modules produces the gains.
- Each baseline runs on its model's default scaffold, which means gains blend harness effects with scaffold differences.
- Fig 4 relies on small subsets without variance or confidence intervals, and Table 3 spans only 3 benchmarks and 2 backbones.
- Train and test overlap is not discussed, and the generator's own run cost is not reported separately.
- Table 4's classification of competing systems is the authors' own. The extraction notes a text glitch in Table 2 ("83.961.3").

## See Also

- [[Harness Anatomy]] — prerequisite-for
- [[Meta-Harness End-to-End Optimization]] — alternative-to (searches for a harness ahead of time)
- [[Agentic Harness Engineering]] — alternative-to
- [[Harness-R1 Learned Harness Editing]] — alternative-to
- [[Budget Tracker and BATS]] — related (cost-aware harness behaviour)
