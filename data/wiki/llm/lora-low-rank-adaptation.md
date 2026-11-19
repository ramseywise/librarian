---
title: LoRA Low-Rank Adaptation
tags: [llm, fine-tuning, concept]
summary: "LoRA freezes the pre-trained weights and trains a rank-r product BA added to selected weight matrices; on GPT-3 175B it cut trainable parameters about 10,000 times and matched or beat full fine-tuning on three tasks (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-hu-2021-lora.md
---

# LoRA Low-Rank Adaptation

Hu, Shen, Wallis et al. (preprint, arXiv v2, October 2021) ask whether a big pre-trained model can be adapted for a downstream task through low-rank weight updates alone, keeping quality near full fine-tuning while cutting memory and adding no inference latency. Their hypothesis is that the weight change during adaptation has a low intrinsic rank, motivated by [[Intrinsic Dimension of Fine-Tuning]].

## Mechanism

- The pre-trained weight W0 is frozen. The update is the product BA, where r is small: B is d x r and starts at zero, A is r x k and starts as random Gaussian noise. The layer output is h = W0x + (alpha/r)BAx.
- Because B starts at zero, the update is zero at the start of training.
- In the experiments LoRA is applied only to the attention projection matrices (mostly the query and value projections); the MLPs stay frozen.
- Once training ends, BA can be summed into W0, which leaves inference cost the same as for a fully fine-tuned model. Adapter layers, by contrast, added inference latency in the authors' measurement (table below).
- alpha/r scaling: alpha does not change with r; the authors say setting alpha behaves roughly like setting the learning rate, which means less retuning as r varies.
- Many small modules can share one base model, and switching tasks means swapping A and B. Frozen parameters need no gradients or optimizer state, and the authors credit this with a hardware requirement up to 3 times lower under adaptive optimizers.

## Reported results (self-reported)

| Setup | Result |
|---|---|
| GPT-3 175B, Adam, vs full fine-tuning | trainable parameters down 10,000 times, GPU memory down 3 times |
| GPT-3 175B, r = 4 on query and value | checkpoint 350 GB down to 35 MB; the 350 GB base model is still needed at deployment |
| GPT-3 175B training VRAM | 1.2 TB down to 350 GB |
| GPT-3 175B, WikiSQL accuracy | 73.4 with 4.7M LoRA parameters, 74.0 with 37.7M, against 73.8 for full fine-tuning (single run, fluctuation about 0.5%) |
| GPT-3 175B, MNLI-m | 91.7 (4.7M LoRA) against 89.5 |
| GPT-3 175B, SAMSum Rouge | 53.8/29.8/45.9 against 52.0/28.0/44.5 |
| GPT-3 175B throughput | 43.1 tokens/s per V100 against 32.5 for full fine-tuning |
| RoBERTa-large, GLUE average (median of 5 seeds) | 89.0 with 0.8M parameters against 88.9 for full fine-tuning (355M, numbers from prior work) |
| DeBERTa XXL, GLUE average | 91.3 with 4.7M against 91.1 for full fine-tuning (1500M) |
| GPT-2 medium, E2E BLEU (mean of 3 seeds) | 70.4 with 0.35M trainable parameters; full fine-tuning with 354.92M scored 68.2 |
| GPT-2 medium adapter latency, batch 1, length 128 | AdapterH adds 30.3%; LoRA adds none |

In a low-data test on GPT-3 175B (MNLI with 100 training examples) LoRA scored 63.8, full fine-tuning 60.2 and prefix-embedding tuning 37.6, where chance is 33.3. Prefix methods degraded as special tokens increased (a drop beyond 256 tokens for prefix-embedding and 32 for prefix-layer), whereas LoRA stabilised as parameters grew. Combining LoRA with prefix-embedding tuning raised WikiSQL to 76.2 (302.1M parameters) but not MNLI.

## Which matrices and what rank

With an 18M parameter budget on GPT-3 175B, adapting both query and value (r = 4) gave WikiSQL 73.7 and MultiNLI 91.3, against 70.4 and 91.0 for the query alone (r = 8). A rank of one sufficed for adapting both on WikiSQL (73.4 at r = 1, 73.8 at r = 8). In the subspace analysis (layer 48 of 96) the leading singular direction found by A at r = 8 and at r = 64 overlapped, with normalised similarity above 0.5; the authors offer this as the explanation for why r = 1 works. The update also amplifies directions that W does not emphasise (factor about 21.5 at r = 4 for the query matrix in that layer). On GPT-2 medium the best rank was between 4 and 16 depending on the metric, with hyperparameters tuned at r = 4.

## Limits

- After merging, serving several tasks in one batch is awkward, since each task has its own A and B; keeping them unmerged and choosing per input is possible only where latency is not critical.
- Only attention weights were adapted; MLP, LayerNorm and bias adaptation are left to future work, and the choice of matrices is heuristic.
- A small r is not expected by the authors to work for all tasks; for a task in a language far from the pre-training language, r near d_model might be required.
- The GPT-3 results are single runs, with one typical variance figure given instead of error bars per entry; the WikiSQL fluctuation (+/-0.5%) is the same size as the gap to full fine-tuning.
- Several baseline figures are taken from earlier papers whose setups differ, and not every baseline appears in every experiment.
- Hyperparameters in the rank study were tuned at r = 4, which may leave other ranks looking worse than they could be. How optimal rank relates to model size is open, and why LoRA works is not established.
- The training memory saving still requires the whole frozen base model to sit in VRAM.
- The evaluation is GPT-3, RoBERTa and DeBERTa era, with no instruction-tuned, chat or quantised base models.

## See Also
- [[Intrinsic Dimension of Fine-Tuning]] — prerequisite-for (motivates the low intrinsic-rank hypothesis)
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for (the family LoRA belongs to)
- [[QLoRA 4-Bit Quantized Finetuning]] — extends
- [[DoRA Weight-Decomposed Low-Rank Adaptation]] — extends
- [[T-Few and (IA)3 Few-Shot PEFT]] — alternative-to (LoRA is a baseline there)
- [[AdapterDrop Efficient Adapters]] — alternative-to (adapters add inference latency that LoRA avoids)
- [[Prefix-Tuning and Prompt Tuning]] — alternative-to
