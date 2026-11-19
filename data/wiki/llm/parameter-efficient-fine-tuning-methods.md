---
title: Parameter-Efficient Fine-Tuning Methods
tags: [llm, fine-tuning, comparison]
summary: "The PEFT family compared: freeze the base model and train a small piece (adapters, a low-rank update, a prefix or prompt, bias terms, a representation intervention), plus the memory arithmetic and hyperparameter advice from Huyen's finetuning chapter."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch07-finetuning.md
  - data/raw/papers/2026-11-07-li-2021-prefix-tuning.md
  - data/raw/papers/2026-11-07-lester-2021-power-scale-parameter-efficient-prompt.md
  - data/raw/papers/2026-11-07-zaken-2022-bitfit.md
  - data/raw/papers/2026-11-07-zhang-2023-llama-adapter.md
  - data/raw/papers/2026-11-06-wu-2024-reft.md
  - data/raw/papers/2026-11-07-sun-2022-black-box-tuning-language-model.md
  - data/raw/papers/2026-11-07-dettmers-2023-qlora.md
---

# Parameter-Efficient Fine-Tuning Methods

Huyen (*AI Engineering*, chapter 7, a 2024 text) defines PEFT as getting close to full finetuning while training several orders of magnitude fewer parameters. The methods differ in what they leave trainable.

| Method | What is trained | Page |
|---|---|---|
| Adapters | Two small modules per transformer block (Houlsby et al., as cited by Huyen) | this page |
| LoRA | Two small matrices A and B whose product is the weight update; W stays frozen and the product is merged back after training | this page |
| QLoRA | LoRA adapters on a 4-bit quantised, frozen base | [[QLoRA 4-Bit Quantized Finetuning]] |
| DoRA | Another low-rank adapter method (see its page) | [[DoRA Weight-Decomposed Low-Rank Adaptation]] |
| Prefix-tuning, prompt tuning | Continuous vectors prepended to the input (prefix-tuning at every layer, prompt tuning at the embedding layer) | [[Prefix-Tuning and Prompt Tuning]] |
| BitFit | Only the bias terms (plus a classifier) | [[BitFit Bias-Term Fine-Tuning]] |
| LLaMA-Adapter | Prompts in the top layers behind a zero-initialised gate | [[LLaMA-Adapter Zero-Initialized Attention]] |
| ReFT | A learned edit of hidden states at chosen positions | [[LoReFT Representation Finetuning]] |
| Black-box tuning | A low-dimensional vector, found with no gradients | [[Black-Box Tuning for Language-Model-as-a-Service]] |

## Numbers Huyen reproduces from the papers

- Houlsby et al.'s adapters in BERT trail full finetuning by under half a point on GLUE (0.4%) with 3% of the parameters trained; tuning only part of BERT-large took roughly a quarter of its parameters to equal full finetuning there.
- Hu et al. report LoRA on GPT-3 175B equalling or exceeding full finetuning on several tasks with about 4.7M trained parameters (0.0027% of the full count). With a fixed 18M budget (0.01%), spreading rank 2 over all four attention matrices scored best on WikiSQL and MultiNLI, ahead of putting r=8 on one matrix or r=4 on two.
- LoRA adapter memory is small: 37.7 MB for GPT-3 175B at r=2 on query and key, against 350 GB of weights (16-bit, 18.87M parameters).
- Serving 100 per-customer models: with W of 4096 x 4096 (16.8M parameters) and rank 8, each adapter has 65,536 parameters, so 100 kept separate take 23.3M parameters against 1.68B merged. Huyen advises keeping adapters separate for multi-LoRA serving and merging for a single LoRA model.

## Memory arithmetic (worked examples)

- A 7B model trained in full with Adam at 16 bits takes 56 GB for the weights, gradients and optimiser states together (three values per trainable parameter), before counting activations.
- Inference memory for a 13B model stored at 2 bytes per weight is 31.2 GB, assuming activations plus the key-value cache add 20% over the weights.
- Gradients plus optimiser states for 13B trainable parameters at 2 bytes come to 78 GB; if only 1B parameters are trainable the figure is 6 GB.

## Practitioner guidance

- Huyen advises starting with LoRA and trying full finetuning afterwards, noting that with only a few hundred examples full finetuning may give no gain over LoRA.
- Ranks of 4 to 64 usually suffice, and a larger rank need not raise quality (Raschka's own tasks did best at r=256). Huyen suggests keeping the ratio of alpha to r within 1:8 to 8:1 and tuning both.
- Learning rate: search between 1e-7 and 1e-3, beginning at 0.1 to 1 times the rate pretraining ended on and pushing it up while the loss curve stays stable. Batches under eight can make training unstable (the author says she found no good explanation); accumulate gradients if memory forces small batches. Epochs: 1 to 2 when there are millions of examples, possibly 4 to 10 for thousands. The prompt's share of the loss defaults to 10%.
- Finetune for form and use retrieval for facts; if a model has both kinds of failure, start with retrieval. In Ovadia et al.'s current-events QA on Mistral-7B, the base model with RAG scored far above finetuned variants without it, and finetuning plus RAG scored below the base model with RAG. Across Mistral 7B, Llama 2-7B and Orca 2-7B, putting RAG on a finetuned model beat RAG on the base model for MMLU in 43% of cases. See [[RAFT Retrieval-Augmented Fine-Tuning]].
- Case evidence in the chapter: zero-shot GPT-4-0314 beat the 50B BloombergGPT on FiQA sentiment and ConvFinQA, a model that needed 1.3 million A100 GPU hours (estimated $1.3M to $2.6M for compute alone). Grammarly's finetuned Flan-T5 models, 60 times smaller and trained on 82,000 pairs, outperformed a specialised GPT-3 variant.
- Model merging (task vectors, TIES and DARE pruning before merging, depthwise scaling, as in SOLAR 10.7B, which grew a 7B model from 32 to 48 layers) is described as experimental.

## Limits

- Many of the chapter's tables are reproduced from other papers; its one experiment is a count of open issues in huggingface/peft.
- Written in 2024; the author states LoRA does not reach full finetuning and focuses on LoRA over attention matrices, which later work revised. Merging methods are called experimental and may become outdated.
- The chapter covers supervised and adapter finetuning; preference finetuning is only mentioned in the overview.
- Method pages cite single-paper results on different models and tasks, so the rows above are not a controlled comparison.

## See Also
- [[DoRA Weight-Decomposed Low-Rank Adaptation]] — instance-of (a LoRA variant)
- [[QLoRA 4-Bit Quantized Finetuning]] — instance-of (LoRA on a quantised base)
- [[Prefix-Tuning and Prompt Tuning]] — instance-of (input-side PEFT)
- [[BitFit Bias-Term Fine-Tuning]] — instance-of (bias-only PEFT)
- [[LLaMA-Adapter Zero-Initialized Attention]] — instance-of (gated prompts)
- [[LoReFT Representation Finetuning]] — alternative-to (edits representations, not weights)
- [[Black-Box Tuning for Language-Model-as-a-Service]] — instance-of (gradient-free prompt tuning)
- [[S-LoRA Multi-Adapter Serving]] — related (serving many LoRA adapters)
- [[Intrinsic Dimension of Objective Landscapes]] — related (why few parameters can suffice)
- [[Fine-Tuning as Prompt Compression]] — related
