---
title: Eval-Driven Development (EDD)
tags: [eval, llm, pattern]
summary: Writing the eval suite before the agent exists — ATDD reconstructed for non-deterministic systems, where first-ness buys honesty rather than design pressure.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-02_eval-driven-development.md
---

# Eval-Driven Development (EDD)

EDD is [[Specification by Example]] reconstructed for systems whose output is
probabilistic. The practice: author the behavioral case set *before* the agent
can satisfy it, then build to green.

Anthropic's guidance states it directly — "build evals to define planned
capabilities **before** agents can fulfill them, then iterate until the agent
performs well" — and makes the same ambiguity argument SBE makes about prose:
"two engineers reading the same initial spec could come away with different
interpretations… An eval suite resolves this ambiguity."

The academic framing (arXiv 2411.13768, *EDDOps*) positions evaluation as "a
continuous, governing function rather than a terminal checkpoint," arguing that
static test suites are structurally inadequate for agents because agents are
"open ended, probabilistic, and shaped by system-level interactions over time."

---

## Two lineages that converged

| Lineage | Practice | Unit | Who authors |
|---|---|---|---|
| Classical (1999–2010) | TDD | function | dev |
| Classical | ATDD | feature/story | dev + PM + QA |
| Classical | [[Specification by Example]] | requirement | three amigos |
| AI-native (2023–2026) | **EDD** | agent behavior | whoever owns the product |

The load-bearing claim of the classical lineage is *not* "tests catch bugs" — it
is that a test is a less ambiguous way to write a requirement than prose is. The
artifact is an **executable specification**: requirement, acceptance criterion,
and regression suite in one document, which therefore cannot drift from the code
the way a PRD does. EDD inherits exactly this argument.

---

## Why "first" is load-bearing here specifically

For TDD, first-ness buys **design pressure** — writing the test first forces a
callable interface and honest dependencies. Real, but obtainable other ways,
which is why TDD adoption was always a matter of taste.

For evals, first-ness buys **honesty**, and there is no substitute:

> Evals written after the agent exists get graded against what you built, not
> what you wanted. You look at the output, think "yeah, that seems about right,"
> and write it down as the expected answer. You have just encoded your bugs as
> the specification.

Nobody does this deliberately; everybody does it — the output is right there and
it is the only anchor available. Writing the cases while the agent does not yet
exist is the only structural defense, because at that point there is nothing to
anchor to *except* what you actually want.

The symmetric risk: a golden set invented at discovery can encode wishful
thinking just as easily as a post-hoc set encodes bugs. Mitigation is
source-risk traceability — every case cites a real scope risk.

---

## How the loop differs from red→green

1. **Gradient, not binary.** You are at 34/50, not pass/fail. There is no moment
   where "the test goes green."
2. **Every change is a global change.** You tweak a prompt to fix three failures
   and land at 33/50 because the tweak broke four cases you were not watching.
   The prompt is one shared surface for all behavior — there is no local fix.
   *This is the core reason the whole suite must exist before tuning starts:*
   with ten cases you would have seen 3 fixed and shipped it.
3. **Regressions arrive unprovoked.** A passing test stays passing until someone
   edits the code. A passing eval can go red because the vendor shipped a new
   model checkpoint, the corpus drifted, or a dependency changed a default.
   Hence the named-owner requirement — eval suites decay, test suites do not.

---

## Three layers, not one

| Layer | Instrument | Practice | Differs in an AI project? |
|---|---|---|---|
| Functions, parsers, adapters | unit tests | TDD | **No** — identical to CRUD |
| API endpoints, wiring | integration tests | ATDD | **No** — identical to CRUD |
| Agent behavior | evals | **EDD** | **Yes** — this is the new layer |

EDD is a third layer stacked on top, not a replacement for the first two. See
[[Eval vs Test Distinction]] for why conflating the instruments is the most
likely way to get an EDD adoption wrong.

---

## See Also
- [[Eval Harness Anatomy]] <!-- auto-linked -->
- [[Eval Ladder]] <!-- auto-linked -->
- [[Eval vs Test Distinction]] — prerequisite-for
- [[Specification by Example]] — extends
- [[Golden Set Mechanics]] — extends
- [[Anthropic Three-Tier Eval Taxonomy]]
- [[TDD as Coding-Agent Harness]] — alternative-to
- [[Skill Pipeline Dryrun Testing]] — instance-of (a regression harness over a conversational pipeline)
