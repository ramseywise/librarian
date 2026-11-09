---
title: ALCE Citation Benchmark
tags: [eval, reference]
summary: "ALCE asks a prompted LLM to retrieve, answer and cite from 100-word passages on ASQA, QAMPARI and ELI5, scoring fluency (MAUVE), correctness and NLI-checked citation recall and precision; the paper reports weak citation quality even for ChatGPT and GPT-4 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-gao-2023-enabling-large-language-models-generate.md
---

# ALCE Citation Benchmark

Gao and colleagues (EMNLP 2023) build a benchmark for the question of how well an LLM can answer with citations when given retrieved passages, and whether that can be scored automatically and reproducibly. The extraction describes it as the first reproducible benchmark of this kind (the paper's framing). Given a question and a corpus of 100-word passages, a system has to retrieve, answer and cite. The systems evaluated are prompted LLMs paired with ready-made retrievers, and no weights are updated. Datasets: [[ASQA]], QAMPARI and ELI5.

## Metrics

- **Fluency:** [[MAUVE]].
- **Correctness:** dataset-specific (for ASQA, exact-match recall of the short answers).
- **Citation recall:** scored 1 only when a citation exists and the cited passages jointly entail the statement.
- **Citation precision:** each citation is checked, and one is irrelevant when it cannot support the statement by itself and dropping it leaves the remaining supporting citations unaffected.
- Entailment is checked by a T5-11B NLI model (TRUE), validated against human annotation on 100 ASQA and 100 ELI5 examples.

## Prompting strategies compared

VANILLA (passages in the prompt), SUMM and SNIPPET, INTERACT and INLINESEARCH (the model searches during generation), CLOSEDBOOK with POSTCITE (answer with no passages, then attach a best-matching passage as the citation), and RERANK (sample four answers, keep the one with highest automatic citation recall).

## Findings

The extraction's numbers for the main table are not preserved, so the findings below are directional. All are the paper's own and self-reported, on the setups named.

- On ELI5 (Sphere corpus, BM25), roughly half of the generations from ChatGPT and GPT-4 lack full support from the passages they cite.
- On ASQA (ChatGPT gpt-3.5-turbo-0301, GTR top-5 passages, two demonstrations, mean of three seeds), closed-book POSTCITE gets much lower citation recall than VANILLA.
- A shortcut beats the metric: answering with the first two sentences of the top passage and citing it gives near-perfect citation recall but low correctness. Top-5 GTR passages cover only 56.8 percent of ASQA answers.
- SUMM with 10 passages raised ASQA EM recall and lowered citation quality for ChatGPT; INLINESEARCH was worse than VANILLA.
- ChatGPT-16K did not gain from more passages (5, 10, 20), while GPT-4 (8K) improved with more passages on ASQA EM recall. LLaMA-2-70B-Chat reached correctness comparable to the OpenAI models with lower citation quality.
- Fine-tuned Fusion-in-Decoder (T5-base) with POSTCITE lagged ChatGPT on ASQA.
- Metric validation: ALCE detects irrelevant citations with recall 75.6 and precision 66.1, a high false-positive rate because NLI cannot see partial support. On ELI5, ROUGE-L is gameable: the top BM25 passage scores ROUGE-L 19.1 with claim recall 3.0.
- Sub-claim generation was spot-checked: of 120 sub-claims (from 40 ELI5 answers, text-davinci-003), 112 were judged relevant and faithful.

## Limits

- MAUVE is sensitive to output length, so it may be unstable.
- Citation quality is bounded by NLI accuracy, which cannot detect partial support.
- RERANK picks by the same recall score that then evaluates it, so its automatic gain is inflated relative to human-judged recall (the human gain was smaller).
- ELI5 claims may not cover every valid answer. The datasets leave out multi-hop reasoning, math and code.
- Only prompting is studied; training models to cite is left open. Models are 2023-era; RERANK, ChatGPT-16K and GPT-4 were single seeded runs.

## See Also
- [[RAG Evaluation]] — prerequisite-for
- [[Long-Form QA Evaluation Hurdles]] — related (the earlier critique of ELI5 evaluation)
- [[Generative Search Engine Verifiability Audit]] — related (a concurrent human audit of citations)
- [[Grounding Claim Methodology]] — related
- [[LFQA Attribution and SALAD]] — related (attribution annotation on ELI5)
- [[RAGChecker]] — related
- [[LongCite and LongBench-Cite]] — related
