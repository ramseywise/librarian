---
title: Agent Retry Taxonomy
tags: [llm, agents, infra, reference]
summary: "Not all failures are retryable — a per-failure-mode response table, retry at both call and node level, and the move that makes a retry a re-plan: feed the error back as context — plus the layered failure/recovery/termination taxonomy with data-set ceilings."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--05-verification-loops.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--05-verification-loops.md
---

# Agent Retry Taxonomy

**Not all failures are retryable.** Treating them uniformly is how a rate limit and a model
refusal get the same three attempts.

## The Table

| Failure | Response |
|---|---|
| **Transient** (network, rate limit) | Retry with exponential backoff (2×, jitter ±20%), max 3 |
| **Tool error** | Retry once, then escalate |
| **Model refusal** | **Never retry** — it will refuse again |
| **Schema violation** | Return the validation error; retry once with it in context |
| **Context exhaustion** | Compact or reset, then resume — see [[Long-Horizon Execution]] |
| **Fatal** | Stop; surface the error |

Two budget rules:

- **Retry budget is per-invocation, not per-tool** — otherwise five tools with three retries
  each become **fifteen attempts**.
- **Circuit-break after 5 consecutive failures** with a 60s cooldown, then fail fast.

> **Degrade loudly.** A partial result carries a `degraded: true` flag. **Silent degradation
> is worse than failure because it looks like success.**

## Retry at Two Levels

A single retry tier is too coarse for a multi-step workflow. Retry at **both the individual
LLM call and the logical node** — the whole step in the agent's plan:

- **Call-level** absorbs transient noise: a timeout, a rate limit, a malformed response.
  *Nothing about the plan was wrong.*
- **Node-level** re-runs the step. Use it when **the call succeeded but the step didn't
  achieve its purpose.**

**Retrying the wrong level wastes the attempt.** Re-issuing a call cannot fix a step whose
*approach* was wrong; re-running a whole node to recover from a rate limit **pays again for
work that already succeeded**.

## Feed the Error Back as Context

The move that makes retries more than repetition:

> **Give the agent the error, not just another attempt.**

An identical retry re-runs the reasoning that just failed and **tends to fail identically**.
Pass the failure back in — the database error message, the generated query, and the original
context all return to the model, which then produces a *corrected* query rather than the
same one. Cap at 3 attempts, after which the tool **reports failure honestly**.

This generalizes the schema-violation row above to every retryable failure, and **it is what
makes a retry a re-plan**.

It also explains why the two-retry rule holds: **once the error is already in context,
further attempts add no new information**, so a third failure genuinely indicates a bad spec
rather than bad luck. See [[Loop Detection and the Two-Retry Rule]]. Writing the error so
it's actionable — what broke, why the rule exists, how to fix it — is
[[Agent-Oriented Error Messages]].

## Failure, Recovery, and Termination

The table above is per failure *mode*; a production harness also needs the failures sorted
by *layer*, because each layer has different detection and different recovery (taxonomy
from Li, *AI Agents in Depth*, ch. 5, distilled from production harness source):

| Layer | Examples |
|---|---|
| **API** | 429s, overload, timeouts, dropped connections, output truncated at the token limit |
| **Tool** | Hallucinated tool names, malformed arguments, exceptions, the same error recurring |
| **Context** | Window overflow, failed compaction, a tool call missing its paired result |
| **Control flow** | No-progress loops and **death spirals** — error handling that calls the LLM, fails, and cascades |

### Detect: classify, then count

- Ask whether a retry *could* help before retrying.
- Fingerprint `hash(tool, args)`; a repeated fingerprint is a no-progress loop.
- Keep a **separate failure counter per recovery path**, so one path's ceiling isn't masked
  by another's successes.
- Watch for failures that never raise: **silent stalls** (a stream stays open with no data —
  SDK timeouts usually cover only connection setup, so add an idle watchdog) and **broken
  trajectories** (an unpaired tool call — patch with a placeholder in production, but
  *refuse* in a training-data collection mode, where synthetic placeholders pollute the data).

### Recover: escalate through increasingly visible stages

1. **Silent retry** with backoff and jitter, honouring `retry-after`. Retry the main loop;
   *drop* failed background calls (title generation and the like) so they don't amplify into
   quota contention.
2. **Degrade and continue.** On truncation, raise the output cap, then ask the model to
   continue from the break. On persistent overload, fall back to another model — stripping
   provider-specific blocks from the history first.
3. **Surface to the user**, with what was already tried.

Tool-layer errors **never end the session**: they return as structured tool results, and
malformed arguments are repaired programmatically. Treat the whole recovery loop as the
unit — **withhold intermediate errors** from users and event subscribers until recovery has
definitely failed.

### Terminate: every recovery path needs a ceiling, set from data

Claude Code's compaction circuit breaker trips after **3** consecutive failures. Before it
existed, one session failed more than **3,000** times in a row, futile retries cost about
**250,000 API calls a day**, and over **1,000 sessions** saw failure streaks of 50+. For
death spirals, disable model-invoking side effects on the error path (the classic case: a
stop hook that calls the LLM to write a commit message after a context overflow) and add a
recursion-depth counter. Above all of it sit max turns, a session budget, and escalation to a
human.

## See Also
- [[Agent Deployment Anti-Patterns]] <!-- auto-linked -->
- [[Verification Loops]] — related
- [[Loop Detection and the Two-Retry Rule]] — extends
- [[Execution Boundaries and Guardrails]] — related
- [[Harness Engineering]] — related (part of)
- [[Loop Termination Design]] — related (error type decides strategy change; the cap decides the ceiling)
- [[Agent-Oriented Error Messages]] — related
- [[Three-Layer Termination Check]] — related (success-side termination)
- [[Text-to-SQL as a Retrieval Strategy]] — instance-of (bounded error-as-context retry)
- [[Python Concurrency Models]] — prerequisite-for (asyncio retry with backoff and jitter, timeouts, Semaphore)
- [[Python Closures and Decorators]] — related (the retry decorator-factory shape)
- [[TypeScript Async Patterns]] — related (retry with backoff, timeouts and AbortSignal in TS)
