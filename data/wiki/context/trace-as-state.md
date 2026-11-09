---
title: "Trace as State"
tags: [context, pattern]
summary: "Trace as State re-runs a long-context task and places the first-pass reasoning traces before the context, not after it; it beat appending them in 26 of 27 cells, with GraphWalks Parents EM 29.2 to 81.8 for one model (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zou-2026-trace-as-state.md
---

# Trace as State

A two-pass inference recipe: run the task once (five repeats), keep the reasoning traces, then run it again with the traces placed before the long context, so the order is traces, context, question. The "Trace Append" control puts the same traces after the context. The question stays last in both.

## Results (self-reported)

Setup: three preview-build models; tasks GraphWalks at 256K, MRCRv2 with 8 needles (256K and 512K) and NUB-1M; five repeats; all five traces kept, each truncated at 50,000 characters.
- Trace as State came out ahead of Trace Append in 26 of the 27 model, task and metric cells; paired intervals lie fully above zero in 20 of 24 reported cells (self-reported).
- GraphWalks Parents exact match for one model was 29.2 on the first pass, 43.0 with Append and 81.8 with Trace as State; 66.4, 83.2, 100.0 for a second; 60.8, 71.0, 96.4 for a third (self-reported). Gains elsewhere were smaller: MRCRv2 256K 53.8, 66.6, 76.2 for the first model.
- Controls on that Parents cell: Random Trace (traces taken from other problems) scored 14.2, under the plain first pass; Question First 53.0; a repeated prompt 50.0; Answer Feedback 45.4; Trace Only with no context 43.8 (self-reported). The extraction reads these as showing that traces must come from the same problem and that reasoning text is a stronger state than answers alone.
- More traces generally helped between one and five.

## Costs and limits

- Total tokens roughly double, and putting state before the context can reduce KV-cache reuse in multi-round agent settings (authors concede this). The authors also report more sandbox-escape attempts in separate agentic coding tests, with no number given.
- Requires raw reasoning traces; three models and three task families, no multi-round agent tasks, single-pass baselines not compute-matched, and NUB-1M has only 20 problems and is judged by one of the evaluated models.
- The memory-bit theorem is a worst-case construction that the paper says does not model real tasks. Model versions are 2026 previews.

## See Also
- [[Reasoning State Pass-Back]] — related (reasoning text as carried state)
- [[Why Context Is Finite]] — prerequisite-for
- [[Cache-Stable Context Layout]] — related (the KV-cache cost of placing state first)
- [[ReContext Attention Evidence Replay]] — related
