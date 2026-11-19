---
title: MuSiQue Multihop QA
tags: [eval, language-tasks, benchmark]
summary: "MuSiQue composes filtered single-hop questions into 2-4 hop questions so that no sub-question can be answered without the previous answer; a Longformer-Large model scores 42.3 answer F1 on it against 72.9 on equal-size HotpotQA and 2WikiMultihopQA training sets (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-trivedi-2022-musique.md
---

# MuSiQue Multihop QA

Trivedi et al. build a multihop QA dataset bottom-up so that, by construction, it needs connected multihop reasoning and resists shortcuts. Two versions exist: **MuSiQue-Ans** (about 25K questions of 2-4 hops) and **MuSiQue-Full** (about 50K, adding unanswerable contrast questions).

## Construction

The source pool is made of single-hop questions drawn from five datasets built on Wikipedia. They are filtered, then paired when one answer bridges to the next question, and Longformer models drop pairs solvable by disconnected reasoning. Pairs become DAGs of two to four hops. The split is designed to limit train-test leakage, each question gets a 20-paragraph context containing positive distractors, and MTurk workers write the final wording. The **MuSiQue condition** requires that no sub-question can be answered if its predecessor's answer is masked, and none without context. **Disconnected reasoning** is reaching the correct answer without using all the supporting facts.

## Results (self-reported)

- With 20K training instances for each dataset, end-to-end Longformer-Large reaches 42.3 answer F1 on MuSiQue-Ans, whereas HotpotQA-20k and 2WikiMultihopQA-20k both give 72.9.
- Best model (Select+Answer, RoBERTa-large selector with Longformer-Large answerer): 47.3 on MuSiQue-Ans validation against 74.9 (HotpotQA) and 79.5 (2Wiki). Human answer F1 is 78.0 (upper bound 88.6), a gap of about 27 points against 10 and 5.
- Under step execution, answer F1 drops as questions get longer: 57.9 for two hops, 47.9 for three and 28.1 for four.
- A single-paragraph model gets 32.0 against 64.8 (HotpotQA) and 60.1 (2Wiki); the disconnected-reasoning score is 37.8 against 68.8 and 63.4.
- Ablations on end-to-end F1 from 42.3: a random split without leakage control gives 87.3, removing the disconnection filter 60.6, and 10 Wikipedia distractors in place of 20 positive ones 57.2.
- Ground-truth decompositions add 9.4 answer F1 to step execution.
- A human check matched the gold answerability label on 45 of 50 MuSiQue-Full instances (one author).

## Limits

- Only fine-tuned Longformer, BART and T5-family models were tried, with no prompted LLMs, so the results are dated for current use.
- The task is reading comprehension over 20 supplied paragraphs; an open-domain version is left to future work.
- The disconnection filter covers head questions' first condition and uses transformer models, which could bias difficulty (an RNN baseline checks this).
- Hyperparameters, optimiser, hardware and seeds go unreported, and the human score comes from 125 questions per dataset.

## See Also
- [[HotpotQA]] — alternative-to
- [[2WikiMultiHopQA]] — alternative-to
- [[KILT Benchmark]] — related
- [[SEM First-Answer-Gated Search Reward]] — related (MuSiQue as the search-expected half of the training mix)
