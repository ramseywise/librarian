---
title: ETHICS Benchmark
tags: [eval, reference]
summary: "ETHICS is a dataset of over 130,000 scenarios for testing whether a language model predicts everyday moral judgments across justice, deontology, virtue, utilitarianism and commonsense morality; on its adversarially filtered Hard Test every model tested averaged under 50% (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-hendrycks-2020-aligning-ai-shared-human-values.md
---

# ETHICS Benchmark

Hendrycks, Burns, Basart et al. (arXiv 2008.02275, ICLR 2021) ask whether language models can
predict widespread human moral judgments. They build ETHICS, with over 130,000 contextualised
scenarios in five ethical perspectives: justice, deontology, virtue, utilitarianism and
commonsense morality. Their hypothesis is that fine-tuning models on scenario-based ethics data lets
them learn part of the link between facts about the world and human values, though incompletely.

## How it is built

Scenarios come from crowdsourcing on MTurk and from Reddit. They are cleaned by multi-annotator
consensus and contrast-set construction, then
adversarially filtered with a distilBERT and distilRoBERTa ensemble. The highest-loss examples
form the **Hard Test**, next to a normal Test set. Each task fine-tunes the transformers on its Dev set; GPT-3 is evaluated few-shot. The utilitarianism task trains a utility function with a
pairwise loss: minus the log of the sigmoid of the utility difference between two scenarios.

## Results (self-reported)

Setup is fine-tuning on Dev, best run, scores averaged over the five tasks, unless noted.

- ALBERT-xxlarge has the top average on the normal Test set. On the Hard Test, every model
  averages under 50%.
- Few-shot GPT-3 Davinci (175B) scores 39.3 on the Test set and 32.3 on the Hard Test. On Test it trails the fine-tuned
  transformers; on the Hard Test utilitarianism and commonsense tasks it competes with them. Its accuracy rises slowly from Ada (2.7B) to Davinci.
- The GloVe word-averaging baseline is the weakest model, only just above random on the Test average.
- On a set of about 1,000 contentious commonsense examples, predictive uncertainty separates
  contentious from clear-cut cases poorly (BERT-large 58%, ALBERT-xxlarge 56%, RoBERTa-large best).
- RoBERTa-large's utility function is inconsistent: U(I won $100,000.) = 15.2, above
  U(I won $101,000.) = 14.9, above U(I won $101,101.) = 11.5; it is also framing-sensitive, with
  U(half full) = 0.2 against U(half empty) = -1.7.
- English-speaking Indian annotators agree with 93.9% of the US-derived commonsense Test labels,
  which the authors read as some cross-cultural disagreement.

## Limits

- Annotators were English speakers from the US, Canada and Great Britain, so the labels reflect
  Western moral views.
- It covers clear-cut scenarios only, not dilemmas or contentious topics; its datasheet warns
  against use on ambiguous dilemmas, notes that Reddit posters may be identifiable, and says no update is planned.
- A grid search on the normal Test set picked hyperparameters and the best run is shown, which
  flatters the Test numbers; seed counts are not given.
- The Dev set is too small to instil ethical knowledge in a model; the dataset measures, and does
  not teach.
- The authors call it a first step. The models are from before 2021 (BERT family, GPT-3), so the
  numbers have dated for current LLMs.

## See Also
- [[Extreme-Risk Model Evaluation]] — related (a different safety evaluation, of capabilities and propensity)
- [[Constitutional AI and RLAIF]] — related (an alternative way to specify values to a model)
- [[TruthfulQA]] — related (another alignment-flavoured benchmark built adversarially against a model)
- [[Benchmark Prompt Format Sensitivity]] — related
