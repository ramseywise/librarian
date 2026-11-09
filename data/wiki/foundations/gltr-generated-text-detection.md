---
title: GLTR
tags: [foundations, concept]
summary: "GLTR scores each token's probability, rank and predictive entropy under a detection language model and colours the text by rank bucket; in a 35-student study the overlay raised human detection of fake text from 54% to 72% (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-gehrmann-2019-gltr.md
---

# GLTR

Gehrmann, Strobelt and Rush (ACL 2019 system demonstrations, arXiv 1906.04043) ask if basic statistical tests computed under a language model, displayed as a visual overlay, let non-experts spot machine-written text. Their hypothesis is that generators over-sample the head of the distribution, so their text has fewer low-rank words than human writing, and that the effect survives in a black-box setup where another large LM does the detecting. GLTR names the open-source tool they deployed publicly, pronounced Glitter.

## Mechanism

The detector, either GPT-2 117M or BERT, supplies each token's probability, rank and predictive entropy. The interface paints tokens by rank band (green up to 10, yellow up to 100, red up to 1,000, purple beyond) and shows histograms. The authors checked the features by fitting logistic regression to three generated and three human sources, and ran a human study comparing detection with and without the overlay.

## Results (self-reported)

- In a study with 35 students (five texts per round, 90 s a text; two GPT-2 samples at temperature 0.7, one Heliograf text, two NYT texts) the GPT-2 117M overlay lifted accuracy at flagging fake text from 54% to 72%, untrained. Round one, with no overlay, was only just above chance.
- With no overlay, people trusted Heliograf text over GPT-2 text. Only 40% of the texts were genuine, but 56.0% of them were trusted (p < 0.01).
- Logistic regression with cross-validation over 50 articles from each of 6 sources, using a white-box GPT-2 117M detector (the fake text came from GPT-2 1.5B and from Heliograf), found rank-bucket features the best separator and bag-of-words the worst. A BERT detector, which is black box here, scored almost the same AUC on rank buckets.
- Features based on average probability are weaker and vary a lot: 0.71 +-0.25 with GPT-2 and 0.70 +-0.27 with BERT.
- Under GPT-2, genuine text more often contains words outside the top 100 predictions, including against lower-temperature sampling. The classifier's odds ratio for a word being the top-1 prediction is 0.09.
- A claim from Fig 5: human text still picks high-rank words in low-entropy contexts, which sampled text does not (NYT compared with GPT-2 at temperature 0.7).

## Limits

- The authors admit the key assumption, sampling biased toward the head of the distribution, is itself a weakness: adversarial schemes might defeat the overlay, though tail sampling harms coherence.
- Text generated from a hidden seed follows a different conditional distribution, and only a preliminary qualitative look was taken.
- Data are small (50 articles for each of six sources), AUC variance spans +-0.07 to +-0.27, the people tested are 35 students in a single NLP class reading 5 texts a round, and false-positive rates are not analysed.
- The extraction notes: the detectors date from 2019 (GPT-2 117M, BERT) and current LLMs, with different sampling and instruction tuning, were not tried. The related-work section says the entropy result flipped relative to Lavergne et al. (2008) as language models got better.
- Only a statistical signature is detected, not misinformation.

## See Also
- [[DetectGPT]] — alternative-to (curvature of log probability instead of rank buckets; names GLTR as a baseline)
- [[Green-List LLM Watermark]] — alternative-to (embeds a mark rather than reading a statistical signature)
- [[Min-K% Prob Pretraining-Data Detection]] — related
