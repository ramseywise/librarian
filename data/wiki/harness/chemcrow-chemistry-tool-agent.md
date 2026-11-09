---
title: ChemCrow Chemistry Tool Agent
tags: [harness, agents, tools, concept]
summary: "ChemCrow wraps GPT-4 in a ReAct loop with 18 chemistry, search, safety and reaction tools; the authors report four robot-executed syntheses and expert preference over tool-less GPT-4 on 14 tasks, while a GPT-4 judge ranked the two the other way round (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-bran-2023-chemcrow.md
---

# ChemCrow Chemistry Tool Agent

ChemCrow tests whether a language model given expert chemistry tools can handle work (planning and running syntheses, designing molecules) that the bare model does badly. The base model is GPT-4 at temperature 0.1, prompted through LangChain in the ReAct format of Thought, Action, Action Input and Observation. It has 18 tools covering chemistry, literature search, safety and reaction planning, including a reaction-prediction service and a literature question-answering tool. The claim is that the tools reduce hallucination and open up capabilities the model lacks.

## Reported results

All results are self-reported by the authors.

- **Robot synthesis.** The agent planned and executed four syntheses (an insect repellent and three thiourea organocatalysts) on a cloud robotic platform, each giving the anticipated compound. The extraction notes that predicted procedures were not always directly executable and needed iterative fixing.
- **Guided discovery.** With a human in the loop, the agent fitted a random forest to chromophore data (one solvent only) and proposed one molecule; the compound that was made peaked at 336 nm where the target was 369 nm, and the model's RMSE was 37 nm.
- **Expert comparison.** On 14 tasks, four expert chemists preferred ChemCrow to GPT-4 prompted as an expert chemist, especially on complex tasks; the tool-less model did better mainly on easy, memorised tasks. The scores appear only in figure images, so this write-up has no numbers for them.
- **LLM judge disagrees.** A GPT-4 evaluator told to act as a teacher judged the tool-less model better on average, which the authors read as a preference for fluent, complete-looking answers. Same 14 tasks.
- **Tool output versus reading it.** In five independent runs of one task the tools returned the right products each time, but in two runs the model read a SMILES string as a trans alkene and so reached wrong conclusions about the mechanism.
- **Safety tools.** A controlled-chemical or explosive check halted execution on a nitroglycerin-analogue task with a warning.

## Limits

- Hallucination, hard-to-evaluate output and reproducibility are the stated limitations; tools cannot fully repair flawed model reasoning, and quality is bounded by the tools (the agent should not be expected to outdo the retrosynthesis tools it relies on).
- The evaluation has just 14 tasks with implicit selection bias, and it uses a closed model, so single results cannot be reproduced. The public release includes 12 of the 18 tools.
- Numeric expert scores and the 95% intervals are in figures, not text.

## See Also
- [[ReAct Pattern]] — prerequisite-for
- [[Tool Definitions as Prompts]] — related
- [[LLM-as-Judge Evaluation]] — related (judge and experts disagreed here)
- [[Execution Boundaries and Guardrails]] — related (safety tools that halt execution)
