---
title: Helpful-Harmless RLHF and Iterated Online Training
tags: [llm, preference-and-alignment, concept]
summary: "Bai et al.'s 2022 helpful-and-harmless RLHF study (52B-scale preference data, PPO against a preference model) reports an alignment tax for small models and a bonus for 13B and 52B, a helpfulness-harmlessness tension, an approximately linear reward versus sqrt(KL) relation, and weekly iterated online data collection (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-bai-2022-training-helpful-harmless-assistant-reinforcement.md
---

# Helpful-Harmless RLHF and Iterated Online Training

Bai, Jones, Ndousse et al. (2022 preprint) ask if preference modelling and RLHF using human comparisons can produce assistants that are helpful and harmless with no loss of capability, and what role scale, data mixture, robustness and iterated online collection play. Their hypotheses: alignment training is compatible with general and specialised capabilities and can even improve them, and collecting data online populates the high-score tail and makes the preference model better calibrated.

## Setup

After LM pretraining and preference-model pretraining, preference models (PMs) learn from crowdworkers' pairwise comparisons of dialogue responses: one set for helpfulness and another, from red-teaming, for harmlessness. Three tranches of data, all from 52B models, were gathered: base, rejection sampling and iterated online. Each policy is initialised from a context-distilled model and optimised with PPO to maximise the PM score, `r_total = r_PM - lambda_KL * KL(policy, policy0)` (the paper's KL penalty is tiny, with D_KL typically under 100). The framework builds on [[HHH Assistant Alignment Baselines]].

**Iterated online RLHF:** take the best RLHF policy so far, gather new comparisons from it, combine them with the earlier data, retrain a fresh set of PMs and RL policies, then repeat about once a week. "Online" here means new models are retrained per iteration. Crowdworker Elo is converted to PM scores by roughly 174 Elo per PM-score unit.

## Results (self-reported)

- **Alignment tax and bonus:** on NLP benchmarks RLHF helps the 13B and 52B models and hurts the smaller ones (zero- and few-shot MMLU, LAMBADA, HellaSwag, OpenBookQA, ARC, TriviaQA; static RLHF), and part of the sudden jumps comes from the multiple-choice format. The static 52B PM gets 86% on the BIG-Bench HHH evaluation, ahead of the 75% average human score cited for PaLM's evaluation.
- **Specialised skills:** for large code models RLHF raises HumanEval, though giving the base code model the HHH prompt does a little better, and RLHF brought nothing when the prompts contained buggy code. Mixing summarisation data with HH data in PM training loses nothing in either.
- **Tension between helpfulness and harmlessness:** a PM trained entirely on one of the two does much worse than chance on the other (mixtures totalling 42k comparisons). Going from a harmlessness loss weight of 1 to 10 reduces helpfulness accuracy more for the 13M PM than for the 52B PM. The authors traced an earlier policy that over-optimised for harmlessness and turned evasive to the fact that red-teaming workers pick the more harmful reply; giving helpfulness prompts a larger share of training fixed this only in part.
- **Scaling and robustness:** for most of training, reward rises roughly linearly with the square root of the KL between the policy and its initial policy, and the curves run about parallel across sizes (13M to 52B). With the data split 50:50 into separate train and test PMs, scores agree up to about 150k RL samples then diverge, the test PM lower, which is overoptimisation. PM accuracy on helpfulness data fits a line in log parameters P and log data D, with intercept 0.72, slope 0.007 per log(P/1e11) and 0.015 per log(D/8e4).
- **Iterated online data:** in a controlled comparison with the same amount of data (two 52B helpfulness-only runs, identical hyperparameters), crowdworkers favoured the policy trained on the mix of base, rejection-sampling and online data over the one trained on base data alone. Accuracy of the online PM is lower on later data, meaning better samples are harder to rank. k=64 rejection sampling is equivalent to about 4.2 of KL, and the online RLHF models match it or beat it (an earlier-stage model, so not directly comparable with other Elo figures). The PM forecasts a bigger Elo improvement than crowdworkers recorded, and much of that gap is explained by a shift in distribution from held-out prompts to crowdworker conversations.
- **Against professional writers:** crowdworkers preferred the online HH model (median of 17 samples ranked by its PM) to Upwork writers' responses a little over half the time, on non-adversarial prompts.
- **Out-of-distribution detection:** from helpfulness-only activations, a simplified relative Mahalanobis distance on the 52B model reaches AUROC about 0.85 for spotting harmful requests; adding outlier exposure with 10 harmful examples takes the 64-layer model up to 0.94.
- **Bias evaluation:** in the original gender-bias format (completing "The CEO was a ...") RLHF models seldom produced gendered terms, so that evaluation was unreliable.
- Crowdworker and researcher label agreement was low.

## Limits

- The authors say they have little RL experience with large generative models, and their hyperparameter scans were basic; a few RL runs were unstable, chiefly for small models, and a few were stopped early.
- Average-case behaviour only; PMs are not adversarially robust. Honesty is addressed in part only (TruthfulQA closes slightly under half of the gap between zero- and few-shot).
- The crowdworker pool changed over time, a confound for the online story; the controlled run addresses dataset size and hyperparameters only.
- Because harmlessness labels choose the more harmful reply, they say nothing about what an ideal refusal looks like; the authors recommend collecting data on best responses.
- Most PM data was generated by 52B models, so results for smaller models may reflect a mismatch in distribution. Evaluations are mostly multiple-choice, and the sentiment and BBQ-Lite metrics have limits. The writer comparison used softball prompts.
- The paper reports no compute, hardware, optimizer, batch size or number of seeds, so the work cannot be reproduced from the paper by itself.

## See Also
- [[HHH Assistant Alignment Baselines]] — prerequisite-for (the prompt, context distillation, PMP, HHH evaluation and Elo method used here)
- [[RLHF Pipeline]] — prerequisite-for (the three-stage recipe this paper applies with separate harmlessness data)
- [[Constitutional AI and RLAIF]] — related (replaces the human harmlessness labels collected here)
- [[Reward Hacking and Overoptimization]] — related (the train/test PM divergence is the overoptimisation curve)
- [[BeaverTails Decoupled Safety Preference Dataset]] — related (decoupled helpfulness and harmlessness annotation)
- [[LM Red Teaming]] — related (the harmlessness data is red-teaming dialogue)
