---
title: Tool Design as Harness Surface
tags: [llm, agents, mcp, concept]
summary: "Tools are designed for a reader with no docs and no follow-up question — capability form and granularity, the five-section contract whose negative sections do the work, parameter fidelity, output discipline, and the four gating questions that decide confirmation, retry, and serialization."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--03-tool-design.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--03-tool-design.md
---

# Tool Design as Harness Surface

Tools are the agent's action surface, and their descriptions are the routing logic. **This
is where most harnesses leak.**

Where [[Tool Design as Context Engineering]] treats tools as consumers of window space,
this page treats them as a harness contract: what ships in the definition, and which
properties decide whether a tool needs a gate.

## ACI, Not API

Tool design follows **ACI principles — Agent-Computer Interface, not Application
Programming Interface.** A tool is designed for a reader with no documentation, no type
hints, no autocomplete, and **no ability to ask a follow-up question**. It sees a name, a
description, and a parameter schema.

- **Boundaries must be explicit.** Where one tool ends and the next begins has to be legible
  from descriptions alone.
- **Parameters must be error-proof.** Prefer enums over free strings, absolute paths over
  relative, required over optional-with-surprising-default.
- **Examples belong inside the definition**, not in external docs. *Content invisible to the
  agent is non-existent.*

> When a tool is used wrongly, **check the tool description before questioning the model's
> capability.**

See [[ACI (Agent-Computer Interface)]].

## The Clarity Test

> **"If a human engineer can't definitively say which tool should be used in a given
> situation, an AI agent can't be expected to do better."**

Hand your tool list to a colleague with no context, describe three realistic tasks, and ask
which tool they would reach for. **Every hesitation is a bug in a description or an overlap
that needs collapsing.**

Tools should be *"self-contained, robust to error, and extremely clear with respect to their
intended use."* The dominant failure mode is **bloated tool sets with overlapping
functionality** — and the Terminal Bench gain in [[Harness Engineering]] came partly from
*reducing* tools. **Subtraction is a legitimate optimization.**

## Capability Form and Granularity

Before writing a description, decide what *kind* of capability this is (Li, *AI Agents in
Depth*, ch. 4):

| Decision | Default | Exception |
|---|---|---|
| **Form** — dedicated tool vs skill + general executor | Skill + executor when parameters are complex, the procedure changes often, or the model is strong enough to compose it | Dedicated tool when the call is frequent, parameters are simple, or a smaller model must get it right every time |
| **Granularity** — one tool per format vs one tool with a type parameter | One `read_document(path, file_type)` beats `read_pdf` / `read_docx` / `read_xlsx` | Split only when formats need genuinely different arguments |
| **Generality** — general code interpreter vs narrow tool | General: it covers the long tail for free | Narrow when security, permissions or performance demand it, or the general route is unreliable (`grep` is dedicated because its flags differ across OSes) |

Selection accuracy falls off once a model faces more than roughly a hundred tools, so every
dedicated tool spends a shared budget — the quantitative case for subtraction. Past that
point, load tools on demand: [[Dynamic Tool Discovery]].

## The Five-Section Tool Contract

The structure that turns a one-liner into a decision procedure:

| Section | Purpose |
|---|---|
| **What it does** | The operation, plainly |
| **WHEN TO USE** | Positive triggers — the situations this tool owns |
| **WHEN NOT TO USE** | Boundary cases that belong to a neighboring tool |
| **DO NOT USE FOR** | Hard negatives — misuse patterns seen in practice |
| **EXAMPLES** | Concrete invocations with realistic arguments |

**The two negative sections do the heavy lifting.** Positive descriptions alone leave the
model to infer boundaries between similar tools; explicit negatives are what disambiguate
`search` from `grep` from `read`.

Each entry in `DO NOT USE FOR` should be **ratchet output** — traceable to an actual
observed misuse.

Three more things the description must carry:

- **Concrete formats, not types.** "Phone number in E.164, e.g. `+14155550123`" or "RFC 3339
  timestamp" leaves no room for guessing; "a string" leaves all of it.
