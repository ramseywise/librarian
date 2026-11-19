---
title: HHH Assistant Alignment Baselines
tags: [llm, preference-and-alignment, concept]
summary: "Askell et al.'s 2021 study treats a helpful, honest and harmless assistant as a laboratory: a short HHH prompt and its context-distilled version give a baseline with little alignment tax, ranked preference modelling beats imitation learning, and a preference-model pre-training stage improves sample efficiency (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-askell-2021-general-language-assistant-as-laboratory.md
---

# HHH Assistant Alignment Baselines

Askell, Bai, Chen et al. (2021 preprint) test whether two simple baselines (prompting, context distillation) and four ways of training (imitation learning, then binary discrimination, then ranked preference modelling, then preference-model pre-training) can turn a general language model into an assistant that is helpful, honest and harmless, and how each one changes with model size. Their hypotheses: on ranked tasks ranked preference modelling should outperform imitation learning while on binary tasks it should not, and an extra pre-training stage on big public preference datasets should make finetuning more sample-efficient.

## Setup

Decoder-only Transformers from 13M to 52B non-embedding parameters, pretrained on 400B tokens. Each is tested bare, with a prompt made of 14 HHH conversations, and with a context-distilled form of that prompt. Across 9 finetuning evaluations the comparison covers imitation learning, binary discrimination and ranked preference modelling.

## Named mechanisms

- **Context distillation:** train p_theta(X) to match the prompted initial model p0(X|C) by minimising the KL loss `D_KL(p0(X|C) || p_theta(X))`, where the context C stays fixed and X is sampled from a big corpus. The prompt ends up in the weights rather than in front of the input.
- **Preference-model pre-training (PMP):** an extra stage placed after LM pretraining and ahead of finetuning on a small preference set, using large public preference data (Stack Exchange, Reddit, Wikipedia edits).
- **Binarization:** each ranked pair A > B yields two binary comparisons, GOOD:A over BAD:A, and BAD:B over GOOD:B, so that ranked data can train a binary model.
- **Alignment tax:** the drop in performance caused by an intervention, found by evaluating once with the prompt and once without it.
- The preference-model loss is `L_PM = ln(1 + exp(r_bad - r_good))`; for PMP the combined loss `L_total = lambda * L_PM + mu * L_LM,good` was used; a pure PM loss transfers poorly.

## Results (self-reported)

- **Prompting:** a simple HHH prompt gives a workable baseline with improved scaling on the HHH evaluations, TruthfulQA and toxicity; context distillation behaves similarly. According to the authors large models pay little or no alignment tax for prompting: it hurts small code models but improves 13B and 52B on HumanEval and QuixBugs (T=0.6, top P=0.95), and gives a small tax on LAMBADA without strong size dependence.
- **Human preference:** contractor Elo (about 6k pairwise MTurk comparisons) rises linearly with log model size from 197M to 13B, then is flat between 13B and 52B. At 13B and 52B, raters pick the fully prompted model over its context-distilled counterpart about 53% of the time.
- **Toxicity** (setup: RealToxicityPrompts, 500 prompts of each kind, toxic and non-toxic, with 25 samples of 20 tokens per prompt at temperature 1 and top P of 0.90, scored by Detoxify): with no intervention, toxicity grows as models get larger; prompting and context distillation lower it, with a bigger effect on toxic prompts at the larger sizes (from 12B). Letting the prompted model emulate human replies lowered toxicity more than the interventions did, so Human: tokens were blocked.
- **Honesty:** for the largest models the context-distilled prompt gives a small gain on TruthfulQA MC1 (official sum-logprobs metric); honesty is the best HHH category.
- **Ranked versus binary:** ranked preference modelling outperforms imitation learning and improves faster with scale, while binary discrimination adds little (mean over 3 ranked and 6 binary evaluations, 13M to 52B). On code correctness (about 500k functions) preference modelling and imitation learning are similar, which the authors attribute to a stronger imitation baseline than Cobbe et al.'s.
- **PMP:** with 500 pairs, binary PMP carries over better than ranked PMP; at 500 finetuning pairs the PMP mix benefits models above roughly 1B parameters, and benefits them less at 5k. PMP trained on the PM loss alone transfers badly, whereas PM plus LM loss transfers well. Adding an end-of-context token raises PM performance, and restricting the imitation loss to response tokens clearly helped. On summarization, ensembling PMP models gives roughly 0.5% in accuracy.

## Limits

- The prompt was ad hoc and unoptimised, and its text is not in the PDF (gist only). The authors accept that prompt design has serious limits and may merely teach imitation of the training distribution.
- The HHH evaluations consist of around 200 comparisons written by the authors, and they ignore how much the model knows (for honesty). Contractors could not tell 13B from 52B, and the authors blame rater incentives for the Elo plateau.
- Automated toxicity detection has known issues, and much larger decreases may be possible with dedicated interventions.
- Whether a task counts as binary or ranked can be ambiguous; 52B code correctness was left out to save compute; the 52B PMP loss is off-trend for an unknown reason; no seeds, optimizer, absolute learning rate or hardware are reported. A previous version of the paper used a non-standard TruthfulQA formulation, and this one corrects it.

## See Also
- [[Helpful-Harmless RLHF and Iterated Online Training]] — extends (Bai et al. take the model specifications, PMP, context distillation, HHH evaluation and Elo method from this paper)
- [[RLHF Pipeline]] — related (the preference-model loss is the Bradley-Terry form)
- [[Bradley-Terry Preference Model]] — related
- [[TruthfulQA]] — related (MC1 evaluation of the prompt)
- [[RealToxicityPrompts]] — related (the toxicity evaluation used here)
