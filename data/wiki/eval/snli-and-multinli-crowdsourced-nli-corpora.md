---
title: SNLI and MultiNLI Crowdsourced NLI Corpora
tags: [eval, language-tasks, benchmark]
summary: SNLI (570,152 pairs written against image captions) and MultiNLI (433k pairs over ten genres, with matched and mismatched test sets) are the two crowdsourced entailment/neutral/contradiction corpora; both papers report 2015-2018 baselines.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bowman-2015-large-annotated-corpus-learning-natural.md
  - data/raw/papers/2026-11-08-williams-2018-broad-coverage-challenge-corpus-sentence.md
---

# SNLI and MultiNLI Crowdsourced NLI Corpora

Both corpora ask crowdworkers to write three hypotheses for a given premise, one each for entailment, neutral and contradiction. Numbers below are the papers' own (self-reported).

## SNLI (Bowman et al., EMNLP 2015)

Premises are Flickr30k captions (about 160k captions, about 30k images), shown to Mechanical Turk workers without the image; about 2,500 workers contributed. The corpus has 570,152 pairs, split into 550,152 for training and 10,000 each for dev and test. Roughly 10% of pairs (56,951) were validated by four more annotators, giving five labels each. Premises average 14.1 tokens and hypotheses 8.3.

- Of the validated pairs, 98% have a three-annotator consensus and 58% are unanimous across five; overall Fleiss kappa is 0.70, by label 0.77 for contradiction, 0.72 for entailment and 0.60 for neutral. An individual label matches gold 89.0% of the time.
- 3-class test accuracy (550,152 training pairs): lexicalized feature classifier 78.2% (99.7% on train), 100d LSTM sentence encoder 77.6% (GloVe 840B init, 3x200d tanh classifier), sum of words 75.3%, plain RNN 72.2%. Unlexicalized features alone give 50.4%.
- In the learning curve (log scale, from a single pair up to a million), the lexicalized classifier with only 100 examples already beats the unlexicalized one, and the LSTM curve is steeper.
- Transfer: an LSTM initialised from SNLI parameters reaches 80.8% on SICK test against 71.3% from SICK alone; trained on SNLI only, it gets 46.7% on SICK. The SICK state of the art then was 84.6%.

## MultiNLI (Williams et al., NAACL 2018)

The same writing procedure on premises drawn from ten genres of spoken and written English, giving 433k pairs. Dev and test pairs are relabelled by four more workers and the gold label is the majority of five. Test data comes in two kinds: matched (same sources as training) and mismatched (not closely resembling training sources). Premises average 22.3 words and hypotheses 11.4.

- Test accuracy for ESIM trained on MultiNLI is 72.3 matched and 72.1 mismatched; BiLSTM 66.9 on both; CBOW 64.8 matched; most-frequent class 36.5 and 35.6. Only ESIM passes 70%.
- On MultiNLI the baselines land roughly 15% below their SNLI scores; ESIM trained on SNLI gets 86.7 on SNLI test. Adding 15% of SNLI to MultiNLI training leaves ESIM at 72.4 matched, 71.9 mismatched.
- Validation: 58.2% of pairs are unanimous (SNLI 58.3%), an individual label matches gold 88.7% of the time (SNLI 89.0%), and 1.8% of pairs have no gold label.
- Annotation tags: negation is the one tag with label skew (48% contradiction); modals appear in 28% of dev pairs against under 1% of SNLI; comparatives and superlatives (17% of pairs) cost the baselines 3-4 points.

## Limits

- SNLI: only models that scale to the full corpus were tested; sentence encoders cannot compare premise and hypothesis word by word; labels depend on a caption-grounded scenario, so coreference indeterminacy is reduced, not removed. Models fail on world knowledge, lexical relations and role-reversal cases, and the attempt to transfer to RTE-3 failed (it had 800 training examples). The lexicalized classifier overfits its training set. Hyperparameters and seeds are not reported.
- MultiNLI: matched and mismatched scores are similar, so the cross-genre test did not yet discriminate between models (the authors expect it to matter as models improve). No hypothesis-only baseline is given and the authors acknowledge spurious cues such as negation. Premises are single sentences, hypotheses come from 387 workers with no demographics. Baselines are CBOW, BiLSTM and ESIM only, with no seeds, variance or significance tests.
- The MultiNLI paper notes its baselines are far below later pretrained models.

## See Also
- [[Adversarial NLI and HAMLET Collection]] — extends (human-and-model-in-the-loop rounds built on SNLI and MultiNLI training data)
- [[SuperGLUE and CoLA Language Understanding Benchmarks]] — related (SuperGLUE's BERT++ baseline fine-tunes on MultiNLI first)
- [[FEVER Fact Verification Dataset]] — related
