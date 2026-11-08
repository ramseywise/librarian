---
title: "RAG vs Long Context: Evaluation Evidence"
tags: [rag, llm, comparison]
summary: "Two 2024 evaluations disagree in emphasis: one finds long context ahead of RAG on filtered QA but RAG winning on about 10% of questions, the other finds RAG accuracy peaking then falling as more passages are retrieved, driven by hard negatives."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2024-long-context-vs-rag-llms.md
  - data/raw/papers/2026-11-06-jin-2024-long-context-llms-meet-rag.md
---

# RAG vs Long Context: Evaluation Evidence

Both papers are preprints and both report their own results (self-reported).

## Li et al.: long context against RAG head to head

- **Setup:** 12 datasets, questions answerable without context removed using GPT-4o with strict exact match, then distractor passages added. 19,188 questions after expansion, 13,628 kept. The RAG arm used summarization-tree retrieval (RAPTOR); the same GPT-4o or GPT-4-Turbo answered in both arms. Long-context input was truncated from the back when over the window.
- **Result (strict EM):** long context answered 56.3% correctly and RAG 49.0%. Long context alone was right on 2,287 questions and RAG alone on 1,294, so close to 10% of questions only RAG answered correctly. The authors read this as retrievers not being replaceable by long-context models.
- **By source:** Wikipedia 873 long-context-only wins against 348 RAG-only; stories 842 against 391; papers and reports 531 against 507; dialogue 31 against 44. Yes/no "other" questions favour RAG, 54 against 140.
- **Retriever choice** (a sample of about 1,563 questions, an inference by the extractor): RAPTOR 38.5% correct, then window parsing at 35.5% and tree index at 30.1%, an OpenAI embedding model (21.6%), BM25 (20.4%) and Contriever (20.1%). Chunk-based retrievers trail the summarization-based one.

## Jin et al.: more retrieved passages is not monotone

- **Setup:** NQ, with PopQA in the appendix. Retrievers e5 (Recall@40 0.90 on NQ) and BM25 (0.73). Four models were tested (two Gemma chat models, Mistral-Nemo-12B and Gemini-1.5-Pro), with k raised up to each model's limit. Curves only; the extraction gives no accuracy table.
- **Finding:** with the strong retriever, accuracy rises then falls or plateaus as k grows. With BM25 accuracy mostly keeps climbing, or dips a little. Accuracy stays below retrieval recall at every k.
- **Hard negatives:** with one gold passage plus N negatives, negatives from stronger retrievers hurt more (e5 above Contriever, above BM25, above random). Precision@k did not predict the damage. The authors argue that needle-in-a-haystack style tests use random negatives and so under-measure the RAG problem.
- **Mitigations:** a training-free reordering that puts the best passages at the two ends of the prompt gave little at small k and a steady gain at large k. Fine-tuning with 40 retrieved passages per example beat both the chat model plus RAG and fine-tuning without retrieval, on nine unseen datasets; adding an explicit reasoning step helped again.

## Reading the two together

They test different variables (long context against retrieval, versus the size of the retrieved set), on different models and datasets, so their numbers do not combine. They agree that retrieval quality and the kind of irrelevant text matter.

## Limits

- Li et al.: only two generator models; the Wikipedia long contexts are synthetic, which the authors say may bias against RAG, so that source's long-context lead is confounded. No cost, latency, chunk size or top-k is given, contexts stop around 67K words, and there are no confidence intervals. The text says 13,651 kept questions once and Table 3 says 13,628. The abstract's "comparably" for the summarization retriever is looser than the tables support.
- Jin et al.: results are plotted, not tabulated, so magnitudes are not quotable. The explanation that hard negatives drive the decline is the authors' reading, supported by the controlled negatives test.
- Both are 2024 models; newer ones may shift the balance.

## See Also
- [[Cache-Augmented Generation]] — related (a third option, preloading a small corpus instead of retrieving)
- [[LongRAG Long Retrieval Units]] — related (long units as a middle path)
- [[Long-Context Prompting]] — prerequisite-for (how to use a long window)
- [[RAG Retrieval Strategies]] — prerequisite-for (the retrieval side of the comparison)
- [[Context Retrieval Strategies]] — related (assembling retrieved context)
- [[BlockSearch In-Context Retrieval at Million-Token Scale]] — related (in-context retrieval collapses at 10,000 documents; a fix is reported)
