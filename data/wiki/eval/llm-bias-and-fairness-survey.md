---
title: LLM Bias and Fairness Survey
tags: [eval, reference]
summary: "Gallegos et al.'s survey (Computational Linguistics 50:3) organises LLM bias evaluation into embedding, probability and generated-text metrics and mitigation into pre-, in-, intra- and post-processing, and lists the weaknesses of each."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-gallegos-2024-bias-fairness-large-language-models.md
---

# LLM Bias and Fairness Survey

# LLM Bias and Fairness Survey

Gallegos, Rossi, Barrow and colleagues (arXiv 2309.00770, Computational Linguistics Volume 50 Number 3) address three questions: how to define social bias and fairness in LLMs, how to measure them through metrics and datasets, and how to mitigate them, along with the limits of each route. The survey ran no experiments, so every number here is quoted from other work.

## Definitions

- **Social bias:** unequal treatment or outcomes across social groups, rooted in historical and structural power imbalances.
- **Group fairness:** a statistical outcome measure that is approximately equal across groups, within a tolerance epsilon. **Individual fairness:** similar individuals get similar treatment.
- **Representational harms** demean or subordinate a group (for example derogatory language, stereotyping, erasure, misrepresentation, toxicity, exclusionary norms, or uneven system performance), whereas **allocational harms** spread resources or opportunities unevenly. The taxonomy covers 7 representational and 2 allocational harms.
- **Local bias** concerns associations between a word and its context; **global bias** concerns a whole stretch of text.

## Taxonomy of metrics

Metrics fall into three classes by which model output they use: embeddings (WEAT, SEAT, CEAT), token probabilities, and generated text. The toxicity metrics for generated text follow the RealToxicityPrompts protocol, which takes 25 generations per prompt scored by Perspective API. Expected Maximum Toxicity takes the highest score; Toxicity Probability marks a prompt toxic when any generation reaches 0.5.

## Datasets cited (sizes as the survey reports them)

WinoBias covers 40 occupations in 3,160 sentences; CrowS-Pairs 1,508 pairs across nine bias types; StereoSet 16,995 instances; BBQ 58,492 examples across nine groups; RealToxicityPrompts 100,000 prefixes; BOLD 23,679 prompts; HolisticBias 460,000 prompts over 13 axes and close to 600 descriptor terms. For the Equity Evaluation Corpus the text and Table 4 differ, with 8,640 in one and 4,320 in the other.

## What the survey says about the metrics

- Bias measured in embeddings relates weakly or not reliably to bias in downstream tasks; Goldfarb-Tarrant et al. 2021 found no dependable correlation.
- Generation settings such as length, temperature and top-k can reverse what a generated-text metric concludes from one dataset.
- Blodgett et al. 2021 found that nearly half the instances in Winogender, WinoBias, StereoSet and CrowS-Pairs leave unclear which stereotype is being tested.
- Edits that keep the meaning (swapping synonyms or adjectives) in Winogender and Bias NLI can shift bias scores sharply.

## Mitigation by stage (Table 5 names 13 mechanisms)

The stages are pre-processing, in-training, intra-processing (altering inference behaviour without more training) and post-processing. Examples reported:

- Removing 10-20% of parameters with WANDA made models harder to jailbreak, but pruning more is harmful, and pruning 30% or beyond raised bias by gender, race and religion in hate-speech classifiers.
- Gira et al. 2022 held over 99% of parameters fixed and tuned only layer norm or position embeddings, evaluating on WinoBias and CrowS-Pairs.
- Thakur et al. 2023 debiased with as few as 10 chosen examples; Borchers et al. 2022 built their low-bias job-ad set out of the least biased tenth of the examples.
- Prompts requesting diversity or gender equality left bias in place (Borchers et al. 2022), and biased and unbiased prompts produced alike outputs (Li and Zhang 2023).
- Decoding that suppresses toxicity can worsen bias by silencing minority dialects like African-American English (Xu et al. 2021).
- Wang et al. 2022 supply a corpus of politeness rewrites: 10K by humans and 100K by models.

## Recommended practices

Pair any embedding or probability metric with a task-level evaluation. Report the model, decoding settings, prompts and templates alongside each metric. Name the harm being targeted. Test datasets for construct, content and ecological validity. Do not rely on mitigation that only masks or replaces identity words. State the fairness assumption behind a loss or reward. Check that toxicity filters do not remove minority dialects. Put bias evaluation into model documentation, with audits and adversarial testing that go past static benchmarks.

## Limits

- The authors concede a technical-solutionist framing; the taxonomies follow implementation rather than downstream harm or context.
- Scope is model training and evaluation only, leaving out problem formulation, data collection and deployment, and English-language papers only.
- Few empirical comparisons of in-training mitigations exist, and few studies compare techniques across stages.
- The extraction notes chat models that are instruction-tuned and RLHF-aligned came too late to be targets in the survey, and most of its metrics were built for masked models from the BERT period or GPT-2-style completion.
- Internal inconsistency: the text and Table 4 disagree on the size of the Equity Evaluation Corpus (8,640 against 4,320).

## See Also
- [[BBQ Bias Benchmark]] — instance-of
- [[Group Fairness Criteria and the Impossibility Results]] — prerequisite-for
- [[LLM Judge Biases]] — related (a different sense of bias: in the evaluator)
- [[LM Red Teaming]] — related
