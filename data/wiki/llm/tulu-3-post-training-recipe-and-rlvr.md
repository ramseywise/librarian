---
title: Tulu 3 Post-Training Recipe and RLVR
tags: [llm, preference-and-alignment, pattern]
summary: "Tulu 3's four-stage open post-training pipeline on Llama 3.1 (decontaminated prompts, SFT, length-normalised DPO on on-policy preference data, then PPO with a binary verifiable reward called RLVR) and the ablations it reports for each stage."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-lambert-2024-tulu-3.md
---

# Tulu 3 Post-Training Recipe and RLVR

Lambert et al. test whether an entirely open post-training stack on Llama 3.1 base models (released data, evaluation code, SFT, DPO, plus a new RL stage) can reach or pass the instruct releases of other open models and several closed ones. Their working hypothesis: thorough prompt curation and decontamination, preference data generated on-policy, and RL against verifiable rewards raise targeted skills (maths, exact instruction following) while leaving the rest intact.

## Pipeline

1. Prompt curation and decontamination.
2. SFT on roughly 939k prompts.
3. DPO with length normalisation, trained on a synthetic mix of on-policy and off-policy pairs labelled by a GPT-4o judge. Each log-ratio is divided by its response's length to counter length bias; the variant is borrowed from SimPO ([[SimPO and PRO Reference-Free Preference Optimization]]). The objective is `log sigma( (beta/len_c) * logratio(chosen) - (beta/len_r) * logratio(rejected) )`; see [[DPO Loss and Implicit Reward]].
4. **RLVR**, RL with verifiable rewards: the usual RLHF objective, but a checking function v(x,y) stands in for the reward model, paying alpha for a verifiably right answer and 0 otherwise. PPO optimises it on about 30k prompts in the style of GSM8K, MATH and IFEval: `max E[ v(x,y) - beta * KL(pi || pi_ref) ]`.

Models come at 8B, 70B and 405B and are scored on a development suite and a separate held-out suite. Figures below are (self-reported), one run per configuration.

## Results

- RLVR applied to the 8B DPO model lifts GSM8K, MATH and marginally IFEval, but the development-suite average barely moves: 64.4 to 64.8 at 8B and 75.9 to 76.0 at 70B. At 70B, MATH improves while GSM8K stays at 93.5. A few 8B RLVR runs scored higher on GSM8K (and up to 84.8 on IFEval) but had lower averages.
- At 405B, training on the MATH train split only raised MATH by more than 5 points in 25 steps; compute ended the run at 75 steps. The RLVR 405B average is above both the 405B DPO and SFT models, and the comparison on a dev-suite subset lists GPT-4o 80.5, DeepSeek V3 79.0 and Llama 3.1 405B Instruct 78.1.
- The reward value alpha = 10 was fixed from pilots, untuned. Mixing reward-model scores into the verifiable reward does worse than the verifiable reward alone (GSM8K; KL beta swept from 0.1 to 0.001). The best GSM8K test score, and better averages, came from starting the PPO value function off a general reward model, not off the DPO model.
- A weaker KL penalty means the policy drifts further from its start and usually averages lower; IFEval-constraint runs at beta 0.01 emitted degenerate text. RLVR started from the weaker SFT model arrives at the same verifiable reward as from DPO, with a larger KL at equal beta.
- Algorithm ablation, early SFT checkpoint, UltraFeedback data (SFT base averages 55.7): PPO 55.5, DPO 55.2, and SimPO's best 52.9. Only length-normalised DPO (batch 32, learning rate 5e-7, beta 5, a single epoch) came out ahead of the SFT base. The source says PPO cost much more than DPO and scored slightly lower than it, but the extraction lists only plain DPO (55.2), not a length-normalised DPO figure (see Limits); this is why the pipeline uses DPO for preferences and keeps PPO for RLVR. See [[UltraFeedback Scaled AI Feedback Dataset]].
- Against DPO on UltraFeedback alone, the complete Tulu 3 preference mix wins by 3.3 at 70B and 1.8 at 8B. Pairs built from the SFT model's own samples beat a wholly off-policy set on aggregate. Of three persona-based preference sets, just Persona IF contributes. Re-using prompts with fresh pairs (64k grown to 383k pairs) gave nothing. The judge (GPT-4o, Llama 3.1 405B or GPT-4 Turbo) matters little; GPT-4o is marginally best.
- Online DPO (reward model trained on 82K Skywork pairs, 200K episodes over math prompts) gave little or no GSM8K improvement and hurt MATH; it and rejection sampling were abandoned as poor value for the compute.
- IFEval gains do not carry over: the final 8B model reaches 82.4 on IFEval and 24.3 on IFEval-OOD.
- SFT: summing rather than averaging the loss at lr 5e-6 did best (Llama 3.0, Tulu 2 mixture). At 70B the new SFT mix reaches 72.6 against 63.6 for the Tulu 2 mix.

## Limits

- The preference-algorithm ablation (Table 18) uses one early SFT checkpoint, UltraFeedback only, batch 32, a single run per method and no variance estimate.
- Internal inconsistency: the PPO-versus-DPO statement (PPO slightly lower) is not backed by the listed plain-DPO figure (55.2 against PPO 55.5), and no length-normalised DPO number is given.
- The authors call the PPO-versus-DPO comparison untuned, since the reward model was trained once; PPO may improve with more tuning or compute.
- RLVR spans only maths and verifiable instruction following. Development and RLVR targets overlap with evaluation benchmarks, and the IFEval-OOD score points to overfitting on IFEval constraints.
- Every RL checkpoint used precedes the last saved step; the 405B RLVR run halted at 75 steps with MATH still improving.
- Training omits long context, multiple turns, other languages, tool use and agents; the data is English-centred with a mean of 2.4 turns.
- Evaluation sets may have been in the closed models' training; some closed-model scores were imputed or copied from model cards, and the comparisons date from Nov 2024 models.
- Seed variation is reported only for SFT, where it was noticeable.
- Internal inconsistency: for the 70B RLVR run, KL coefficient and warmup are listed as 0.07 and 0.07 in the Table 21 caption, yet Section 6.4 gives 0.7 and 0.1.

## See Also
- [[DPO Loss and Implicit Reward]] — prerequisite-for (the preference-tuning objective, here length-normalised)
- [[SimPO and PRO Reference-Free Preference Optimization]] — prerequisite-for (source of the length-normalised variant, and a compared baseline)
- [[RLHF Pipeline]] — prerequisite-for (the PPO objective RLVR modifies)
- [[Reward Hacking and Overoptimization]] — related (KL-penalty over-optimisation seen in RLVR runs)
- [[Outcome vs Process Reward Models]] — related (verifiable outcome rewards)
- [[Post-Training for Agents]] — related
