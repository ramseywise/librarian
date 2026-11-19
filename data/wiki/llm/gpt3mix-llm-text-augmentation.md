---
title: "GPT3Mix: LLM Text Augmentation"
tags: [llm, pretraining-and-data, pattern]
summary: "GPT3Mix prompts GPT-3 with a mixture of k real labelled examples, takes the generated text and the normalised label-token likelihoods as a soft label, and adds the synthetic data to fine-tune BERT-style classifiers in low-data settings."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-yoo-2021-gpt3mix.md
---

# GPT3Mix: LLM Text Augmentation

Yoo et al. (Findings of EMNLP 2021) test whether an LLM, prompted with a blend of real examples, can write believable synthetic text with soft labels that helps small fine-tuned classifiers. They expect it to outperform shallow or latent-space mixing methods, and expect the benefit to go beyond memorisation.

## Method

Draw k=2 labelled examples and assemble a prompt from a description header, the text-label pairs and a prefix. GPT-3 writes a new text plus a label token, and the normalised likelihoods over label tokens become the soft label: each label y' gets a probability proportional to the LM's likelihood of that label's verbaliser token, given the prompt built from the generated text x' and the specification. The task specification S=(T, L, v) consists of the text type, the label type and a verbaliser mapping labels to tokens. Ten synthetic samples per real one are combined with the real subsample, and a BERT or DistilBERT classifier is trained on the mix with cross-entropy. To probe memorisation the paper also builds RT20, a movie-review benchmark dated after the GPT-3 training data.

## Results (self-reported)

- Across 7 datasets at a 0.1% subsample (davinci, ratio 10), GPT3Mix raises BERT-base average accuracy, with SST-2 showing a big margin over EDA and back-translation.
- BERT-large trained with GPT3Mix on 1.0% of SST-2 reaches the level of BERT-base trained on all of it.
- Gains stay large on RT20 (DistilBERT, 1.0%), so memorisation cannot be the whole explanation.
- Ablations on SST-2 0.1% with DistilBERT: soft labels outperform hard labels obtained by beam search; k=2 was compared to k=1; a bigger generator does better (davinci over ada); the open GPT-neo 1.3B comes close to davinci; and a specification written for the task beats a generic one.
- Using the wrong label-type word (linguistic acceptability) wrecks augmentation on CoLA at 0.1%, down to 38.8%.
- On full SST-2, adding synthetic data at a 1:1 ratio improves BERT-base accuracy.

## Limits

- Specifications were written by hand and selected per task on validation data; a bad one can drop under the baseline (CoLA 38.8%).
- Coverage is limited to classification with single-token labels, and GPT-3 inference cost goes up with k.
- At 1% on TREC6 and SUBJ, GPT3Mix fails to beat the baselines; SUBJ labels are vague.
- Bias and toxicity from the LM may carry into the synthetic data.
- The seed count is inconsistent (15 data seeds in Sec 4.1, 10 repeats in the Table 1 caption); per-dataset sizes are missing; the ablations use curie or DistilBERT and smaller ratios.
- The paper notes that GPT-3 davinci, accessed through the OpenAI Beta API, has since been retired.

## See Also
- [[Synthetic Instruction Data: Curation and Verification]] — related
- [[Back-Translation with Monolingual Data]] — related
- [[UDA: Unsupervised Data Augmentation]] — alternative-to
