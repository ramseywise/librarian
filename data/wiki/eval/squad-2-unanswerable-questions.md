---
title: SQuAD 2.0 Unanswerable Questions
tags: [eval, language-tasks, benchmark]
summary: SQuAD 2.0 adds 53,775 crowdworker-written unanswerable questions with plausible wrong answers to SQuAD, so a model must abstain; the best 2018 model scored 66.3 F1 against 89.5 for humans.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-rajpurkar-2018-know-what-you-dont-know.md
---

# SQuAD 2.0 Unanswerable Questions

Rajpurkar, Jia and Liang (ACL 2018, short paper) ask whether a reading dataset with adversarially written unanswerable questions can force extractive models to know when the paragraph supports no answer. The dataset is called SQuADRUn here and SQuAD 2.0 elsewhere.

## Construction

Crowdworkers wrote unanswerable questions about [[SQuAD]] paragraphs. The questions are required to look relevant to the paragraph and to have a plausible answer span. The 53,775 new questions were merged with the SQuAD splits. A negative example is a passage paired with an unanswerable question. Of 100 random dev negatives checked by hand, 93% were truly unanswerable.

The paper compares this against two automatic ways of making negatives: TFIDF and RULEBASED (negatives following Jia and Liang 2017).

## Results (self-reported)

Three existing no-answer models were trained with an abstention threshold tuned on dev.

- Best model (DocQA + ELMo, trained and tested on SQuADRUn) reaches 66.3 F1 on test, 23.2 below humans at 89.5 (a majority vote among 4.8 answers per question on average).
- A baseline that always abstains reaches 48.9 test F1.
- The same architecture trained on SQuAD scores 85.8 F1 against 91.2 for humans, a gap of 5.4.
- Dev F1 for DocQA + ELMo is 67.6 on SQuADRUn, 83.0 on SQuAD + TFIDF and 89.6 on SQuAD + RULEBASED, so crowd-written negatives are the harder ones (15.4 below the best of the other two).
- For both models and humans, about half of the wrong answers given to unanswerable questions were the plausible answers the writers had planted.

## Limits

- Only three extractive models of 2017-2018 were evaluated; no training hyperparameters or seeds are reported, and the abstention threshold was tuned on dev.
- Human accuracy here is a majority of 4.8 answers, unlike the single human of SQuAD 1.1, so the gaps are not strictly comparable.
- The Appendix A.2 distractor results are not in the extracted PDF.

## See Also
- [[SQuAD]] — prerequisite-for (the base data, splits and EM/F1 metrics)
- [[Reading Comprehension and Conversational QA Datasets]] — related (QuAC and CoQA also contain unanswerable questions)
