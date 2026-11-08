---
title: Long-Form QA Evaluation Hurdles
tags: [eval, concept]
summary: "Krishna et al.'s 2021 control experiments on long-form QA (ELI5, KILT): random retrievals barely move ROUGE-L, a copied question beats a retrieval-augmented system on it, and humans prefer gold answers 68% to 14%, so leaderboard gains there say little about answer quality (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-krishna-2021-hurdles-progress-long-form-question.md
---

# Long-Form QA Evaluation Hurdles

Krishna, Roy and Iyyer (NAACL-HLT 2021, arXiv 2103.06332) ask whether long-form question answering (LFQA) systems, the ELI5 dataset and the metrics used on them (ROUGE-L, human A/B tests) support a real measure of progress. They build a system that tops the KILT ELI5 leaderboard, a 486M-parameter Routing Transformer conditioned on the top 7 Wikipedia paragraphs from a contrastively trained dense retriever (C-REALM), then use control experiments on that system to probe the evaluation.

## Control experiments and what they showed

All figures about the authors' own system are self-reported.

- **Random retrievals.** Swapping the retrieved paragraphs for random Wikipedia paragraphs at inference barely changes ROUGE-L (RT + C-REALM, nucleus p = 0.6, ELI5 validation). The Spearman correlation between ROUGE-L and unigram overlap with the retrievals is near zero, and it is 0.13 even on the roughly 23% of instances in which retrieval did surface the gold document (self-reported). In a human A/B test at p = 0.6, raters split 40% (78) for predicted retrievals against 33% (64) for random ones, within 7 points (self-reported).
- **Train/validation overlap.** Of 300 sampled validation questions, at least 81% have a paraphrase among their 7 nearest training questions, and all have a topically similar one (three crowd raters per pair, majority vote, then manual checking). A RoBERTa-large paraphrase classifier trained on QQP flags far fewer overlaps than the raters do. Retrieval does much better on overlapping questions, while generation barely improves (p = 0.6).
- **Trivial lower bounds.** On ELI5 validation, an answer made of the question repeated five times scores 20.0 ROUGE-L against 16.1 for RAG, and a random training answer scores 16.2. On test the figures are 16.9 (copied input), 14.1 (RAG) and 15.5 (random training answer). The copied-question and random-answer baselines are the authors' own; RAG is the comparison system.
- **Upper bounds.** Choosing the best of the 7 retrieved training answers by oracle gives 28.5 ROUGE-L on validation, above every system; this is not a deployable system. The authors' system also out-scores the longest gold answer on ROUGE-L (the gold answer being scored against the other references, about 12 per question), yet raters prefer gold answers to its generations 68% to 14% at p = 0.6 (138 of 203 ratings) and 72% to 17% at p = 0.9 (self-reported).
- **Length.** Truncating the p = 0.6 model's outputs to the first 10% of tokens (18.2 tokens) drops ROUGE-L from 24.4 to 17.4; repeating the truncated text 1/f times to restore the length gives 18.2, which is still lower.
- **Leaderboard.** On KILT ELI5 test the authors' system reaches a KILT R-L of 23.2 with R-Prec 10.7, Recall@5 24.6 and F1 22.9 at p = 0.6. Generation-only BART beats RAG and BART + DPR on ROUGE-L on the same leaderboard, which the paper reads as retrieval not helping generation there.

Ablations on the retriever (validation retrieval): R-Prec 13.3 at batch size 12,288 against 6.8 at 512, and 13.3 when initialised from REALM against 9.3 from ICT.

## What the human evaluation adds

In interviews, the volunteer annotators said each pair took them around two minutes and that unfamiliar technical topics made correctness hard to judge. A/B tests give a relative preference only.

## Limits

- The no-grounding result is shown for one system; other generators were not tested (leaderboard comparisons are indirect), and the authors' explanations (source-reference divergence, overlap between train and validation questions, long-text pretraining) are hypotheses.
- The raters were 20 volunteers, mostly computer-science graduate students and not domain experts; there are no significance tests, some table cells have fewer than 50 samples, and Fleiss kappa on the overlap annotation is 0.29.
- Overlap annotation covers 300 validation questions, and its no-overlap subset has only 53 samples.
- Generator hyperparameters were chosen manually with no search, and no seeds or variance are reported.
- Upper bounds exist for validation only because test answers are hidden, and the best-of-7 train answer is an oracle.
- The models are from 2021 (BART, RAG, T5-base); no LLM-judge or faithfulness metric was evaluated. The extraction does not say which perplexity value is the one with retrieval.

## See Also
- [[Eval Metric Interpretation Pitfalls]] — prerequisite-for
- [[Output Length Confounds Reference Metrics]] — related (the same length effect on n-gram scores)
- [[RAG Evaluation]] — related (checking that the generator uses what was retrieved)
- [[Text Metrics Beyond N-gram Overlap]] — related (learned and embedding alternatives to ROUGE and BLEU)
