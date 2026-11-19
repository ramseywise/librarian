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
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch03-exploring-llms-as-powerful-ai-engine.md
  - data/raw/papers/2026-11-08-llm-engineers-handbook-ch05-supervised-fine-tuning.md
  - data/raw/papers/2026-11-07-hu-2021-lora.md
  - data/raw/papers/2026-11-07-liu-2022-few-shot-parameter-efficient-fine.md
  - data/raw/papers/2026-11-08-guo-2021-parameter-efficient-transfer-learning-diff.md
  - data/raw/papers/2026-11-08-ruckle-2021-adapterdrop.md
  - data/raw/papers/2026-11-08-aghajanyan-2021-intrinsic-dimensionality-explains-effectiveness-language.md
---

# Parameter-Efficient Fine-Tuning Methods

Huyen (*AI Engineering*, chapter 7, a 2024 text) defines PEFT as getting close to full finetuning while training several orders of magnitude fewer parameters. The methods differ in what they leave trainable.

| Method | What is trained | Page |
|---|---|---|
| Adapters | Two small modules per transformer block (Houlsby et al., as cited by Huyen) | this page |
| LoRA | W stays frozen; the update is the product of two small matrices A and B, merged into W once training ends | [[LoRA Low-Rank Adaptation]] |
| QLoRA | LoRA adapters on a 4-bit quantised, frozen base | [[QLoRA 4-Bit Quantized Finetuning]] |
| DoRA | Another low-rank adapter method (see its page) | [[DoRA Weight-Decomposed Low-Rank Adaptation]] |
| Prefix-tuning, prompt tuning | Continuous vectors prepended to the input (prefix-tuning at every layer, prompt tuning at the embedding layer) | [[Prefix-Tuning and Prompt Tuning]] |
| BitFit | Only the bias terms (plus a classifier) | [[BitFit Bias-Term Fine-Tuning]] |
| LLaMA-Adapter | Prompts in the top layers behind a zero-initialised gate | [[LLaMA-Adapter Zero-Initialized Attention]] |
| ReFT | A learned edit of hidden states at chosen positions | [[LoReFT Representation Finetuning]] |
| (IA)3, T-Few | Learned vectors that rescale keys, values and the inner activations of the feed-forward blocks; T-Few is a fixed recipe on T0 built around them | [[T-Few and (IA)3 Few-Shot PEFT]] |
| Diff pruning | W stays frozen and a sparse difference vector is added to it, with a relaxed L0 penalty setting the mask | [[Diff Pruning Sparse Task Difference Vectors]] |
| AdapterDrop | Houlsby or Pfeiffer adapters with those in the first n layers removed | [[AdapterDrop Efficient Adapters]] |
| Black-box tuning | A low-dimensional vector, found with no gradients | [[Black-Box Tuning for Language-Model-as-a-Service]] |

## Numbers Huyen reproduces from the papers

- Houlsby et al.'s adapters in BERT trail full finetuning by under half a point on GLUE (0.4%) with 3% of the parameters trained; tuning only part of BERT-large took roughly a quarter of its parameters to equal full finetuning there.
- Hu et al. report LoRA on GPT-3 175B equalling or exceeding full finetuning on several tasks with about 4.7M trained parameters (0.0027% of the full count). With a fixed 18M budget (0.01%), spreading rank 2 over all four attention matrices scored best on WikiSQL and MultiNLI, ahead of putting r=8 on one matrix or r=4 on two.
- LoRA adapter memory is small: 37.7 MB for GPT-3 175B at r=2 on query and key, against 350 GB of weights (16-bit, 18.87M parameters).
- Serving 100 per-customer models: with W of 4096 x 4096 (16.8M parameters) and rank 8, each adapter has 65,536 parameters, so 100 kept separate take 23.3M parameters against 1.68B merged. Huyen advises keeping adapters separate for multi-LoRA serving and merging for a single LoRA model.

## Numbers from the method papers

Each figure is the authors' own (self-reported) and keeps its setup; the setups differ, so the rows are not comparable with each other.

