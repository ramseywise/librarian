---
title: Stored Instruction Computer LLM Memory Universality
tags: [foundations, concept]
summary: "Schuurmans shows a frozen LLM plus an external associative memory and a regex loop can run a universal Turing machine, verified by 29 greedy prompts on Flan-U-PaLM 540B; it is a computability argument, not evidence about how agents use memory."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-schuurmans-2023-memory-augmented-large-language-models.md
---

# Stored Instruction Computer LLM Memory Universality

Schuurmans asks whether a frozen LLM can compute more once it is wired to a writable external memory and a loop that feeds results back. The construction is a stored instruction computer: the LLM plays the CPU, an external associative memory (a dictionary) plays the RAM, and only finite-state regex processing sits around the model. The paper claims that with no memory, an LLM whose input is a string of bounded length is no more powerful than a finite automaton.

## Mechanism

A Python driver takes the next prompt from the instruction register, MEMORY['op'], fills in stored values via `@[x]` placeholders (nesting limited to depth 2, keeping the processing finite-state), queries the LLM, substitutes `%[x]` placeholders in its reply, uses regexes to apply assignments and integer `+=`/`-=` updates to memory, and loops until `op` equals `halt`. Assigning a different string to `op` branches. A prompt program, made of one boot prompt and 15 instruction prompts, encodes the transition table of U15,2, a universal Turing machine with 15 states and 2 symbols (a machine from Neary and Woods). Correctness reduces to the model returning the right output on 29 finite (state, symbol) prompts.

## Result

Flan-U-PaLM 540B at temperature 0 (greedy), one call per case, returned the correct result string for all 29 prompts (self-reported), so the frozen model plus memory exactly simulates U15,2 with no weight changes. The construction contrasts with earlier universality results that needed modified weights or high precision.

## Limits

- The extraction notes that each case got a single greedy call on a single model, with no repeated runs, failure rates or other models, and no statement that the weights are public.
- Universality assumes unbounded memory and perfectly reliable answers on all 29 prompt-result pairs, and it does not address how effectively real agents use memory.
- The author reports brittleness: not every large model tried succeeded, prompts had to be terse, and if-then-else conditionals could not be made reliable (the construction uses just if-then), which rules out simulating smaller machines such as U6,4.
- The extraction notes the regex handling is rudimentary, deeper nested substitution would go beyond finite-state power, and the result depends on a 2022-era model.

## See Also
- [[Neural Turing Machine]] — related (external memory with a controller)
- [[Memory Architecture]] — related
- [[Transformer Architecture]] — related
