---
title: Summarization and Translation Hallucination Studies
tags: [eval, concept]
summary: "Two pre-LLM studies of hallucination in generated text: a human annotation of five XSum systems found hallucinations in over 70% of summaries and entailment as the best automatic proxy, and a token-level detector trained on synthetic noise reached average F1 near 0.6 on translation and summarization sets (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-maynez-2020-faithfulness-factuality-abstractive-summarization.md
  - data/raw/papers/2026-11-08-zhou-2021-detecting-hallucinated-content-conditional-neural.md
---

# Summarization and Translation Hallucination Studies

Both studies treat hallucination as generated text that the source does not support, and both split it into **intrinsic** hallucination (the source's information is misrepresented) and **extrinsic** hallucination (content absent from the source). Maynez adds **factual hallucination**, extra content that happens to be true.

## Maynez et al. (ACL 2020): human annotation of XSum

On 500 XSum test articles, three annotators per pair marked hallucinated spans and judged factuality for summaries from four models and for the gold references. Findings in that setup:

- Hallucinations of either kind appear in more than 70% of the single-sentence summaries.
- More than 90% of extrinsic hallucinations were erroneous.
- The gold references have 7.4% intrinsic and 73.1% extrinsic hallucination, so XSum gold summaries count as largely unfaithful.
- The BERT-initialised seq2seq system (BERTS2S) produced the most faithful and factual summaries (26.9% faithful), while the pointer-generator PTGEN had the lowest extrinsic rate.

Against these labels, a textual-entailment classifier correlated best with faithfulness (moderate), ROUGE-1 only very weakly, and a QA-based score almost not at all; entailment correlated only weakly with factuality. Choosing among four systems' outputs by entailment probability raised faithfulness by almost 5 points absolute at a cost in ROUGE (self-reported); training the entailment model further on annotations of faithful summaries gave a small additional gain (5-fold cross-validation).

## Zhou et al. (Findings of ACL 2021): token-level detection

The task is to label hallucinated tokens in a translation or summary without a reference at test time. Training data is synthetic: the true target is noised and BART decodes a hallucinated variant without seeing the source, and tokens changed according to edit distance are labelled hallucinated. XLM-R (translation) or RoBERTa (summarization) is fine-tuned on source, target and synthetic output with a token-classification loss plus a masked-language-model loss.

- Across six benchmark sets (two translation systems, four XSum systems) the detector averaged F1 near 0.6 (self-reported).
- On Zh-En outputs of MBART it scored F1 41.92 against 9.93 for an alignment baseline (self-reported).
- On XSum BERTS2S it scored 55.45 against 55.13 for word overlap and 53.07 for synonym matching, so its edge there is small (self-reported).
- Used as a loss mask in self-training on a Chinese-English patent set, token loss truncation brought the predicted hallucination rate down, from 10.00 to 6.37 (self-reported), and it gave the best flores BLEU in WMT19 corpus filtering for both language pairs.

## Limits

- Maynez: only XSum, five systems from 2017 to 2020, no model larger than BERT-Base or the small GPT-2; an entailment score uses no reference and can be gamed (a first sentence is always entailed), so it must be paired with ROUGE; the entailment model had learned from sentence pairs rather than document-summary pairs. The paper proposes no fix for hallucination.
- Zhou: the authors say the task is far from solved; annotator agreement on translation labels is moderate (about 0.56); synthetic edit-distance labels are not guaranteed correct; intrinsic and extrinsic are not told apart; the translation evaluation set is 250 sentences in one language pair; the XSum detector is hampered by a 512-token input limit that truncates articles; appendices are missing from the supplied PDF.

## See Also
- [[LLM Hallucination Surveys]] — related (LLM-era surveys that reuse the intrinsic/extrinsic vocabulary)
- [[Summary Factual Consistency Metrics]] — related (FactCC and QAGS, other proxies for faithfulness)
- [[Hidden-State Hallucination Probes]] — related (detection from model internals rather than a trained token classifier)
