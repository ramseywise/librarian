---
title: Dialogue Pretrained Models (DialoGPT, LaMDA, BlenderBot 3)
tags: [llm, pretraining-and-data, comparison]
summary: "Three dialogue model reports compared by setup: DialoGPT (GPT-2 on Reddit chains with MMI reranking), LaMDA (137B with quality and safety discriminators and a tool-calling groundedness fine-tune) and BlenderBot 3 (one OPT-based model running ten control-token modules); all figures self-reported."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-zhang-2020-dialogpt.md
  - data/raw/papers/2026-11-07-thoppilan-2022-lamda.md
  - data/raw/papers/2026-11-07-shuster-2022-blenderbot-3.md
---

# Dialogue Pretrained Models (DialoGPT, LaMDA, BlenderBot 3)

Each report builds a conversational model on a transformer and adds a different mechanism for response quality. The survey view of this area is on [[Open-Domain Dialogue Systems]].

| Model | Base and size | Data | Added mechanism |
|---|---|---|---|
| DialoGPT | GPT-2 architecture at 117M, 345M and 762M, either started from random weights or from GPT-2 weights | about 147M Reddit conversation instances (2005-2017, filtered) | MMI reranking with a backward model |
| LaMDA | decoder-only, 2B, 8B, 137B | 1.56T words, a mix of dialog and web text | quality, safety and groundedness fine-tuning; toolset calls with cited URLs |
| BlenderBot 3 | 3B R2C2 (encoder-decoder), plus 30B and 175B decoder-only models from OPT | about 4M fine-tuning examples (1.13B tokens), one epoch, plus pretraining LM data | ten control-token modules, internet search, long-term memory |

## DialoGPT: Reddit chains and MMI reranking

All turns of a Reddit reply-chain path are concatenated into one text ended by an end-of-text token, and the model is trained as an ordinary language model, with the target's probability built as a product of per-token conditionals, each conditioned on the source and the earlier target tokens. The authors hypothesise that this models the flow of a conversation, the joint distribution of target and source, more finely. **MMI reranking:** draw 16 candidates by top-K sampling (K=10), then pick the candidate that a backward model, scoring the source given the hypothesis, gives the lowest loss; this discourages bland replies. A reinforcement-learning attempt using the backward likelihood as reward converged to a parroting degenerate solution on the transformer.

- Reddit 6K multi-reference set, 345M initialised from GPT-2 with beam search: BLEU-2 21.76% against 17.90% for the human reference. DSTC-7 (2208 instances, 5 references), 345M, beam 10, no grounding: BLEU-4 6.05% against 1.83% for Team B and 3.13% for a held-out human response.
- MMI raises METEOR and diversity but lowers BLEU against greedy decoding on Reddit 6K.
- Human evaluation (2000 sampled sources, 3 judges per pair): 345M chosen over PersonalityChat on relevance in 72% of judgements; 345M with MMI preferred over the human response for relevance (48% against 43%) and informativeness. Without MMI, the 345M model and the human response do not differ significantly on relevance (p=0.0552), and neither do the 345M and 762M models (bootstrap, 10K iterations).
- GPT-2 initialisation matters more at 117M: from scratch against GPT-2 init, Reddit 6K BLEU-4 is 1.77% against 1.55% but NIST-2 is 1.23 against 2.39.

## LaMDA: fine-tuning for quality, safety and groundedness

The pre-trained models get fine-tuned on crowdworker-labelled data so that a single model both generates and discriminates for quality (SSI) and safety, and a further fine-tune teaches it to call tools (a retriever, a calculator and a translator) so its claims are grounded and carry citations. Groundedness is the share of responses with claims about the external world that authoritative sources can support, out of all responses containing such claims. The authors hypothesise that scale by itself improves quality but does little for safety and groundedness.

- Safety barely improves with scale before fine-tuning: pre-trained 2B 84.8 against pre-trained 137B 88 (1458 adversarially collected turns, a turn counts as safe if 2 of 3 raters see no violation).
- After fine-tuning, the 137B model gets 73.2% groundedness and 65% citation accuracy (784 turns from Dinan et al., majority of 3 crowdworkers).
- The fine-tuning data amounts to under 0.001% of the pre-training data.
- The domain-grounded "Everest" agent still gives unattributable facts in about 30% of responses (600 turns, 4 agents, 3 labels each).
- Pre-training the 137B model ran 57.7 days on 1024 TPU-v3 chips, using 3.55E+23 FLOPs and 451 MWh, roughly 26 tCO2e.

## BlenderBot 3: modular supervision in one model

One transformer is fine-tuned to run ten modules chosen by control tokens (the extraction names these eight: deciding whether to search, generating the query, writing a knowledge response, extracting entities, generating memories, deciding on memory access, accessing memory and producing the dialogue response), chained one after another, with Mojeek supplying external search. The 175B model starts from OPT-175B (see [[Open Pretrained Model Reports Comparison]]). Its public deployment at blenderbot.ai added a separate safety classifier and canned responses.

- In short MTurk crowdworker chats (100 dialogues per model), BB3-175B earns the top final rating of the models compared and the lowest rate of factual errors (the extraction gives no values).
- Deployment: organic users liked 4% of 9197 BB3-175B messages. Crowdworkers agreed with user dislikes 79% of the time, and 42% of bad human utterances were rude or inappropriate (31% of human utterances were judged bad; 3 crowdworkers, majority).
- In the adversarial unsafe setting of Safety Bench, 27.8% of BB3-175B responses were flagged against 16.1% for BB1.
- From companion papers (reported, not run here): the best troll-robust method cuts error from 31% to 12% on SAFETYMIX with 50% trolls.

## Limits

- DialoGPT: the model is released without decoding code because of occasional toxic output; it can offend and reflects gender and historical biases. Automatic metrics rate the model above the human reference, and the authors explain that by one prompt having many valid replies. The paper omits optimizer, learning rate, seeds, context length, head count, dropout and wall-clock time; quantitative evaluation is single-turn, and multi-turn claims rest on examples. The judge spam filter may have biased results toward extremes.
- LaMDA: safety is one coarse aggregate metric built for a US context; groundedness progress is limited to simple facts; crowdworkers skew 25-34 and were not checked against experts; adversarial collection surfaces frequent failures and misses rare ones; no seeds or confidence intervals; optimizer, learning rate and safety threshold are not stated. The authors call it a recipe, not a final production model.
- BlenderBot 3: mistakes include off-topic, nonsensical, incorrect and rude replies, and fixes for them cost engagingness. Continual learning is at an early stage, and the paper does not retrain on data from deployment. Safety benchmarks are static and crowd-sourced. English only. The 3B and 175B deployment statistics were collected at different times. OPT baseline prompts were not tuned. There is no ablation of the modular design against a single pass, and the 175B model overfits after more than one epoch. The release uses modular supervision but not DIRECTOR.

## See Also

- [[Open-Domain Dialogue Systems]] — prerequisite-for
- [[Open Pretrained Model Reports Comparison]] — prerequisite-for (OPT is BlenderBot 3's base)
- [[Transformer Architecture]] — prerequisite-for
- [[Toolformer Self-Supervised Tool Use]] — related (tool calls for grounding)
