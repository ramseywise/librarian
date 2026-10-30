---
title: Eval vs Test Distinction
tags: [eval, llm, concept]
summary: A test tells you your code is broken; an eval tells you your product got worse — two different instruments with different targets, graders, cadences, and failure semantics.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-02_eval-driven-development.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--01-what-an-eval-is.md
---

# Eval vs Test Distinction

Tests and evals are not the same instrument, and a real AI project needs both.
Conflating them is the most common way to get an [[Eval-Driven Development (EDD)]]
adoption wrong.

---

## The comparison

| | Test | Eval |
|---|---|---|
| Target | your code | the model's behavior |
| Output | deterministic | probabilistic |
| Assertion | `assert x == y` | pass *rate* over a set ≥ threshold |
| One case failing | a bug, always | maybe noise, maybe regression |
| Grader | code | code / LLM-judge / human |
| Run cost | milliseconds, free | seconds–minutes, costs money |
| Runs on | every commit | pre-merge / nightly |
| When red | code is wrong | *something* moved — prompt, model, data, or code |
| Owner | whoever wrote the code | needs a named owner; decays otherwise |

**A test tells you your code is broken. An eval tells you your product got worse.**

---

## Why neither substitutes for the other

An agent can have 100% green unit tests and be useless — every function does
exactly what it says on the tin, and the thing still gives bad answers. That
failure is invisible to tests *by construction*, because the defect is not in the
code: it is in the prompt, the retrieval, the tool descriptions, or the model
itself.

The inverse also holds. Evals will never catch an off-by-one in your pagination.

## Legibility is the underlying reason

Deterministic code is *legible* — you can read a function and know what it does,
which is why tests are a productivity and regression tool there: valuable, and
skippable. You cannot read a prompt and know what it does. There is no
legibility, so there is no substitute for running cases.

"Should I write evals?" is therefore not a discipline question the way TDD was.
Without them you have no readout at all — not a weaker readout: none.

---

## The seam by determinism (course framing)

| Behavior | Deterministic? | Check with |
|---|---|---|
| Prompt rendering, schema validation, retry logic, routing tables | Yes | **Unit tests** — assert exact values |
| Tool-call arguments parse, output matches a JSON schema | Yes, given an output | **Deterministic graders inside an eval** |
| Answer quality, grounding, helpfulness, task success | No | **Evals** — many tasks, many trials, rates not assertions |

Rules that follow:
- **Never assert a specific model response string in a unit test.** It flakes, and the fix is to loosen it until it checks nothing.
- **Unit tests gate merges; evals measure rates** — an eval result is a proportion with an error bar ([[Eval Error Bars and Sample Size]]).
- **Mock the model in unit tests, never in evals.** An eval with a mocked model measures the mock.

## See Also
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] <!-- auto-linked -->
- [[Eval-Driven Development (EDD)]] — prerequisite-for
- [[Golden Set Mechanics]]
- [[Anthropic Three-Tier Eval Taxonomy]]
- [[RAG Eval Gate Contract]]
- [[Forecast Grader Thresholds]] — instance-of
- [[Agentic Engineering and the New SDLC]] — extends (output vs trajectory evaluation, and tests as the intent-communication channel)
- [[Differential Parity Testing Against the Original]] — extends (an executed original implementation as the test oracle)
- [[Eval Falsifiability]] — extends
- [[Generation-Under-Contract Eval Harness]] — extends (a third eval kind: producer-driving, not row-grading)
- [[Run-Then-Assert Eval CI]] — extends
