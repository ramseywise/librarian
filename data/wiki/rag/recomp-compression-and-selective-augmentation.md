---
title: RECOMP Compression and Selective Augmentation
tags: [rag, concept]
summary: "RECOMP compresses retrieved documents into a short extract or summary before they are prepended, and trains the abstractive version to return nothing when retrieval would not help; QA lost a few EM points at about 5% of the tokens in the authors' setup."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-xu-2023-recomp.md
---

# RECOMP Compression and Selective Augmentation

RECOMP (Xu, Shi and Choi, 2023) puts a compressor between the retriever and the language model. The retrieved documents are reduced to a few sentences or a short summary, which is prepended to the input. Two compressors are trained. The extractive one is a 110M dual encoder initialised from Contriever that picks sentences from the top 5 documents; positives are the sentence giving the best LM log-likelihood or exact match, negatives are top-ranked sentences that score lower. The abstractive one is a T5-large (775M) trained on summaries written by a gpt-3.5-turbo teacher. An example keeps a summary only if the end-task score with it beats the score with no retrieval; otherwise its target is the empty string. That is **selective augmentation**: the compressor learns to emit nothing. When several pieces of evidence are joined, they run in ascending retrieval score so the best-scored one ends up nearest the question.

## Results (self-reported)

Setup for QA: the LM is Flan-UL2 20B, the retriever contriever-msmarco over Wikipedia cut into 100-word passages, with the top 5 documents and a 5-shot prompt.

- Abstractive compression to about 5% of the tokens costs 2 EM on NQ (36 against 660 tokens, EM 37.04 against 39.39) and 3.7 EM on TriviaQA.
- On HotpotQA (500 dev examples) the extractive compressor is better: 11% of the tokens for a loss of 2.4 EM (75 against 684 tokens, EM 30.40 against 32.80); abstractive scores 28.20.
- The abstractive compressor prepends a summary to only 33% of language-modeling examples; 4-24% of its training targets are empty (NQ 25%, TQA 16%, HotpotQA 4%, Wikitext 24%).
- Language modeling (WikiText-103, GPT2 117M, BM25 every 32 tokens): top-1 document gives perplexity 32.90, top 5 gives 35.53, none 37.84; more text is not always better.
- On NQ, the trained extractive compressor reaches EM 36.57 with 37 tokens. Single-sentence baselines trail it: Contriever at 30.06 and DPR at 34.32, with BM25 (25.82) and random picks (23.27) lower still.
- On NQ dev, when the gold answer is missing from the evidence, the LM copies a wrong answer from it 51% of the time with the top-1 document, 81% with the top 5, 85% with gpt-3.5 summaries and 39% with the trained compressor.
- The authors checked 30 non-empty summaries by hand per dataset and found the trained summaries less faithful than the teacher's (useful: NQ 80 against 83, TQA 77 against 83, HotpotQA 40 against 50).
- Transfer to LLaMA-13B on NQ is weaker: 34.38 (extractive) and 36.32 (abstractive), while full top-5 documents give 37.04 and no retrieval gives 30.89.

## Limits

- Multi-hop abstractive compression needs further study by the authors' own account; the extractive compressor fixes the sentence count and has no selective augmentation.
- Each compressor is trained for a single dataset and base LM; training needs scoring with the target LM, and its cost is not reported. Faithfulness is not trained for.
- One retriever setup, short-context 2023 LMs (Flan-UL2, GPT2, GPT-J, LLaMA-13B); oracle numbers use the gold answer.
- The extraction flags garbled cells: the GPT2-XL top-1 token count ("14", likely about 141), an abstractive oracle NQ F1 of 84.87 against EM 45.60, and an extractive TQA oracle F1 (80.46) below its EM (84.61). Those cells are not used here.

## See Also
- [[In-Context RALM and REPLUG]] — prerequisite-for
- [[LLMLingua Coarse-to-Fine Prompt Compression]] — alternative-to (compresses the prompt with a small LM rather than a trained retrieval compressor)
- [[Soft Context Compression for RAG (CLaRa and REFRAG)]] — alternative-to
- [[Context-Aware Compression]] — related
- [[RAG Reranking]] — related
- [[COCOM Context Embeddings Compression]] — alternative-to (embedding-level rather than text-level compression)
