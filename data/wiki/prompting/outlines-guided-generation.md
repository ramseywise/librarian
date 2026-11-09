---
title: Outlines Guided Generation
tags: [prompting, concept]
summary: Outlines casts constrained generation as a finite-state machine over the vocabulary, precomputing an index from state to allowed tokens so each step applies a logit mask at roughly constant cost; it guarantees format, not correctness, and the paper's evidence is thin.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-willard-2023-efficient-guided-generation-large-language.md
---

# Outlines Guided Generation

The Outlines paper treats guided text generation as moving through a finite-state machine. A regular expression is compiled into an FSM. Before generation, an index is built that maps each FSM state to the vocabulary tokens that keep the output valid. At each decoding step, the current state selects its set of allowed tokens, a mask is applied to the logits, and the sampled token moves the machine to its next state.

## Claims

- The per-token cost is O(1) on average, against O(N) for the common approach of scanning the vocabulary, where N is 50,257 for GPT-2 (self-reported).
- The index for a naive Python-grammar setup takes about 50 MB (self-reported).
- A context-free grammar extension, using an LALR(1) parser with a trie on the parser stack, is described but has no experiment.

## Evidence

The one runtime test is a single sample: GPT-2, one regular expression, compared with one library (Guidance) with caching and token healing turned off, for 20 to 100 tokens. The extraction read the plot axes only, with a plot range up to about 120 seconds. Small GPT2-medium examples show that a constrained answer can be well formed and wrong: the guided output "Is 1+1=2? Always" is valid and false. The constraint guarantees shape, not truth.

## Limits

- Thin evidence: one model, one regex, one comparison library, one sample.
- No measurement of output quality.
- A 2023 snapshot; there is no benchmark against ReLM, PICARD or Synchromesh.
- The extraction notes a duplicate reference and a cross-reference error in the paper.

## See Also
- [[Structured Output]] — prerequisite-for
- [[Ctrl-G HMM Logical Control]] — alternative-to (the Ctrl-G paper contrasts the two approaches)
- [[Length Limits Are a Fit Layer, Not a Prompt]] — related (deterministic enforcement of output constraints)
- [[Logits Masking and Grammar-Constrained Generation]] — alternative-to
