---
title: Eval vs Test Distinction
tags: [eval, llm, concept]
summary: A test tells you your code is broken; an eval tells you your product got worse — two different instruments with different targets, graders, cadences, and failure semantics.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-02_eval-driven-development.md
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

## See Also
- [[Eval-Driven Development (EDD)]] — prerequisite-for
- [[Golden Set Mechanics]]
- [[Anthropic Three-Tier Eval Taxonomy]]
- [[RAG Eval Gate Contract]]
- [[Forecast Grader Thresholds]] — instance-of
