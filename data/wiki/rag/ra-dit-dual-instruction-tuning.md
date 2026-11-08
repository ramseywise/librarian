---
title: RA-DIT Dual Instruction Tuning
tags: [rag, foundations, llm, pattern]
summary: "RA-DIT fine-tunes the language model on retrieved-chunk prompts and, separately, the retriever's query encoder on the LM's own preferences, giving a small average gain over off-the-shelf retrieval-augmented prompting at 65B."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lin-2023-ra-dit.md
---

# RA-DIT Dual Instruction Tuning

RA-DIT (ICLR 2024, arXiv 2310.01352) tunes the two halves of a retrieval-augmented model in two separate stages rather than end to end.

1. **LM tuning (RA-IT).** Each training example is paired with about three retrieved chunks, each as its own instance. Because wrong chunks are included, the model learns to ignore misleading retrieval and fall back on its own knowledge; an unanswerable-passage set in the mix teaches "I don't know".
2. **Retriever tuning (LSR).** The retriever is updated so that chunks the LM finds helpful score higher, with the LM scoring the top-10 chunks (temperature 0.01). Only the query encoder is updated; keeping the document encoder fixed scored 57.8 against 55.8 when both are updated, and means the index is not re-embedded.

## Results (self-reported)

Setup: a 65B LLaMA with the DRAGON+ retriever over a 399M-chunk corpus, ten chunks per query.

- Against untuned REPLUG, average over MMLU, NQ, TriviaQA and ELI5: 0-shot 43.1 to 50.5, 5-shot 52.7 to 55.2.
- Against ATLAS 11B fine-tuned per task, one RA-DIT 65B model, tuned on the pooled 64-example sets, scored 60.9 against 56.8 on eight KILT-style tasks, winning six. The sizes are not matched.
- Dev-set ablation (5-shot, 10 tasks): baseline 53.8, retriever-tuned only 54.4, LM-tuned only 53.9, both 54.6. Gains are small.
- RA-IT against plain instruction tuning with retrieval, 0-shot: 51.0 against 47.7; 5-shot 55.8 against 55.6.
- Retriever data mix: 95% corpus-derived plus 5% multi-task data gave +0.6 average over the untuned retriever.
- Corpus matters: Wikipedia 2021 54.7, Wikipedia 2018 51.9, CommonCrawl only 47.0 (5-shot dev). The authors read this as the model following whatever index it is given.
- Non-retrieval commonsense average moved 72.1 to 74.5, up on 7 of 8 sets.

## Limits

- The extraction notes the introduction's percentages (for example NQ +22% 0-shot) do not match Table 2's point differences (28.8 to 35.2).
- Dev-set gains from the dual tuning are around a point or less. Iterating the two stages gave no further gain in preliminary runs, which are not tabulated.
- The ATLAS comparison mixes model sizes and fine-tuning regimes. Parallel per-chunk encoding was both trained and tested in the same form, which may favour it.

- The extraction notes the DRAGON+ row in Table 7 (53.4) does not equal the baseline in Table 6 (53.8), which it attributes to few-shot truncation differences (footnote 11), and that Table 6 labels the method "RIT" where the text says RA-IT. Compare only within a table.

## See Also
- [[RL for Retrieval Policies]] — prerequisite-for (the wider question of tuning retrieval from downstream signal)
- [[RAG Retrieval Strategies]] — prerequisite-for (retrieval choices the tuned model sits on)
- [[RAG Reranking]] — related (another way to adapt retrieval to the reader)
- [[UPRISE Universal Prompt Retrieval]] — related (a retriever trained from a frozen LM's scores)
