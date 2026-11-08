---
title: AI Research Preference Model
tags: [loop, pattern]
summary: "A research preference model ranks candidate experiments by pairwise comparison before any is run, which lets a research-agent search spend its compute on the likelier winners."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-foster-2026-ai-research-preference-models.md
---

# AI Research Preference Model

Foster et al. (an August 2026 preprint) put a judge between the generator and the executor in a tree-search research agent. The authors report that language models forecast absolute scores and execution outcomes unreliably, so the model ranks candidates instead.

## Mechanism

- At each Draft or Improve step the generator proposes a batch of candidates (15 in the main setup).
- The preference model runs a pairwise knockout tournament over them, shown the validation scores of a few earlier executed nodes selected by breadth-first order.
- Only the winner is executed. Two variants: inference-only, and agentic, which can run a quick pilot experiment in a sandbox clone first. Debug steps stay random.

## Results (self-reported)

On 20 text and tabular tasks, 24 hours on one GPU, 10 seeds: average normalised score 0.684 without the model, 0.711 inference-only and 0.729 agentic, against oracle ceilings of 0.748 and 0.759. The guided variants reached the baseline's final score in about 15 hours. Selection advantage per run correlates with the final score (Pearson 0.55). Offline, pilot experiments lifted pairwise accuracy from judgment alone to 78.5% (5 minutes) and 84.0% (4 hours); an LLM arbiter over three judges (69.4%) beat a majority vote (68.0%).

## Limits

- Significance is modest: the probability of improvement over no model is about 0.59, with 95% interval bounds just above 0.5.
- The generator and the preference model are the same Qwen model in the end-to-end runs.
- The extraction notes that the context-count labels on the offline scaling numbers are unreliable.
- Cost of the judging and pilot compute is not counted in the 24-hour budget; only the executed candidate's compute is.

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Bradley-Terry Preference Model]] — related (pairwise preference ranking)
- [[Rehearse Focused Outcome Memory]] — alternative-to
- [[SIFT Judge-Guided Self-Improvement Tree Search]] — alternative-to
- [[AIRA Draft-Debug-Improve Search]] — prerequisite-for
