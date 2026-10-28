---
title: Score-Delta Retry Guard
tags: [rag, pattern]
summary: Stop a retrieval retry before the model is called when the new top score is not meaningfully better than the previous one (curr_top ≤ prev_top + ε, ε = 0.05). That saves 1–2 s and one LLM call on dead-end queries, at the cost of a fixed threshold that occasionally skips a small but useful improvement.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/support-agents/invocation-flow.md
  - data/raw/claude-docs/project-g/docs/support-agents/invocation-flow.md
---

# Score-Delta Retry Guard

## The waste it removes

A support agent that retries retrieval when results look weak has a predictable dead end.
For a query with no good match in the knowledge base, the retry returns the same weak
results, and the model is then called only to confirm the same negative answer. That costs
one wasted retrieval and one wasted LLM call, roughly 1–2 s per dead-end query.

## The mechanism

Compare the **top score of the two most recent retrieval calls**. If the latest is not
better than the previous by more than a margin ε, stop retrying:

```python
_SCORE_DELTA_EPSILON = 0.05
if len(kb_calls) >= 2:
    prev, curr = kb_calls[-2]["top_score"], kb_calls[-1]["top_score"]
    if curr <= prev + _SCORE_DELTA_EPSILON:
        inject_stop_message()   # "further retrieval will not help — answer or escalate"
```

The same guard ran in two frameworks:

- **ADK:** a named `before_model` callback (`inject_retry_stop`), one of four small
  functions behind a 7-line dispatcher. It replaced a 70-line waterfall, and splitting it
  made each check testable and early-returnable on its own.
- **LangGraph CRAG:** an edge condition in the decision node,
  `attempts >= 2 AND curr_top ≤ prev_top + ε → end`, ordered after the max-retries check.

**Capture the previous score before overwriting passages.** The fetch node records
`prev_top_score` *before* it replaces `state.passages`, so the decision node always has
two adjacent scores to compare. Capture it after the overwrite and the guard compares a
score with itself.

## Tradeoff

The threshold is fixed. A retry that would have improved the top score by 0.04 is declared
futile even when it would have produced a better answer. The guard was monitored through
traces, not tuned per query. Scores are also only comparable within one retrieval mode
(see [[GCP Vertex AI Search vs AWS Bedrock KB]]), so ε belongs to the mode it
was tuned on.

## See Also
- [[CRAG Retry Logic]] — extends (an early-exit edge for the retry loop)
- [[Safeguards Architecture — Five Protection Layers]] — instance-of (listed as the "skip second LLM" guard)
- [[Loop Detection and the Two-Retry Rule]] — related (the same "more attempts add no information" argument, measured by score instead of count)
- [[Context Compaction]] — related (passage pruning runs in the same callback chain)
