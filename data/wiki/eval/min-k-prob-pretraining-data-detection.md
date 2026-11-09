---
title: Min-K% Prob Pretraining-Data Detection
tags: [eval, pattern]
summary: "Min-K% Prob scores a text by the average log-probability of its lowest-probability tokens to guess whether a model trained on it; on the WikiMIA benchmark it averaged AUC 0.72 against 0.67 for perplexity, and caught about a fifth of members at a 5% false-positive rate (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-05-shi-2023-detecting-pretraining-data-large-language.md
---

# Min-K% Prob Pretraining-Data Detection

Shi et al. (arXiv 2310.16789, ICLR 2024) ask whether a given text was in a language model's pretraining data, with the model treated as a black box that returns token probabilities. The detector needs neither a reference model nor knowledge of the training corpus.

## The method

Take every token's probability given its prefix, select the k% with the lowest probabilities, and average their log-probabilities. A higher average points to a member. The authors tried k between 10 and 50 on validation data with one LLaMA model, picked k = 20, and used it everywhere. Detection by this score does not need a threshold when reported as AUC.

## WikiMIA

WikiMIA pairs 394 non-member Wikipedia event pages (created after 1 January 2023) with 394 randomly chosen member pages from before 2017 (also printed as before 2016), truncated to 32, 64, 128 or 256 tokens, in original and ChatGPT-paraphrased forms.

## Results (self-reported)

- **Headline.** Over five open models (Pythia-2.8B, NeoX-20B, LLaMA-30B, LLaMA-65B, OPT-66B), both settings, the mean AUC was 0.72, with perplexity the strongest baseline at 0.67; Neighbor and Zlib averaged 0.65, Lowercase 0.61, a smaller reference model 0.66. The authors call this a 7.4% relative gain.
- **At a fixed false-positive rate.** TPR at 5% FPR averaged 22.2 (Zlib 20.6, perplexity 19.3).
- **Simulated downstream contamination.** LLaMA-7B received one more epoch (learning rate 1e-4) over 27M tokens of RedPajama text into which 200 examples per dataset were inserted (0.1% contaminant), with 200 more held out. Mean AUC was 0.86 against 0.84 for perplexity; per dataset, IMDB 0.98, BoolQ 0.91, Commonsense QA 0.80 and TruthfulQA 0.74. At learning rate 1e-5 AUC dropped to 0.64, 0.59, 0.76 and 0.56 on four of the five datasets (LSAT QA 0.72).
- **Trends.** Larger models, longer texts and more duplicated occurrences all made detection easier. Detecting outlier contaminants got easier as the corpus grew, while detecting in-distribution text got harder.
- **Copyrighted books.** With text-davinci-003, validation AUC was 0.88 against 0.84 for perplexity, and nearly 90% of 100 Books3 books were flagged above 50% contamination.
- **Unlearning audit.** On a model fine-tuned to forget Harry Potter, 188 of about 1,000 chunks looked suspicious, 5.3% of completions scored 4 or higher from GPT-4, and the 103 selected questions had ROUGE-L recall 0.23 against 0.10 for unselected ones.

## Limits

The only fitted threshold (books) is not printed, and the book test treats all 100 books as positives with no negative control beyond the validation set; validation positives are "likely" members. Members and non-members differ in date as well as membership, and the paper does not test whether the score picks up that shift. The contamination numbers come from a small fine-tuning simulation rather than real pretraining, and near-chance AUC appears at the lower learning rate. The one closed model covered is text-davinci-003, because token probabilities are required. The 7.4% is relative, about 5 AUC points. There are no confidence intervals or seeds, and there is no limitations section.

## See Also
- [[Eval Contamination Defenses]] — related (a probabilistic leak check for models whose training data is unknown)
- [[MLE-bench]] — related (contamination checks on a benchmark)
- [[Diffusion Model Training-Data Extraction]] — related (extraction of memorized training data from generative models)
- [[Green-List LLM Watermark]] — related (the other direction: marking output so it can be traced)
- [[DetectGPT]] — related (zero-shot detection from model probabilities)
