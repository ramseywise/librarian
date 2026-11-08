---
title: Agent Primitives Latent Composition
tags: [harness, pattern]
summary: Agent Primitives reduces multi-agent systems to three reusable blocks (review, voting and selection, planning and execution) that pass KV-cache state instead of text and are composed per query by an LLM organizer; reported gains are 12.0 to 16.5 points over one agent on Qwen3 models (self-reported, ICML 2026).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jin-2026-agent-primitives.md
---

# Agent Primitives Latent Composition

Jin et al. (UIUC, ICML 2026, arXiv 2602.03695) decompose multi-agent systems into three primitives
that each expose the interface of a single agent: Review (a solver and critic loop), Voting and
Selection (parallel solvers and a selector) and Planning and Execution (a planner and executor). An
LLM organizer chooses primitives and combines them for each query, guided by a knowledge pool of 45 structures
drawn from published systems. Primitives communicate by KV-cache state, and the authors report that
re-encoding positions (a RoPE offset) is needed when concatenating caches.

## Motivating tests (self-reported)

- Mid-context instruction injection (351 InfiniteBench examples, Qwen3-8B): compliance at the midpoint
  was 15.6% for natural-language communication against 73.3% for KV-cache.
- Injected irrelevant sentences (100 GSM8K problems, Qwen3-8B, synthetic noise): natural-language
  messaging gave accuracy of 100, 91, 73, 47 and 40% with 0, 1, 3, 10 and 25 added sentences, while the KV variant gave 100, 100, 100, 93 and 77%.

## Results (self-reported)

- Mean gain on eight benchmarks (math: AIME24/25, MATH, GSM8K; code: HumanEval+, MBPP+; medical: MedQA; science: GPQA-Diamond) and five
  backbones: +13.9 (Qwen3-4B), +16.5 (8B), +12.0 (14B), +6.6 (R1-Distill-Qwen-32B) and +6.3 points
  (R1-Distill-Llama-70B). Text-communicating multi-agent systems gained +2.4 to +7.3 on Qwen3-8B; the single-agent
  baseline there averaged 58.8 and primitives 75.3 (the +16.5 above). Composition beat the best single primitive by 3.5 to 7.0 points.
- Cost: about 3,350 tokens against 14,343 for text multi-agent on Qwen3-4B; latency about 1.3 to 1.6
  times a single agent. For Qwen3-14B and the distilled models tokens were within about 0 to 14% of single.
- Llama-3-70B workers with a GPT-5.2 organizer beat eight published methods (MATH 72.4 against single
  50.6; GPQA 53.2 against 33.6-40.2); some published methods fell below the single agent.
- Ablations: random structure choice cost 6.6 to 12.4 points; removing the pool cost 4.9 to 11.9.
  Text to KV gave +10.0 to +13.4 on AIME25 (Qwen3-8B). Without position re-encoding, Llama-based
  backbones collapsed (for example 85.3 to 31.1 on HumanEval+).

## Limits

- Accuracy, token and latency numbers are from different runs; single-run tables with no seeds.
  Whether the pool held in-domain entries for the comparison benchmarks is not stated, and the pool
  contains structures from the same baselines. The latent-channel ablation covers one benchmark and one
  model; the noise tests are synthetic.
- Extraction note: the accuracy rows for the two organizer settings in the cost table are identical,
  so one accuracy figure is likely reused.
- The extraction lists inconsistencies in the source: the Table 8 caption names Qwen3-4B and 8B but
  the table holds Qwen3-4B and 14B; the Table 3 caption says "three models" but the table covers
  Qwen3-8B plus the two distilled models; the extracted Table 14 repeats one distilled-model block
  under the same label and omits one latency; the ablation is named "KV PoPE" in prose yet
  "RoPE" in the table, and the extraction reads it as RoPE.
- A competing latent system is cheaper but unstable across backbones (a 10.1-point average loss on one).

## See Also
- [[Harness Orchestration]] — prerequisite-for
- [[Multi-Agent Context]] — prerequisite-for (agents sharing state)
- [[Multi-Agent Topology Patterns]] — related
- [[Conductor Learned Orchestration]] — alternative-to
