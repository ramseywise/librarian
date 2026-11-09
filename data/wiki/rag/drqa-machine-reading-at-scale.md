---
title: DrQA Machine Reading at Scale
tags: [rag, pattern]
summary: "DrQA answers open-domain questions from Wikipedia by pairing a non-learned TF-IDF plus hashed-bigram retriever with a BiLSTM span reader."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-chen-2017-reading-wikipedia-answer-open-domain.md
---

# DrQA Machine Reading at Scale

The question is whether open-domain factoid QA can use Wikipedia as its only knowledge source. The paper defines **machine reading at scale (MRS)**: combine document retrieval with machine comprehension, retrieving the few relevant articles among over 5 million and scanning them for the answer. DrQA is the system. Its Document Retriever returns 5 articles from a TF-IDF index over words plus hashed bigrams, with nothing learned. Its Document Reader is a 3-layer BiLSTM applied to each paragraph; it predicts where an answer span begins and ends, and the final answer is whichever span has the highest raw (unnormalised) score over all paragraphs. Training uses SQuAD plus **distant supervision (DS)**, which automatically pairs Wikipedia paragraphs with question-answer pairs that came without a paragraph.

## Results

All numbers are self-reported.

- Given the gold paragraph, the Document Reader on its own gets 70.0 exact match and 79.0 F1 on SQuAD test (single model), ahead of every published single model then.
- In the full-Wikipedia setting (5,075,182 articles, retriever top 5, multitask DS reader) SQuAD dev exact match is 29.8. Moving from a given paragraph to all of Wikipedia drops exact match sharply (69.5 given-paragraph dev).
- With the right document supplied but no paragraph, exact match is 49.4; the paper attributes many false positives to sentences on the right topic.
- Over SQuAD dev questions, the answer string appears in the 5 pages from the bigram-hashing retriever 77.8% of the time, against 62.7% for Wikipedia Search (presence of the string, not relevance).
- WikiMovies test: unigram TF-IDF scores 54.4, below Wikipedia Search at 61.7, and adding bigrams raises it to 70.3. WebQuestions goes the other way slightly: 74.4 with bigrams, 75.5 without.
- Dropping the aligned question embedding together with the exact-match features takes SQuAD dev F1 from 78.8 down to 59.4.
- In the full-Wikipedia setting, multitask DS training outperforms SQuAD-only training on all four datasets; the extraction reads most of that as extra in-domain data, not task transfer.
- YodaQA, which draws on Freebase and other resources, beats DrQA on CuratedTREC (31.3 versus 25.4) and by more on WebQuestions (39.8 versus 20.7); YodaQA's figures come from its benchmarks wiki.

## Limits

- Paragraphs are handled independently in reader training; nothing is aggregated across paragraphs or documents.
- The retriever and reader are trained separately, not jointly.
- SQuAD questions were composed while looking at a paragraph and are ambiguous alone, so part of the full-Wikipedia drop reflects the dataset.
- The retrieval metric tests for the answer string, not for relevance.
- Learning rate, epochs, seeds, hardware and compute go unreported, and the text gives no code URL.
- BM25 and bag-of-embeddings retrieval are described as worse, without numbers.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Shared-Normalization Multi-Paragraph Reading]] — extends (replaces the cross-paragraph argmax with comparable confidences)
- [[FEVER Fact Verification Dataset]] — extends (reuses the retriever as its first stage)
- [[ORQA and the Inverse Cloze Task]] — alternative-to (learned retrieval instead of a fixed retriever)
- [[Fusion-in-Decoder]] — alternative-to (generative reader over many passages)
- [[BiDAF Bi-Directional Attention Flow]] — related
