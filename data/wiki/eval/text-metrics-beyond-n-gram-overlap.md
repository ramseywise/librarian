---
title: Text Metrics Beyond N-gram Overlap
tags: [eval, concept]
summary: "Four 2019-2020 metrics that replace word overlap with something else: BERTScore (greedy embedding matching), BLEURT (BERT pretrained on synthetic perturbations, then tuned on human ratings), CodeBLEU (BLEU plus syntax-tree and data-flow matches) and USR (reference-free dialog scoring), each reporting gains on its own correlation setup (self-reported), plus a 2022 study where ROUGE and human preference ranked prompted GPT-3 summaries in opposite order."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-zhang-2019-bertscore.md
  - data/raw/papers/2026-11-07-sellam-2020-bleurt.md
  - data/raw/papers/2026-11-07-ren-2020-codebleu.md
  - data/raw/papers/2026-11-07-mehri-2020-usr.md
  - data/raw/papers/2026-11-07-goyal-2022-news-summarization-evaluation-era-gpt.md
---

# Text Metrics Beyond N-gram Overlap

All the numbers are the papers' own and self-reported, and each is tied to its own human-rating setup, so the correlations should not be compared across sections.

## BERTScore

Zhang et al. (ICLR 2020, arXiv 1904.09675) embed the reference and candidate tokens with a pretrained encoder, with no training or fine-tuning. Cosine similarity is computed for every token pair and each token is greedily matched to its most similar counterpart. Averaging gives recall (over reference tokens), precision (over candidate tokens) and F1, optionally weighted by idf and rescaled with a baseline: with b the metric's empirical lower bound, the rescaled score is (R-b)/(1-b).

- WMT18 German-to-English segment level (78k pairs, RoBERTa-large): F1 correlates at 0.550 with and without idf, against 0.415 for sentence BLEU.
- PAWS-QQP dev (667 sentences), AUC for telling adversarial paraphrases apart: 0.693 for the idf variant against 0.527 for BLEU, which is near chance.
- Picking the better system among hybrids (10K hybrid systems, 100 sampled 100K times, WMT18 en-de, translating into English): Hits@1 0.824 against 0.803 for BLEU.
- COCO 2015 captioning (12 systems, M1 human judgements): precision is negatively correlated and F1 reaches only 0.322; recall (with idf) is the best variant.
- The layer to use for RoBERTa-large is the 17th of 24 (WMT16 to-English validation), with correlation dropping sharply in the last layers. Replacing greedy matching with WMD did not consistently help (WMT17, 12-layer uncased BERT).
- Speed on a GTX-1080Ti for 2,998 WMT18 en-de sentences: 15.6 s against 5.4 s for SacreBLEU.

## BLEURT

Sellam et al. (ACL 2020) further pretrain BERT on about 6.5 million synthetic (reference, perturbed) pairs built from 1.8 million Wikipedia segments, with a multi-task loss over 9 signals (BLEU, ROUGE, BERTScore, backtranslation likelihoods, an entailment score and a backtranslation flag). It is then fine-tuned to predict human ratings through a regression head over the [CLS] vector.

- BLEURT (BERT-large, fine-tuned on WMT15-16 ratings) tops the average Kendall Tau on WMT17 into-English pairs, with BERTScore and sentence BLEU behind.
- Pretraining adds up to 7.4 Tau points on WMT17 zh-en for the base model and up to 2.1 on WMT18 (tr-en).
- On a WMT17 resample skewed toward low-quality training data, without pretraining the model drops under BERTScore at a skew of 1.0 and under sentence BLEU from 1.5; the pretrained model falls below those baselines only at skew 3.0 (read from a figure), where 11.9% of the 5,344 training records remain.
- Ablation (WMT17, read from a figure): BERTScore, entailment and backtranslation signals help, while the BLEU and ROUGE signals hurt.
- On WebNLG, the variant fine-tuned on WMT only is competitive with BERTScore with as few as 836 training records.

## CodeBLEU

Ren et al. (arXiv preprint, 2020) define CodeBLEU as alpha*BLEU + beta*(keyword-weighted n-gram match) + gamma*(syntax-tree match) + delta*(data-flow match), and test it against programmer ratings (1 to 5, 10 judges, 50 samples, 3 to 4 systems per task, Pearson over system means).