- **Return value and cost.** What comes back, how large it can be, and whether the call is
  slow, paid, or rate-limited — so the model can plan around it.
- **One to five invocation examples.** In one book's measurement, adding examples moved
  tool-call accuracy from about **72% to 90%**. Negative boundaries matter more than
  restating capabilities.

Structurally, **separate the contract (schema + description) from the execution logic** via
a factory pattern. Contracts are prompt-engineering artifacts that get iterated on and
versioned; implementations are code. *Coupling them means every wording change touches
executable code.*

## The Four Gating Questions

Ask of every tool before it ships:

1. **Reversible?** — can its effect be undone?
2. **Idempotent?** — is calling it twice the same as once?
3. **Observable?** — does it emit a trace the harness can inspect?
4. **Parallel-safe?** — can two instances run concurrently without corruption?

Each failure has a prescribed remedy:

- Fails **#1** → needs a **confirmation gate**.
- Fails **#2** → must not be retried without an **idempotency key**.
- Fails **#3** → **cannot be debugged**.
- Fails **#4** → must be **serialized in the orchestrator**.

## Schema Rules

- `snake_case` **verb-noun** names — `read_file`, `create_issue`, `send_email`. *The name is
  the first routing signal.*
- **Side effects declared in the description**, not just implied by the name.
- **Typed return structure** — never a bare string when the next step needs to branch on the
  result.
- **Structured errors** with a stable `error_code`, plus `is_fatal` and `retry_after` where
  relevant. **An error the agent can classify is an error it can recover from**; a
  stringly-typed one forces guessing.
- **Token-efficient returns.** Return the answer, not the raw dump — offload the dump to
  disk with a path reference.

Zod or Pydantic schemas give you validation and the model-facing schema from one definition.
Pin versions deliberately.

## Parameter Fidelity

**The world the model sees and the world the tool acts on must not drift apart.** Two
silent failure shapes:

- **Silent input transformation.** The harness "helpfully" normalizes arguments — e.g. a
  coding tool converting curly quotes to straight quotes before an exact-match edit, so edits
  to files that genuinely contain curly quotes fail in a way the model can neither see nor
  diagnose.
- **Silent parameter injection.** The tool adds flags or behaviour the model didn't ask for
  (an extra option on `git commit`). The model's picture of what happened is now wrong, and
  so is every later step built on it.

