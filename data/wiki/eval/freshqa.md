---
title: FreshQA
tags: [eval, reference]
summary: "A 600-question benchmark of never-, slow-, fast-changing and false-premise questions with RELAXED and STRICT grading; in April 2023 GPT-4 scored 28.6% STRICT with no search and 75.6% with FreshPrompt search-result injection (self-reported), with the STRICT-RELAXED gap read as the hallucination measure."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-vu-2023-freshllms.md
---

# FreshQA

FreshQA (Vu et al., arXiv 2310.03214, 2023) tests whether a model's answer is current. It has 600 questions in four types: never-changing, slow-changing, fast-changing and false-premise, each at either one-hop or multi-hop difficulty. The split is a 500-question test set (125 per type) and a 100-question dev set (25 per type) unused in the paper. Researchers and Upwork freelancers wrote the questions, all manually reviewed. Annotators recorded the year each answer last changed, a source URL and an expected next review date, and questions likely to change more than weekly were excluded. Maintainers update answers by hand.

## Grading

- **RELAXED** gives credit when the main answer is right.
- **STRICT** also needs every claim in the response to be accurate and current. The authors treat the gap between the two as the hallucination measure.
- **FreshEval** is a few-shot LLM judge with separate prompts per mode. It agreed with human raters 96.5% (RELAXED) and 96% (STRICT) on 100 answers (self-reported); two authors agreed 99% and 96% on the same 100.

## Results (self-reported; models run 26 April 2023, temperature 0, 500-question test set, authors graded)

- Without search, overall accuracy ranged from 0.8% to 32.0% STRICT and 0.8% to 46.4% RELAXED across T5 770M to PaLM 540B, Codex, GPT-3.5, ChatGPT and GPT-4.
- GPT-4's STRICT scores by type were 12.0 (fast-changing), 4.0 (slow-changing), 64.3 (never-changing) and 33.9 (false-premise), 28.6 overall.
- False-premise accuracy stayed within 0.0 to 1.6% for T5 and PaLM at every size, while OpenAI models scored 25.8 to 42.7% STRICT.
- **FreshPrompt** places Google Search results in the prompt, ordered oldest to newest, plus few-shot demonstrations, in one call. With 10 evidences and 5 demonstrations, GPT-4 moved from 28.6 to 75.6 STRICT and 46.4 to 77.8 RELAXED, shrinking the gap from 17.8 to 2.2 points. GPT-3.5 with 5 evidences went from 26.0 to 56.0 STRICT. On STRICT the comparison points were Perplexity at 52.2, GPT-3.5 plus Self-Ask at 41.6 and plain Google Search at 39.6.
- GPT-4 STRICT with 1, 5, 10 and 15 evidences was 61.4, 70.6, 75.6 and 77.6; 15 demonstrations scored 74.6, so evidence count mattered and demonstrations did not.
- Adding an explicit premise-check instruction lifted false-premise STRICT by 23.4 points for GPT-3.5 and 6.4 for GPT-4, yet cut GPT-3.5's overall STRICT from 56.0 to 35.2.
- For PaLM 540B on pre-2022 questions, few-shot beat chain-of-thought under STRICT; the authors say chain-of-thought leaves more room for hallucination.

## Limits

Answers go stale between maintainer updates, and only Google Search, one query per question and simple English questions were tested. No confidence intervals, with 125 questions per type. The authors who built the method did all grading, agreement rests on 100 answers as raw agreement, and the model behind FreshEval is not named. The results are one April 2023 snapshot of models since superseded; the authors note newer versions can browse, and the authors report that ChatGPT and GPT-4 displayed knowledge beyond their stated cutoffs.

## See Also
- [[Tool-Augmented Factuality Checking]] — related (evidence-from-search idea applied to checking rather than answering)
- [[Eval Contamination Defenses]] — related (temporal freshness as a defence)
- [[RAG Evaluation]] — related
- [[TruthfulQA]] — alternative-to (a factuality benchmark built around imitative falsehoods rather than currency)
- [[FACTS Leaderboard]] — alternative-to (a four-part factuality suite that includes a search sub-benchmark)
- [[UQ Unsolved Questions Benchmark]] — related (a versioning rule for a semi-live question set)
