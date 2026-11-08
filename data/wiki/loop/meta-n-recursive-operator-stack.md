---
title: "Meta^n Recursive Operator Stack"
tags: [loop, pattern]
summary: "Meta^n keeps one improving operator fixed and recurses on its input instead, feeding each layer the traces and code of the layer below; most of the gain comes from the plain context string passed between layers."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kim-2026-meta-n.md
---

# Meta^n Recursive Operator Stack

Kim et al. (an August 2026 preprint) argue that self-modifying agents such as STOP, Gödel Agent, DGM and HyperAgents each hold some driver layer fixed for stability, which the authors say caps realised meta-depth at about 2.5 on their own half-credit scale. Meta^n freezes the operator and grows its input: every layer receives the traces of the stack beneath it plus the code that produced them.

## Findings (self-reported)

- Removing recursion lowered archive-best validation score from 0.845 to 0.714 (Gemma, CO-Bench), 0.886 to 0.806 (GPT-5.2, CO-Bench) and 0.917 to 0.759 (GPT-5.2, AlphaEvolve math).
- About 72% of that gain came from the inter-layer context string, about 15% from the code library, about 13% from machinery such as beams and retries.
- Held-out CO-Bench: 0.851 against 0.814 for OpenEvolve and 0.451 for Gödel Agent with Gemma; 0.870 against 0.702 and 0.527 with GPT-5.2. Giving Gödel Agent 5x and 10x budget lifted it only to 0.615 and 0.628. The authors explain this through the fixed driver: Gödel Agent relies on the model choosing to modify itself, which it rarely does, while the operator emits an injection every time.
- Deeper layers regress individual tasks (41% of chain-task pairs regress at depth 3), and the next layer repairs them because it sees the code. Rollback is absent at depth 2 and appears at depth 3 in 55% (code) or 33% (prompt) of emissions. Mean score peaks at depth 3.
- Agentic mode costs 4 to 10 times the tokens; at matched compute it still leads OpenEvolve (S2D 0.732 against 0.718; LawBench 0.784 against 0.745) (self-reported).
- The gain depends on headroom: absent on SWE-Bench, where the operator never activates, and on AlgoTune, where the seed is strong.

Every layer here is the same model. See also [[Harness Updating vs Harness Benefit]].

## Limits

- Scores are validation archive-best, with no held-out pass for the ablations; three seeds.
- Meta-depth is an author-defined metric.
- Role labels on 596 emissions come from two LLM raters with Cohen's kappa 0.59 on average (0.30 to 0.37 on abstract roles).
- Gödel Agent was run in a corrected configuration set up per task; through its published interface it scores close to 0.
- The ARC-AGI-2 held-out claim is in the text, not in a table, per the extraction.
- A single group, preprint.

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Loop State File]] — prerequisite-for
- [[Red Queen Gödel Machine]] — alternative-to
- [[Harness Updating vs Harness Benefit]] — related (evolver capability)
