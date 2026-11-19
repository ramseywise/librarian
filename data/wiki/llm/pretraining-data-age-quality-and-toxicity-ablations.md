---
title: Pretraining Data Age, Quality and Toxicity Ablations
tags: [llm, pretraining-and-data, concept]
summary: "Longpre et al. (NAACL 2024) pretrain 28 1.5B models on C4 and Pile variants and find that data age, quality filtering, toxicity filtering and domain mix each shift performance, with a trade-off between benchmark scores and toxic generation (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-longpre-2024-pretrainers-guide-training-data.md
---

# Pretraining Data Age, Quality and Toxicity Ablations

Longpre, Yauney, Reif et al. study how pretraining-data age, which source domains are included, and quality or toxicity filtering each alter downstream results and toxic behaviour. Using T5X they train 28 separate decoder-only models of 1.5B parameters (LM-XL) from scratch, plus a 20M LM-SMALL for one scaling check, and describe this as the biggest openly documented ablation of pretraining data. The variants are C4 built from four Common Crawl years (2013, 2016, 2019, 2022), quality-filtered and toxicity-filtered C4, and the Pile minus one of nine domains in turn. Approximate deduplication ([[Deduplicating Training Data (ExactSubstr and NearDup)]]) is applied to both datasets. Every model is finetuned per task and scored relative to the unfiltered model, across benchmarks for temporal shift, QA, identifying toxicity and generating toxic text. All numbers below are self-reported.

## Data age

- For each year of gap between pretraining data and evaluation data, LM-XL loses 0.4 points on average, compared with 2.8 for a gap between finetuning data and evaluation data (five temporal tasks, finetuned in the training-year split). The pretraining effect is small and not significant for the 20M model.
- Larger models degrade more from pretraining misalignment, and the effect is asymmetric, steeper when the evaluation year comes after the pretraining year.
- The authors say finetuning does not repair the mismatch, and cite an estimate that older variants of BERT, RoBERTa, GPT-2 and T5 draw roughly 58% of Hugging Face model downloads (as of April 2023).

## Quality and toxicity filters

- With the quality filter at T=0.975, 91% of C4 stays and average relative QA performance rises by 2.5; most QA categories gain 1-6% although at least 10% of the data is dropped. The inverse filter removes the best 27% by quality and costs 3.1 points of average QA performance.
- A toxicity filter at T=0.5 keeps 76% of C4 and lowers average QA performance by 2.7. At the strongest setting (T=0.3) the RTP-T toxic-generation score on C4 drops from 84.6 to 55.0, while toxicity identification falls by 5.2.
- The inverse toxicity filter at T=0.06 yields the best toxicity identification, 1.4 over the full Pile.
- On RepBias, the toxic-generation score is 11.1 percent higher with a T=0.9 quality filter than with unfiltered C4.
- Both notions are defined purely through classifier scores, from the PaLM quality classifier and the Perspective API.

## Domain coverage

- Dropping Common Crawl (26.9% of the Pile) produces the biggest declines in toxicity generation and toxicity identification of all domain ablations; the paper also names Books and OpenWeb as large contributors.
- The Pile's Books domain has 4.3x the mean profanity and 1.9x the text quality (the baseline is not stated), which the authors give as the reason high-toxicity documents score high on quality.
- QA is still best when pretraining uses all or almost all of the sources, so mixed sources win over targeted data.
- The authors advise documenting how pretraining data is spread over time, and tuning curation policy like a hyperparameter.

## Limits

- English only and two datasets (C4, Pile); the authors expect composition to matter more for multilingual models.
- Each configuration was run once, with no seeds or repeats given the cost; compute and wall-clock time are not reported. Models and code were not released.
- The quality classifier is proprietary, so that filter is not reproducible, and Perspective is a black box that Pozzobon et al. 2023 showed shifts over time.
- Only finetuned settings are studied, not zero- or few-shot prompting; scale is 1.5B (20M for the temporal scaling check).
- RefinedWeb, Dolma and RedPajama appeared after the experiments; the authors expect the findings to carry over.
- A domain ablation also shrinks the data, so the two effects are confounded, a point the authors make for the toxicity filters.
- Section 2.3 says 27 QA datasets and Appendix D says 30.

## See Also
- [[Dolma Open Pretraining Corpus]] — related (a larger open corpus with its own filter ablations)
- [[Extracting Training Data from Language Models]] — related
- [[Continued Pretraining for Domain Adaptation]] — related