If a transformation is necessary, **return it in the result** ("normalized 3 quote
characters"). The inverse direction — model-supplied facts the tool must *not* trust — is
[[Belief Parameters with a Ground-Truth Gate]].

## Output Discipline

The return path is as much part of the tool as the call:

| Tool type | Rule |
|---|---|
| **Search** | Structured results (title, location, snippet, score) with pagination — never one unbounded blob |
| **Read** | `offset`/`limit` windows and **visible** truncation ("lines 1–200 of 4,812"). Silent truncation is the dangerous case: the model believes it saw the whole file |
| **Read-only, generally** | Mark them, so the orchestrator can cache and parallelize them |
| **Execution** | Fail fast on invalid input; for long output return head 50 + tail 50 lines and save the rest to a file whose path is in the result |
| **File writes** | Run the linter automatically after the write and return its findings with the result, while the context is fresh |
| **Multimodal input** | Choose image vs OCR text deliberately — layout-heavy content needs the image, dense text is cheaper and more reliable as OCR |
| **Bulk data** | The **artifact pattern**: the model writes the SQL (and chart code); the system executes it and renders rows straight to the user. Data never passes through the model |

**Parallel calls need fault boundaries.** Each tool declares whether it is
concurrency-safe (default: no). A call can start executing as soon as its arguments finish
streaming and validate; a failure aborts only the calls in the same batch that depend on it.

Search and edit tools for coding agents are compared in
[[Coding-Agent Search and Edit Schemes]].

## Progressive Disclosure: Skills

Loading every tool and MCP server at startup **degrades performance before the agent starts
working** — context is consumed and selection accuracy drops as the candidate set grows.

Skills invert this. A short name and description (*what* + *when*, ~10 tokens) stay
resident; the full procedure loads only when the task activates it. **A capability library
of dozens of skills costs a few hundred tokens at rest.**

Same mechanism as progressive disclosure in [[Context Anatomy]], applied to *capability*
rather than knowledge. The measured cost of eager loading, the retrieval and `tool_search`
alternatives, and the KV-cache rule for schemas loaded mid-session are in
[[Dynamic Tool Discovery]]. **MCP solves interoperability; skills solve choice overload.**

## MCP vs In-Process

| Choose MCP when | Choose in-process when |
|---|---|
| Multiple distinct callers need the capability | Only this agent uses it |
| A security boundary must be crossed | Trust domain is shared |
| It deploys independently | It ships with the agent |
| Discovery matters (tools change at runtime) | The tool set is fixed |
| It holds its own state | It's stateless |

Cost: latency per hop, plus a process to operate. **Default to in-process; promote when one
of the left-hand conditions actually holds** rather than in anticipation. See
[[MCP Protocol]].

What the protocol gives you: three primitives (**tools, resources, prompts**) over two
transports (**stdio** locally, **Streamable HTTP** remotely; the older SSE transport is
deprecated). What it doesn't: it is request–response, so a server notification does not
wake an idle agent — event-driven behaviour needs its own channel
([[Asynchronous Agent Event Loop]]).

A third-party server is also code and *text* you didn't write sitting in the model's context
— description poisoning, compromised versions, tool shadowing, broad credentials. Mitigations
and the structural defence are in [[Lethal Triad]].

## Write-Operation Safety

For anything that mutates, sends, or spends:

1. The description **declares the side effect** explicitly.
2. A **confirmation step** precedes irreversible execution.
3. An **idempotency key** is supplied by the caller so retries are safe.
4. Model-generated inputs are **validated against schema before execution** — tool inputs
   are agent-composed and therefore only semi-trusted. See
   [[Execution Boundaries and Guardrails]].

> Tools without idempotency keys must not be auto-retried. **Retrying a non-idempotent write
> is how one transient timeout becomes three charged invoices.**

When the downstream API offers no idempotency key:

- **Query before mutate.** Before retrying, check whether the first attempt already landed
  ("does order #123 already have a refund?").
- **Two-phase call.** `prepare_*` validates and returns a preview plus a short-lived
  **confirm token**; `commit_*` executes only with that token. A retry with a spent token is
  rejected rather than executed twice, and the preview gives a human or reviewer something
  concrete to approve ([[Proposer-Reviewer and Sidecar Gating]]).

## Asynchronous Tool Interfaces

Models assume a tool call is immediately followed by its result. For tools that take
minutes, put the asynchrony in the interface: **name the initiation, not the completion**
(`initiate_phone_call` returning a task ID, with completion arriving as an event), give the
task ID `get_status` / `cancel` verbs, and give event-trigger tools precise filters. See
[[Asynchronous Agent Event Loop]].

## See Also
- [[Agentic Engineering and the New SDLC]] <!-- auto-linked -->
- [[Harness Maturity and Failure Modes]] <!-- auto-linked -->
- [[Iterative Harness Simplification]] <!-- auto-linked -->
- [[Harness Engineering]] — related (part of)
- [[Harness Anatomy]] — related (part of)
- [[ACI (Agent-Computer Interface)]] — extends
- [[Tool Design as Context Engineering]] — related
- [[Execution Boundaries and Guardrails]] — prerequisite-for
- [[Dynamic Tool Discovery]] — extends (tool loading at scale)
- [[Belief Parameters with a Ground-Truth Gate]] — extends (policy checks inside the tool)
- [[Coding-Agent Search and Edit Schemes]] — extends
- [[Asynchronous Agent Event Loop]] — extends (async tool interfaces)
- [[Lethal Triad]] — related (MCP supply-chain risk)
- [[Tool Definitions as Prompts]] — prerequisite-for (how a single definition is rendered into and read from the prompt)
- [[Agent Deployment Anti-Patterns]] — instance-of (namespacing and tool consolidation for #2)
