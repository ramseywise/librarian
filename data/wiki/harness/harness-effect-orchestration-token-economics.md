---
title: Harness Effect on Token Economics
tags: [harness, concept]
summary: A vendor study that swapped the orchestration layer (cache-stable prefix, compaction, offload, delegation) on 22 enterprise tasks and 6 models and reported lower cost per task at about the same completion; no ablation.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ali-2026-harness-effect.md
---

# Harness Effect on Token Economics

Ali et al. (Writer, Inc., an October 2026 preprint) claim that token cost is driven more by how orchestration is done (assembling context, caching, compacting, delegating, retrying) than by the choice of model. Both the tested harness and the Palmyra X6 model come from the authors, and the extraction notes the last author is a co-founder; treat the figures as vendor-reported.

## Setup and results

Setup behind every number: 22 locked enterprise tasks; six models, namely Palmyra X6 plus Sonnet 4.6, Gemini 3.1, and also Flash 3.5, Qwen 3.6 and GLM 5.1; two arms, a production loop frozen on 2026-06-07 versus the Writer Agent Harness. An LLM panel judges, one pinned price table sets prices, and the baseline was run a single time.

- Per task, cost dropped 41% (from $0.21 down to $0.12). The median wall-clock time fell by 44%, from 48 s to 27 s, and tokens dropped 38%, from 14.2k to 8.8k (self-reported).
- Completion of tasks rose from 0.78 to 0.81; at n=22 the authors call that parity (self-reported).
- Cost per model fell by between 33% (Gemini 3.1) and 61% (Flash 3.5) (self-reported). Under the baseline, picking the cheapest model over the dearest saved 36%.
- Of 48 capability-by-model cells, 30 improved, 11 were unchanged and 7 regressed, all on Flash, Qwen and GLM (self-reported).
- For multi-step research synthesis, the most expensive task, cost went from $0.61 to $0.33 and quality from 0.80 to 0.60 (self-reported).
- One identical-prefix call read 7,876 of 7,886 prompt tokens from cache. The extraction stresses this is a single call, not a benchmark.
- Sub-agent delegation scores (Palmyra 0.86 down to Qwen 0.42) have no baseline arm.

The authors' framing is that the harness sets the floor while the model sets the ceiling, and that an orchestration feature has a capability floor below which it produces failures. The design is described through six named mechanisms: a prefix that keeps the cache stable, structured compaction, offloading of context behind a firewall for sub-agents, suspension that is durable, governance of spend on failures, and invariants that hold across models. These are asserted from the design, not tested.

## Limits

- No ablation: nothing is removed from the harness, so savings are not attributed to any mechanism. It is a whole-system swap.
- With n=22, quality claims are only directional; the baseline is a single run without variance; one vendor pair and one enterprise-assistant workload.
- The correlation of 0.99 between leverage and baseline score rests on 6 models.
- The extraction notes the sub-agent result has no single-agent comparison, so the paper does not test whether delegation helps.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Harness Anatomy]] — prerequisite-for
- [[Harness Orchestration]] — related
