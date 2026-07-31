---
title: Dialogue Transformers — TED Policy
tags: [foundations, concept]
summary: Transformer Embedding Dialogue (TED) policy (Rasa, 2020) applies self-attention at the discourse level — over dialogue turns rather than tokens — outperforming LSTM-based policies on sub-dialogue handling while being simpler and faster than REDP.
updated: 2026-07-19
sources:
  - raw/pdfs/2020-10-01-rasa-dialogue-transformers.md
---

# Dialogue Transformers — TED Policy

The Transformer Embedding Dialogue (TED) policy (Vlasov et al., 2020) replaces RNN-based dialogue policies with a transformer whose [[Self-Attention Mechanism]] operates over the sequence of **dialogue turns**, not tokens within a single turn.

## Motivation: Interleaved Discourse Segments

Real conversations contain interleaved topics. A user might interrupt a hotel booking flow with chit-chat, then return to the task. Grosz and Sidner (1986) modeled this as discourse segment stacks, but strict stacks can't handle arbitrary revisitation of topics.

**RNNs** process the entire sequence by default — every turn updates the hidden state. In low-resource settings, they struggle to learn when to "forget" irrelevant turns.

**Transformers** have no such assumption. Self-attention selects which turns are relevant at each step, naturally ignoring irrelevant history.

## Architecture

### Featurization
- **Modular mode**: external NLU provides intent + entity labels (binary vectors)
- **End-to-end mode**: raw utterances encoded as bag-of-words vectors
- **Slots**: binary vectors (present/absent/not-important)

### Unidirectional Transformer
Input: sequence of (user input, system action, slots) per turn. The transformer is unidirectional — upper triangle masked to prevent attending to future turns.

### Similarity-Based Action Selection
Transformer output and system actions are embedded into a shared 20-dimensional semantic space. Dot-product loss (same as [[DIET Architecture]]) maximizes similarity with the correct action and minimizes similarity with negatives:

```
L = -<S+ - log(exp(S+) + sum(exp(S-)))>
```

At inference, the current dialogue state is compared to all possible system actions by dot-product similarity.

## Key Results

### Sub-Dialogue Handling
On Rasa's REDP dataset (task-oriented dialogues with non-cooperative interruptions):
- **TED matches REDP** (purpose-built LSTM+attention+copy mechanism) performance
- **Significantly outperforms vanilla LSTM**
- Achieves this with a **simpler, faster, more general** architecture
- In extreme low-data regime, REDP slightly wins (due to its copy mechanism for repeating questions)

### Attention Visualization
Attention weights are naturally sparse and interpretable:
- Series of chit-chat interactions are **completely ignored** when the model returns to task completion
- The policy picks key dialogue steps from history (e.g., provided slot values) and ignores uninformative turns

### MultiWOZ Results
On MultiWOZ 2.1 (10,438 dialogues, 7 domains):
- Modular TED: 73% accuracy, 0.63 F1
- End-to-end TED: 64% accuracy, 0.28 F1
- **History independence discovered**: reducing history from 10 to 2 turns barely affects scores — MultiWOZ depends weakly on dialogue history
- TED and LSTM perform comparably on this dataset (as expected, since long-range dependencies are absent)

### Practical Advantages
- Faster training than REDP (fewer epochs needed)
- No specialized architecture (no copy mechanism, no attention modifications)
- Same architecture handles both modular and end-to-end setups

## Connection to Agent Engineering

TED demonstrates that transformer self-attention is not just for language modeling — it's effective at the **orchestration level** where the sequence elements are entire dialogue turns, not tokens. This principle applies directly to:
- Agent systems that must decide which conversation history is relevant for the next action
- [[HistoryCondenser]] and context management — selectively attending to relevant history
- Multi-turn agent loops where irrelevant tool calls or user digressions should be ignored

## See Also
- [[Transformer Architecture]] <!-- auto-linked -->
- [[DIET Architecture]] — extends (DIET provides NLU for TED's modular mode)
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Open-Domain Dialogue Systems]] — instance-of
- [[HistoryCondenser]] — extends (both address selective history attention)
- [[Summarization Node]] — extends (compaction as alternative to attention-based selection)
