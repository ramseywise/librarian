---
title: Code as Policies Language Model Programs
tags: [llm, gui-and-embodied-agents, concept]
summary: "Code as Policies few-shot prompts a code LLM to write Python robot policy code that calls perception and control APIs; hierarchical code generation filled undefined functions recursively and reached 39.8% pass@1 on HumanEval (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-liang-2023-code-as-policies.md
---

# Code as Policies Language Model Programs

Liang, Huang, Xia et al. (preprint arXiv v4, May 2023, cs.RO) ask whether code-writing LLMs, prompted few-shot with no training, can author robot policy code that reads perception outputs and sets control primitive parameters, and whether that carries over to new instructions. A language model program (LMP) is any program a language model generates and a system executes.

## Mechanism

- The prompt holds Hints (such as imports) and Examples (comment-to-code pairs); the LLM then writes Python that calls perception and control APIs.
- Hierarchical code generation: undefined functions in the generated code are found by parsing the abstract syntax tree and filled in depth-first by a function-generating LMP. The authors see this as chain-of-thought via functional programming, and cite recursive book summarisation as inspiration.
- Safety checks before running: no imports, no names beginning with double underscores, no exec or eval inside the generated code; the code is then run with exec.

## Reported results (self-reported)

- Spatial-geometric questions (code-davinci-002 at temperature 0 on 51 questions, split into 28 on picking objects and 23 on picking positions; a position counted as right within 1 cm): writing Python beat natural-language reasoning, vanilla and chain-of-thought.
- HumanEval (164 problems, code-davinci-002): hierarchical generation raised pass@1 over flat generation; the contribution list gives 39.8% P@1. Hierarchical generation was triggered on only 6.5% of those 164 problems.
- RoboCodeGen, a new benchmark of 37 problems with human-written unit tests, shows pass rate rising with model size (GPT-3 6.7B against 175B InstructGPT, hierarchical).
- Simulated tabletop (50 trials per task with 10 blocks and 10 bowls): on unseen attributes and unseen instructions, long-horizon success exceeded a natural-language planner and CLIPort (which had 30k demonstrations for training). On seen attributes and instructions, CLIPort beat Code as Policies on spatial-geometric tasks, and CLIPort fails on the unseen spatial-geometric set.

## Limits

- Limited by the range of things the perception APIs can express and by the primitives available; just a few primitive parameters can be tuned before prompts become oversaturated.
- Commands that are much longer, more complex, or pitched at another level of abstraction than the Examples (building a house out of blocks, for instance) are hard for it.
- Assumes every instruction is feasible and cannot tell beforehand whether a response is correct.
- Numeric evaluation covers only restricted simulated tasks, and none is given for real robot settings.
- Transfer across embodiments is fragile, and the reactive controllers are basic, with gains that are not adjusted using execution feedback.
- Drawing many samples (P@100) is impractical for LMPs, so greedy output alone is used. Codex model sizes are not public, and code-davinci-002 is compared with code-davinci-001 in prior work.

## See Also
- [[Inner Monologue Embodied Feedback Planning]] — related (planning with feedback; source of the sim environment)
- [[SayCan Affordance-Grounded Skill Selection]] — related (LLM planning with skill affordances)
- [[Program-Aided Language Models (PAL)]] — related (code as the reasoning medium)
- [[HumanEval and pass@k]] — related
- [[Chain-of-Thought Prompting]] — prerequisite-for (the baseline hierarchical generation is likened to)
