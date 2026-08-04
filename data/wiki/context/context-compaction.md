---
title: Context Compaction
tags: [llm, agents, concept]
summary: Transforming a large interaction history into a smaller continuation state — the technique that separates an agent that dies at the window limit from one that runs for hours.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--04-compression-compaction.md
---

# Context Compaction

The **Compress** lever of [[Context Engineering]]. Near the context limit, summarize what
has happened, reinitialize the window with the summary, and continue.

> It is the difference between an agent that dies at the window limit and one that runs for
> hours.

## Compression vs Compaction

Different scopes, often conflated:

- **Compression** — reducing an individual artifact *before* it enters the window (a
  query-conditional document summary, a truncated tool result). Per-item, pre-injection.
- **Compaction** — reducing the accumulated *history* into a continuation state. Whole
  window, mid-session.

**You need both.** Compression bounds what each item costs; compaction bounds what the
session costs.

## The Pipeline

```
Raw interaction history
        ↓
Prune irrelevant content          <- abandoned branches, superseded attempts
        ↓
Replace bulky tool outputs        <- keep the conclusion, drop the payload
        ↓
Extract structured task state     <- files touched, decisions, open TODOs
        ↓
Summarize older reasoning         <- compress the middle, lossy but bounded
        ↓
Preserve recent messages verbatim <- the last N turns stay untouched
        ↓
Compact continuation context
```

**The final step matters most.** Recent turns stay verbatim because the agent's immediate
working state lives there — half-finished edits, the error currently being debugged.
*Summarizing the last three turns is how a compaction loses the thread.*

## Retention Priority

What survives, in order:

1. **Architectural decisions — do not summarize.** "We chose X over Y because Z" must
   survive verbatim. Lose the reasoning and the agent re-litigates a settled decision, or
   silently contradicts it.
2. **Modified files and critical changes.** The diff-so-far is *state*, not history.
3. **Verification status** — which tests ran, what happened.
4. **Unresolved TODOs and rollback notes.**
5. **Tool output — deletable.** Retain the pass/fail conclusion, discard the payload.

**The asymmetry between 1 and 5 is the core insight.** A 40k-token test output compresses
to `"17 passed, 2 failed: test_auth_retry, test_token_refresh"` with essentially no loss. A
one-sentence architectural rationale cannot be compressed at all without losing what makes
it useful.

## Component Techniques

| Technique | What it does | Loss profile |
|---|---|---|
| **Sliding window** | Keep the last N turns, drop older | Total loss of dropped content |
| **Summarization** | LLM-compress a span into prose | Lossy, unpredictable — depends on the summarizer |
| **Pruning** | Delete by rule (dead branches, superseded attempts) | Total but targeted; safest when rule-driven |
| **State extraction** | Pull structured facts into a compact record | Lossless for what's extracted, total for what isn't |
| **Tool-result clearing** | Replace raw output with its conclusion | Near-lossless for verbose output |

**Tool-result clearing is the highest-value / lowest-risk.** Tool output is usually the
largest and least reusable content in an agent's window. *Clear it first, before reaching
for lossy summarization.*

**State extraction is what makes compaction safe.** If task state lives in a structured
record rather than implicitly in the prose of the conversation, summarizing the prose costs
little. **Agents that write their state down survive compaction; agents that keep it in the
transcript do not.**

## Trigger Points

- Approaching the window limit (~80% is a common threshold)
- **Phase boundaries** — a completed plan step, a finished skill invocation, a focus switch
- Before spawning subagents that will re-derive context
- After large reads that won't be needed again

**Phase boundaries are the better trigger.** Compacting at a natural seam produces a clean
summary; compacting mid-edit at 95% occupancy forces a summary of an incoherent state.

## API-Level Support

OpenAI's Responses API exposes compaction directly: after appending output items, drop
items preceding the most recent compaction item. The general pattern — **the compaction
item is a checkpoint, and everything before a checkpoint is discardable.**

## Crash Recovery

Same solution, related failure mode. For long-running tasks write progress **to disk**, not
just to context — then a crash, overflow, or deliberate restart resumes from the last
checkpoint instead of restarting the task.

> Past roughly thirty minutes of agent runtime, crash recovery is mandatory rather than
> optional. The probability of *some* interruption over a long run approaches one.

Same mechanism as structured note-taking — see [[Memory as Context]]. **State on disk
survives everything that happens to a context window.**

## Prompt Caching Interaction

Compaction **invalidates the cache from the compaction point forward** — you have rewritten
the prefix. Worth it, but it means:

- Don't compact more often than necessary; each compaction pays a full re-prefill
- Structure the post-compaction window so stable parts (system prompt, tools) still lead,
  preserving a cacheable prefix
- Compacting at phase boundaries amortizes the cost across the phase that follows

## See Also
- [[Long-Horizon Execution]] <!-- auto-linked -->
- [[Context Anatomy]] <!-- auto-linked -->
- [[Context Engineering]] — part-of
- [[Context Failure Modes]] — mitigates
- [[Memory as Context]] — extends
- [[Context Retrieval Strategies]] — complements
