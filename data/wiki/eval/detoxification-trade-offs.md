---
title: Detoxification Trade-offs
tags: [eval, safety-and-bias, comparison]
summary: "Welbl et al. and Xu et al. both find that lowering an LM's toxicity score costs language-modelling quality and does so unevenly: text in African-American English and about minority identities loses most, and automatic toxicity scores stop agreeing with humans once toxicity is low (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-welbl-2021-challenges-detoxifying-language-models.md
  - data/raw/papers/2026-11-08-xu-2021-detoxifying-language-models-risks-marginalizing.md
---

# Detoxification Trade-offs

Two 2021 papers evaluate methods that reduce an LM's toxicity, on the [[RealToxicityPrompts]] metrics, and ask what the reduction costs. Both start from the hypothesis that a toxicity classifier carries its own biases into the model it steers. Welbl et al. describe Xu et al. as contemporary work that they extend to more models, demographics and datasets.

## Metrics used

- **Probability of Toxicity**: how often at least one of 25 continuations scores above 0.5.
- **Expected Maximum Toxicity**: the highest score among 25 continuations, averaged over prompts.
- **Loss gap**: difference in LM loss from the standard LM on the same documents.

## Welbl et al. (Findings of EMNLP 2021)

Setup: a 1.4B TransformerXL trained on C4, either on all of C4 or with documents above a Perspective toxicity threshold removed (**train-filter@X**). On top of that, a decoder filter (**test-filter**: draw as many as K continuations and output the first that a BERT classifier rates under a threshold, or the lowest-scoring one if none does) and PPLM. Evaluation used Perspective on RealToxicityPrompts, three human raters, loss differences on BOLD and TwitterAAE, and LAMBADA. Results are self-reported.

- Combining train-filter@0.05, test-filter and PPLM drives automatic toxicity close to zero, a reduction of 6 times on toxic prompts and 17 times on non-toxic prompts relative to earlier best results (20-token continuations).
- Even the unfiltered C4 model is less toxic than GPT-2 without a prompt, and far fewer C4 documents are toxic than in the GPT-2 corpus.
- The strongest training filter raises C4 validation loss to roughly the level of a standard 417M model (loss 2.62), a third the size, and LAMBADA accuracy falls sharply. The loss increase is concentrated on text Perspective labels toxic.
- Of the generations the train-filter@0.05 LM produced that Perspective flagged above 0.5, 30.2% mention "gay", against 4.1% for the standard LM, which the authors read as false positives on identity terms.
- After strong detoxification most Perspective-flagged samples (above 0.75) are false positives according to humans, and human-Perspective correlation collapses in the top bin. The Spearman correlation is smaller for the filtered models than for the unfiltered one.
- Dialect: train filtering amplifies AAE text's already higher loss. With TwitterAAE tweets as prompts, automatic metrics rate the detoxified LMs as still more toxic on AAE prompts, whereas human raters see about the same toxicity (average 0.02 for AAE against 0.04 for white-aligned English, train-filter@0.05).
- BOLD gender domain: train filtering raises loss the most for Hispanic-American text, and for text about female actors compared with male actors, even though the unfiltered LM had its lowest loss on Hispanic-American.
- If test-time filtering accepts at least a fraction epsilon of samples, the per-token loss for a document of n tokens rises by no more than -ln(epsilon)/n, whichever classifier is used, so likelihood-based bias metrics can miss the bias it introduces.
- Text quality ratings (comprehensible, grammatical, consistent) barely change; the toxicity classifier used by PPLM scores a lower F1 once it is trained on the filtered corpus.
- Annotating toxic content hurt most annotators' well-being (32.1% chose "a bit more" as their most negative response).

## Xu et al. (NAACL-HLT 2021)

Setup: GPT-2 medium detoxified with DAPT, PPLM, GeDi and output filtering, using Jigsaw Civil Comments; compared with plain GPT-2 by perplexity on white-aligned English (WAE), African-American English (AAE) and minority-identity-mention (MIM) tweets, and by MTurk pairwise preference on continuations of 50 WAE and 50 AAE prompts.

- Under strong GeDi settings, perplexity grows much more for AAE than for WAE. With PPLM, perplexity on non-toxic WAE goes up 2.1 times, against 4.3 times on MIM tweets.
- Over 80% of annotators judged GeDi to be less on-topic than the GPT-2 baseline; on AAE prompts GeDi was preferred for topicality about half as often as on WAE prompts.
- All four techniques generate less toxicity than the baseline, but filtering does poorly because GPT-2 rarely gives non-toxic continuations of toxic prompts.
- The authors explain this by saying toxicity datasets, through how they were annotated and sampled, mark AAE and identity mentions as toxic far too often (the authors point to work by Sap and by Dixon, 2018 to 2019). They argue this and do not test it.

## Limits

- Welbl: English only, one 1.4B model, one run per configuration; inter-rater alpha is only 0.48 to 0.49. Toxicity covers one aspect of harm, not stereotypes or distributional bias, and loss gaps are an imperfect bias metric. Perspective is used beyond the domain it was trained on (forum comments), and 20-token continuations carry little context, so truncation may yield false positives.
- Welbl: PPLM ran on 10K prompts only; the highest toxicity band of the combined setting has 3 samples. Annotation instructions lacked race or dialect priming. The authors say the trade-off with bias need not be unavoidable if less biased classifiers become available, and caution against generalising the absolute and relative efficacy of the techniques.
- Xu: only GPT-2 medium and four techniques; human evaluation uses 100 prompts with no significance testing stated. The authors admit that some of the quality drop is domain shift (trained on comments, evaluated on Twitter). The causal claim gets no ablation using debiased data, and no remedy is tried. For perplexity GeDi omega was 0.3, not the default of 30.

## See Also
- [[RealToxicityPrompts]] — prerequisite-for (the benchmark and metrics both papers evaluate on)
- [[Stereotype and Gender Bias Benchmarks]] — prerequisite-for (BOLD supplies the topic-coverage measurement)
- [[ToxiGen]] — related (balanced machine-generated data aimed at the same classifier bias)
- [[Bias Amplification and Mitigation Methods]] — related (other mitigations with a quality or performance cost)
- [[LLM Bias and Fairness Survey]] — related (mitigation by stage)
- [[Pretraining Data Age, Quality and Toxicity Ablations]] — related (toxicity filtering at the pretraining-data stage)
