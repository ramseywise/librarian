---
title: Three-Layer Termination Check
tags: [llm, agents, eval, pattern]
summary: "A floor under 'verify' — static, runtime, and system checks run in order with each gating the next — because unit tests are blind by design to boundary defects and an agent left alone runs the fastest test and declares victory."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--05-verification-loops.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--01-what-a-harness-is.md
---

# Three-Layer Termination Check

"Verify" needs a floor, or the agent runs the fastest available test and declares victory.
Make the layers explicit, ordered, and gating:

| Layer | Checks | Proves |
|---|---|---|
| **1. Static** | Syntax, types, lint, architecture rules | It is well-formed |
| **2. Runtime** | Tests run; app starts and reaches ready; critical path executes; side effects (DB rows, files) are correct | It runs |
| **3. System** | End-to-end flow driven as a user would, against real dependencies | It is *correct* |

Written into the instruction file as the **definition of done**: done means end-to-end
verification passed, not "code is written"; never run level N+1 while level N fails;
skipping a required level (e.g. level 3 for a cross-component change) means not done.

## Why Unit Tests Are Not Enough

Isolation and mocks make unit tests fast and precise — and **blind by design** to the defects
that live at boundaries:

- **Interface mismatch** — caller passes a relative path, callee expects absolute; both mocked
  tests pass.
- **State propagation** — a migration changes the schema while a cache holds the old shape;
  each test starts fresh, so nothing notices.
- **Resource lifecycle** — handles, connections, sockets leak only when components compose.
- **Environment dependency** — correct with everything mocked, broken with real config,
  latency, or permissions.

End-to-end checks also **change how the agent writes code**: an agent that knows it will be
checked end to end starts reasoning about upstream interfaces and error paths. The cost is
seconds of test time, negligible inside an agent loop.

## Ordering Rule: No Refactor Before Verified

"Cleaning up while I'm here" moves the line between verified and unverified code and can
break paths that were implicitly working. **Order the work correctness → performance →
style**, and refactor only after the core behaviour passes all required layers.

## Relation to Other Checks

- The layers are where [[Agent-Oriented Error Messages]] get emitted — a failing layer is
  only half a feedback loop without a WHAT/WHY/FIX message.
- Within each layer, prefer the cheapest decisive mechanism ([[Verification Loops]]).
- A check that silently exercises nothing is the failure covered by
  [[Scan-Floor Guard Against Silent No-Op Checks]].

## See Also
- [[Verification Loops]] — extends (the forced verification pass, given a floor)
- [[Harness Subsystem Attribution]] — instance-of (the feedback-subsystem fix for "claims done")
- [[TDD as Coding-Agent Harness]] — related
- [[Artifact Is Not Evidence: Push and Probe]] — related (layer 3 verifies behaviour, not the artifact)
- [[Execution Boundaries and Guardrails]] — related
- [[Long-Horizon Execution]] — related
