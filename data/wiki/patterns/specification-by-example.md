---
title: Specification by Example
tags: [patterns, concept]
summary: The classical practice (ATDD/SBE) of expressing a requirement as a concrete example rather than prose, producing an executable specification that cannot drift from the code.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-02_eval-driven-development.md
---

# Specification by Example

A requirements practice from the classical agile lineage (Fowler, Adzic, Larman),
sibling to Acceptance Test-Driven Development. The unit is a *requirement*, and
it is authored jointly — the "three amigos": dev, PM, QA.

## The load-bearing claim

Not "tests catch bugs." The claim is that **a test is a less ambiguous way to
write a requirement than prose is.**

The prose-requirements → build pipeline has a silent failure mode: two engineers
read the same spec and build different things. SBE closes it by making the
example the spec.

## Executable specification

The resulting artifact serves three roles at once — requirement, acceptance
criterion, and regression suite — and therefore **cannot drift from the code the
way a PRD does.** A prose spec and its implementation diverge silently; an
executable one fails.

## Lineage

| Name | Unit | Who writes it |
|---|---|---|
| TDD | function | dev |
| ATDD | feature/story | dev + PM + QA together |
| **SBE** | requirement | three amigos |

[[Eval-Driven Development (EDD)]] is this same argument reconstructed for
non-deterministic systems, where the ambiguity problem is sharper because the
implementation is not legible at all.

---

## See Also
- [[Eval-Driven Development (EDD)]] — extends
- [[Eval vs Test Distinction]]
- [[TDD as Coding-Agent Harness]]
- [[Conversational Test Fixture Design]] — instance-of (the expected artifact committed as the spec)