- Using the recommended weight set of 0.1, 0.1, 0.4 and 0.4, the correlations are 0.981 (text-to-code, 4 systems), 0.975 (Java-to-C# translation, 4 systems) and 0.980 (Java bug-fix refinement, 3 systems), above BLEU on all three.
- On refinement, exact-match accuracy correlates better than CodeBLEU: BLEU scores sit at 90.35 to 92.80 across three systems while accuracy is 3.00 to 17.6 and the human score 1.378 to 2.022 (500 test samples).
- In the ablation, the syntax-tree component by itself reaches 0.985 on text-to-code against 0.977 for the full metric, and the weighted n-gram component by itself reaches 0.985 on refinement.

## USR

Mehri and Eskenazi (ACL 2020) combine three RoBERTa sub-metrics, a masked-language-model likelihood and two retrieval scores that give the probability a reply is the true one rather than a random one, through a regression fitted to human ratings. It needs no reference reply, which suits dialog where many replies are acceptable. Six researchers rated six qualities of responses to 60 contexts from each of two corpora (Topical-Chat and PersonaChat), and the authors compared USR with 13 overlap and embedding metrics.

- For Overall Quality at system level, Spearman correlation is 1.0 on both corpora, with Pearson at 0.92 and 0.82. The extraction gives PersonaChat turn-level correlation as 0.48 in the paper's abstract.
- A constant reply made of the ten most common tokens beat the corpus's Transformer on F-1 (Topical-Chat).
- On PersonaChat the retrieval sub-metric alone, given the context, beats the full metric on Overall Quality; on Topical-Chat, METEOR is the best non-USR metric for Maintains Context.
- The authors say USR should be used alongside human evaluation.

## Metrics on prompted GPT-3 summaries

Goyal, Li and Durrett (2022 preprint) compare zero-shot text-davinci-002 with BRIO and T0 in an A/B study on 100 recent articles each from CNN and BBC, where three Prolific annotators voted on each article. Annotators preferred GPT-3 by at least 20 points over the next system, significant by paired bootstrap (self-reported). Reference-based metrics ranked it the other way: ROUGE-L on 500 test articles was 31.44 for BRIO against 24.71 for GPT-3 on CNN, and 41.04 against 20.60 on XSum. The paper also reports that existing reference-free metrics fail on these summaries. Agreement among annotators was low (Krippendorff alpha 0.05 to 0.18) and unanimous best-summary choice for GPT-3 occurred for under 30% of articles.

## Limits

- BERTScore: no configuration wins everywhere. It misses factual slips (Tuesday for Monday) and unit equivalences, needs a reference, and the layer choice came from WMT16, which belongs to the same family as the test years. The evidence is translation, captioning, paraphrase detection and one compression set, with no open-ended generation.
- BLEURT is English, sentence-level and reference-based; the authors leave open whether to drop the BLEU and ROUGE signals. No seeds, variance or significance tests are reported, and the drift tests use a synthetic skew, not real drift.
- CodeBLEU: each correlation comes from just three or four systems with 50 rated samples, and the correlations themselves have no significance test, and the weights were tuned on the same human scores with no held-out check. The extraction gives the refinement correlation as 0.980 in the results and 0.979 in the limits, and does not reconcile the 0.981 (recommended weights) and 0.977 (ablation) text-to-code figures. It also flags the keyword weight in the keyword-weighted n-gram component as inconsistent (5x against 4x), which bears on the 0.985 refinement figure. Only Java and C# are covered; nothing is executed.
- USR: only 60 contexts per corpus, annotated by six researchers; the system-level figures come from very few systems (the extraction infers 5 for Topical-Chat and 4 for PersonaChat). The best sub-metric differs between corpora, training hyperparameters are not stated, and it may not suit non-generative systems.
- Goyal et al.: the extraction notes annotators made one overall-quality choice with no stated definition of quality, the study covers English news only and one model since superseded, and GPT-3's training data is unknown and may include summarization preference data.

## See Also
- [[Eval Metric Interpretation Pitfalls]] — prerequisite-for
- [[GPTScore]] — alternative-to (scores text by model probability instead of a trained or embedding-based metric)
- [[Output Length Confounds Reference Metrics]] — related (an n-gram failure these metrics try to avoid)
- [[Long-Form QA Evaluation Hurdles]] — related (ROUGE-L tested with trivial baselines)
- [[Summary Factual Consistency Metrics]] — related (QAGS reports BERTScore as a baseline)
- [[ROSCOE Reasoning Chain Metrics]] — related (uses BERTScore and BLEURT as baselines)
- [[MAUVE]] — instance-of
- [[BARTScore]] — instance-of (a likelihood-based metric)
- [[PEGASUS Gap-Sentence Pretraining]] — related (ROUGE-based claims)
