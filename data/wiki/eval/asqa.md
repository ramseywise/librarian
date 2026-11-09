---
title: ASQA
tags: [eval, reference]
summary: "A long-form QA dataset of 6,316 ambiguous factoid questions whose answers must cover every interpretation, scored by DR, the geometric mean of ROUGE-L and a reader-based Disambig-F1; 2022 T5-large baselines sit far below humans (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-stelmakh-2022-asqa.md
---

# ASQA

Stelmakh and colleagues (EMNLP 2022) ask how long-form question answering can be given both a dataset and a precisely defined correctness metric. Their answer is to use ambiguous factoid questions from AmbigQA, where a good paragraph-length answer has to cover every disambiguated reading. Their hypothesis is that an answer is good when a reader could answer every disambiguated question from it, so a metric built on that idea should agree with human judgment.

## Dataset and metric

There are 6,316 questions in total, each with a paragraph-long answer written by annotators from Wikipedia that includes every disambiguated short answer. On the dev sets, answers average 64.8 words, compared with ELI5 at 103.0 and MS-NLG at 14.6. Annotators agree at 49.6 ROUGE-L F1, where ELI5 reaches 16.9.

The metric DR (the paper calls it Disambiguation-Rouge) is the geometric mean of two scores:

- **Disambig-F1:** a RoBERTa reader trained on SQuADv2 answers each disambiguated question using the generated answer as its passage; the score is the token-level F1 of its answers.
- **ROUGE-L** against the reference answers.

A companion score, STR-EM, checks whether each short answer string appears in the long answer.

## Results

Self-reported by the paper, on the ASQA dev set unless noted.

- Baselines: joint passage retrieval (JPR) alone, closed-book T5-large, open-book T5-large reading K top JPR passages, an oracle, and a pair of human conditions. Humans without context get 40.6 DR (200 questions, annotators searching by themselves) and humans given the disambiguations get 61.8. The oracle, T5 given gold support documents, gets 52.5.
- Open-book T5 with five passages beats closed-book T5 by 17.0 DR points, and its DR sits well below human performance. A random-retrieval baseline gets 7.8 DR.
- JPR@1 has 4.6 higher Disambig-F1 than open-book T5 with one passage but is about 197 words long, and the DR scores are similar. The gap between open-book T5 and JPR on Disambig-F1 widens as K grows (read from a figure, K of 1, 3, 5), which the authors read as T5 losing information from passages it reads.
- Human study (45 dev questions, six systems, judged by the authors): DR correlates best (Pearson) with the overall human score among the automatic metrics compared. Human accuracy is 8.4 for closed-book T5 and 28.0 for open-book T5 with five passages, against 94.3 for humans with context.

## Limits

- Disambig-F1 and STR-EM capture recall alone, so an answer padded with hallucinated content can still score well; the only penalties are indirect, through ROUGE-L and through distractors that confuse the reader.
- Annotator agreement may be inflated because all annotators share the AmbigQA disambiguations. Disambig-F1 needs a strong reader, and domains outside Wikipedia may need that reader fine-tuned.
- The human study is small and judged by the paper's authors; DR and Disambig-F1 are not significantly different. Disambig-F1 underestimates human accuracy but preserves the ordering.
- T5 training details are not given, and the baselines are 2022 T5-large models. Compared with ELI5 and MS-NLG, ASQA is far smaller.

## See Also
- [[Long-Form QA Evaluation Hurdles]] — prerequisite-for
- [[ALCE Citation Benchmark]] — related (uses ASQA as one of three datasets)
- [[FLARE Forward-Looking Active Retrieval]] — related (evaluated on ASQA)
- [[RAG Evaluation]] — prerequisite-for
- [[SQuAD]] — related (the reader behind Disambig-F1 is trained on its second version)
