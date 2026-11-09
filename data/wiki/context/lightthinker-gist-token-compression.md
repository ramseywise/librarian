---
title: "LightThinker Gist-Token Compression"
tags: [context, pattern]
summary: "LightThinker trains a model to compress each finished thought into a few gist tokens and drop the text; on Qwen it cost 1% accuracy for 26% less time and 70% lower peak tokens, and LightThinker++ adds commit, expand and fold primitives (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhang-2025-lightthinker.md
  - data/raw/papers/2026-11-06-zhu-2026-lightthinker.md
---

# LightThinker Gist-Token Compression

Reasoning models fill their own context with thought tokens. LightThinker compresses inside the reasoning trace itself.

## LightThinker

After each thought, a compression trigger leads to a few cache (gist) tokens, an output token and the next thought; the original thought text is discarded and later steps see only the compressed content. Compression and generation are separate steps. It is trained by supervised fine-tuning on a 17k-example set, on Qwen2.5-7B and Llama3.1-8B starting from R1-Distill.

Results (self-reported), averaged over GSM8K, MMLU, GPQA and BBH with greedy decoding and a 10240-token output cap:
- Qwen: accuracy 62.90 to 62.80, time 13.68h to 10.17h, peak tokens 4336 to 1289, and the Dep metric (area under the context-length curve) 16.6M to 3.7M.
- Llama: accuracy went from 71.25 to 66.85, time from 10.42h to 10.34h, and peak tokens from 3571 to 1055. The time saving is negligible and the accuracy cost larger.
- Splitting at thought boundaries beat compressing every 6 tokens into 2 by 6.2% (Qwen) and 5.6% (Llama). An eviction baseline kept accuracy but was 51% (Qwen) and 72% (Llama) slower than vanilla.

## LightThinker++

Implicit compression is lossy and irreversible, so LightThinker++ gives the model explicit memory primitives: commit archives a step as a summary, expand restores the raw step, fold hides it again. Trained by supervised fine-tuning on teacher trajectories.
- Throughput setting, Qwen2.5-7B: accuracy 60.02 against 59.62 for a vanilla fine-tune on the same data, peak tokens 3120 to 940 (-69.9%) (self-reported).
- Removing expand and fold dropped accuracy from 60.1% to 53.6% (self-reported).
- Agentic, a fine-tuned 30B mixture-of-experts model, Pass@1 changed on xBench-DeepSearch from 38.3 to 44.0, on BrowseComp-ZH from 31.5 to 36.9 and on BrowseComp-EN from 16.0 to 18.1 (self-reported).

## Limits

- Tested on models of 7-8B for reasoning and one 30B model for agents; it needs fine-tuning, so it is not a prompt-only technique.
- LightThinker++ is compared only with its own fine-tuned baseline, not with other context-management agents. The authors' "semantic denoising" account is only a hypothesis. A case study shows implicit compression dropping numbers, and it degrades on dense hard-logic traces.
- The sizes of the MMLU and BBH subsets are not stated, and the tables use different time units.

## See Also
- [[Context Compaction]] — prerequisite-for
- [[Focus Active Context Compression]] — alternative-to
- [[AgentFold Context Folding]] — alternative-to
- [[Reasoning State Pass-Back]] — related