- LoRA, GPT-3 175B, WikiSQL, single runs with about +/-0.5% fluctuation: 4.7M trainable parameters reach 73.4 and 37.7M reach 74.0, against 73.8 for full fine-tuning. Under an 18M budget on the same model, adapting both query and value projections (r=4) scored 73.7 on WikiSQL and 91.3 on MultiNLI, against 70.4 and 91.0 for the query projection alone (r=8). The trained checkpoint shrinks to 35MB (r=4, query and value) from 350GB, but serving still needs the full 350GB base model.
- (IA)3, T0-3B: 540K added parameters against 9.1M for LoRA, and it is the only PEFT method in that comparison to beat full-model fine-tuning (nine held-out datasets, with the unlikelihood and length-normalised losses). T-Few on T0 11B beat few-shot GPT-3 175B in-context learning on those held-out tasks (median over 5 few-shot subsets; the GPT-3 figures are copied from Brown et al.).
- Diff pruning, BERT-large, evaluated on the GLUE test server at 0.5% target sparsity (one hyperparameter-searched run per task): structured diff pruning matches fully fine-tuned BERT-large, adding 0.5% parameters per task. Storage per task in a basic Python estimate (float32 weights, int32 positions): 13.6 MB, against 51.7 MB for adapters and 1297.0 MB for full fine-tuning. Each minibatch takes between 1.5x and 2x as long to train as in ordinary fine-tuning.
- AdapterDrop, RoBERTa-base, 8 GLUE tasks: specialised AdapterDrop with the first five layers' adapters dropped retains 97.1% of what the standard adapter averages on GLUE, while a standard adapter with five layers removed only at test time drops to 89.0%. Timing, BERT-base configuration: Pfeiffer-adapter training steps are as much as 60% quicker than full fine-tuning (sequence length 128, batch 32), and inference is 4-6% slower.

## Why few parameters can suffice

Aghajanyan et al. fine-tune inside a d-dimensional random subspace and record the smallest d that gets to 90% of full fine-tuning accuracy (d90). RoBERTa-Large gets there on MRPC with about 200 trainable parameters (structure-aware variant). The authors treat d90 as an upper bound, and across 18 public models MRPC d90 falls as parameter count rises. Hu et al. cite this work as the motivation for LoRA's hypothesis that the weight update has a low intrinsic rank. See [[Intrinsic Dimension of Fine-Tuning]].

## Memory arithmetic (worked examples)

- A 7B model trained in full with Adam at 16 bits takes 56 GB for the weights, gradients and optimiser states together (three values per trainable parameter), before counting activations.
- Inference memory for a 13B model stored at 2 bytes per weight is 31.2 GB, assuming activations plus the key-value cache add 20% over the weights.
- Gradients plus optimiser states for 13B trainable parameters at 2 bytes come to 78 GB; if only 1B parameters are trainable the figure is 6 GB.

## Figures from a second book (Raieli and Iuculano, chapter 3)

Raieli and Iuculano's agents book (chapter 3) calls LoRA and adapters the PEFT methods in widest use and prefers them to full fine-tuning when models are very large. It reports that LoRA trains 17.5 million out of GPT-3's 175 billion parameters, and adapters (1024 to 24 to 1024, under 50K parameters each) matching full BERT fine-tuning with 3.6% more parameters. Both differ from the figures above: Hu et al.'s 4.7M and 18M budgets are other configurations, and Huyen gives 3% for adapters where the second book gives 3.6%. The chapter relays other work and runs no experiments.

## Practitioner guidance

