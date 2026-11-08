---
title: AIOS
tags: [harness, concept]
summary: "AIOS puts an operating-system kernel beneath existing agent frameworks: agent requests become syscalls on LLM, memory, storage and tool queues, served by a scheduler that can pause and resume generation; the reported gain is up to 2.1x throughput on one GPU (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-mei-2024-aios.md
---

# AIOS

Mei et al. (Rutgers; a COLM 2025 paper, first on arXiv in March 2024) describe a kernel that sits under agent frameworks and handles resources, leaving planning and multi-agent topology to the frameworks. The extraction notes that the paper's own taxonomy puts this scheduling in the kernel, not in orchestration.

## Mechanism

- **Syscalls.** An agent query is split into LLM, memory, storage and tool calls. Each becomes its own thread, which waits until the scheduler lets it run, and joins a queue for its type. FIFO and Round Robin schedulers are evaluated; priority schedulers are said to be derivable but are not tested.
- **Context manager.** It snapshots a half-finished generation so a Round Robin time slice loses no work. A text variant serves closed APIs; a logits variant keeps beam-search state. Against uninterrupted runs both variants scored 1.0 on BLEU and on BERT score (self-reported; Mistral-7B and Llama-3-8B, context switching on versus off).
- **Memory and storage.** Per-agent memory lives in RAM and spills to disk by LRU-K past 80% of the block; storage adds a vector database, versioning (20 versions by default), locks and rollback. Design only, with no evaluation.
- **Tool manager.** It checks parameters before execution and counts instances for tools with parallel-access limits, skipping ahead to a non-conflicting request.
- **Access manager.** Privilege groups map agent IDs to groups, and irreversible operations ask the user. It covers cross-agent data access, not tool authorization in general; no attack test is reported.
- **SDK.** Existing frameworks (ReAct, Reflexion, Autogen 0.2, Open-Interpreter, MetaGPT) are patched at their LLM-call functions, so agent code is unchanged.

## Results (self-reported)

- Throughput up to 2.1x, measured with Reflexion agents on HumanEval using Llama-3.1-8b. One A5000 24GB GPU served a single prompt at once, with up to 250 agents running concurrently under Round Robin. This is the best cell; other frameworks gain less and appear only in unlabelled charts. The abstract says "faster execution" while the body measures throughput.
- Scheduler ablation (ReAct, HumanEval, Llama-3.1-8b, one configuration): overall time 152.1 s without AIOS, 74.2 s FIFO, 77.3 s Round Robin; p90 wait 11.0, 5.0 and 4.2 s.
- Success rates move little, in single runs with GPT-4o-mini at temperature 1.0: ReAct on HumanEval moved from 48.8 to 50.6 and on GAIA from 5.5 to 7.3; Autogen on GAIA from 7.3 to 9.7; Open-Interpreter on MINT from 45.9 to 48.7; several cells did not change.
- Time grows roughly linearly from 250 to 2000 agents on Llama-3.1-8b and Mistral-7b, with the gap to the baseline widening (the counts were reached by duplicating the 164 HumanEval samples; values are read from chart axes).

## Limits

- Authors list as future work semantic scheduling, faster snapshots, shared memory, and safety hardening (jailbreaking, cross-agent memory access, encryption); none is implemented or tested.
- The speedup is tied to baselines that retry after out-of-memory errors; the extraction notes it may shrink against batching servers, which the paper does not compare.
- One GPU, one model serving one prompt at a time, mostly single-agent coding benchmarks, single runs, no variance. Explanations for accuracy gains (prompt enhancement, regex tool-call validation) are not ablated.
- Internal inconsistencies noted by the extraction: the abstract says 2.1x faster execution but the body measures throughput (wall-clock is about 2.0x in the scheduler table); Table 7 says Llama-3-8B while the text says Llama-3.1-8b; the numbering of the two tool-call validation mechanisms is garbled.
- Models are dated (Llama-3.1-8b, Mistral-7b, GPT-4o-mini).

## See Also
- [[Harness Orchestration]] — prerequisite-for
- [[Execution Boundaries and Guardrails]] — related (access manager)
- [[Loop Detection and the Two-Retry Rule]] — related
- [[MemGPT / Letta Virtual Context Memory]] — related (OS metaphor for memory)
