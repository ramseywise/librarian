---
name: prototype
description: Prototyping and exploration mode for quickly validating ideas, APIs, or technical approaches. Use when the user wants to prototype, explore, spike, or try something out before committing to a production implementation. Not for production code.
---

Prototype or explore $ARGUMENTS. Apply all rules below strictly.

## Purpose
- Goal is fast learning and validation, not production-ready code
- Answer a specific question: "Does this work?", "How does this API behave?", "Is this approach feasible?"
- State the question being answered before writing code

## Rules
- No TDD — tests are optional during prototyping
- BCE layering and strict architecture rules are relaxed
- Shortcuts are allowed (hardcoded values, minimal error handling, skipped validation)
- Do not refactor or clean up existing production code as part of prototyping
- Keep prototype code clearly separated — use a `prototype/` directory or clearly mark files as experimental

## Workflow
1. Clarify the question or hypothesis being tested
2. Write the minimum code needed to answer it
3. Run it and observe the result
4. Document findings: what worked, what didn't, what was surprising
5. Decide together with the user: adopt (rewrite properly), adapt (refactor into production), or discard

## Output
- After prototyping, summarize findings as a comment in ROADMAP.md or as an ADR if the finding influences architecture
- If the prototype code is to be adopted, switch back to the `/backend` or `/frontend` skill and rewrite with full rules (TDD, BCE, validation, etc.)
- Never merge prototype code directly into production paths
