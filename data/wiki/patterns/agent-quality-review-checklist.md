---
title: Agent Quality Review Checklist
tags: [llm, eval, reference]
summary: Nineteen agent-system-specific review checks across six families — prompt/LLM smells, tool safety, workflow state, retrieval/context, memory write-back, and accountability — of which "safeguard in prose only" is named the highest-value finding.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/agents/agent-quality.md
---

# Agent Quality Review Checklist

The `scan-agent-quality` dimension (`AQ-` prefix) covers defects that only exist in
agent systems — problems a generic correctness or safety scanner has no checklist for.
It is **conditionally dispatched**, only when `detect-signals` reports
`is_agent_code: true` (LLM framework imports or agent path patterns).

## Prompt / LLM smells

1. **Hardcoded prompt strings** — prompts inline instead of in a `prompts/` dir.
   Non-blocking; cross-references SANYI `BN-1`.
2. **Unvalidated model output** — LLM output fed downstream with no structured-output
   schema or output bound. Flag missing Pydantic/JSON schema validation.
3. **Model selection hardcoded** — model names/versions in source rather than config.
4. **Token budget ignored** — no context-length guard, no truncation strategy.

## Tool safety

5. **Write-capable tools without confirmation** — state-mutating tools (write files, send
   messages, mutate DB) dispatched with no confirmation or dry-run mode.
6. **Tool retry unsafety** — retrying a non-idempotent tool with no idempotency guard.
7. **Output validation missing** — tool return values used without schema check.
8. **Permission not enforced at boundary** — access control in prose instructions only,
   not in the tool implementation.

## Workflow state

9. **Unbounded graph** — agent loop with no termination condition or iteration cap.
10. **No partial-success handling** — multi-step workflow fails silently at step N with no
    indication of what completed.
11. **Missing explicit handoffs** — agent-to-agent handoff with no state serialization or
    handoff contract.

## Retrieval and context

12. **Stale/conflicting context** — retrieved content used with no freshness check or
    provenance tracking.
13. **Prompt injection via retrieval** — user-controlled content injected into a prompt
    without sanitization.
14. **Retrieval scoping missing** — query not scoped to authorized data.

## Memory write-back

15. **Inference stored as fact** — model output persisted with no confidence tracking or
    approval gate.
16. **No correctability** — memory writes with no way to correct bad entries.

## Accountability and safeguards

17. **Safeguard in prose only** — a claimed safety behavior (escalation path, validation
    gate, confidence threshold) that exists in prompt instructions but not in
    deterministic code. **"Always flag these — they are the highest-value findings for
    agent systems."** Often `blocker` for production agent code.
18. **No human takeover path** — agentic loop with no mechanism for a human to interrupt
    or take over.
19. **Evaluation missing** — no eval harness for the agent behavior; relying on
    single-run manual testing.

## The organizing principle

Twelve of the nineteen checks reduce to one question: **is the guarantee enforced, or
merely described?** Prose-only permissions (#8), prose-only safeguards (#17), unvalidated
model output (#2), unvalidated tool returns (#7), and inference stored as fact (#15) are
all the same defect at different layers — a claim about behavior with no deterministic
code holding it up. The scanner is accordingly instructed to **Grep for code backing**
before accepting any claimed safeguard, rather than reading the prompt and believing it.

The remaining checks are agent-specific versions of ordinary reliability concerns:
termination (#9), idempotency (#6), partial failure (#10), and interruptibility (#18).

## See Also
- [[Parallel Dimension Scanner Architecture]] — extends
- [[Merge Impact and Evidence State]] — prerequisite-for
- [[ACI (Agent-Computer Interface)]] — extends
- [[MCP Server Security Patterns]] — alternative-to
