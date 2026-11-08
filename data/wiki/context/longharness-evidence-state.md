---
title: LongHarness Evidence State
tags: [context, concept]
summary: LongHarness keeps a source-linked evidence bank and a conclusion state with explicit open gaps outside the interaction history, and scored well above direct baselines and shell-based harnesses on 100M-token corpus QA, though its ablations show most of the gain comes from the shared scaffold (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-huang-2026-longharness.md
---

# LongHarness Evidence State

Huang et al. (2026, Shanghai AI Laboratory) target question answering over corpora of up to about 100M tokens. The harness separates two persistent states from the running history.

- **EvidenceBank.** Facts with links back to their sources. Superseded or retracted evidence is revised explicitly instead of being appended next to the old value.
- **Conclusion State.** Current conclusions with unresolved gaps listed, which steers what the agent explores next.

The authors argue that this curbs unbounded exploration and drift of evidence, where a corrected value is seen but an earlier one still reaches the answer. Their case study is one randomly chosen Codex failure that made 103 consecutive backward reads and then kept the stale value.

## Results (self-reported)

GLM-5.3-Flash on OfficeQA Pro, scored by exact match, with one run per setting in the main table. The direct baselines receive BM25 passages inside a 256K window. Budgets differ by harness. LongHarness is allowed 200 steps, 60 searches and 1M tokens read in total, while Codex and Claude Code are allowed 200 turns and 200 tool calls.
- V1 (133 questions): 15.8 direct and 60.2 LongHarness, best other harness 48.1 (Claude Code). V2 (90 questions): 4.4 direct, 61.1 LongHarness, best other 42.2 (Codex).
- Qwen3.8-Flash: 61.7 against 53.4 on V1, and 51.1 against 50.0 on V2.
- Three runs with GLM: V1 59.90 (std 0.43) against 49.37, V2 59.63 (std 1.28) against 41.11 (std 4.00).
- Median turn counts, V1 then V2: LongHarness 22 and 30, Claude Code 21 and 116, Codex 19 and 43. Codex ran out of turns on 3.8% of V1 questions and 21.1% of V2 questions. The paper offers its explanation only as plausible.
- Ablation, V1 then V2, against 60.2 and 61.1 for the full system: history only 55.6 and 53.3, no coevolution 54.9 and 51.7, append-only evidence 56.4 and 51.1, free-text notes 53.4 and 53.3. The extraction notes that every ablated variant still beats the direct baselines and sits within about 8 points of the other harnesses on V1. On that reading, much of the gain comes from the scaffold all of them share (search, bounded reads, computation).

## Limits

- The paper has no limitations section. Its main table is a single run, and only the GLM backbone has repeats.
- Baselines are not matched on tools: LongHarness has purpose-built search and read tools, the others use a shell. No cost or latency figures, only turn counts.
- An LLM (GPT-5.6-Luna) audits failures and also grades AA-LCR. The direct-model AA-LCR figures were taken from an outside leaderboard, not rerun here.
- On Qwen the V2 margin is only 1.1 points. Only QA tasks are tested, with no compaction, reset or handoff experiment. The extraction notes that the columns of its Table 3 are jumbled and that it could not verify the model names.

## See Also
- [[Context Compaction]] — alternative-to (explicit revisable state against summaries)
- [[PRO-LONG Programmatic Memory]] — related
- [[Coding Agents as Long-Context Processors]] — related (the shell-based baseline family)
- [[Context Retrieval Strategies]] — related
