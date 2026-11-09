---
title: Self-Collaboration Role-Based Code Generation
tags: [graph, concept]
summary: Three ChatGPT instances given analyst, coder and tester roles exchange text on a shared blackboard in a waterfall order; reported Pass@1 gains of 29.9 to 47.1 percent relative over one ChatGPT agent, with the tester simulating tests rather than running code (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-dong-2024-self-collaboration-code-generation-chatgpt.md
---

# Self-Collaboration Role-Based Code Generation

Self-collaboration (ACM TOSEM; arXiv v3, May 2024) asks whether a single agent loses to several instances of the same LLM that are given role instructions within a software-development workflow. Three ChatGPT sessions start from role instructions (a team description, a role description and the user requirement) that make them analyst, coder and tester, in a simplified waterfall model. They pass natural-language output to one another via a shared **blackboard**: the analyst writes a decomposition and plan, the coder writes code, the tester simulates testing (no code is executed) and reports, and the coder repairs the code until the tester says "Code Test Passed" or the cap of n interactions is hit. No training is involved.

## Results (self-reported)

Setup unless stated otherwise: ChatGPT gpt-3.5-turbo-0301 with three roles, at most 4 interactions, temperature 0 and 512 max tokens, in the "NL + signature + use cases" setting, scored as Pass@1.

- Relative Pass@1 gains of 29.9% to 34.6% on HumanEval, HumanEval-ET, MBPP and MBPP-ET and 47.1% on CoderEval.
- HumanEval 74.4 against 57.3; HumanEval-ET 56.1 against 42.7; MBPP 68.2 against 52.2; MBPP-ET 49.5 against 36.8. Prompting baselines on HumanEval score 65.2 (self-planning), 61.6 (self-debugging), 55.5 (iter-improving) and 44.6 (zero-shot CoT).
- GPT-4: HumanEval 90.2 against 67.7; MBPP-ET 62.1 against 49.2. APPS (first 1000 interview and competition tasks): 3.4 against 1.2. CoderEval average 29.14 against 19.82.
- Role ablation (HumanEval, NL-only): coder alone 45.1, with analyst 54.9, with tester 56.8, full team 63.5. Role instruction (64.4) beats zero-shot instruction (60.0) and 4-shot (58.1). Adding a compiler (64.6) is comparable to the full team; pair programming scores 57.4. Without signatures and use cases, on MBPP NL-only, coder plus tester (64.9) beats coder plus analyst (54.8).
- Most of the gain arrives with the first interaction round, as MI=0 gives 45.1 and MI=1 gives 60.4. In a manual error analysis, 18.4% of tasks the coder failed were corrected and 36.5% remained unpassed.
- The ability appears around 7B parameters among open chat models and grows with size.

## Limits

- The benchmarks work at function level, and the authors concede that claims about repository-level work rest on two qualitative case studies.
- The tester does not execute code; single run at temperature 0, no variance or significance tests.
- The authors suspect data contamination in MBPP, and the analyst role hurts on NL-only MBPP.
- Needs capable base models; token cost is higher than a single coder (values only in a figure); ChatGPT limits capped interactions at 4.
- Baselines use prompts from the original papers; the multi-agent field has since moved on (the extraction's note).

## See Also
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[CAMEL Role-Playing Inception Prompting]] — related
- [[Verification Loops]] — related
