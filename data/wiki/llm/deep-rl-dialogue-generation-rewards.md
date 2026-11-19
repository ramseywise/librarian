---
title: Deep RL Dialogue Generation Rewards
tags: [llm, reinforcement-learning, pattern]
summary: "Li et al. train a chatbot with policy gradient over simulated two-agent conversations, rewarding ease of answering, information flow and semantic coherence with fixed weights 0.25, 0.25 and 0.5, so replies are judged by the course of the dialogue rather than the next turn."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-li-2016-deep-reinforcement-learning-dialogue-generation.md
---

# Deep RL Dialogue Generation Rewards

Li, Monroe, Ritter and colleagues (EMNLP 2016) ask whether a chatbot can be taught the long-term course of a conversation, not just the next turn, by policy-gradient RL on rewards the developer defines. Their hypothesis is that simulated dialogues scored on three heuristics (ease of answering, information flow, semantic coherence) yield more interactive, varied and lasting conversations than a maximum-likelihood sequence-to-sequence model or the mutual-information model.

## Mechanism

1. An attentional encoder-decoder (4 LSTM layers) is first trained by maximum likelihood on OpenSubtitles.
2. A mutual-information policy-gradient stage refines it, and the result initialises the RL policy.
3. Two copies of the policy converse for up to 5 simulated turns, with 5 candidates per step.
4. REINFORCE updates the policy on a weighted combination of three heuristic rewards, using a curriculum over dialogue length. The gradient has the form of the log-probability of the sampled reply times (reward minus a baseline b).

The reward is r = 0.25 r1 + 0.25 r2 + 0.5 r3. The only reward the extraction defines in detail is r1, **ease of answering**: take each of 8 dull responses, compute the length-normalised log likelihood of giving it as the answer to the generated turn, average, and negate.

## Results (self-reported)

- The RL model sustains simulated dialogues longer than the mutual-information model, which sustains them longer than plain sequence-to-sequence (on 1,000 test inputs, with dialogues capped below 8 turns).
- RL unigram and bigram diversity beat the baselines (beam size 10 for RL and sequence-to-sequence).
- Over 200 simulated 5-turn conversations with 3 judges each, RL beats the mutual-information model on preference; on 500 single-turn items (3 judges each) its replies are rated easier to answer.
- There is no significant single-turn quality gain (500 items, 3 judges).
- On a random sample of 2,500 pairs, RL scores below the mutual-information model on single-reference BLEU, though above sequence-to-sequence.

## Limits

- Hand-defined rewards cannot cover what defines an ideal conversation; the authors say rewards should ideally come from humans.
- Cost grows exponentially, so only very few candidates and simulated turns are affordable.
- Only limited history is considered, so dialogues can fall into cycles longer than one turn.
- The model sometimes starts a less relevant topic, a trade-off between relevance and non-repetition.
- Detecting the end of a dialogue relies on matching 8 dull phrases, which yields false positives and negatives.
- Learning rate, batch size, hidden size, steps and compute are not reported, and no code release is stated.

## See Also
- [[MMI Objective for Generic Responses]] — prerequisite-for
- [[MIXER Sequence-Level Training and Exposure Bias]] — prerequisite-for (the curriculum from maximum likelihood to REINFORCE it borrows)
- [[REINFORCE with a Baseline]] — prerequisite-for
