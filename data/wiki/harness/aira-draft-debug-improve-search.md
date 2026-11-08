---
title: AIRA Draft-Debug-Improve Search
tags: [harness, pattern]
summary: "AIRA-Compose and AIRA-Design run a greedy tree search of draft, debug, improve and analyze operators to design neural architectures; one-shot agents produced no valid submissions and only a third of open-ended autoresearch steps scored."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-pepe-2026-agentic-discovery-neural-architectures.md
---

# AIRA Draft-Debug-Improve Search

Pepe et al. (FAIR at Meta, 2026) apply the AIRA-dojo harness to two jobs: composing hybrid architectures from primitives (AIRA-Compose) and designing models for the Long Range Arena (AIRA-Design), and then replay Karpathy's autoresearch task.

## Mechanism

Four operators: Draft makes initial candidates, Debug fixes execution or logic errors, Improve refines a working solution, Analyze reads the solution at each step. The greedy policy drafts five solutions, improves the node with the best validation score, and debugs whenever Analyze flags a bug. Each task has an isolated scorer holding hidden test labels, and the agent validates on a held-out 30% of the training set.

## Findings (self-reported)

- One-shot agents produced no valid submissions in 960 runs (20 seeds, 8 agents), while 12 greedy agents ran 720 runs.
- Validation was a poor guide to test in the example the paper shows (0.3869 against 0.5827), though submitted accuracy tracked the best seen for most agents.
- Autoresearch: about a third of steps (3,936 of 11,530) produced a valid score. The best bits-per-byte, 0.968, came from one seed of the variant with literature access, starting from a 1.0121 baseline here (0.998 originally); medians were near 0.99. About 20% of experiments beat the originally reported gain. Seven of 27 features were ever the only change in an improvement step, because rewriting whole files yields compound edits that block attribution.
- More freedom hurt weaker agents: the configurable setup helped four greedy agents and hurt seven.
- At 1B parameters and 37.5B tokens, an agent-designed transformer beat Llama 3.2 on loss (2.734 against 2.815, three seeds). The hybrid results are single-seed.

## Limits

- Agent designs recombine known methods, by the authors' own account; the recursive self-improvement framing is aspirational because no loop closes.
- The abstract's faster-scaling percentages have no body-text derivation (extraction note).
- Baselines such as Nemotron are approximated; only 16-layer proxies were scored; the aggregation steps are not agentic.
- No cost per result and no comparison of search policies.
- Model names will age.

## See Also
- [[Verification Loops]] — related
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Loop Scorekeeper]] — prerequisite-for
- [[AI Research Preference Model]] — extends
