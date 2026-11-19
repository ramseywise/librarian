---
title: Open Pretrained Model Reports Comparison
tags: [llm, pretraining-and-data, comparison]
summary: "Setup-by-setup comparison of the OPT, BLOOM, GPT-NeoX-20B, OLMo and PaLM technical reports: data, size, hardware, architecture changes, instabilities, and what each release made public (all numbers self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zhang-2022-opt.md
  - data/raw/papers/2026-11-07-workshop-2022-bloom.md
  - data/raw/papers/2026-11-07-black-2022-gpt-neox-20b.md
  - data/raw/papers/2026-11-07-groeneveld-2024-olmo.md
  - data/raw/papers/2026-11-07-chowdhery-2022-palm.md
---

# Open Pretrained Model Reports Comparison

Five reports describe how a large decoder-only model was pretrained, and these five get rows here; [[GLM-130B Stability Recipe and INT4 Quantization]], [[Pythia Training Suite and Memorization]], [[LLaMA 1 and Llama 2 Open Foundation Models]] and [[GPT-3 and Few-Shot In-Context Learning]] have their own. All figures are the papers' own.

| Model | Sizes | Pretraining data | Hardware and parallelism | What was released |
|---|---|---|---|---|
| OPT | 125M to 175B (8 sizes) | English corpus of about 180B tokens drawn from RoBERTa's data, part of the Pile and PushShift Reddit | OPT-175B on 992 A100-80GB, FSDP plus Megatron tensor parallelism, FP16 weights | models 125M to 66B, OPT-175B on request, logbook, metaseq code |
| BLOOM | 560M to 176B | ROOTS, about 341B tokens plus 25B repeated; 46 natural and 13 programming languages | 384 A100 80GB on Jean Zay, Megatron-DeepSpeed, 3D parallelism with ZeRO stage 1 | weights under the Responsible AI License, code under Apache 2.0 |
| GPT-NeoX-20B | 20B | the Pile, 150,000 steps at batch about 3.15M tokens | 96 A100-40GB, tensor parallel 2, pipeline parallel 4 | weights, checkpoints every 1000 steps, gpt-neox code |
| OLMo | 1B and 7B | 2T-token sample of Dolma (2,668B tokens in total) | LUMI (AMD MI250X) and MosaicML (NVIDIA) clusters, FSDP/ZeRO, bf16 | weights, Dolma, code, 500+ checkpoints, logs, SFT and DPO adaptations; Apache 2.0 |
| PaLM | 8B, 62B, 540B | 780B-token single-epoch mixture (795B for 62B) | 6144 TPU v4 chips across two pods with Pathways, no pipeline parallelism | not stated |

## Architecture and tokenizer choices

- **OPT** uses GPT-3-style decoder-only transformers with AdamW and GPT-3 hyperparameters.
- **BLOOM:** 70 layers, ALiBi position embeddings and an embedding LayerNorm. In 1.3B ablations, ALiBi trained more smoothly and scored better downstream than learned or rotary positions. The byte-level BPE vocabulary has 250,680 entries, 200 of them reserved, and its size was chosen so it divides by 128 and by 4 under tensor parallelism. On Universal Dependencies treebanks, fertility is 11% lower than the monolingual CamemBERT tokenizer for French and 13% higher than the monolingual Arabic BERT tokenizer for Arabic, which overshoots the authors' 10-point target.
- **GPT-NeoX-20B:** 44 layers, hidden 6144, 64 heads; rotary embeddings on 25% of dimensions, parallel attention and feed-forward (`x + Attn(LN1(x)) + FF(LN2(x))`), all dense layers, and a newly trained BPE tokenizer with 50257 tokens, fitted on the Pile. On the Pile validation set it needs roughly 10% fewer tokens than GPT-2's tokenizer (5% fewer once whitespace tokens are excluded) and about as many on C4. One Python snippet encodes to 39 tokens instead of 55. In Mesh Transformer JAX the parallel layout raised throughput by 15% with similar early loss. Hyperparameters were interpolated from GPT-3.
- **PaLM:** a parallel layer in which attention and the MLP each read a normalised copy of x and both outputs are added back to x, plus SwiGLU, multi-query attention, rotary embeddings and Adafactor, each borrowed from cited work. Going parallel cost a little quality at 8B; the authors assumed no loss at 540B, extrapolating from the smaller runs.
- **OLMo:** decoder-only, AdamW. Adaptation is Tulu-style SFT, then DPO on UltraFeedback.

## Instabilities and compute

- OPT-175B was restarted by hand at least 35 times in roughly two months, because of hardware failures. Divergences were handled by lowering the learning rate and restarting from earlier checkpoints, and lowering gradient clipping from 1.0 to 0.3 early helped stability.
- BLOOM's 104B preliminary runs with float16 on V100s diverged irreversibly; bfloat16 mixed precision on A100s fixed the instability. The best configuration hit 156 TFLOPs per GPU, half the 312 TFLOPs peak. The run lasted about 3.5 months and used 1,082,990 compute hours.
- NeoX reached 117 TFLOPS per GPU.
- PaLM 540B reached 46.2% model FLOPs utilization (57.8% hardware, with rematerialization) where the comparison figures are GPT-3 at 21.3%, Gopher at 32.5% and Megatron-Turing NLG at 30.2%. Two pods gave about 1.95x one pod's throughput. Loss spiked about 20 times despite gradient clipping; the mitigation was to restart and skip 200 to 500 batches.
- Carbon, as each paper reports it: OPT-175B about 1/7th of GPT-3's footprint; BLOOM about 81 t CO2eq in total (11 equipment, 25 energy, 45 idle), or 433 MWh and 25 t against OPT's 324 MWh and 70 t for training energy only; NeoX 31.73 t (43.92 MWh, 1830 hours); OLMo 239 MWh across both 7B runs and an estimated 69.78 tCO2eq for pretraining in all, treating the LUMI run as zero (it would be 3.54 tCO2eq at the hydro intensity of 0.024); PaLM 271.43 tCO2e.

