---
title: Why Context Is Finite
tags: [context, llm, agents, concept]
summary: Attention divides a fixed budget across n² token pairs, so added tokens thin attention rather than expanding capacity — the marginal return curve turns negative, not merely flat.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--01-why-context-is-finite.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--01-why-context-is-finite.md
  - data/raw/papers/2026-11-06-mohsin-2025-fundamental-limits-llms-scale.md
  - data/raw/papers/2026-11-06-xiong-2023-effective-long-context-scaling-foundation.md
---

# Why Context Is Finite

The mechanism note. Every technique in [[Context Engineering]] is a response to the
constraint described here.

## Attention Budget

Every token costs something **even when it is harmless**. LLMs have a finite attention
budget — the pool of representational capacity drawn on when processing a window. Adding
tokens does not expand the budget; it divides the existing budget across more claimants.

The mechanism is architectural: in a transformer every token attends to every other token,
producing **n² pairwise relationships** for n tokens. Doubling the context quadruples the
attention pairs the model must resolve while the parameters resolving them stay fixed.
**Attention gets thinner, not just slower.** See [[Self-Attention Mechanism]].

Two consequences:

- **Token cost is not the binding constraint.** A 150k window that fits comfortably in
  budget and latency can still degrade output quality.
- **"It fits in the window" is not an argument for including something.** Window capacity
  is an upper bound on what is *possible*, not a target.

## Context Rot

**Context rot** is the empirically observed decline in a model's ability to accurately
recall and use information as occupancy grows. Not a cliff at the window limit — gradual
degradation beginning well before it.

| Shape | What it looks like |
|---|---|
| **Middle neglect** | Start and end recalled; the middle is not — "lost in the middle" |
| **Distractor sensitivity** | Plausible-but-wrong nearby content pulls the answer off target, more so as the window grows |
| **Instruction decay** | System-prompt constraints obeyed early are quietly dropped later |
| **Needle degradation** | Exact-match retrieval of a planted fact degrades as filler increases, *even when the fact is verbatim present* |

**The last one is the important one.** The fact is there, unmodified, and the model still
misses it. This is why "include it just in case" is a real cost rather than free
insurance — filler actively degrades retrieval of the signal it surrounds.

Long-context handling techniques (**position encoding interpolation**, letting a model
address sequences longer than it trained on) extend the addressable range. **They do not
repeal rot — they move where it starts.** See [[Positional Encoding]].

## Diminishing Marginal Returns

```
signal
  ^
  |        ....----____
  |     ..'            ''--___          <- each added token returns less,
  |   .'                      '--__        then returns negative
  | .'
  +-------------------------------> tokens in window
     ^ high-signal      ^ filler
```

**The curve turns negative, not merely flat.** Past a point, adding a marginally relevant
document makes output worse than omitting it, because it competes for attention with the
tokens that mattered.

This is the economic argument for retrieval strategy, compaction, memory offloading, and
sub-agent isolation — all exist to keep the window on the left side of that curve.

## Implications for Practice

1. **Curate, don't accumulate.** The default action on a new piece of context is to
   *justify* it, not to include it.
2. **Measure occupancy, not just cost.** Track percentage of window used as a health
   metric independent of dollars.
3. **Position matters.** If content must be included, order it. See [[Context Anatomy]].
4. **Prefer a pointer to a payload.** A file path the agent can read on demand costs a
   handful of tokens; the file costs thousands. See [[Context Retrieval Strategies]].
5. **Plan for sessions that outlive the window.** Long-horizon work needs compaction and
   external memory, not a bigger window. See [[Context Compaction]] and
   [[Memory as Context]].

## A theory paper on the limit

Mohsin (arXiv 2511.12869, preprint under review at TMLR) is a theory-plus-survey paper with no experiments of its own; the extraction judges that its numbers are all borrowed and that nothing citable comes from it beyond the cited sources. What it offers is labelled theory: Lemma 4 and Corollary 1 argue that softmax attention needs a margin of about ln N over N items, and a failure bound for retrieval multiplies how much a distractor is exposed by how much attention it gets.

Its empirical claims are cited from others, so cite the originals. A single irrelevant passage cutting accuracy by up to 30% comes from Yang et al. 2025b (setup not given in this paper); poisoned retrieval reaching about 90% attack success with five poisoned documents per query in a knowledge base of millions of entries comes from the PoisonedRAG work; and a "70B model with 64K effective context" figure comes from Wang et al. 2024c.

## Effective Window Against Nominal Window

A 2023 study on Llama 2 continual pretraining (self-reported) fits validation loss as a power law in context length up to 32,768 tokens, L(c) = (alpha/c)^beta + gamma, with beta rising with model size (0.45 at 7B to 0.51 at 70B). It reports that the original RoPE gave no useful attention past roughly 4,000-6,000 tokens despite long continual pretraining, and that setting the RoPE base frequency to 500,000 instead of 10,000 repaired this (7B, a first-sentence-retrieval probe, 80B tokens at 32,768 sequence length). A model's usable window may be far shorter than its advertised one, and finding it takes a probe task. Continued pretraining came close to the quality of pretraining on long sequences from the start while spending about 40% fewer FLOPs, and long documents in the data mattered less than data quality.

Limits: Llama 2 only, no needle-in-a-haystack test, dated models; the loss result is not a task result, and one QuALITY series in the extraction is flat after 8k although the text calls the trend monotonic.

## Limits

- The extraction flags rigor problems: the proof of Theorem 2 is flawed (the index it defines reduces to k, so each model is reached a single time instead of infinitely many times); Lemma 3 covers only sinusoidal position encodings, and the claim for rotary encodings is asserted without proof; several propositions are stylised or labelled testable claims; its figures plot values cited from others or illustrate, not data produced there.
- The extraction also notes that the paper is inconsistent about where some numbers originate, for example a repeated Wang et al. 2024c citation.

## See Also
- [[Context Engineering]] — related (part of)
- [[Context Failure Modes]] — related (causes)
- [[Context Anatomy]] — related (mitigated by)
- [[Context Window Budgeting]] — prerequisite-for
- [[Position Interpolation]] — instance-of
- [[Artificial Hippocampus Networks]] — instance-of
- [[IN2 Training and VAL Probes]] — related
