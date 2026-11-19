---
title: "Back-Translation with Monolingual Data"
tags: [llm, pretraining-and-data, pattern]
summary: "Sennrich et al. pair target-language monolingual sentences with a synthetic source made by a reverse NMT system and mix them 1-to-1 with parallel data, with no architecture change, gaining 2.7 to 3.7 BLEU (self-reported) on WMT15 and IWSLT tasks."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sennrich-2016-improving-neural-machine-translation-models.md
---

# Back-Translation with Monolingual Data

Sennrich et al. ask whether NMT training can exploit monolingual text in the target language while leaving the architecture alone. Their hypothesis is that such text sharpens the model's estimate of p(T), and matters most when parallel data is scarce or from another domain. **Back-translation** is an automatic translation of monolingual target text into the source language; the resulting source sentence is called **synthetic**.

## Method

An existing target-to-source NMT system translates the monolingual target sentences back into the source language; each resulting (synthetic source, real target) pair is then blended with the genuine parallel data at a 1-to-1 ratio. The baseline alternative fills the source with a dummy `<null>` and freezes encoder and attention on monolingual batches. Models are Groundhog attentional GRU encoder-decoders with BPE (89 500 merges); see [[Subword Tokenisation: BPE and SentencePiece]].

## Results (self-reported)

- English-German, WMT15, single models, newstest2014/2015, detokenised case-sensitive BLEU, 44m parallel plus 36m synthetic instances: +2.8 to 3.4 BLEU over the parallel baseline. German-English gains 3.6 to 3.7 BLEU, larger than deep fusion.
- Turkish-English, IWSLT14, 320k parallel plus 3.2M Gigaword synthetic, tokenised BLEU averaged over tst2011-2014: +2.7 BLEU, 0.5 above fusion.
- Dummy-source monolingual data (ratio 1-1, trained twice as long, English-German): 0.4 to 0.5 BLEU single, 1 BLEU ensemble. Continuing baseline training another week gave no improvement, a control for training time.
- Domain adaptation to TED (English-German, WMT-trained system, embeddings fixed): one epoch on 200k back-translated in-domain WIT data gives +1.2 BLEU on tst2015; fine-tuning on 200k in-domain parallel data gives 28.4 (+2.9); tuning on monolingual TED text with a dummy input brought nothing.
- A 6 BLEU difference in back-translator quality (greedy, beam 12, synthetic-trained German-English systems) gave only 0.6 to 0.7 BLEU difference in final English-German quality.
- Combining independently trained systems gains 0.8 to 1.0 BLEU over an ensemble of 4 checkpoints taken from a single run.
- The benefit is larger for NMT than for a phrase-based SMT system (Moses, 5-gram KN LM): +2.9 against +0.7 on the WMT sets and +1.2 against +0.1 on IWSLT.
- The parallel-only Turkish model overfits quickly; mono and synthetic data delay overfitting, and Gigaword synthetic data gives the best dev cross-entropy (tst2010). Synthetic text made from the same parallel corpus ("parallelsynth") still adds 1.7 BLEU on average for Turkish-English, a smaller gain than the Gigaword-based variant.
- Naturalness of words built from subwords (English-German newstest2015, ensembles, one native-speaker annotator, 100 unattested words per system, blinded): parallel 74.9%, plus monolingual 84.6%, plus synthetic 82.5%.

## Limits

- Just a small random slice of the monolingual data was used; bigger or curated synthetic sets, and varying the synthetic quantity, were not tried.
- Sensitivity to back-translation quality was tested only through decoding variants.
- Each result is a single run, with no seeds or significance tests; the 4-checkpoint ensembles come from one run and so have little diversity.
- One author did the naturalness annotation (n=100 per system).
- Monolingual data on the source side was not studied, and the model is a 2015 RNN, not a Transformer.
- With the dummy-source method, a higher monolingual proportion would cause the model to forget how to condition on the source.
- Learning rate, batch size, hidden sizes and epochs are not given here.

## See Also
- [[Subword Tokenisation: BPE and SentencePiece]] — prerequisite-for
- [[Synthetic Instruction Data: Curation and Verification]] — related
