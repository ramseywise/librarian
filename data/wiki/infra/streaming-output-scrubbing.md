---
title: Streaming Output Scrubbing
tags: [infra, llm, pattern]
summary: Scrubbing secrets from a streamed LLM response in transit via a TransformStream with a carry window — the only seam that preserves streaming while guaranteeing scrubbed bytes are the only bytes the caller sees.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-50-plan.md
---

# Streaming Output Scrubbing

An output guard that runs *after* generation has a seam problem that input guards
do not have: by the time the check could run, the tokens are already moving. A
handler returning `result.toUIMessageStreamResponse()` has three possible seams,
and two of them are wrong.

## The three seams

| Option | What it costs |
|---|---|
| Poison the stream (abort mid-flight on a hit) | The leaked tokens have **already been rendered client-side**. Scrubbing after display is theater, and it turns one bad token into a dropped response. |
| Buffer the whole response, scrub, then send | Correct, but deletes streaming — the entire reason `toUIMessageStreamResponse()` exists. |
| **Transform in transit** (chosen) | Scrub each chunk as it passes through a `TransformStream`. Preserves streaming; scrubbed bytes are the only bytes the caller ever sees. |

**Chosen: transform in transit**, implemented as `guardTextStream()`.

## The carry window

The naive version of transform-in-transit fails on chunk boundaries: a secret
split across two chunks matches neither. The fix is a **carry window** — hold
back the last `CARRY_CHARS` characters of each chunk, prepend them to the next,
and any match shorter than the carry window is caught regardless of where the
boundary falls.

What makes this sound rather than a compromise: the secret shapes being matched
(`sk-…`, `AKIA…`, `ghp_…`) are **bounded-length tokens**. Bounded length is the
precondition for streaming scrubbing. The window is sized *above the longest
pattern* rather than guessed.

The residual limitation is real and bounded: a credential longer than
`CARRY_CHARS` straddling a boundary can slip through. Because it is bounded, it
gets **documented in the module header rather than hidden** — a limitation you
can state precisely is a different object than one you discovered in production.

## Why the input guard is unaffected

`checkInput` runs pre-model-call and returns a refusal `Response` with no stream
interaction at all. It has no seam problem, so it lands first and alone — and a
blocked turn costs **zero tokens**, because the guard fires before the agent is
ever invoked. See [[Input Guardrails Pipeline]].

## The three layers in a request path

Output scrubbing is one of three guard layers, each on a different untrusted
surface:

| Layer | Surface | Why it is untrusted |
|---|---|---|
| `checkInput` | the last user turn | direct injection |
| `filterContent` | tool / retrieval output | **indirect injection** — non-user text entering the next prompt |
| `checkOutput` | the response stream | credential leakage from the model |

The middle layer is the one most often missed. Tool results are text that enters
the next prompt without a human ever having typed it; wrapping the tool registry
is the same seam that span-instrumentation wrapping uses.

## Shipped-but-unwired is not protection

The motivating defect: `security/guards.ts` and `guards.py` shipped in every
rendered project with a README describing exactly where each layer belongs — and
**nothing called them**. The only importer was a test file; the Python twin had
no importer at all.

> A scaffold that ships an input guard, a content filter and an output scrubber
> *looks* protected and is not.

This is the [[Verified Runtime Capability Constraint]] applied to security: the
artifact's presence is not evidence of its participation. The remedy is
mutation-style wiring tests where each docstring names the exact edit that makes
the test fail — import alone proves nothing, since an import satisfies a linter
while the call site stays empty.

## See Also
- [[Input Guardrails Pipeline]] — prerequisite-for
- [[Safeguards Architecture — Five Protection Layers]] — instance-of (the post-generation layer)
- [[Verified Runtime Capability Constraint]] — extends
- [[PII Masking Approaches]] — alternative-to
