---
title: RealToxicityPrompts
tags: [eval, safety-and-bias, reference]
summary: "RealToxicityPrompts is 100K naturally occurring web prompts with Perspective toxicity scores, used by Gehman et al. to show that five pretrained LMs reach toxic continuations from innocuous prompts and that no steering method fully prevents it (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-gehman-2020-realtoxicityprompts.md
---

# RealToxicityPrompts

Gehman, Gururangan, Sap et al. (Findings of EMNLP 2020, arXiv 2009.11462) ask how far pretrained LMs can be prompted into toxic text, how well controllable generation prevents it, and where the toxicity in pretraining data comes from. Their hypothesis is that models absorb toxicity from the pretraining data, which means both steering applied after pretraining and more careful data selection are needed. They call the failure **neural toxic degeneration**: an LM emitting toxic, racist or sexist text when the prompt was harmless.

## Construction

Sentence-level prompts are sampled from OWTC, stratified by Perspective API toxicity score, and each sentence is split into a prompt and a continuation. This gives 100K prompts, of which 22K are toxic. Five LMs generate continuations and the Perspective API scores them. The score, TOXICITY, is defined as a rude, disrespectful or unreasonable comment that is likely to make people leave a discussion.

Two metrics are used below, the **probability of toxicity** and the **expected maximum toxicity**; [[Detoxification Trade-offs]] defines them (the definitions there come from its own sources, not from this paper's extraction).

## Results (self-reported)

Setup unless noted: each prompt gets 25 samples of 20 tokens drawn with nucleus p=0.9, and a sample counts as toxic when Perspective TOXICITY is at least 0.5.

- On prompts that are not toxic, every one of the five models has a toxicity probability of roughly 0.5 or more. For GPT-2 that means about even odds of at least one toxic continuation among 25 samples. The extraction gives no per-model values beyond this.
- Unprompted generation (only a start-of-sentence token, a pool of 10K spans, 1K bootstrap resamples): after 100 generations GPT-2's expected maximum toxicity is 0.65. Within 100 generations all five LMs pass 0.5, and within 1K most pass 0.9.
- 327 prompts yield toxicity of 0.9 or above from every model tried, steered ones included; 1,225 do so from the five out-of-the-box models.
- Prompt and continuation toxicity are slightly anti-correlated.

### Six steering methods on GPT-2

DAPT (further pretraining on the non-toxic subset, about 150K OWTC documents) lowers the toxicity probability on non-toxic prompts. PPLM lowers it most, but was run on only 10K prompts with 10 generations each because of cost. A word filter (the LDNOOBW list set to zero probability) barely helps, and so does conditioning on an ATCON `<|nontoxic|>` token. Vocab-shift (beta=3) was also tested; the extraction gives no values for it. The authors conclude that no steering method fully solves toxic degeneration.

### Where the toxicity in training data comes from

- 4.3% of OpenAI-WT documents (the GPT-2 corpus, about 8M documents) have TOXICITY of 0.5 or more, against 2.1% of OWTC (38 GB, about 8M documents).
- GPT-2 was pretrained on at least 40K documents from the quarantined /r/The_Donald (overlap of the two corpora, so a lower bound). Banned or quarantined subreddits supply at least 3% of OWTC documents (212K).
- News-site reliability (Baly et al. 2018 ratings) correlates negatively with the toxic proportion of a site's documents.
- The authors recommend documenting pretraining data.

### How far the scorer can be trusted

Three authors rated 100 OWTC documents: 88% pairwise agreement with Perspective, Pearson 0.83. On 100 GPT-2 generations agreement was lower, 80% with Pearson 0.65.

## Limits

- Perspective is imperfect: the authors note that it penalises mentions of minority identities and African American English, and leans on lexical cues.
- Five LMs only, no masked LMs; the models are GPT-2-small-era plus GPT-3 davinci, with no instruction-tuned models.
- The toxicity figures for the web corpora are lower bounds, since OpenAI-WT carries no metadata.
- PPLM's row rests on a 10K-prompt subset and 10 generations per prompt, so it cannot be compared directly with the others.
- The appendices were not in the supplied PDF, and the extraction leaves several table values blank (GPT-3 and GPT-2 toxic-prompt probabilities, vocab-shift, ATCON).

## See Also
- [[Detoxification Trade-offs]] — extends (human evaluation and quality costs of the mitigations first compared here)
- [[ToxiGen]] — related (a machine-generated implicit-hate dataset, aimed at detectors rather than LM continuation)
- [[HELM Holistic Evaluation]] — related (also scores toxicity with the Perspective API)
- [[Stereotype and Gender Bias Benchmarks]] — related (other bias benchmarks, scored on likelihoods or classifiers)
- [[LLM Bias and Fairness Survey]] — related (lists RealToxicityPrompts among its datasets)
- [[Pretraining Data Age, Quality and Toxicity Ablations]] — related (RTP toxic-generation rates under pretraining filters)
