---
title: "Agent-Native Memory Systems Evaluation"
tags: [memory, comparison]
summary: "A comparison of many agent memory designs on LoCoMo, LongMemEval, DB-Bench and LongBench reports no single winner, retrieval behaving as evidence completion, and raw text beating summaries (self-reported); some authors are affiliated with MemOS, per the extraction, and the paper's text and figure disagree on the DB-Bench leader."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhou-2026-we-ready-agent-native-memory.md
---

# Agent-Native Memory Systems Evaluation

This preprint (June 2026) compares a set of memory systems and two baselines, long context and embedding retrieval, across five workloads and eleven datasets. The systems include MemoChat, Mem0 and Mem0g, MEM1, MemAgent, MemTree, Zep, Cognee, LightMem, SimpleMem, MemOS, MemoryOS, A-MEM and Letta. Benchmarks are LoCoMo, LongMemEval (through MemoryAgentBench), DB-Bench (through LifelongAgentBench) and LongBench, run on several backbones including GPT-5.4 variants. The paper defines a memory system as a four-module tuple covering write, store, query and update steps. Its headline finding is that no architecture dominates; the right structure depends on which bottleneck the workload has.

## Findings

Every result below is the paper's own report (self-reported), with the extraction's setup noted per bullet.

- **Leaders differ by workload.** (Figure 7, default backbone, per-system values read from figure labels) the paper reports Zep leading LongMemEval judge accuracy at 48.0, Cognee leading ROUGE-L F1 at 35.3, and MemOS leading LoCoMo exact match at 11.5. It also reports Zep leading knowledge-update questions (44.4 substring exact match) and Cognee leading temporal reasoning (18.7).
- **Letta is weak on conversation, per the paper.** It reports 0.0 exact match on LoCoMo and 23.0 judge accuracy on LongMemEval (default backbone, single runs). See [[MemGPT / Letta Virtual Context Memory]] for the design itself.
- **Retrieval is evidence completion.** The paper reports SimpleMem with the best Recall@1 (39.0), but A-MEM (69.5 and 85.9) and MemTree (59.7 and 80.5) ahead at Recall@5 and Recall@10 (evidence-recall setup, default backbone). The paper says flat embedding retrieval degrades as the gold evidence sits further from the query.
- **Raw beats compressed.** In a LightMem ablation on LoCoMo, the paper reports that keeping raw user text gives 24.2 exact match and 38.9 F1, a summary gives 8.5 and 15.6, and a compressed form matches raw on LoCoMo (23.6 and 38.6) yet drops LongMemEval substring match from 26.0 to 10.7. It also reports that a deeper MemTree helps access but cannot bring back dropped content.
- **Store broadly, filter late.** The paper reports MemOS with its fast write path scoring 25.5 exact match on LoCoMo against 2.5 for the fine-grained path, though the fine path is slightly better on LongMemEval (22.3 against 20.7).
- **Planning helps, reflection does not add.** The paper reports SimpleMem best with query planning alone (20.7 answer F1) and not with planning plus reflection.
- **Cost follows maintenance scope.** Local update paths are cheap; graph-wide consolidation and whole-memory rewrites cost the most. The paper reports normalised utility of 82.0 costing MemoryOS 28.6 s per query, and Cognee and Zep passing 84 at 116.5 s and 155.1 s. Utility is relative to this system set only.
- **Backbone shifts absolute scores more than ranking.** On LoCoMo across four backbones the paper reports MemOS answer F1 spanning 32.2 to 41.2 (the three further backbones give 41.2, 38.6 and 41.2), and the extraction notes the backbone names are read from a garbled legend.
- **Conservative consolidation is the best default, narrowly.** The paper reports MemoryOS gaining 23.2 to 23.5 F1 with conservative merging, a difference with no variance reported, and delayed flushing losing accuracy (20.6).

## Limits

- Some authors are affiliated with MemOS (per the extraction), one of the evaluated systems. The paper has no limitations section, results are single runs, and the promised future directions do not appear in the text.
- Internal inconsistency noted by the extraction: the text names Long Context (48.20 exact match) and MemoChat (55.40 task success) as the DB-Bench leaders, but the figure labels show Letta at 61.6 on both, the highest value, and the text never discusses it. The figure needs checking against its image.
- Count mismatch: the abstract-level setup says twelve systems, but the paper lists fourteen names (including Mem0g and Letta); the extraction repeats the mismatch and the paper's own count is not resolved here.
- Per-system numbers come from figure labels, and the utility score is a mean of six min-max normalised metrics, so it only ranks this set.
- Differences of a few tenths of a point, such as the consolidation result, carry no variance.

## See Also
- [[Memory Architecture]] — prerequisite-for
- [[Multi-Session Agent Benchmarks]] — prerequisite-for (the benchmarks used here)
- [[Designed Memory vs Raw-Record Search]] — related (raw text beating summaries; the paper's ablation points the same way)
- [[A-Mem Zettelkasten Agentic Memory]] — related (one evaluated system)
- [[Mem0 Extract-and-Update Memory]] — related (one evaluated system)
