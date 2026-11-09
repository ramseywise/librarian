---
title: RECITE Recitation-Augmented Generation
tags: [rag, pattern]
summary: "RECITE has an LLM write out a relevant passage from its own memory before answering a closed-book question, then majority-votes over 20 sampled recitations; it beats direct prompting on Natural Questions across four models, though TriviaQA gains are small for the strongest model (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-sun-2022-recitation-augmented-language-models.md
---

# RECITE Recitation-Augmented Generation

Sun and colleagues (ICLR 2023) ask whether closed-book question answering improves when an LLM first writes out a passage it judges relevant, drawn from memory, in place of fetching one from a corpus. The hypothesis is that explicit recitation aids memory, and that varying the recitation helps because a question can often be answered from several different passages.

## Mechanism

- **Recite-and-answer:** a few-shot prompt has the model produce a recitation for the question and then answer with that recitation in view. Twenty recitations are sampled with top-k sampling and the answers majority-voted (self-consistency).
- **Multiple-recite-and-answer** handles multi-hop questions.
- **Passage-hint diversified recitation:** a **passage hint** is an identifier made from a passage's section titles and its position within the section. For NQ, a PaLM-62B is fine-tuned for 10,000 steps on synthetic question, hint and passage data so it can sample hints and recite each greedily.

## Results

Self-reported. The extraction lists most outcomes as comparisons without scores, so the direction is given where numbers are missing.

- NQ, 5-shot, closed-book, 20 paths: recite-and-answer beats direct prompting for PaLM-62B, Codex-002, UL2-20B and OPT-30B. With 64 shots PaLM-62B gains less. The fine-tuned diversified recitation is the best NQ result.
- TriviaQA (first 1,024 questions, 5-shot): the gain is small for PaLM-62B (0.46 EM) and larger for UL2-20B. The authors guess that, for strong models, context carried by trivia questions weakens the benefit of recitation.
- HotpotQA (first 1,024 questions, 4-shot): for PaLM-62B, multiple-recite-and-answer outperforms both chain-of-thought and direct prompting (direct 20.51); Codex-002 direct is 28.32.
- Against retrieval (NQ first 1,024 validation, 5-shot): for UL2-20B, BM25 top-1 beats recitation and a ground-truth passage far exceeds both; for Codex-002, recitation beats BM25 top-1.
- UL2-20B TriviaQA is robust across 5 seeds of random exemplars (standard deviation 0.62 against 0.71). The extraction also reports three failure shares, where the answer was never recited, was recited but absent from path outputs, or lost the majority vote, without giving values.

## Limits

- To keep time-sensitive knowledge current the model must be trained or fine-tuned on the new corpus; all intermediate steps are model-generated, so the paper notes it may amplify biases in the weights compared with RAG.
- Temperature, top-k and maximum length are not stated. TriviaQA and HotpotQA are scored on just the first 1,024 questions, NQ on test or dev depending on the labels, and no significance tests are run.
- Diversified recitation was tried only for NQ, with PaLM-62B, a model that is not public. Only three closed-book QA tasks.

## See Also
- [[RAG Retrieval Strategies]] — alternative-to
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Language Model Self-Knowledge]] — related
- [[Self-Ask Prompting]] — related
- [[FLARE Forward-Looking Active Retrieval]] — related
