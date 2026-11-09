---
title: BARTScore
tags: [eval, llm, pattern]
summary: "BARTScore rates generated text by the log-probability BART assigns to producing it from the source (or the reference from it), with the direction chosen per quality aspect; the authors report beating existing metrics in 16 of 22 settings, with prompts helping semantic overlap but not factuality (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-yuan-2021-bartscore.md
---

# BARTScore

BARTScore (Yuan, Neubig and Liu, NeurIPS 2021) treats evaluation of generated text as a text-generation problem. The score sums the BART log-probability of each target token given a conditioning text, weighting tokens uniformly. Four directions are defined: source to hypothesis (the faithfulness reading), reference to hypothesis (precision), hypothesis to reference (recall), and the average of the last two (F score). Variants fine-tune BART on CNN/DailyMail and then ParaBank2, or add a prompt phrase to the decoder input. The underlying bet is that a model trained to turn one text into another will give better text higher likelihood.

## Results (self-reported)

Metrics are compared by correlation with human judgments on machine translation, summarization, factuality and data-to-text sets.

- BARTScore variants beat existing top metrics in 16 of 22 test settings, over 16 datasets and 7 aspects.
- On WMT19 de-en, the prompt "Such as" lifts Kendall's tau by 0.033 over the same variant without a prompt (0.205), passing supervised BLEURT (0.174) and COMET (0.219). Averaged over the seven WMT19 pairs, the full variant stays below supervised COMET (0.339).
- On summarization, vanilla BARTScore beats BERTScore (0.217) and MoverScore (0.200) in average Spearman; the best prompted variant reaches 0.518 (PRISM 0.410).
- On Rank19 factuality ranking, BARTScore+CNN scored near the human figure (0.839 for the human figure, 0.780 for PRISM, 0.721 for QAGS and 0.700 for FactCC). On QAGS-XSUM it reached 0.184 against 0.175 for QAGS, and vanilla BARTScore 0.009.
- Paraphrase fine-tuning lowered factuality performance (Rank19: 0.788 with CNN+Para against 0.836 with CNN), and prompts did not help it.
- T5 and PEGASUS backbones gave no improvement over BART on WMT19.

## Limits

- Prompts help semantic-overlap aspects, but effects on factuality are inconsistent and on linguistic quality unpredictable.
- Weaker on extractive than abstractive summarization systems (REALSumm, 24 systems).
- Prompts were built by hand from synonyms; searched discrete prompts did worse. The MT prompt was chosen on WMT18 development data only.
- Fine-tuning on NeR18 did not help; that dataset has only seven systems that are easy to tell apart.
- No seeds or variance are reported and BART's model size is not stated. The paper predates LLM-as-judge methods and validates only against human correlation.

## See Also
- [[Text Metrics Beyond N-gram Overlap]] — prerequisite-for
- [[GPTScore]] — alternative-to (also scores text by model likelihood under a prompt)
- [[Summary Factual Consistency Metrics]] — related (FactCC and QAGS are baselines on its factuality sets)
- [[Summarization and Translation Hallucination Studies]] — related
