---
title: WebGPT Browser-Assisted Question Answering
tags: [llm, agent-training, concept]
summary: "WebGPT fine-tunes GPT-3 to use a text-based web browser and answer ELI5 questions with references, trained by behaviour cloning, a reward model and best-of-n sampling or PPO; its 175B best-of-64 answers were preferred to human demonstrators' (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-nakano-2021-webgpt.md
---

# WebGPT Browser-Assisted Question Answering

Nakano, Hilton, Balaji et al. (preprint, 2021) test whether a model that browses through a text-only web interface, and is trained from demonstrations plus human preference feedback, can give referenced long-form answers matching or beating those of humans. They expect that adding direct optimisation of answer quality against human feedback to behaviour cloning will pass the demonstrators, which cloning by itself would not.

## Pipeline

1. A text-only browsing environment (Bing search, click, scroll, quote) lets the model collect references while it browses, so labellers can judge factual accuracy without independent research.
2. Behaviour cloning on about 6,000 human demonstrations of GPT-3 models (760M, 13B, 175B) answering [[ELI5 Long-Form QA Dataset]] questions.
3. A reward model trained on about 16,000 comparisons.
4. Optimisation against the reward model by PPO reinforcement learning and/or best-of-n rejection sampling.

Data collected in total: comparisons 21,548, and for ELI5 5,711 demonstrations and 21,068 comparisons.

## Reported results (self-reported)

- The 175B behaviour-cloned model with best-of-64 against the 175B reward model was preferred to the human demonstrators' answers on the ELI5 test set (judged by human comparison against detailed criteria; ties scored 50%; sampling temperature 0.8; browsing capped at 100 actions).
- The same model was preferred to the highest-voted ELI5 Reddit answer (the references were removed, instructions were minimal, and the raters were new contractors). The authors report that the best model of Krishna et al. (2021) was preferred to the reference answers only 23% of the time.
- Rejection sampling (best-of-64) beat the behaviour-cloned model; the PPO model was also preferred over it, with a smaller gain than rejection sampling.
- [[TruthfulQA]]: 175B best-of-64 answers were truthful 75% of the time (human evaluation, answers truncated to 50 tokens).
- Scaling on the validation 175B reward model: doubling demonstrations raises the policy's reward-model score by about 0.13, doubling comparisons raises reward-model accuracy by about 1.8%, and doubling policy parameters raises the score by roughly 0.09 (a noisy trend).
- TriviaQA dev was also evaluated, where a GPT-3 175B model, tuned on 256 questions, pulled a short answer out of the browsing model's output.
- Labeller agreement: labeller-labeller 73% (neutral versus non-neutral counted as 50%).

The paper defines imitative falsehoods as false statements the training objective itself incentivises (such as common misconceptions) and non-imitative falsehoods as failures to achieve the objective, which include most hallucinations.

## Limits

- For questions outside the training distribution, WebGPT can still cite unreliable sources (seen on TruthfulQA) and err more often than people.
- Labellers found subtle hallucinations hard to detect, which means non-imitative falsehoods were never directly tested.
- Reference-based evaluation encourages cherry-picking convincing references and accepting a question's implicit assumptions.
- The experiment on question stance used just 60 questions and did not give a clear result.
- No compute, hardware or seeds are reported, no code or weights were released, and the RL runs used no exponential moving average for the 760M and 13B reward models, due to a bug.
- The rejection-sampling versus RL comparison is confounded by RL hyperparameter tuning and reward-model overoptimisation; the validation predictor is expected to overestimate for large n.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[RLHF Pipeline]] — prerequisite-for (the behaviour cloning, reward model and PPO recipe it applies to browsing)
- [[Reward Model Overoptimization Scaling Laws]] — related (best-of-n against a reward model)
- [[TALM Tool-Augmented Language Models]] — alternative-to (another early route to tool use, by self-play instead of human feedback)
- [[Toolformer Self-Supervised Tool Use]] — alternative-to
- [[Imitation Learning and Inverse RL]] — related
