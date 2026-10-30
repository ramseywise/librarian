---
title: Agent Trace Anatomy
tags: [infra, eval, reference]
summary: "A trace is one request as a tree of spans (invoke_agent, chat, execute_tool, retrieval) carrying inputs, outputs, tokens, latency and versions — complete when it answers six questions, standardized by OpenTelemetry GenAI conventions, and the shared raw material for offline evals, online scoring, cost attribution and new dataset rows."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--08-tracing-and-observability.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--06-evaluating-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--README.md
---

# Agent Trace Anatomy

You can't grade what you didn't record. Final-output evals say *that* something failed;
traces say *where*. Without them a trajectory grader has nothing to read, a grounding grader
can't see the retrieved text, efficiency regressions are invisible, and an agent bug can't be
told from an eval bug. Agent-eval courses put tracing before any evaluator for this reason.

## Shape

```
invoke_agent  support-agent                       2.8s
├── chat      (plan)                              0.9s   1,840 in / 120 out
├── execute_tool  search_help_center              0.4s
│     └── retrieval: 5 chunks, top score 0.82
├── execute_tool  lookup_order (order_id=8812)    0.2s
└── chat      (answer)                            1.3s   3,210 in / 260 out
```

| Span type | Record |
|---|---|
| Agent / request (root) | User/session ID, prompt + config version, final output, outcome label, total cost |
| Model call | Model ID, full input messages, output, tokens in/out/cached, latency, finish reason |
| Tool call | Name, arguments, result or error, latency |
| Retrieval | Query after rewrite, returned IDs **and text**, scores, rank |
| Guardrail / judge | Verdict, reasoning, grader version |

Record **versions on the root span** — prompt, model, tool set, index, config. "Which change
caused this?" is unanswerable without them. Treat `finish_reason: max_tokens` as an error, not
a completion.

## The six questions a complete trace answers

1. What did the user ask, and what did they get?
2. Which steps ran, in what order?
3. What did the model see at each step (the full context)?
4. Which tools were called with what, and what came back?
5. Where did the time and money go?
6. Which versions of everything were running?

A question the traces can't answer is the instrumentation gap to fix first.

## OpenTelemetry GenAI semantic conventions

Standard span and attribute names make traces portable across backends: operation names
`invoke_agent`, `chat`, `execute_tool`, `embeddings`; `gen_ai.request.model`,
`gen_ai.response.model`, `gen_ai.response.finish_reasons`; `gen_ai.usage.input_tokens` /
`output_tokens`; `gen_ai.tool.name`, `gen_ai.tool.call.id`. Instrument with OTel (or
OpenInference, which maps to it) and backends can be switched without re-instrumenting; most
agent frameworks emit these spans with one-line setup. The conventions do **not** cover
quality, safety or grounding scoring — those stay project-local.

## Traces → evals → datasets

- **Scores live on spans** — a bad score is one click from its full context.
- **Datasets come from traces** — export a failing trace's input and state as a new row.
- **Offline and online share grader code** — two implementations drift apart.

Choose a backend (Phoenix, [[Langfuse Platform]], LangSmith, Braintrust, W&B Weave, or an
APM accepting OTel GenAI spans) on four capabilities: run evals over stored traces, attach
scores back to spans, build datasets from traces, compare two experiments side by side.

## Cost and latency attribution

Roll up span → request → user / feature / slice. Report **cost per success** (at 50% success
the real cost is 2× per-run cost), where tokens go (system prompt, retrieved context,
history, tool results), **cache hit rate** (a prompt change that breaks the cacheable prefix
can double cost overnight — [[Prefix Caching]]), and p95 latency by step. Agent cost grows
faster than step count because every turn re-sends the context: thinking tokens (500–2,000
per turn can multiply cost 3–5×), large tool outputs billed again on every later turn, and
detours. Set a per-task cost cap and log thinking tokens separately.

## Privacy and retention

Traces hold user input, so decide up front: what is redacted before storage, who sees raw
traces, retention — and whether eval rows derived from traces inherit the same limit and
consent.

## See Also
- [[Observability and Runtime Patterns]] — extends (backend choice and tracing setup)
- [[Langfuse ADK Tracing Patterns]] — instance-of (a framework's span tree in one backend)
- [[Observability & Evaluation Glossary]] — related (vocabulary)
- [[A Trace Is Not a Number of Record]] — related (what traces should not be used for)
- [[Online Eval Sampling]] — prerequisite-for (online graders read sampled traces)
- [[Trajectory Over Outcome]] — prerequisite-for (trajectory grading needs recorded paths)
