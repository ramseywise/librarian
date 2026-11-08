---
title: Four Levels of AI Design Complexity
tags: [foundations, concept]
summary: "A CHI 2020 framework says AI is hard to design for because of capability uncertainty and output complexity, and sorts systems into four levels by how many of the design challenges they bring; rule-based simulators prototype levels one and two but not three and four."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-re-examining-whether-why-how-human.md
---

# Four Levels of AI Design Complexity

Yang, Steinfeld, Rose and Zimmerman (CHI 2020) ask whether designing for human-AI interaction is uniquely difficult, and why. Their answer is a conceptual framework built from their own cases, not an empirically tested one. The extraction notes that this Yang is not the SWE-agent author, so cite with the full name or title.

## Two sources of difficulty

- **Capability uncertainty:** doubt over the system's abilities and how well it performs. It continues after deployment, because performance can keep fluctuating and diverging as the system gains new data; the paper says it improves for users and contexts that produce rich data and worsens for infrequent users and atypical situations.
- **Output complexity:** how complex the outputs are, from a small fixed set to open-ended adaptive outputs. The authors argue this, not unpredictability, is the root cause: a bot that emits random words is unpredictable yet easy to simulate, while a quasi-random assistant resists simulation.

Both dimensions are continua.

## The four levels

| Level | Name | What it means |
|---|---|---|
| 1 | Probabilistic systems | trained on one closed dataset, emitting a small fixed set of outputs (face detection, toxicity detectors) |
| 2 | Adaptive systems | outputs adapt to user profile and context, with no learning after deployment |
| 3 | Evolving probabilistic systems | performance changes with new data, outputs still probabilistic |
| 4 | Evolving adaptive systems | both: learn after deployment and produce adaptive open-ended outputs (search engines, feed rankers, suggested replies) |

The text describes levels one and four; the extraction read levels two and three from the framework figure. Level 4 is a superset of the challenges in levels 2 and 3. At level 1 the authors say existing sketching and prototyping methods suffice; at level 4 designers meet all four challenges they list: understanding capabilities, envisioning, iterative prototyping and collaborating with engineers.

## Prototyping consequence

Rule-based simulators and Wizard-of-Oz setups work for levels 1 and 2 but cannot easily prototype systems that learn from user-generated data (levels 3 and 4), since inference errors cannot be simulated. Field trials lose rapid iteration. In related work the authors found no empirical test of the proposed AI design tools, and argue that guidelines from other authors apply to non-AI systems too.

## Limits

- Method: cases mostly from the authors' own research, design and teaching, plus interviews with 14 designers and managers, a survey of 98 more, 10 AI engineers and 13 veteran designers, and workshops. The authors concede this is neither representative nor comprehensive, and call the framework a moderate first step. No outcome metrics or counts of designers per level are given.
- It predates LLMs and agents; the paper does not say whether open-ended output complexity applies to them.
- Internal inconsistencies: none found by the extraction beyond levels two and three being drawn in a figure and barely described in the text.

## See Also
- [[Microsoft ML Workflow Survey: Nine Stages and an Activity Maturity Index]] — related (a practice study of ML teams, from the engineering side)
- [[Concept-Drift Detector Families and Prequential Evaluation]] — related (post-deployment performance change, the source of capability uncertainty)
