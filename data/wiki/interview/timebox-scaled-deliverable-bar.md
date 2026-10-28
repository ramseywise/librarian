---
title: Timebox-Scaled Deliverable Bar
tags: [interview, llm, pattern]
summary: Test coverage, file organisation, and observability expectations are a dial set by the assignment window rather than a constant — the one-hour "don't write tests" advice inverts at three hours, and the async ambiguity protocol inverts the live-round clarify-first reflex.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-08-01_code-test_openai-work-trial.md
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-08-01_code-test_tooling-audit.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-08-02-LAE-115-code-test-formats.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-08-02-LAE-115-code-test-formats.md
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

## What actually eats a 60-minute window

A tooling audit run before a timed one-hour build measured where the minutes go. It found
that the bar is set less by the work than by the overhead around it:

- **Scaffold, dependency install, and first run took 15–20 minutes.** That is about a third
  of the session spent before any graded code exists. A pre-built, already-installed
  skeleton is the single largest time recovery.
- **The critical gap was the LLM client.** It had no retry, no timeout, no token-limit
  guard, and no structured-output validation. Each omission fails *silently*: a hang with
  no timeout, or a truncated response parsed as complete. This is the "fails silently is
  worse than fails loudly" principle above, found in the candidate's own tooling.
- **Only fast, targeted helpers fit the window.** Plan, research, and review workflows that
  produce a verdict cost 15–30+ minutes each. The fix is to pre-decide those choices before
  the session, not to let a workflow decide them during it.
- **An eight-minute design checklist** replaces open-ended design: name 2–3 non-functional
  requirements, narrate one key trade-off aloud, sketch the simplest flow that works. Skip
  scale, optimization, and clarifying-question rounds at this window.

The audit confirms the dial from the other side. At one hour the deliverable bar is low
because the fixed costs are high.

When the two research sources were compiled into a single study guide, the main risk was
that the guide would argue with itself. One source lists "write a test suite" as something
strong candidates should *not* do in the last 20 minutes. The other calls a missing test
suite the top rejection reason. Copying either statement verbatim produces a contradiction.
The guide only holds together if both land *as the dial*, each qualified by its timebox.
The executed edit was checked with a grep for unqualified anti-test lines, and a provenance
note now names the disagreement so a later reader does not have to rediscover it. The
round's format table grew from three tiers to five: live, 1h code test, 1–3h technical
test, 3–6h Work Trial, and presentation/defense.

## See Also
- [[AIE Code-Test Flaw Taxonomy]] — alternative-to (its advice holds at the 1h window, this dial above it; conflict resolved 2026-08-04, see `_conflicts.md`)
- [[System Design Interview Study Guide]] — alternative-to (live-round clarify-first vs. async state-and-proceed)
- [[Situation-Indexed Decision Tree]] — extends (advice indexed by situation, not by topic)
- [[Durable vs Performative Knowledge Split]] — prerequisite-for (round-technique material, not durable knowledge)
- [[AI-Assisted Take-Home Playbook]] — extends (time budget, scaffold choice and presentation for AI-assisted take-homes)
