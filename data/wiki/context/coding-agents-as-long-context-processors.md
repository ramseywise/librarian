---
title: Coding Agents as Long-Context Processors
tags: [context, concept]
summary: Cao et al. (2026) treat a huge text corpus as a folder of files and let an off-the-shelf coding agent (Codex with GPT-5) read it with shell search and Python; it beat the best published result on four of five long-context benchmarks, while adding a retriever did not reliably help.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-cao-2026-coding-agents-effective-long-context.md
---

# Coding Agents as Long-Context Processors

The setup puts the corpus on disk, one file per document in a directory tree, and gives a coding agent only the path and the question. The agent uses ripgrep, sed line-range reads and Python scripts of its own devising. No retriever is supplied in the main configuration.

## Results (self-reported)

Codex v0.46.0 with GPT-5 on 200 randomly drawn examples per benchmark. Baselines were rerun on that same subset. The best-published figures come from full test sets and serve only as a reference point.

| Benchmark | Codex, no retriever | Best published |
|---|---|---|
| BrowseComp-Plus | 88.50 | 80.00 |
| Oolong-Synthetic | 71.75 | 64.38 |
| Oolong-Real | 33.73 | 24.09 |
| LongBench-v2 | 61.50 | 63.30 |
| Natural Questions | 56.00 | 50.90 |

- Standard RAG over the same corpora scored lower on all five (for example 65.00 on BrowseComp-Plus and 13.38 on Oolong-Real). A ReAct agent with retrieve and get-document tools sat in between.
- Full-context GPT-5 over windows of 200K tokens scored 59.22 on Oolong-Synthetic and 22.45 on Oolong-Real. On two benchmarks it saw a 100K sample, and there the authors attribute the unexpectedly high scores (20.0 and 27.0) to probable contamination.
- Adding a retriever (Gemini embeddings or BM25) did not reliably help and often lowered scores (BrowseComp-Plus 88.50 without, 84.00 and 78.50 with). The authors hypothesise that the retriever becomes the default path and displaces the agent's own file exploration; native search commands per run fell from 14.92 to 8.33 to 9.84. They call the mechanism an open question.
- Layout matters: on a 100-example BrowseComp-Plus subset a folder tree gave 89.0 against 83.0 for a single JSON file, with sed use up from 0.61 to 4.48 reads per run.
- Strategy varied by task without instruction: iterative query refinement on multi-hop search, scripts that count and aggregate on Oolong, mostly direct reading on LongBench.
- Per-query cost for Codex without a retriever ran from $0.111 to $0.703, above RAG ($0.006 to $0.111) and, on the Oolong sets, below full-context GPT-5 ($0.770 and $1.421 against $0.419 and $0.194).

The authors credit native tool skill and familiarity with file systems, inferred from ablations and traces.

## Limits

- Only 200 examples per benchmark, no intervals, one main agent and model. Claude Code ran on two benchmarks only. The file-layout test used 100 examples of one benchmark.
- BrowseComp-Plus is a closed world that guarantees the gold documents exist. LongBench shows no gain. The retriever comparison is confounded by how it is prompted.
- The authors concede that coding agents are tuned for programming work, not for reasoning over long text.

## See Also
- [[Context Retrieval Strategies]] — prerequisite-for
- [[Why Context Is Finite]] — related
- [[PRO-LONG Programmatic Memory]] — related (same read-with-code idea over a log)
- [[Progressive Disclosure and Skill Packs at Library Scale]] — related (navigation versus retrieval)
- [[Context Failure Modes]] — related
