---
title: Post-Training Reasoning Data Primer
tags: [foundations, concept]
summary: "A 2026 survey of over 150 public studies on the data side of reasoning post-training: difficulty is relative to the base model, small curated sets work only inside the base model's support, coverage is a recipe, and self-play moves curation rather than removing it; it reports no results of its own."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2026-primer-post-training-reasoning-data.md
---

# Post-Training Reasoning Data Primer

Li et al. (Peking University, Tsinghua and Qiyuan Tech; arXiv 2606.02113, preprint, June 2026) survey over 150 public studies on the data behind reasoning post-training. The extraction stresses that the primer has no experiments, datasets or numbers of its own; each finding below is restated from cited work, and the wording is the primer's synthesis rather than a measurement. What it adds itself is a framework made of a taxonomy, an attribution ledger and eight reporting checklists (called traps) that ask for items such as inference budget, decontamination status, teacher, verifier version, pass-rate band, temperature, rollout count and base model.

## Claims it restates

- **Difficulty is relative to the base.** One problem may be out of reach for a given base and trivial for a different one. DAPO discards any prompt group that every rollout solves or none does, while Skywork-OR1 estimates difficulty separately for each model (see [[DAPO]]).
- **Small sets need support.** Few demonstrations (LIMO, s1) succeed only if the skill lies inside the base policy's support; large pools (OpenThoughts, Big-Math) pay off when the useful signal sits far out in the tail, or must span multiple bases or domains.
- **Does RL expand capability?** Some work reads current RLVR as sharpening what the base can already reach; counter-work relaxes this with longer horizons, external rollouts or different metrics, so the answer depends on which assumption is broken.
- **Ceiling versus efficiency.** A reading device splits scaling into a reachable ceiling (moved by data, verifier and context) and approach efficiency (moved by loss design, sampling and warm-start distillation); total data is unique data times reuse. The authors call the equations a reading device, not a law.
- **Coverage is a recipe, not a count.** What a model inherits is set by the mix of sources, the filters and the choice of teacher, not by the example count; synthetic data can also shrink diversity over generations, pass on teacher quirks and leak benchmark items.
- **Reward channels are brittle.** A judge model can be tricked by trigger tokens, a rule-based checker can wrongly reject right answers, and a learned verifier can be gamed.
- **Self-play keeps curation.** It moves it into an anchor such as an answer, interpreter or majority vote (STaR, R-Zero, Absolute Zero, TTRL).
- **Agent data as replayable episodes.** Cleaned success-only SFT traces remove the failures, retries and state differences where credit assignment is visible.
- **Long CoT is not faithful reasoning,** and process-reward models need their own tests.
- Frontier recipes converge on long-CoT SFT or distillation followed by GRPO-style RLVR; the primer says optimiser visibility is not causal isolation.

## Limits

- Authors state: closed pipelines and proprietary mixtures are not covered; it is organised by questions and is not a formal meta-analysis; sources range from peer-reviewed papers to preprints, tech reports and model cards, so no causal ranking is claimed; recipes are not re-run, contamination is not audited and verifiers are not validated.
- Citation-heavy with little detail per claim, and it cites many 2026 works the extractor could not check. It cannot be cited for a measured number; cite the origin papers.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[DAPO]] — prerequisite-for (dynamic sampling as a difficulty filter)
- [[Outcome vs Process Reward Models]] — related
- [[Rejection Sampling Fine-Tuning]] — related (verifier turned into SFT data)
- [[Reward Hacking and Overoptimization]] — related
