---
title: Context Window Budgeting
tags: [context, context-management, llm, concept]
summary: "Deciding the token split across instructions, evidence and working space before the window fills — reserve output first, cap every growing component, value each chunk by its marginal information, and set the budget by ablation against the effective (not advertised) window."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--03-budgeting-the-window.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--02-context-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--README.md
---

# Context Window Budgeting

Every component in the window competes for one finite budget ([[Why Context Is Finite]]).
Budgeting means deciding the split *before* the window fills, so the important pieces are
never the ones squeezed out. It sits under the **Compress** lever of [[Context Engineering]].

## The Window as an Economy

| Spend | Buys | Over-spent | Under-spent |
|---|---|---|---|
| **Instructions** (system prompt, rules, examples) | Reliable behaviour | Diluted attention; rules contradict | Model guesses at the task |
| **Evidence** (retrieved docs, tool results, memory) | Grounding | Distraction, context rot | Hallucination |
| **Working space** (history, scratch reasoning, output) | Room to think and answer | Truncated output, lost recent turns | No room for reasoning |

**Investments vs expenses.** A 60-token rule that prevents a class of errors on every call
is an *investment* — it belongs in the stable prefix. A 3,000-token tool result consulted
once is an *expense* — clear it once used ([[Context Compaction]]).

## The Formal View

The context-engineering survey writes context as an assembly of typed components,
`C = A(c_instr, c_know, c_tools, c_mem, c_state, c_query)`, and context engineering as
optimising the assembly function `A` for expected reward subject to `|C| ≤ L_max`.
**Context engineering is designing `A`, not writing any single component.** Two
consequences:

1. **The constraint binds before `L_max`.** Quality falls long before the hard limit, so
   budget against the *effective* window, not the advertised one.
2. **Value is marginal, not absolute.** A chunk is worth what it adds about the answer
   *given everything already in the window* (`I(Y*; c | C_rest)`). A second document
   restating the first is "relevant" and worth almost nothing. **Redundancy is the most
   common way budget is wasted.**

## Allocation Starting Points

Course heuristics, not measured optima — e.g. a pyramid of ~20% core instructions, ~30%
critical context and examples, ~30% recent history, ~15% auxiliary, ~5% reserve. The
numbers matter less than two rules:

- **Reserve the output first.** `max_tokens` plus any thinking budget comes off the top.
  A window filled to the limit with input leaves no room to answer.
- **Give every growing component a ceiling.** History, tool results and retrieved chunks
  grow without bound unless capped; the cap is what triggers compaction.

## Spending Less per Component

- **System prompt — progressive reduction.** Write the full version, then delete elements
  one at a time while re-running the eval set; remove anything whose deletion moves no
  score. Task guidance beats persona biography (a 15-token directive outperforms a 90-token
  résumé); ask for three output sections, not seven.
- **Examples.** Few-shot returns diminish fast — 0→1 is the biggest step. Two to five
  usually capture most of the gain; pick diverse examples and boundary near-misses, cover
  every output class (including "none"/"refuse"), and select by similarity to the query
  when traffic is heterogeneous. See [[Few-Shot Prompting]].
- **History.** Windowing (recency), summarisation (gist), key-value state (decisions).
  Production systems combine all three: structured state for decisions, a rolling summary
  for narrative, a short raw window for recent turns.
- **Evidence.** Rerank top-20 to the best 5; return identifiers before contents; truncate
  or paginate at the *tool boundary*, not after results land.

## Budgeting with a Cache

Prompt caching changes the **cost** side without changing the **attention** side. A
cached 20k-token prefix is cheap and fast but still occupies attention. Order stable
before dynamic for cost ([[Cache-Stable Context Layout]]); remember that a cache hit does
not make bloat harmless for quality.

## Measuring Token Efficiency

1. **Log tokens per component** on every call (system, tools, retrieved, memory, history,
   input, output).
2. **Ablate** — drop one component, re-run the eval set, record Δ quality and Δ tokens.
3. **Track quality per 1k tokens** alongside absolute quality.
4. **Find the cliff edge** — plot score against total context length; the knee is the
   effective budget for that model and task.

The ablation and sweep protocols are in [[Evaluating Context]]; measuring the fixed
overhead a harness adds is in [[Measuring Fixed Context Overhead]].

## See Also
- [[Why Context Is Finite]] — prerequisite-for
- [[Context Engineering]] — extends
- [[Evaluating Context]] — prerequisite-for (ablation sets the budget by evidence)
- [[Cache-Stable Context Layout]] — extends (the cost side of the budget)
- [[Context Compaction]] — prerequisite-for (ceilings are what trigger compaction)
- [[Measuring Fixed Context Overhead]] — extends
- [[Context-Aware Compression]] — extends
- [[Multi-Agent Context]] — extends
