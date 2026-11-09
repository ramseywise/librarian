---
title: Open-Domain Dialogue Systems
tags: [foundations, concept]
summary: Survey of frameworks for open-domain conversation — retrieval-based (score candidates), generation-based (seq2seq/PLM), and hybrid methods — with two key goals (informative via knowledge grounding, controllable via persona/strategy/safety).
updated: 2026-11-09
sources:
  - data/raw/pdfs/2020-01-01-conversational-ai.md
  - data/raw/papers/2026-11-07-adiwardana-2020-towards-human-like-open-domain.md
  - data/raw/papers/2026-11-07-henderson-2019-training-neural-response-selection-task.md
  - data/raw/papers/2026-11-08-lu-2024-blending-all-you-need.md
  - data/raw/papers/2026-11-08-learning-towards-conversational-ai-survey-07d04bbf.md
  - data/raw/papers/2026-11-08-2011-00564v1.md
---

# Open-Domain Dialogue Systems

Open-domain dialogue systems have no fixed topic constraints, unlike task-oriented systems (slot-filling, specific domains). The goal is satisfying human communication needs — acting as a digital companion providing engaged conversation (Fu et al., 2022).

## Three Frameworks

### 1. Retrieval-Based

Searches a candidate pool and selects the best response. Core: encoding function e() + scoring function s().

**Shallow interaction**: encode context and response independently, then compute match score (bilinear, MLP, cosine). Examples: TF-IDF matching, CNN/RNN encoders.

**Deep interaction**: allow context and response to interact during encoding (cross-attention, word-level matching). Examples:
- **SMN** (Sequential Matching Network): matches each utterance-response pair separately via RNN, then aggregates with CNN
- **DAM** (Deep Attention Matching): replaces RNN with hierarchical self-attention for multi-grained matching
- **DUA** (Deep Utterance Aggregation): weights context utterances by relevance

### 2. Generation-Based

Generates responses word-by-word, typically via encoder-decoder architecture.

- **Seq2Seq**: RNN encoder-decoder with attention (Sutskever et al., 2014; Bahdanau et al., 2015)
- **Variational methods**: VAE-based models adding latent variables for diversity
- **Pre-trained language models**: DialoGPT, Blender, PLATO — fine-tuned on dialogue data

**Key challenge**: generic/safe responses ("I don't know"). Addressed via diversity-promoting objectives, knowledge grounding, and persona conditioning.

### 3. Hybrid

Combines retrieval and generation — e.g., retrieve candidate responses then use them as templates or additional context for generation.

## Two Goals

### Informative
Ground the dialogue with external knowledge:
- **Knowledge-grounded conversation (KGC)**: structured KGs, unstructured documents (Wikipedia)
- **Multi-modal grounding**: images, video, audio
- **Profile/persona**: consistent character attributes

### Controllable
Control the behavior and style:
- **Persona consistency**: maintain character across turns
- **Emotion/sentiment control**: generate responses with appropriate emotional tone
- **Strategy/policy**: follow conversation strategies (persuasion, negotiation)
- **Safety**: avoid toxic/offensive content — an important step toward deployment

## Figures from the survey (AI Open, 2022)
The survey's comparison collects results from the original papers rather than re-running them: on Ubuntu Corpus V1 the best retrieval result is BERT-FP at R1@10 0.911, the best pre-BERT is MSN at 0.800, and TF-IDF scores 0.410. Dataset sizes it quotes include Ubuntu at 930,000 dialogues and Wizard of Wikipedia at 166,787 training utterances. The extraction notes several dataset sizes differ between the survey's table and its text. The authors say their selection is not complete, and the survey predates instruction-tuned models.

## Task-oriented slot filling and intent classification

A 2020 preprint survey (Louvan and Magnini) covers the task-oriented side: **slot filling** tags each token of an utterance with a slot label, and **intent classification** assigns one intent label to the whole utterance. It sorts neural models into independent, joint and transfer-learning families and quotes results from other papers on ATIS and SNIPS, without re-running or normalising them. Its conclusions:

