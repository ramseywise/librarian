---
title: Belief Parameters with a Ground-Truth Gate
tags: [llm, agents, pattern]
summary: "Put the policy check inside the execution tool: optional expected_* parameters force the model to look facts up first (a checklist), but carry no authority — every policy fact comes from the database and server clock, and belief/truth mismatches are logged."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--03-tool-design.md
---

# Belief Parameters with a Ground-Truth Gate

From Li's τ-bench airline example (*AI Agents in Depth*, ch. 5): the policy check lives
**inside** the execution tool, in two layers.

```python
def cancel_reservation(reservation_id, reason,
                       expected_cabin_class=None,    # model's belief, audit only
                       expected_has_insurance=None):
    r = db.get_reservation(reservation_id)   # facts from the DB, never from args
    now = server_clock.now()                 # time from the server, never from args
    if expected_cabin_class not in (None, r.cabin_class):
        log_mismatch(...)                    # wrong belief, or injection
    ...                                      # rules evaluated on r and now only
```

## Layer 1 — The Parameters Are a Checklist

To fill in `expected_*`, the model has to look the facts up first. Often it **notices the
violation itself** and offers an alternative ("economy without insurance can't be cancelled;
you could rebook") **without making the call at all.**

## Layer 2 — They Carry No Authority

Every policy fact comes from the database and the server clock. A model-supplied
`current_time` or `has_insurance` would be **one hallucination or one injection away
from bypassing the gate.** Log mismatches between belief and ground truth — **the mismatch
rate is the argument for keeping the server check.**

## Prompt Rules for Understanding, Code Rules for the Gate

Keep the rules in the system prompt too, so the model can *explain* the policy and suggest
compliant alternatives. The prompt is for comprehension; the code is the gate. This is
"encode constraints, don't document them" ([[Execution Boundaries and Guardrails]]) with the
documentation kept for a different job.

## Related: Parameter Fidelity

The inverse failure — the harness silently changing what the model asked for — is covered in
[[Tool Design as Harness Surface]]. Both rest on the same principle: **the world the model
sees and the world the tool acts on must not drift apart.**

## See Also
- [[Tool Design as Harness Surface]] — extends
- [[Execution Boundaries and Guardrails]] — instance-of (policy enforced in code)
- [[Bounding Agents Rather Than Trusting Them]] — instance-of
