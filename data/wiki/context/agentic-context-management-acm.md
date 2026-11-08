---
title: Agentic Context Management (ACM)
tags: [context, concept]
summary: ACM gives the agent two tools, one to summarise everything since the last call while saving the raw messages to disk and one to query them by id, so the agent chooses when to compress; post-training a 9B model on it lifted BrowseComp-Plus Pass@1 from 0.635 to 0.727 (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2026-acm.md
---

# Agentic Context Management (ACM)

Li et al. (CMU and Meta, 2026) move the compression decision from a fixed threshold to the agent.

## Mechanism

- `manage_context` summarises everything since its previous call and stores the raw messages on disk under a summary id.
- `query_memory` retrieves stored messages by that id, so detail dropped from a summary can be recovered.
- The agent decides when to call, which gives a sawtooth in context size. The contrast is a separate summary agent forced at a fixed fill level (the 90% in the paper's figure is only an example).
- Training: a Qwen3.5-9B student, with trajectories from a Qwen3.5-397B-A17B teacher.

## Results (self-reported)

BrowseComp-Plus Pass@1 (150 test and 680 training questions): ReAct scores 0.570 and ReSum 0.608, while ACON reaches 0.614 and ACE 0.589. ACM scores 0.635 untrained and 0.727 after post-training, a 27% relative gain. Peak context was 63k tokens for ReAct, 68k for ReSum and 54k for ACM.
- DeepSearchQA rose from 0.367 to 0.425 while peak tokens went from 46K down to 41K. SWE-Bench Verified rose from 0.489 to 0.530 with peak tokens from 59k down to 50K.
- Untrained GPT-5.5 makes almost no calls to the tools. Pass^4 rose from 34.1 to 59.3 and Pass@4 from 73.5 to 82.0 for the trained model.
- Ablation: distillation alone 0.623, ACM data alone 0.727, both 0.734.

## Limits

- It needs a base model capable of long rollouts. Qwen3-4B-thinking collapsed into two-turn rollouts (3.4% against 57.3% for the 9B). Baselines were re-implemented.
- The extraction notes that the actual threshold is never stated and that there are no intervals, cost or latency figures, prefix-cache analysis, other student sizes or comparison against a tuned threshold. The benefit of trigger timing is not separated from the benefit of lossless retrieval.

## See Also
- [[Learned Proactive Compaction]] — alternative-to
- [[Context Compaction]] — prerequisite-for
- [[Scroll Event Log and Eviction Index]] — related
- [[PRO-LONG Programmatic Memory]] — related
