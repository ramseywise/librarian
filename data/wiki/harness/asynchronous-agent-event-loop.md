---
title: Asynchronous Agent Event Loop
tags: [llm, agents, infra, pattern]
summary: "A resident agent drains a queue of structured events and consumes them only at safe points — cancel, queue, or answer in parallel — with placeholder results to keep tool calls paired, numbered batches so none are ignored, and async tool interfaces that name the initiation, not the completion."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--07-orchestration.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--03-tool-design.md
---

# Asynchronous Agent Event Loop

Models are trained on a synchronous assumption: a tool call is immediately followed by its
result, and a user message arrives only when the agent is idle. A **resident** agent breaks
both — user messages, tool results, timers, webhooks, and messages from other agents arrive
at unpredictable times. The model (Li, *AI Agents in Depth*, ch. 4) is an **event loop**.

## The Loop and Its Safe Points

Each iteration drains a batch of events from the queue, appends them to the trajectory,
calls the LLM once, and runs the tools it chose. **Events are consumed only at safe points**
— the end of a reasoning stretch or a tool return, never mid-step. Cancellation is checked
at safe points too (the same discipline as Go's `ctx.Done()`).

**Model each input as a structured event:** source (who), channel (how), content (what,
including urgency), context (which thread or task). This keeps a *user command* distinct
from a *tool result that contains a command* — the prompt-injection case.

## Three Strategies

They differ only in how they treat the safe point:

| Strategy | For | Mechanics |
|---|---|---|
| **Cancel** — force a safe point now | User interrupts, supervisor orders, urgent alerts | Abort the stream or tool, drain the queue, append everything, re-invoke |
| **Queue** — wait for the next safe point | Routine input, tool results, timers | Append as a batch when the step finishes; a correction ("only last month") arrives with the results it modifies, saving a round trip |
| **Parallel** — don't wait | Independent cheap queries | Answer in a side session; append the exchange to the main trajectory, marked parallel |

Hard-coded routing misses semantics; a **small classifier model as the event router** picks
the strategy.

## Keeping a Synchronous Model Sane

1. Write the assistant message, including any tool call, to the trajectory as soon as it is
   produced.
2. Write the tool result only when the tool completes.
3. If an interrupt lands mid-tool, insert a **placeholder result** ("still running in the
   background; handle the new event first") so every call stays paired; deliver the real
   result later as a new event.
4. If an interrupt lands mid-thought, discard the partial thinking.
5. Queue non-urgent events and append them in a batch.

Two failure modes to design around: **placeholders invite hallucinated results** (interrupt
only when genuinely urgent), and **in a batch the model tends to answer only the last
event** — number them (`[Unprocessed event 2/4]`) and close with a summary line ("4 events:
1 tool result, 2 user messages, 1 reminder; address all of them").

**Polling is the fallback, not the design.** Timers and heartbeats make an agent *look*
proactive, but a one-time code arriving during a live call can't wait for the next tick.
Real proactivity needs a push channel into the queue. (MCP is request–response; a server
notification does not wake an idle agent, so event-driven behaviour needs its own channel.)

## Asynchronous Tool Interfaces

Put the asynchrony **in the tool interface** rather than fighting the model:

- **Name the initiation, not the completion.** `initiate_phone_call` returns a task ID at
  once; `phone_call_connected` / `phone_call_ended` arrive later as events. A tool named
  `phone_call` implies the call is over when it returns.
- **Say so in the description:** "Returns a task ID immediately; a separate event arrives
  when the call ends."
- **Give the task ID verbs:** `get_status(task_id)`, `cancel(task_id)`.
- **Event-trigger tools need filters** — timers, shell monitors (wake on new output or a
  keyword), channel connectors — with precise trigger conditions and payloads rich enough
  that the agent needs no extra queries on waking.

Collaboration tools reduce to `spawn`/`cancel`, `send_message`, `list_agents`, each
in one of four modes — **sync, async (task ID + later event), streaming, multi-turn**. A
30-minute research job should never be a sync call.

## See Also
- [[Harness Orchestration]] — extends (orchestration for resident, event-driven agents)
- [[Tool Design as Harness Surface]] — extends (asynchronous tool interfaces)
- [[Duplex Voice Breaks Discrete-Turn Assumptions]] — related (the same broken turn assumption in voice)
- [[Prompt Injection]] — related (structured events separate commands from data)
- [[Long-Horizon Execution]] — related
- [[Python Concurrency Models]] — prerequisite-for (asyncio primitives; never block the loop)
