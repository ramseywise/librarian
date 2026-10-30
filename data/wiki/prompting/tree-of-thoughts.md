---
title: Tree of Thoughts
tags: [prompting, llm, concept]
summary: Generalizes chain-of-thought into search — a propose prompt generates candidate intermediate steps, a value prompt rates each (sure/maybe/impossible), and a code controller runs BFS/DFS with backtracking; GPT-4 went from 4% (CoT) to 74% on Game of 24.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
---

# Tree of Thoughts

Yao et al. (2023); Long (2023). Where [[Chain of Thought]] commits to one path and
[[Self-Consistency]] samples independent paths, ToT **searches**:

1. **Propose** — a prompt generates several candidate "thoughts" (next intermediate steps).
2. **Value** — a prompt evaluates each candidate (*sure / maybe / impossible* — on Game of
   24: can the remaining numbers still reach 24?).
3. **Search** — BFS or DFS over the tree, backtracking from dead ends.

Result: on Game of 24, GPT-4 solved 4% with CoT and 74% with ToT.

**It is an orchestration pattern more than a prompt.** Both steps are ordinary prompts, but
the controller loop lives in code — the same move as any loop pattern in the harness.

**Cheap single-prompt approximation** (Hulbert, 2023): "Imagine three different experts
are answering this question. All experts write down one step of their thinking, share it
with the group, then go on to the next step. If any expert realises they're wrong, they
leave." Useful for a quick probe; not a real search.

Use it for search problems with dead ends (puzzles, planning). For most tasks a reasoning
model or self-consistency is cheaper ([[Prompting Reasoning Models]]).

## See Also
- [[Chain of Thought]] — extends
- [[Self-Consistency]] — extends
- [[Prompting Technique Selection]] — instance-of
- [[LLM Fundamentals Interview Study Guide]] — prerequisite-for
