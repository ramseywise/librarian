---
title: Nucleus Sampling and Text Degeneration
tags: [llm, architecture, pattern]
summary: "Holtzman et al. show that likelihood-maximising decoders (greedy, beam search) loop on open-ended text while pure sampling drifts incoherent, and propose sampling only from the smallest set of tokens whose probability sums to p, measured on GPT-2 Large against human WebText."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-holtzman-2019-curious-case-neural-text-degeneration.md
---

# Nucleus Sampling and Text Degeneration

Holtzman, Buys, Du and colleagues (ICLR 2020) ask which decoding rule gives open-ended text that matches human text on both quality and diversity. They contrast open-ended generation, where the context narrows the output without fixing it, with directed generation such as translation or summarisation. Their hypothesis is twofold: maximising likelihood is the wrong target for open-ended text, and pure sampling fails through an unreliable tail of low-probability tokens, which a dynamic nucleus removes.

## Mechanism

**Nucleus (top-p) sampling** takes the smallest set V(p) of tokens whose cumulative probability under the model is at least p, sets every probability outside it to zero and renormalises inside it by the mass p' of the set, then samples. Because the set is defined by cumulative mass, its size changes with the shape of the next-token distribution; the authors call this a dynamic nucleus. [[Temperature, Top-k and Test-Time Sampling]] covers top-k and top-p at the level of API parameters; this page is the paper behind top-p.

## What they measured

Setup for the conditional-generation rows (greedy, beam width 16, pure sampling, nucleus, top-k): GPT-2 Large (762M parameters), 5,000 generations of up to 200 tokens, each conditioned on a 1 to 40 token prefix from held-out WebText, compared with human WebText (self-reported). The rows on beam widths 32 and 64, repeated phrases, human per-token probability and Self-BLEU state their own setups.

- **Greedy decoding** falls into repetition loops in most generations.
- **Beam search**, width 16, repeats in about 29% of generations, and its perplexity is far below human text. In the authors' unicorn-prompt example (GPT-2 Large and XL, Fig 1), width 32 degenerates into repetition, and at widths of 64 and above GPT-2 Large and XL stop immediately.
- **Probability of a repeated phrase rises with each repetition** (phrases tested from human and random text), which the authors describe as a positive feedback loop.
- **Human text** (Figs 2 and 6) has per-token probability much lower than beam search text, so natural language does not maximise probability.
- **Pure sampling** has perplexity worse than human text.
- **Nucleus sampling at p=0.95** has perplexity closest to human among the tabulated methods and the highest HUSE score. Its repetition rate is 0.36% against 0.28% for human text, and Self-BLEU4 is 0.32 against 0.31 for human text.
- **Top-k=40** scores 0.19 on HUSE; top-k=40 combined with temperature 0.7 scores near zero.
- **Self-BLEU** over 5,000 unconditional documents: temperatures from 0.5 to 1 and k from 1 to 100 give outputs that resemble each other heavily, while p between 0.9 and 1 comes close to the human value.

HUSE rested on 200 generations per method with 20 annotators each, and the top-k and nucleus HUSE scores use an interpolated distribution with mass 0.1.

## Limits

- Only GPT-2 Large and English web text are tested; no instruction-tuned models.
- One run, with no seeds or confidence intervals given.
- The top-k and nucleus HUSE numbers come from an interpolated distribution (mass 0.1), which is a proxy.
- Appendix A attributes the drop in beam search repetition at larger widths mainly to shorter generations, so the width trend does not show a repetition fix.
- For future work the authors name a combination of training-time and inference-time remedies, plus a semantic utility measure.

## See Also
- [[Temperature, Top-k and Test-Time Sampling]] — prerequisite-for
- [[Hierarchical Story Generation]] — related (the top-k sampling baseline this paper evaluates)
- [[Diverse Beam Search]] — related (another change to decoding to avoid the beam search failure)
