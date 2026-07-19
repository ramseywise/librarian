---
title: Open-Domain Dialogue Systems
tags: [foundations, concept]
summary: Survey of frameworks for open-domain conversation — retrieval-based (score candidates), generation-based (seq2seq/PLM), and hybrid methods — with two key goals (informative via knowledge grounding, controllable via persona/strategy/safety).
updated: 2026-07-19
sources:
  - raw/pdfs/2020-01-01-conversational-ai.md
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
- [[Input Guardrails Pipeline]] — extends (safety/controllability)
- [[Agents Interview Study Guide]] — instance-of
