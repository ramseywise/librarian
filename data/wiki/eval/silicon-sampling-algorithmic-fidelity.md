---
title: Silicon Sampling and Algorithmic Fidelity
tags: [eval, concept]
summary: "Conditioning a language model on real survey respondents' first-person backstories to get one synthetic respondent per person; Argyle et al. report GPT-3 matched human subgroup patterns in US politics, with strong partisans well predicted and pure independents not (group-level only)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-argyle-2023-out-one-many.md
---

# Silicon Sampling and Algorithmic Fidelity

Argyle et al. (Political Analysis 31, 337-351, 2023) ask whether GPT-3, given the sociodemographic backstory of a real person, can substitute for a particular human subgroup in social-science studies. **Algorithmic fidelity** is their name for how closely the model's pattern of links between ideas, attitudes and social contexts mirrors the pattern inside a human subgroup. **Silicon sampling** is the method: each respondent in a real survey (American National Election Studies 2012, 2016 and 2020, and the Pigeonholing Partisans data) becomes a first-person backstory prompt, and GPT-3 completes it, giving one silicon subject per human. Drawing the backstories from a known representative sample corrects the skewed marginals of the training text. No training is involved. The authors propose four criteria for judging fidelity; the extraction does not list them.

Three studies compare silicon and human samples:

- **Study 1, word lists.** Raters recruited through Lucid labelled GPT-3 word lists as human about as often as lists written by people. Raters guessed the writer's partisanship correctly more often for human lists than GPT-3 lists, with both above the 33% chance level. The study cost about $29 on GPT-3 (self-reported).
- **Study 2, vote choice.** Silicon and ANES vote choice were compared by tetrachoric correlation and proportion agreement. Strong partisans were nearly perfectly predicted in 2012. Weak partisans and low-interest respondents were predicted less well, and pure independents were the failure case, with near-zero correlation in 2020. GPT-3 overestimated the average Republican vote probability in 2020, a year outside its training period.
- **Study 3, item structure.** Using ANES 2016, 11 questions in the prompt predicted the 12th, and the average gap between ANES and GPT-3 Cramér's V values across item pairs was small.

The extraction gives no numeric values for the rows in Studies 2 and 3.

## Limits

Only GPT-3 and only US politics and public opinion were tested. The match is at group level; individual-level correspondence was not evaluated, and the authors decline to set numeric thresholds for algorithmic fidelity. Pure independents were poorly predicted and each year shows mild marginal bias. The 2020 test lacks variables such as state and flag patriotism, and it tests only in part on data from after the 2019 end of the corpus. The supplementary material holds the prompts, ablations, model comparisons, sampling-parameter variation and costs; the extraction did not read it. The authors warn of misuse such as targeted misinformation, manipulation and fraud.

## See Also
- [[Simulated User Evaluation]] — related (a model plays a person, there to test an agent rather than to study a population)
- [[Synthetic Dataset Generation for RAG Eval]] — related (model-generated stand-ins for real data)
- [[HITL Annotation Pipeline]] — related (a model replacing human raters)