- Joint models nearly solve both datasets when in-domain data is sufficient (one BERT model with an intent gate is quoted at 99.76 intent accuracy on ATIS and 98.78 slot F1 on SNIPS), so the authors say chasing the leaderboards is not worthwhile; the datasets are solved, not language understanding. ATIS is skewed, with more than 70 percent of intents being flight search.
- When target-domain data is scarce, multi-task learning gives the largest gain over single-task learning, a gain that shrinks as data grows; pre-train and fine-tune also helps, with fine-tuning more prone to forgetting. With no target annotation the choice is zero-shot at the cost of writing slot and intent descriptions.
- Zero-shot cross-lingual and few-shot slot filling still have large room for improvement.

Limits: survey only; its comparison table mixes models with and without gold named-entity features and different splits; coverage ends in mid-2020 with no LLM or prompting methods.

## Three system papers (self-reported)

**Meena (Adiwardana et al. 2020).** A 2.6B-parameter chatbot judged by SSA, the average of the share of replies rated sensible and the share rated specific. Interactive evaluation: 100 conversations of 14-28 turns, labelled by a 5-worker majority vote. Full Meena (sample-and-rank with N=20, top-k 40, plus a repetition rule and a safety layer) scores 79%; the base model 72%; humans 86%. Baselines: DialoGPT 48%, Cleverbot 56%, XiaoIce 31%. Across Meena variants, test perplexity correlates with SSA at R-squared 0.93 (interactive) and 0.94 (static, 1,477 contexts). A GenericBot answering "I don't know" scores 35% static SSA against 51% for DialoGPT, which is why specificity is scored. Limits: static contexts are 1-3 turns of mostly social chat; interactive chats are short; nothing shows whether the perplexity trend holds at lower perplexity; XiaoIce and Mitsuku were tested via their web apps by volunteers, XiaoIce with state not reset and a shared account.

**Reddit-pretrained response selection (Henderson et al. 2019).** A dual-tower encoder is pretrained on 727M Reddit context-response pairs (about 18 hours on 13 K80 nodes), then fine-tuned with FT-DIRECT or FT-MIXED (3:1 mix). Metric R100@1: banking FAQ 94.8 fine-tuned against 27.3 for the pretrained model used as is. Limits: the extraction notes "six" and "five" target domains in different places; single scores; fine-tuning hyperparameters not stated.

**Blended (Lu et al. 2024).** The responder is chosen uniformly at random each turn among Pygmalion 6B, Chai 6B and Vicuna 13B. In a 30-day A/B on the Chai platform with a Pygmalion 6B control, delta-alpha was 1.7 against 0.5 for GPT-3.5 and delta-gamma 2.1 against 1.4, at 1.4x against 29.2x the cost. Limits: no confidence intervals, inconsistent group sizes, one platform, mechanism asserted not tested.

## Connection to Agent Systems

Modern agent architectures inherit concepts from dialogue systems:
- **Retrieval-augmented generation** descends from hybrid dialogue methods
- **Tool use** extends beyond pure dialogue to action execution
- **Context management** (which turns to attend to) is solved by [[Self-Attention Mechanism]] in models like [[Dialogue Transformers — TED Policy]]
- **Safety/guardrails** builds on controllable dialogue research — see [[Input Guardrails Pipeline]]

## See Also
- [[Dialogue Transformers — TED Policy]] — instance-of
- [[DIET Architecture]] — extends (NLU component for dialogue systems)
- [[Voice Agent Patterns]] — extends
- [[LLM-Blender PairRanker and GenFuser]] — alternative-to (Blended mixes models per turn at random)
- [[Input Guardrails Pipeline]] — extends (safety/controllability)
- [[Agents Interview Study Guide]] — instance-of
- [[Open-Domain Chatbot Recipes (BST and Minimum-Length Beam)]] — extends (recipe study: fine-tuning data, retrieval and decoding choices)
- [[Build it Break it Fix it (Dialogue Safety)]] — related (offensive-language detection for dialogue)
- [[Wizard of Wikipedia]] — instance-of
