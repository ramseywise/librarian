---
title: Code Generation Prompting
tags: [prompting, pattern]
summary: Prompt shapes for code — instruction→code, comments→code, signature completion with stop sequences, schema→SQL, explain-code, parseable unit-test prompts and fill-in-the-middle — plus the over-refusal trap of generic safety system prompts; context and verification remain the biggest levers.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--11-applications.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--prompt-library.md
  - data/raw/papers/2026-11-07-chen-2023-teaching-large-language-models-self.md
  - data/raw/papers/2026-11-06-zheng-2024-opencodeinterpreter.md
---

# Code Generation Prompting

| Pattern | Prompt shape | Notes |
|---|---|---|
| Instruction → code | System: language, style, "code only"; user: the task | Specify language and version; ask for code only if you will parse it |
| Comments → code | Docstring or numbered step comments | Models often omit imports and setup — **always run the result** |
| Completion | Signature plus comment; let it continue | Stop on `\ndef` / `\nclass` ([[Stop Sequences and Completion Anatomy]]) |
| Schema → SQL | Table/column definitions, then the question | Include the actual schema; generate fixtures to test against |
| Explain code | Code first, then "explain the above" | A narrow system prompt can make the model refuse adjacent tasks |
| Debug | System sets the reviewer role; user gives code, observed output, expected output | Observed vs expected is the key signal |

**Unit-test prompts:** ask for a fixed number of tests, wrap them in parseable tags
(`[TESTS]…[/TESTS]`), and fix a comment format (`#Test case n:`) above each assert so
tests are individually identifiable ([[Structured Output]]).

## Fill-in-the-middle (FIM)

Give code before and after a gap; the model writes the middle. Editor completion,
docstring generation and type inference all work this way. FIM-trained code models take
dedicated prefix/suffix/middle tokens or a `suffix` API parameter — sending prefix and
suffix as plain chat text only approximates it.

## Over-refusal

A broad safety system prompt ("avoid harmful… or negative content") made a code model
refuse *"how do I kill a process?"*; removing it fixed the answer. Generic safety wording
in a domain prompt costs legitimate answers — scope it to the domain and **test for false
refusals** ([[Evaluating Prompts]]).

## Biggest levers

1. **Context** — relevant files, types, tests.
2. **Verification** — compile, lint, run tests, feed failures back ([[Reflexion]],
   [[Verification Loops]]). Agentic coding is a harness problem.

## Execution Feedback Loops

- **Self-Debug (Chen et al., 2023).** A few-shot loop with no training: generate a program, execute it, have the model explain it or trace it, build a feedback message from the explanation and unit-test results, and repeat for up to 10 turns. Gains were reported on TransCoder, MBPP and Spider (about 12 points for Codex on TransCoder with unit-test and explanation feedback, self-reported); the extraction notes that without execution feedback the gains are small or negative.
- **OpenCodeInterpreter (Zheng et al., 2024).** Training on multi-turn execution-feedback data (Code-Feedback) raised a 33B model from 79.0 (70.4) single-turn to 83.2 (76.4) with execution feedback on average benchmark scores (self-reported). Feedback lowered the scores of two baselines (WizardCoder at 33B and Magicoder-S-DS at 6.7B), and the oracle variant that is shown the reference solution (91.6) is a ceiling and cannot be deployed. This is distillation from a stronger model rather than self-improvement, and one table cell carries a typo.

## See Also
- [[Stop Sequences and Completion Anatomy]] — extends
- [[Reflexion]] — extends
- [[Verification Loops]] — extends
- [[Program-Aided Language Models (PAL)]] — alternative-to
- [[Prompts as Document Completion]] — related
- [[Chain of Code]] — related
- [[PIE Performance-Improving Edits Benchmark]] — instance-of (C++ speed-up edits benchmark)
- [[CodeRL Unit-Test Actor-Critic]] — related (trained, not prompted)
