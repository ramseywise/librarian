---
title: Prompting Technique Selection
tags: [prompting, llm, reference]
summary: Which named prompting technique to reach for by problem shape — zero-shot first, few-shot for non-obvious format, CoT and self-consistency for reasoning, ToT for search, PAL for exact computation, ReAct for fresh information, Reflexion when a checker exists, chaining for separable stages.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--README.md
---

# Prompting Technique Selection

Techniques group by what they buy: **examples** teach the task, **reasoning** buys compute,
**search** explores alternatives, **tools** reach outside the model. Each one shapes the
document the model completes ([[Prompts as Document Completion]]).

| Problem | Reach for | Cost |
|---|---|---|
| Task is clear and common | Zero-shot | — |
| Format, style or labels non-obvious | [[Few-Shot Prompting]] | Longer prompt, anchoring |
| Multi-step arithmetic, logic, planning | [[Chain of Thought]] | More output tokens |
| Answers vary run to run on reasoning tasks | [[Self-Consistency]] | N× calls |
| Model lacks background facts | Generated knowledge, or retrieval | Extra call |
| Search with dead ends (puzzles, planning) | [[Tree of Thoughts]] | Many calls + controller |
| Exact computation | [[Program-Aided Language Models (PAL)]] | Sandbox |
| Fresh or private information | [[ReAct Pattern]] / tool use | Loop + tools |
| Can verify and retry | [[Reflexion]] | Retry budget |
| Long task with separable stages | [[Prompt Chaining]] | Orchestration code |

**Reasoning models change the defaults** — much of the reasoning column is built in; see
[[Prompting Reasoning Models]] before adding CoT scaffolding.

## Zero-shot

Instruction only. Works because instruction tuning (FLAN: 1.8k tasks phrased as
instructions) and RLHF generalize to unseen tasks. Start here; add examples only when
zero-shot fails in a way you can name.

## Smaller techniques worth knowing by name

- **Generated knowledge** (Liu et al., 2022) — two calls: generate relevant facts, then
  answer with them in the prompt. Flips a confident wrong answer by putting facts *before*
  reasoning; it cannot add knowledge the model lacks (that needs retrieval).
- **Plan-and-solve** — front-load "devise a plan, then carry it out step by step." Helps
  where zero-shot CoT skips steps; uses no tools but composes with ReAct.
- **Auto-CoT** — cluster questions, take a representative per cluster, generate its CoT
  with zero-shot CoT; filter with simple heuristics (question ≤ 60 tokens, ≤ 5 steps).
  Diversity matters because demos can share the same mistakes.
- **Active-Prompt** — pick the *most uncertain* questions (disagreement across k samples)
  for humans to annotate with CoT: active learning for few-shot selection.
- **ART** — demonstrations of reasoning plus tool use from a task library; pause
  generation at each tool call, splice in output, resume. Now mostly what native tool
  calling does.
- **Directional stimulus prompting** — a small tuned policy model writes a hint (e.g.
  keywords) into the big model's prompt; the idea recurs in routing and query rewriting.
- **Pause tokens** — fine-tune on a meaningless token and insert ~10 after the question:
  extra positions buy compute without words.
- **Multimodal CoT** — rationale from text+image first, answer second; a 1B model beat
  GPT-3.5 on ScienceQA.

## Two CoT rules that are easy to get wrong

- **Reasoning must come first.** "Answer, then explain" gets rationalization.
- **Put reasoning in a parseable place** (a thinking block, or `# Analysis` before
  `# Conclusion`) so the app can strip it.

## See Also
- [[Prompt Engineering]] — instance-of
- [[Chain of Thought]] — extends
- [[Self-Consistency]] — extends
- [[Tree of Thoughts]] — extends
- [[Program-Aided Language Models (PAL)]] — extends
- [[Reflexion]] — extends
- [[ReAct Pattern]] — extends
- [[Four Prompt Criteria]] — prerequisite-for
