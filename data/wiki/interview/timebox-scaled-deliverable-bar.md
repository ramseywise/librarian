---
title: Timebox-Scaled Deliverable Bar
tags: [interview, llm, pattern, conflict]
summary: Test coverage, file organisation, and observability expectations are a dial set by the assignment window rather than a constant — the one-hour "don't write tests" advice inverts at three hours, and the async ambiguity protocol inverts the live-round clarify-first reflex.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-08-01_code-test_openai-work-trial.md
---

# Timebox-Scaled Deliverable Bar

A vendor writeup of OpenAI's code-test and Work Trial formats corrects a specific error in
earlier take-home research: advice derived from a one-hour window was being carried into
longer assignments where it is wrong. The correction generalises into a dial.

**Confidence note:** the source is vendor-published, single-source, and functions as
content marketing for mock-interview services. Its claims are recorded here with
attribution rather than as assertions — in particular its claim that missing tests are the
*single most cited rejection reason* is uncorroborated.

## The dial

| Window | Test expectation |
|---|---|
| **1h timed** | 2–3 tests: happy path, boundary, one failure/error path. Runnable by a single command |
| **1–3h technical test** | The above, plus malformed-input and error-path coverage |
| **3–6h Work Trial** | Full suite: core behaviour, boundaries, failure cases — **named so intent reads without the implementation** |

The same scaling governs file organisation. A single file is correct only at the
degenerate one-hour end; past that, organise by responsibility. And it governs
observability, which at the longer windows is a graded dimension in its own right rather
than a nice-to-have print statement.

This is what corrects [[AIE Code-Test Flaw Taxonomy]], whose "strong candidates do NOT
write a test suite in the last twenty minutes" holds only at one hour. Read as a constant
it is actively harmful at three.

## The reviewer lens

The recommended framing for the grader is concrete rather than rubric-shaped:

> Read the submission **the way they would assess a pull request from a new engineer.**

That reframing does most of the work of the individual criteria. A reviewer looking at a
new engineer's PR does not ask whether the algorithm is optimal; they ask whether they can
tell what it does, whether it fails loudly, whether they'd be comfortable with it in the
repo. It converts a scoring exercise into a judgment already familiar to anyone who has
reviewed code, which is why the derived expectations — naming, organisation, error paths —
cluster around legibility rather than cleverness.

The associated principle, stated directly:

> A system that **fails silently is worse than a system that fails loudly.**

Named anti-patterns at this grain: naive retry without backoff (retry logic that exists
but has no exponential delay reads as cargo-culted, not absent), and unaddressed
concurrency safety.

## The ambiguity protocol inverts between formats

The genuinely non-obvious finding. For an **async** assignment:

> State your interpretation and proceed, documenting the assumptions you made.

This is the opposite of the live-round reflex, where clarifying before designing is step
one of the method (see [[System Design Interview Study Guide]]). Both are correct in their
own format — in a live round the interviewer is present and withholding requirements
deliberately, so asking is the graded behaviour; in an async submission there is nobody to
ask and blocking on ambiguity produces nothing. The source's operative warning is that the
two must be kept apart in the prep material:

> The round docs must not blur the two.

A single "always clarify first" rule silently mis-fires on every async assignment. This is
the same failure mode as any context-free rule — see [[Situation-Indexed Decision Tree]]
for the general fix of indexing advice by situation rather than by topic.

## Other graded dimensions

- **Time estimation is itself graded** — the estimate you give is assessed alongside the
  work, so a submission that overshoots its own stated budget loses on a dimension separate
  from quality.
- **Frameworks are neutral.** No credit for or against a particular stack.
- **AI-tool policy varies by track** and is not inferable from the company; confirm with
  the recruiter rather than assuming.
- Two distinct OpenAI formats exist — a shorter technical test and a longer Work Trial —
  and advice for one does not transfer to the other. That non-transfer is the dial again.

## See Also
- [[AIE Code-Test Flaw Taxonomy]] — contradicts (its one-hour test advice; see `_conflicts.md`)
- [[System Design Interview Study Guide]] — alternative-to (live-round clarify-first vs. async state-and-proceed)
- [[Situation-Indexed Decision Tree]] — extends (advice indexed by situation, not by topic)
- [[Durable vs Performative Knowledge Split]] — prerequisite-for (round-technique material, not durable knowledge)