## Evaluation highlights

- **OPT:** over 14 tasks its mean zero-shot accuracy tracks the GPT-3 trend; matches GPT-3 on 10 and underperforms on ARC Challenge and MultiRC. The authors observe it does not follow declarative instructions, is repetitive, and has a higher toxicity rate than PaLM or Davinci (RealToxicityPrompts).
- **BLOOM:** HumanEval pass@1 15.52% (pass@10 32.20%, pass@100 55.45%) against 28.81% for Codex-12B; the multitask-finetuned BLOOMZ scores 12.06% (see [[XP3, BLOOMZ and mT0]]). One-shot WMT14 en-fr BLEU 34.2 against 43.8 for supervised M2M-100; zero-shot BLEU ranges from 7.90 to 21.96 depending on the prompt. Swahili-Yoruba translation is very poor, with under 50k tokens of each in training.
- **GPT-NeoX-20B:** against FairSeq 13B it wins 22 of 32 evaluations, loses 4 and ties 6 (zero- and five-shot). LAMBADA zero-shot is 0.720 versus 0.683 for GPT-J; its weakest result is HellaSwag at 0.535 versus 0.554 for FairSeq 13B, four standard deviations lower. All models score close to zero on five-shot MATH.
- **OLMo:** the 2.46T-token OLMo-7B checkpoint averages 69.3 across 8 zero-shot core tasks (Catwalk rank classification), where Llama 2 7B gets 70.5, MPT-7B 69.8 and Pythia 6.9B 63.0; OLMo-1B 60.4 against 59.4 for TinyLlama 1.1B and 54.5 for Pythia 1B. Decaying the learning rate linearly to 0 over 1000 more steps boosted perplexity and end-task results. With SFT and DPO, OLMo reaches 46.2 on 0-shot MMLU versus 28.3 for the base. On ToxiGen the base OLMo-7B is toxic 81.4% of the time, a rate that falls to 14.4 after SFT and 1.7 after DPO. The authors say later data and training raised MMLU by 24 points to 52% in a later version, not the paper's model.
- **PaLM:** 540B beats prior best on 28 of 29 English tasks few-shot; MMLU 5-shot 69.3 against 67.5 for Chinchilla 70B (8B 25.3, 62B 53.7). In BIG-bench, around a quarter of the 150 tasks jump by more than 10 points between 62B and 540B, measured against a log-linear projection from 8B to 62B. GSM8K with 8-shot chain of thought: 54% without a calculator and 58% with, against 17% without chain of thought. Memorization of 50-token continuations is 1.6% at 8B and 2.4% at 540B; examples seen over 500 times exceed 40%. Continuing PaLM 62B to 1.325T tokens on a refreshed dataset raised MMLU from 53.7 to 62.8, still short of 540B; repeating data did not help.

## Limits

- OPT: no toxicity or bias mitigation (the authors say the technology is too immature for commercial deployment); validation sets are tiny (CB 56, BoolQ 277, WSC 104) so scale trends are erratic; the effect of mid-run changes cannot be isolated; the carbon figure covers only the final run, while ablations, baselines and downtime roughly double total cost; the OPT-175B training-token count is not stated directly (learning rate decays over 300B tokens against a roughly 180B-token corpus). The Fig 4 caption says OPT one- and few-shot lags GPT-3 while the text says similar on average. The models are English-dominant and likely under-trained.
- BLOOM: the embedding LayerNorm steadied training but hurts zero-shot generalisation, and bfloat16 may make it needless; ablations were run at 1.3B and 6.7B, where outlier features may not carry over; the learning-rate decay never finished and the last 25B tokens were repeated data; mixture-of-experts and state-space designs were out of scope; prompts were not tuned.
- GPT-NeoX-20B: no deduplication tested, no coding evaluation, unintended untied layer norms, GPT-3 five-shot not run, the largest unknown is how the Pile differs from GPT-3's data, single run.
- OLMo: English-only data that can include toxic, personal and copyrighted text; no logs of failed runs; the Tulu mix was designed for Llama and a gap to Tulu 2 remains; carbon figures are lower bounds; code perplexity may be underestimated by contamination.
- PaLM: nothing ablates model size against token count or data quality, and the authors call 62B on 7T tokens against 540B on 780B an open question; only three scales support the discontinuity analysis; single runs; loss spikes had no principled fix; bias and toxicity analyses are English-only and template-based; the Codex comparison is not controlled; some subcorpora repeat data past 780B tokens, and the GPT-3 baselines are the models described in the GPT-3 paper.
- The reports use different benchmarks, prompts and carbon accounting, so the rows are not directly comparable.

## See Also

- [[GPT-3 and Few-Shot In-Context Learning]] — prerequisite-for
- [[Pythia Training Suite and Memorization]] — related (same Pile and GPT-NeoX codebase)
- [[GLM-130B Stability Recipe and INT4 Quantization]] — alternative-to
- [[LLaMA 1 and Llama 2 Open Foundation Models]] — alternative-to
- [[XP3, BLOOMZ and mT0]] — extends (BLOOM multitask finetuning)
- [[Transformer Architecture]] — prerequisite-for
