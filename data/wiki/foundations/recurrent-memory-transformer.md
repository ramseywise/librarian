---
title: Recurrent Memory Transformer (RMT)
tags: [foundations, concept]
summary: RMT passes a few memory tokens from one fixed-size segment to the next on a pretrained transformer, giving linear compute and constant memory; it reached 2M tokens on synthetic fact tasks, though memory is lossy and the tasks are easy.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-bulatov-2023-scaling-transformer-1m-tokens-beyond.md
  - data/raw/papers/2026-11-08-bulatov-2022-recurrent-memory-transformer.md
---

# Recurrent Memory Transformer (RMT)

Bulatov et al. (2023, AAAI 2024 version) add memory tokens to a pretrained transformer. At each step, memory tokens are prepended to a segment, the model runs, and its output memory tokens go into the next segment. Because a single segment sits on the GPU at once, inference memory stays constant and compute grows linearly with input length.

## Setup and results (self-reported)

- A BERT backbone with 512-token segments (499 usable, 10 for memory, 3 special). Training used at most 7 segments with a curriculum that lengthens the task step by step, and evaluation reached 4,096 segments (about 2M tokens).
- Tasks are synthetic bAbI facts hidden in QuALITY filler text: memorize, detect and memorize, and a two-fact reasoning task. Detect-and-memorize is easiest. The text gives no accuracy numbers for these (plots only).
- Training directly on four segments, with no curriculum, neither solved the task nor extrapolated. Once training reached five or more segments, the model generalised almost perfectly to tasks twice as long.
- An analytic FLOP estimate gives RMT 29 times fewer FLOPs than OPT-175B and 295 times fewer than a 125M OPT at 2,048,000 tokens; no run measured this. A measured unoptimised GPT-2 FP32 baseline exhausted an 80 GB GPU at 8K tokens.
- It combines with LoRA and adapters on Pythia-70m (7.30 to 6.97 with one to two segments, from 41.43 for adapters alone), though the table column is labelled loss where the text says perplexity.
- A Lean theorem-proving test gave a modest gain only.

## The original 2022 paper (NeurIPS 2022)

Bulatov, Kuratov and Burtsev first proposed RMT as segment-level recurrence with memory tokens and no architecture change. m real-valued memory tokens go at the start of each segment (read) and the end (write); what the write tokens produce is handed to the following segment as its read tokens, trained with backpropagation through time across segments. It was built on the Transformer-XL code base and also added to pretrained BERT, RoBERTa, DeBERTa and T5 for classification. They hypothesise that dedicated memory tokens hold global information in less space than Transformer-XL's cache of hidden states for every layer.

Results below are self-reported, with the setup beside each.

- WikiText-103, 16-layer model, segment 150: an RMT using 10 memory vectors (BPTT-3) comes close to Transformer-XL caching 25 states per layer (perplexity 25.57, against 29.95 with no memory) and is close to Transformer-XL with memory 75 (24.68). At segment 50, RMT with 1 memory vector is about as good as Transformer-XL with memory 10 (28.98).
- WikiText-103, segment 150, double the training steps: Transformer-XL cache (150) plus 10 RMT memory tokens gave the best result, slightly under the Transformer-XL paper's 24.0.
- enwik8, 12-layer model, segment 128: Transformer-XL with 40 cached states matches RMT with memory 5 (RMT BPTT-1 1.241, Transformer-XL 1.230). Deeper BPTT unrolling lowers WikiText-103 perplexity (memory 10, segment 50, from BPTT-0 at 30.69).
- On quadratic equations (180 tokens split into 6 segments, memory size 30), RMT scored 0.99 +/- 0.002, Transformer-XL 0.93 +/- 0.02, and the baseline without segmentation 0.99 +/- 0.01. On the copy task (360 tokens, memory as large as one segment), RMT stays perfect for as many as 9 segments, whereas Transformer-XL drops to the level of having no memory (read from a figure).
- Hyperpartisan news, RoBERTa-base with 10 memory tokens, 512 tokens per segment, 4 segments: the best F1 in the paper's Table 3, above Longformer (94.80), Big Bird (92.20) and Ernie-Doc-large (96.60).
- The authors say RMT reaches Transformer-XL quality using a memory up to ten times smaller, though Transformer-XL memory counts states of every layer while RMT memory counts vectors at the input only.

## Limits

- The authors concede the 2M-token result is on specialised synthetic tasks, and the distractor text differs from the facts so the lookup is trivial. No comparison with full attention at long lengths, and no aggregation tasks.
- The authors treat full attention as an upper bound, since RMT sees only compressed memory.
- Extraction inconsistencies: "OPT-135M" appears for the 125M model, a segment size printed as "2028", and a LOSS label against perplexity in the text.
- The backbones are old and small (BERT, GPT-2, and two other small decoder models). Backpropagation through time is costly, and the context sizes it cites for GPT-4 and Claude are out of date.
- 2022 paper: the authors concede training instability and GPU memory limits for larger memory with deeper unrolling. Experiments are small (16-layer, 410-hidden language model, synthetic tasks), and batch size, warmup, dropout and seeds are not stated. RMT matches but does not beat Transformer-XL on language modeling at equal training; the best result needs the combination. On associative retrieval at 5 segments RMT dips slightly and Transformer-XL rises above it.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Artificial Hippocampus Networks]] — alternative-to (compressed state for evicted context)
- [[Unlimiformer]] — alternative-to
- [[Why Context Is Finite]] — related
- [[LM2 Large Memory Models]] — alternative-to (gated memory bank in every block)
- [[Offline Recurrence Sleep for Language Models]] — alternative-to
- [[Neural Turing Machine]] — related
- [[End-to-End Memory Networks]] — related
- [[BABILong Benchmark]] — related (the benchmark its long-input results come from)
- [[Focused Transformer Crossbatch Training]] — related (memory attention for long context)
- [[LongMem Side-Network Memory]] — related (side-network memory)
- [[MemLong Retrieval Memory Layers]] — related (retrieval memory layers)
- [[Stored Instruction Computer LLM Memory Universality]] — related