- Huyen advises starting with LoRA and trying full finetuning afterwards, noting that with only a few hundred examples full finetuning may give no gain over LoRA.
- Ranks of 4 to 64 usually suffice, and a larger rank need not raise quality (Raschka's own tasks did best at r=256). Huyen suggests keeping the ratio of alpha to r within 1:8 to 8:1 and tuning both.
- Learning rate: search between 1e-7 and 1e-3, beginning at 0.1 to 1 times the rate pretraining ended on and pushing it up while the loss curve stays stable. Batches under eight can make training unstable (the author says she found no good explanation); accumulate gradients if memory forces small batches. Epochs: 1 to 2 when there are millions of examples, possibly 4 to 10 for thousands. The prompt's share of the loss defaults to 10%.
- Finetune for form and use retrieval for facts; if a model has both kinds of failure, start with retrieval. In Ovadia et al.'s current-events QA on Mistral-7B, the base model with RAG scored far above finetuned variants without it, and finetuning plus RAG scored below the base model with RAG. Across Mistral 7B, Llama 2-7B and Orca 2-7B, putting RAG on a finetuned model beat RAG on the base model for MMLU in 43% of cases. See [[RAFT Retrieval-Augmented Fine-Tuning]].
- Case evidence in the chapter: zero-shot GPT-4-0314 beat the 50B BloombergGPT on FiQA sentiment and ConvFinQA, a model that needed 1.3 million A100 GPU hours (estimated $1.3M to $2.6M for compute alone). Grammarly's finetuned Flan-T5 models, 60 times smaller and trained on 82,000 pairs, outperformed a specialised GPT-3 variant.
- Model merging (task vectors, TIES and DARE pruning before merging, depthwise scaling, as in SOLAR 10.7B, which grew a 7B model from 32 to 48 layers) is described as experimental.

## A practitioner's LoRA recipe (LLM Engineer's Handbook, chapter 5)

The authors suggest starting LoRA at a moderate rank with alpha set to twice the rank, targeting all linear layers, and raising the rank to 64 or 128 if the model underfits (rules of thumb, no source given). Their worked run fine-tuned Llama 3.1 8B with r=32, 3 epochs, an effective batch of 16 and a 2048 maximum sequence length, using Unsloth and TRL; it took 50 minutes on one A100 (self-reported). The setup is one run with seed 0 and no ablation of rank, learning rate or data mix.

## Limits

- Many of the chapter's tables are reproduced from other papers; its one experiment is a count of open issues in huggingface/peft.
- Written in 2024; the author states LoRA does not reach full finetuning and focuses on LoRA over attention matrices, which later work revised. Merging methods are called experimental and may become outdated.
- The chapter covers supervised and adapter finetuning; preference finetuning is only mentioned in the overview.
- Method pages cite single-paper results on different models and tasks, so the rows above are not a controlled comparison.
- LLM Engineer's Handbook ch05: the 50-minute run shows only loss curves (one run, seed 0, no ablations), the authors state that the run is a quick check and not a proper evaluation, and its hyperparameter ranges are rules of thumb without sources.
- Raieli and Iuculano ch03: figures are relayed from other work with no experiments.
- The LoRA extraction's GPT-3 settings differ from those quoted from Huyen above: it gives a 35MB checkpoint for r=4 on query and value, 37.7M trainable parameters as a WikiSQL configuration, and an 18M-budget comparison of r=4 on query and value against r=8 on query alone. Huyen's 37.7 MB (r=2, query and key) and rank-2-over-four-matrices result are not in that extraction.
- Houlsby adapters appear as 3% of parameters above (Huyen) but as 3.6% per task (80.4 GLUE average, BERT-large) and 2.1% for the 64-unit variant in the diff pruning extraction, which copies them from Houlsby et al.
- Method-paper limits: LoRA's GPT-3 results are single runs and its WikiSQL run-to-run fluctuation is about the size of the gap to full fine-tuning; T-Few's experiments are classification or multiple choice only and its design was tuned on the same nine datasets used for evaluation; diff pruning and AdapterDrop were tested only on small encoders (BERT, RoBERTa); in AdapterDrop, CoLA drops sharply when layers are dropped; the intrinsic-dimension study covers sentence classification only and reports no seeds or variance.

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
- [[Intrinsic Dimension of Fine-Tuning]] — related (why few parameters can suffice)
- [[T5 Text-to-Text Transfer Transformer]] — related (compares adapters with full fine-tuning)
- [[Classification Fine-Tuning a GPT: Replace the Output Head]] — related (freezing most of a model and training a new head)
- [[LoRA Low-Rank Adaptation]] — instance-of (the low-rank method in the table, with its own page)
- [[T-Few and (IA)3 Few-Shot PEFT]] — instance-of (rescaling vectors on keys, values and feed-forward activations)
- [[Diff Pruning Sparse Task Difference Vectors]] — instance-of (a learned sparse difference vector)
- [[AdapterDrop Efficient Adapters]] — instance-of (adapter efficiency and layer dropping)
- [[Continuous Prompts: P-Tuning, WARP and Soft-Prompt Mixtures]] — related
- [[LLM vs Fine-Tuned Model Practitioner Survey]] — related
