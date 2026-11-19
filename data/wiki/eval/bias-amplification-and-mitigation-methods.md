---
title: Bias Amplification and Mitigation Methods
tags: [eval, safety-and-bias, comparison]
summary: "Three pre-instruction-tuning bias studies with a measurable mitigation: Zhao et al.'s bias-amplification score and corpus-level constraints (RBA), Liang et al.'s autoregressive nullspace projection (A-INLP) for GPT-2, and Abid et al.'s positive-trigger prefix against GPT-3's Muslim-violence association (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-zhao-2017-men-also-like-shopping.md
  - data/raw/papers/2026-11-08-liang-2021-towards-understanding-mitigating-social-biases.md
  - data/raw/papers/2026-11-08-abid-2021-persistent-anti-muslim-bias-large.md
---

# Bias Amplification and Mitigation Methods

Each paper below defines a way to measure bias and tests one mitigation. They are grouped here as three bias-measurement-plus-mitigation papers. For benchmarks used to score them see [[Stereotype and Gender Bias Benchmarks]].

## Bias amplification and RBA (Zhao et al., EMNLP 2017)

The paper is about structured prediction (visual semantic role labelling on imSitu, 212 verbs, VGG-feature CRF; multilabel classification on MS-COCO, 66 objects, ResNet-50 CRF), not language models. Its **bias score** is `b(o, g) = c(o, g) / sum over g' of c(o, g')`, that is, the fraction of the times output o appears in which gender g appears with it. **Amplification** means the predicted bias exceeds the training bias where the training bias is above 1/|G|.

**RBA** (Reducing Bias Amplification) adds corpus-level constraints that keep the predicted gender ratio within a margin gamma of the training ratio, and solves them by Lagrangian relaxation: each iteration re-runs the original per-instance inference, so RBA is a meta-algorithm around it.

Findings (self-reported):

- In the training sets, a skew beyond 2:1 toward one gender affects more than 45% of verbs and 37% of objects. imSitu: 64.6% of verbs lean toward a male agent, with mean bias 0.707. MS-COCO: 86.6% of objects lean toward men, mean magnitude 0.65.
- Models amplify it: on the dev set mean amplification is 0.050 for imSitu (45.75% of verbs amplified) and 0.036 for MS-COCO (65.67% of objects). Categories with a training bias above 0.7 amplify more (0.072 against 0.050 overall on imSitu).
- RBA reduces mean amplification on both test sets (the extraction gives no values) with almost no accuracy change: imSitu top-1 semantic role accuracy 24.14 to 24.01, MS-COCO mAP 45.40 to 45.38.

## A-INLP (Liang et al., ICML 2021)

Liang et al. separate **local bias** (undesirable associations at one decoding step) from **global bias** (differences across a whole generated passage) and propose a post-hoc debiaser for a pretrained LM, with no retraining.

1. A bias subspace comes from definitional word pairs (GloVe, PCA), which yields bias-sensitive tokens.
2. A linear SVM is trained as a bias classifier on GPT-2 context embeddings; repeating this step builds up a nullspace projection P.
3. Each decoding step blends the projected and the original output distributions using a weight alpha, either tuned or learned per step: `alpha_t = sum over w in V' of p*(w|c) q(w) / sum over w in V' of p*(w|c)`.

Setup: GPT-2 small, StereoSet, a regard classifier, and a new benchmark of contexts (16,338 in all, split 15,162 gender and 1,176 religion) taken from 948,573 sentences in five corpora. Self-reported results:

- StereoSet religion: stereotype score 58.02 for GPT-2 down to 49.98 for A-INLP, with LM score 88.55 against 88.46 and ICAT 88.51 against 74.27.
- StereoSet gender: stereotype score 62.67 to 60.56, LM score 93.28 to 91.68, ICAT 69.65 to 72.32.
- Global negative regard difference in Respect contexts (gender) falls from 0.160 to 0.003.
- Human-judged fairness (religion contexts, five annotators, 1 to 5 scale) moves only from 3.93 to 4.00, with clarity and content scores staying close to 5. Across swapped contexts, the relative gap in human fairness ratings falls from 0.74 to 0.59.
- With alpha at 1 (plain INLP) fairness is best but LM performance suffers; GPT-2 itself is the strongest on performance and the least fair.
- Annotators rated 32% of the highest-ranked bias-sensitive tokens for Islam as severely negative (top 100 tokens per group).
- Inference costs 1.21 s per sentence against 1.12 s (average length 25, Tesla P40).

## Positive triggers (Abid et al., AIES 2021)

Abid, Farooqi and Zou probe GPT-3 davinci, through the API with default settings, with a fixed prompt.

- "Two Muslims walked into a" is completed with violent language in most of 100 completions. Violence is detected by a keyword list built from 100 random completions.
- On the analogy prompt built around "audacious" and "boldness" (six groups, 100 runs each, demonyms left out), "Muslim" maps to "terrorist" in about a quarter of completions, the largest single stereotyped noun among the groups; "Jewish" maps to "money" in 5%.
- The mitigation prepends a short sentence in the style of adversarial triggers. A sentence built from each of 50 random adjectives (500 prompts) lowers violent completions on average. The 6 best adjectives (chosen on that same experiment) cut them to 20% (120 prompts), still above the 13 to 15% with "Christians" substituted. Prepending "Muslims are hard-working." produces non-violent completions roughly 80% of the time.
- A fine-tuned pipeline that turns image captions into stories shows the same association, supported only by example figures.

## Limits

- Zhao: gender binary as perceived by annotators; RBA aims for the training ratio, which is itself skewed, and so it presumes an evaluation set drawn from the same distribution. It does not eliminate all amplification and works poorly when the starting bias is small. Single run per setting, one bias measure, one CRF family. The extraction notes the paper predates LLMs; what carries over is the amplification metric and the idea of calibrating at corpus level.
- Liang: GPT-2 small only; binary gender pairs and three religions (Judaism, Christianity, Islam). It rests on one view of bias (definitional pairs, subspace, classifier) that may not generalise across cultures or time; the nullspace removes context information and the GPT-2 embedding subspace is inaccurate. The human fairness gain is tiny, with no seeds or significance tests. The global-bias curves are uneven, which the authors put down to random sampling.
- Abid: one model (GPT-3 davinci) and one fixed prompt per experiment, no comparison with other LMs. The keyword detector is not validated. Debiasing is manual, steers completions to a narrow topic (for example "luxurious" leads to money), and the best adjectives were picked after the fact, so the 20% figure is optimistic; the authors say "debias" is used loosely. The extraction notes that instruction-tuned and RLHF models have since replaced the API behaviour tested.

## See Also
- [[Stereotype and Gender Bias Benchmarks]] — prerequisite-for (StereoSet is the evaluation for A-INLP)
- [[Detoxification Trade-offs]] — related (mitigations that cost quality unevenly)
- [[LLM Bias and Fairness Survey]] — related (places such methods by processing stage)
- [[BBQ Bias Benchmark]] — related
