---
title: "Algorithm of Thoughts Plus (AoT+) State Memoization"
tags: [prompting, pattern]
summary: "AoT+ adds periodic restatement of the current state to a single-prompt search trace; on PDDL planning benchmarks its ablation credits the restatement, not the hand-written heuristics, and it matches or beats an external-verifier loop at about a third of the tokens (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-sel-2025-llms-can-plan-only-if.md
---

# Algorithm of Thoughts Plus (AoT+) State Memoization

Algorithm of Thoughts (AoT) puts a worked search trace, with backtracking, into a single prompt so the model searches inside one generation. AoT+ (an ICLR 2025 paper) changes two things: the trace restates the current problem state after each step, with identifiers of the form x.y.z, and the in-context traces can be generated randomly rather than written by hand. The restated state acts as a cache the model can attend to instead of recomputing the state from the action history. The paper's stated motivation is attention to the relevant state when the context is long.

## Results

All figures are self-reported. Setup unless noted: Blocksworld and Logistics in the PDDL validity setup of an earlier planning-benchmark paper, single prompt of 4-5 hand-built examples per domain; instance counts and run counts are not stated in the extraction.

- Blocksworld, GPT-4: CoT 35, AoT 45, AoT+ 82, and the external-verifier loop LLM-Modulo 82. With GPT-4o AoT+ gets 73 against 48 for LLM-Modulo; with Claude 82 against 19. Logistics, GPT-4: AoT+ 80 against 70 for LLM-Modulo. The extraction notes that LLM-Modulo was run with its own code base and is partly tuned for GPT-4, so the non-GPT-4 gaps may reflect baseline setup.
- Ablation (GPT-4, Blocksworld): AoT 45, AoT with random traces only 44, memoization only 84, both 82. Logistics: 24, 24, 80, 80. The memoization change carries the gain.
- Mean tokens per problem for GPT-4 on Blocksworld: 650.7 for CoT, 1929.5 for AoT, 2067.8 for AoT+ and 6452.9 for LLM-Modulo, which the paper puts at over three times AoT+.
- Against Tree of Thoughts on its original tasks (self-reported; CoT-SC baseline with 10 samples; the model is not stated): plain AoT, not AoT+, scores 71.0 on Game of 24 against 69.0 for Tree of Thoughts, and 52.0 on crosswords against 46.5. The AoT+R variant scores 70.0 and 54.0.
- Scale: gains are larger for bigger models; on Blocksworld AoT+ gives 5 for LLaMA 3.1 8B and 77 for the 405B model.
- Weak mechanism evidence: with LLaMA-2-13B-chat (not a main-result model), the fraction of attention that falls on solution steps was 86.3% for AoT and 27.0% for AoT+ in Blocksworld.

## Limits

- Compute is not matched across baselines; the verifier loop and Tree-Planner make several calls while AoT+ makes one. No variance, seeds or significance tests are reported; token standard deviations only.
- AoT+ gives no soundness guarantee, unlike a verifier loop; the model restates state itself, so errors can compound. Models are GPT-4-era, so reasoning models are untested.
- Internal inconsistency noted by the extraction: the Logistics AoT+ total of 5606.1 tokens does not equal the sum of its two reported components (2879.4 and 1726.7).

## See Also
- [[Tree of Thoughts]] — prerequisite-for
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[PlanBench o1 Evaluation]] — related (same PDDL planning benchmark family)
- [[Prompting Technique Selection]] — related
