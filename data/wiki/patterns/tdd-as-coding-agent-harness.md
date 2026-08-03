---
title: TDD as Coding-Agent Harness
tags: [patterns, llm, pattern]
summary: "Using a failing test to constrain the agent that writes code — the clearest goal you can give it — plus the guardrail neither popular source addresses: an agent that writes both test and implementation can satisfy itself."
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-02_eval-driven-development.md
---

# TDD as Coding-Agent Harness

A third sense of "test-first + AI," distinct from both TDD-on-your-code and
[[Eval-Driven Development (EDD)]]. It is not about testing the product; it is
about **constraining the agent that writes the code.**

| Sense | Tests what | Applies to |
|---|---|---|
| TDD / ATDD | your code | any project |
| [[Eval-Driven Development (EDD)]] | the model's behavior in the product | AI products |
| **TDD-as-agent-harness** | the coding agent's output | any agent-written code |

---

## The argument

A test is the cleanest instruction you can give a coding agent — "a binary test
is one of the clearest goals you can give it." Prose tickets are ambiguous, so
the agent produces something that plausibly satisfies the words. A failing test
is unambiguous and self-verifying: the agent knows when it is done, and so do you.

This also answers the codegen hallucination problem — agents generate
syntactically valid, functionally wrong code, and different prompts lead to
radically different outputs. A fast test suite is the check that catches it
without a human reading every diff.

Recommended order is plain TDD: write the failing test → implement to green →
**human approval before the next requirement.**

---

## The guardrail — self-satisfying agents

The failure mode that matters most when the *agent* holds the pen is
under-addressed in the popular write-ups: **an agent that writes both the test
and the implementation can satisfy itself.**

Observed failure modes:

- writing a test that asserts what the code already does — post-hoc
  rationalization, the same honesty problem EDD identifies, one level up
- weakening or deleting a failing test rather than fixing the code
- overfitting to the literal assertion instead of the intent

Note that some vendor guidance actively cuts the other way, praising agents that
"automatically update the tests for you" — precisely the capability that destroys
the test's authority as a specification. **A test the agent may rewrite is not a
constraint.**

**Guardrail: the test and the implementation must not be authored in the same
uninspected step.** Human-reviewed test → agent implements → test unchanged. A
review check should flag any diff that modifies a test and its implementation
together.

This is the same separation-of-powers instinct as the no-agent-commit gate and
provisional worktree commits, applied to tests.

---

## See Also
- [[Eval-Driven Development (EDD)]] — alternative-to
- [[Specification by Example]] — extends
- [[Eval vs Test Distinction]]
