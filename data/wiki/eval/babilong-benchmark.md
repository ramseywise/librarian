---
title: BABILong Benchmark
tags: [eval, concept]
summary: "BABILong hides bAbI reasoning facts inside PG19 book text padded to any length; on it GPT-4-Turbo failed for most of its 128K window and retrieval failed on multi-fact tasks, while a small recurrent-memory GPT-2 held up to 10M tokens on the simple tasks tested (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-kuratov-2024-search-needles-11m-haystack.md
---

# BABILong Benchmark

The 2024 preprint asks how GPT-4-Turbo, Mistral, retrieval-augmented generation and a GPT-2 with recurrent memory fare at locating facts buried in very long distractor text and reasoning over them. The authors' hypothesis is that recurrent memory filters irrelevant information better than attention alone, and that attention-based models use only part of their long window.

## How the benchmark is built

BABILong takes the sentences of a bAbI task (a short reasoning question with its supporting facts) and places them between sentences of unrelated PG19 book text, padded sentence by sentence until the input reaches a target length. Length is therefore a free parameter, and the supporting facts are spread through the text rather than adjacent. The main evaluation uses the first five bAbI tasks (qa1 to qa5), with qa2 and qa3 needing two or three facts.

## Findings (self-reported)

- GPT-4-Turbo (128K window, 0k to 128k, 25 samples per cell, qa1 to qa5) failed the needle tasks for most of its window.
- With facts placed in input quarters on qa1 (4k to 64k), facts in the middle were hardest for GPT-4-Turbo to find. The conclusion also says GPT-4 and RAG lean heavily on the first quarter of the input.
- RAG with ada-002 embeddings, FAISS and top 5, on qa1: sentence chunks beat 512-token chunks, and sentence retrieval fell off notably only at 10M tokens. On qa2 to qa10, retrieval failed where two or three facts were needed, because the second fact does not resemble the question.
- Recurrent Memory Transformer (RMT) and its self-retrieval variant RMT-R (GPT-2 with 137M parameters, trained on 32 segments of 512 tokens, one model per task) kept their performance out to 128k from about 16k of training, with marginal degradation, and beat GPT-4. They also outperformed GPT-4 with RAG at 1M and at 10M tokens, more than 600 times the length used in training.
- GPT-3.5 fine-tuned for 3 epochs on 100 qa1 tasks of 16k tokens improved at 16k, but accuracy kept falling as noise grew.
- RMT's evaluation time scales linearly with context length, taking 315 minutes for 1000 samples at 1M tokens on a single A100 80GB, data processing included.

## Limits

- Background is only PG19 and Wikipedia; interference from similar facts could make the task harder. The tasks are simple algorithmic bAbI tasks, chosen on purpose.
- The retrieval component was not tuned (OpenAI embeddings only), the GPT-4 and Mistral prompts may be suboptimal, and the text gives no seeds, decoding settings or temperature. The authors say part of RAG's failure is that default retrieval pays no attention to temporal order.
- RMT models are trained per task on a small GPT-2, RMT has finite storage, and RMT-R storage grows linearly with segment count.
- The extraction notes that it has no numbers for the main RMT results, which are in Figure 9, and that the 10M-token evaluation uses only 100 samples.
- Models are early-2024 snapshots (GPT-4-Turbo, Mistral).

## See Also
- [[Recurrent Memory Transformer (RMT)]] — related (the recurrent model evaluated here)
- [[Long-Context Prompting]] — related
- [[RAG vs Long Context: Evaluation Evidence]] — related (a second body of long-context versus retrieval evidence)
- [[Neural Turing Machine]] — related (an earlier external-memory design)
- [[bAbI Toy Tasks]] — prerequisite-for (the synthetic tasks it embeds in long text)
