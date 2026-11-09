---
title: Sufficient Context Autorater
tags: [rag, eval, llm, pattern]
summary: "Label each (query, retrieved context) pair as sufficient or not with an LLM autorater, then use that label to split RAG errors into retrieval failures and generation failures and to gate abstention."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-joren-2024-sufficient-context.md
---

# Sufficient Context Autorater

The paper (ICLR 2025, arXiv 2411.06037) defines a context as sufficient when it holds enough information to answer the query, judged without needing the ground-truth answer. An LLM autorater assigns the label, which lets a RAG system be analysed in two halves: did retrieval supply the evidence, and did the model use it.

## The autorater

All numbers in this page are self-reported unless noted. On 115 hand-labelled instances drawn from four QA sets (PopQA, FreshQA, NQ, EntityQuestions) chosen as difficult cases whose context is related yet insufficient, Gemini 1.5 Pro with one example scored accuracy 0.930. Zero-shot it scored 0.870, a fine-tuned 24B model (FLAMe) 0.878, an NLI baseline 0.826, and a "does the context contain the ground-truth string" check 0.809. The sample is small.

## Findings on benchmarks

- **Many benchmark instances are insufficient.** At a 6k-token context, autorater labels give sufficient shares of 77.4% (FreshQA), 46.2% (HotpotQA) and 44.6% (Musique). The extraction notes that the mapping of its Figure 2 bars to datasets and lengths is a reading of the extracted bars.
- **Models answer wrongly even with sufficient context.** On a small human-annotated set (size not stated; 54.8% sufficient), hallucination with sufficient context was 14.3% for Gemini 1.5 Pro, 12.7% GPT-4o, 3.2% Claude 3.5 Sonnet, 17.5% Gemini 1.5 Flash and 25.4% Gemma 27B. The authors conclude open-book QA cannot be fixed by retrieval alone.
- **Models still answer correctly without it.** The authors report 35 to 62% correct with insufficient context, and sort the cases into eight types (for example yes/no questions, multi-hop fragments, ambiguous queries, closed-book knowledge).
- **Retrieval makes models abstain less.** With a chain-of-thought prompt and 6000-token context, Claude 3.5 Sonnet's abstention fell from 84.1% to 52%, GPT-4o's only from 34.4% to 31.2%, while Gemini 1.5 Pro's went from 100% to 18.6%. The Gemini 100% is partly produced by FreshQA's time-sensitive questions.

## Selective generation

A logistic regression on two features, the binary sufficiency label and the model's confidence (P(True) for open models, P(Correct) for proprietary ones), decides when to abstain below a threshold. It was tested on HotpotQA and Musique with three generators (Gemini 1.5 Pro, GPT-4o, Gemma 27B). Gemma 27B on HotpotQA improved by more than 10 points in its best-accuracy regions, and Gemini 1.5 Pro by more than 5 near 70% coverage; the abstract states 2 to 10% overall. It is separate from generation, so it does not touch the generator, and the threshold trades coverage against accuracy. No gain appeared for Gemma 27B on Musique. The authors caution that abstaining on every insufficient case can reduce overall performance.

## Fine-tuning for abstention did not work

Mistral 3 7B with LoRA, 2,000 training examples, with "I don't know" targets on 20% of examples (random or insufficient-context-selected) did not abstain more than vanilla RAG. Musique hallucination was 59.4% for vanilla RAG against 74.8 to 75.8% for the idk variants; HotpotQA 44.2% against 56.8 to 57.6%. Training was described as not smooth.

## Limits

- The Table 4 caption ranges (14-16% error; abstain 50-73%) do not match the table rows, where Claude is 3.2% and the 73% belongs to Gemini 1.5 Flash. In the appendix prompt for the fine-tuned autorater the labels look inverted (the extraction's observation).
- The 115-instance autorater test and the human-annotated set behind Table 4 are small.
- The explanation for lower abstention with retrieval is speculation by the authors. The claim that fine-tuning helps correctness holds only on Musique; on HotpotQA it lowered correct answers against vanilla RAG.
- Closed-book correct answers inflate the correct-with-insufficient-context figures.

## See Also
- [[RAG Evaluation]] — prerequisite-for (separating retrieval failure from generation failure)
- [[Agentic RAG — Advanced Patterns]] — related (CRAG and Self-RAG also gate on retrieval quality)
- [[CRAG Retry Logic]] — alternative-to (a retrieval grader that triggers a retry rather than an abstention)
- [[FreshQA]] — related (one of the three benchmarks the labels were applied to)
- [[RAG Retrieval Strategies]] — prerequisite-for (what the retrieval half of the split is measuring)
- [[FILCO Sentence-Level Context Filtering]] — related
- [[Context-Faithful Prompting]] — related (prompting for faithfulness to given context)
