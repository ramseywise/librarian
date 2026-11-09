---
title: Self-Discover
tags: [prompting, pattern]
summary: "Self-Discover has the model select, adapt and implement reasoning modules into a JSON plan once per task, then fill the plan per instance; it reports gains over zero-shot chain of thought with PaLM 2-L and GPT-4, mostly on world-knowledge tasks, and small MATH gains because failures are arithmetic (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhou-2024-self-discover.md
---

# Self-Discover

Self-Discover composes a task-specific reasoning structure with the model itself. Stage 1 runs once per task and uses three meta-prompts plus a handful of unlabeled examples. SELECT chooses relevant modules out of 39 seeds, ADAPT rewrites them to fit the task, and IMPLEMENT assembles a JSON plan, with a human-written plan from a different task as its demonstration. Stage 2 happens for each instance, where the model completes the plan's fields. For MATH the structures are generated per instance rather than per task.

## Results

All figures are self-reported, zero-shot, with PaLM 2-L and gpt-4-turbo-preview.

- Aggregate accuracy, PaLM 2-L then GPT-4: BBH 67 and 81 against zero-shot chain of thought 60 and 75; T4D 69 and 85 against 40 and 52; MATH (200-example subsample) 50.5 and 73 against 42 and 71.
- It beats direct answering on 23 of 25 tasks and chain of thought on 21 of 25 (PaLM 2-L).
- Efficiency: one inference call per instance plus three task-level calls, against 10 times for self-consistency with 10 samples and 40 times for a vote over the 40 modules. The 10-40x claim comes from only two BBH tasks with GPT-4.
- The extraction reads the largest gains as world-knowledge tasks, but could not recover the figure's pairing of values to categories.
- MATH: of 99 wrong predictions from 200 samples, 25.3% had wrong structures and 74.7% were calculation errors, annotated by the authors; they suggest tools or code generation.
- Several GPT-4 BBH tasks regress against chain of thought, for example multistep arithmetic 92 to 70 and penguins 100 to 90.
- Structures discovered by PaLM 2-L transferred to GPT-4 and beat OPRO-optimised prompts on three of four tasks, though OPRO used 20% of the data.

## Limits

- Longer input and output than chain of thought raises cost; zero-shot Llama2 gave low-quality structures, so smaller models must borrow them.
- No variance or seeds; the transfer tests cover few tasks; the extraction notes that the ablation numbers are read from figure ordering, and that on Geometry the middle stage scores below the first, so the "consistent" gain is not strict.
- The models date from late 2023, before reasoning models.

## See Also
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Least-to-Most Prompting]] — related
- [[Buffer of Thoughts]] — alternative-to
- [[Prompting Technique Selection]] — related
