---
title: Code Generation Prompting
tags: [prompting, pattern]
summary: Prompt shapes for code — instruction→code, comments→code, signature completion with stop sequences, schema→SQL, explain-code, parseable unit-test prompts and fill-in-the-middle — plus the over-refusal trap of generic safety system prompts; context and verification remain the biggest levers.
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--11-applications.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--prompt-library.md
  - data/raw/papers/2026-11-07-chen-2023-teaching-large-language-models-self.md
  - data/raw/papers/2026-11-06-zheng-2024-opencodeinterpreter.md
  - data/raw/papers/2026-11-08-fan-2023-large-language-models-software-engineering.md
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
- **OpenCodeInterpreter (Zheng et al., 2024).** Training on multi-turn execution-feedback data (Code-Feedback) raised a 33B model from 79.0 (70.4) single-turn to 83.2 (76.4) with execution feedback on average benchmark scores (self-reported). Feedback lowered the scores of two baselines (WizardCoder at 33B and Magicoder-S-DS at 6.7B), and the oracle variant that is shown the reference solution (91.6) is a ceiling and cannot be deployed. The extraction notes that the training data comes from GPT-3.5 and GPT-4, so part of the gain is distillation from a stronger model and should not be read as self-improvement, and that one Table 2 cell (66.7 against 76.6, plus score above base) is probably a typo in the paper.

## What a 2023 survey reports

Fan et al.'s survey of LLMs in software engineering (a mid-2023 snapshot; figures reported from other work, not re-run) collects evidence relevant to prompting code models:

- Prompt engineering raised Copilot and Codex success rates from about one in four to about three in four on HumanEval and LeetCode, and in one report fine-tuning beat prompt engineering for GPT-4 code generation.
- Over 60% of tasks had no two equal test outputs across repeated ChatGPT code-generation requests, and the survey finds that just 21.1% of LLM code-generation papers treat this as a threat. Few papers report settings such as temperature; the authors advise reporting them conspicuously and using inferential statistics over repeated runs.
- With bugs in the surrounding context, HumanEval completion scores fell by over half.
- Test-based reranking is one of the survey's hybrid approaches; see [[CodeT Generated-Test Reranking]].

## Code as the output format

A different use of code is to write a non-code target (a graph) as Python and prompt a code model to complete it; see [[CoCoGen Code Prompts for Structured Commonsense]].

## See Also
- [[Stop Sequences and Completion Anatomy]] — extends
- [[Reflexion]] — extends
- [[Verification Loops]] — extends
- [[Program-Aided Language Models (PAL)]] — alternative-to
- [[Prompts as Document Completion]] — related
- [[Chain of Code]] — related
- [[PIE Performance-Improving Edits Benchmark]] — instance-of (C++ speed-up edits benchmark)
- [[CodeRL Unit-Test Actor-Critic]] — related (trained, not prompted)
- [[DS-1000]] — related (execution-based code benchmark)
- [[SPoC Pseudocode-to-Code]] — related
- [[CodeT Generated-Test Reranking]] — related (generated tests as a selection signal)
- [[CoCoGen Code Prompts for Structured Commonsense]] — related
- [[LIBRO LLM Bug-Reproducing Tests]] — extends
