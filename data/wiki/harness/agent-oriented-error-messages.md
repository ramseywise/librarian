---
title: Agent-Oriented Error Messages
tags: [llm, agents, infra, pattern]
summary: "Write every check's failure message for the agent — WHAT failed, WHY the rule exists, HOW to fix it — and promote review comments you keep repeating into such checks, so each category of mistake stops needing a human."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--05-verification-loops.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--references.md
---

# Agent-Oriented Error Messages

A failing check is only half a feedback loop. The practice described in OpenAI's harness
engineering write-up is to **write every check's failure message for the agent, including
how to fix it.**

## WHAT / WHY / FIX

```
ERROR: direct import of 'fs' in src/renderer/App.tsx:12                    ← WHAT
WHY:   renderer has no Node.js access, for security                        ← WHY
FIX:   move the call to src/preload/file-ops.ts and use window.api.readFile() ← FIX
```

Compare `"Test failed"` with `"POST /api/reset-password returned 500 — check
EMAIL_SMTP_URL is set; template expected at templates/reset-email.html"`. The first
triggers a blind retry ([[Agent Retry Taxonomy]]); the second is a one-step fix the agent
can make without a human.

- **WHAT** locates the violation precisely (file, line, value).
- **WHY** lets the agent generalize instead of pattern-matching the one instance — and lets
  it avoid the "fix" that satisfies the letter but breaks the reason.
- **FIX** names the sanctioned path, which is what prevents the creative workaround.

Pair it with the principle for architecture checks: **enforce invariants, don't
micromanage implementation** — require "data is parsed at the boundary", not which parsing
library to use ([[Execution Boundaries and Guardrails]]).

## Promote Review Feedback Into Checks

Human review is the most expensive verifier, and it repeats itself. The ratchet from
[[Harness Engineering]] applied to review:

1. Notice a review comment you have written **more than once**.
2. Name the **invariant** it protects.
3. Write the **cheapest decisive check** for it — grep, lint rule, import-graph test, schema
   check.
4. Give it a **WHAT/WHY/FIX** message.
5. Wire it into the standard verification path and record the rule's origin.

Review comments become docs; **docs that keep getting ignored become checks.** Each promoted
comment is one category of mistake that never needs a human again — "capture taste once,
enforce it continuously."

## See Also
- [[Three-Layer Termination Check]] — related (where the messages are emitted)
- [[Verification Loops]] — extends
- [[Agent Retry Taxonomy]] — prerequisite-for (an actionable error is what makes a retry a re-plan)
- [[Harness Engineering]] — instance-of (the ratchet applied to review)
