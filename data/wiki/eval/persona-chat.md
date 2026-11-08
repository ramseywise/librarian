---
title: PERSONA-CHAT
tags: [eval, reference]
summary: A crowd-sourced dialogue dataset in which each speaker plays a written persona, used to test whether profile-conditioned chit-chat models predict the next utterance better and seem more engaging; persona conditioning helped ranking models but not the generative one in the human study.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-zhang-2018-personalizing-dialogue-agents.md
---

# PERSONA-CHAT

Zhang and colleagues (ACL 2018) ask whether conditioning chit-chat agents on explicit textual profiles, their own and their partner's, yields more consistent, engaging dialogue. The dataset has 164,356 utterances over 10,981 dialogs. Mechanical Turk workers write personas, rewrite them without word overlap (a **revised persona**: a rephrase, generalisation or specialisation), then chat in pairs while playing assigned personas.

## Evaluation

Ranking models (IR, Starspace, profile memory, key-value profile memory) and generative models (Seq2Seq, generative profile memory) are scored at predicting the next utterance when given no persona, their own, the partner's, or both. **hits@1**: the model picks the right reply among the true one and 19 random replies from other dialogues. A human study has Turkers chat with each model (100 dialogues per model, scores 1 to 5).

## Results (self-reported; PERSONA-CHAT test, original personas unless stated)

- Giving the Profile Memory ranker its own persona lifted hits@1 from 0.318 to 0.509; KV Profile Memory reached 0.511, the highest automatic score. With revised personas the Profile Memory gain was small (0.354 vs 0.318), and the IR baseline fell from 0.410 to 0.207, below its no-persona 0.214.
- Generative models ranked far worse (generative profile memory 0.125). Seq2Seq perplexity was higher with a persona (40.53) than without (38.08); generative profile memory lowered it to 34.54.
- Human study: engagingness 3.50 for the KV Profile Memory ranker, against 2.13 for an OpenSubtitles-trained model and 1.75 for a Twitter-trained one; human upper bound 4.25. The persona-conditioned generative model (3.13) was not above Seq2Seq without a persona (3.18), and a ranking KV Memory with no persona scored higher (3.88) than the one given its own persona (3.50).
- Persona detection accuracy: 0.81 for KV Profile Memory, 0.59 for KV Memory with no persona, 0.95 for humans.

## Limits

- The extracted PDF lacks the appendix tables and the wording of the human-eval questions.
- The authors say rater variance obscures human-eval differences; no significance tests or rater counts.
- Models are trained heuristically, with hyperparameters not given; results depend on crowdworker instructions (the partner's persona matters less because speakers talk about themselves).
- The training persona version for Table 3 is not stated. The full profile-prediction study is out of scope.

## See Also
- [[Seq2seq Bottleneck and Attention]] — prerequisite-for
- [[Output Length Confounds Reference Metrics]] — related (limits of automatic text metrics)
