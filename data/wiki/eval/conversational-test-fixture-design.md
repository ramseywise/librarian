---
title: Conversational Test Fixture Design
tags: [eval, pattern]
summary: How to author a fixture for a pipeline whose input is dialogue — the volunteer's verbatim words as the input unit, the full expected artifact as the oracle, and a short "key validation points" list naming the specific wrong answers the scenario exists to catch.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/design-dryrun/reference/scenarios.md
---

# Conversational Test Fixture Design

A regression harness for a conversational pipeline ([[Skill Pipeline Dryrun Testing]])
needs fixtures, and a fixture for dialogue looks nothing like a unit-test fixture. The
`/design-dryrun` scenario file is a worked instance of the form: three scenarios, each
supplying *"the volunteer's actual words (simulate as input), expected outputs at each
stage, and the reasoning behind expected values."*

## The input is speech, not a parameter set

Each scenario opens with a block quote of what the volunteer said, in their register —
hedges, digressions, and all:

> *"It's just me on this — I have a free weekend coming up and wanted to see if I could
> build something that helps... No deadline, just a side project to see if it's useful."*

Writing the input as a structured record instead (`team_size: 1, timeline: weekend`) would
destroy the thing under test. The pipeline's first job is *extraction* — turning
unstructured speech into a profile — so a pre-structured fixture would skip the stage most
likely to fail. The scenarios deliberately bury the load-bearing facts inside narrative:
scenario C's `deployment_target: local` has to be inferred from "a free weekend" and "just
Sarah uses this," never stated.

The realism is also carrying constraint information the assertions depend on. Scenario A's
speaker mentions Google Meet and Slack in passing while describing the problem; the expected
`external_systems: [slack, calendar]` is only correct if the pipeline noticed.

## The oracle is the whole artifact

Each scenario's expected output is a complete Project Profile — pain point, org, archetype
with its justification paragraph, five must-demonstrate items, capacity, out-of-scope list,
and the Copier Hints table with a rationale per row. Not a set of assertions over a few
fields.

Committing the full artifact means every section is implicitly asserted, including the ones
nobody thought to write a check for. It also makes the fixture double as documentation of
what good output looks like — the same dual role that makes an executable specification more
durable than a prose one ([[Specification by Example]]).

## Expected values carry their reasoning

Every Copier Hints row pairs a value with why: `duckdb` because *"700 pages is well within
DuckDB's capacity"*; `docker` because *"team needs access; demo day requires a running
service"*; `primary_chat_agent: none` because the task is *"simple generation, not a chat
agent."*

The rationale column is what lets a failure be triaged rather than merely observed. When
actual diverges from expected, the reader can tell whether the pipeline reasoned wrongly or
the fixture's assumption has since become stale — a distinction that is invisible when the
fixture is a bare value.

## Key validation points: naming the wrong answer

Each scenario closes with 3–5 bullets that name the specific mistake the scenario exists to
catch, usually as a contrast:

- *"`project_type` MUST be `workflow` (not `agent` — the core value is the multi-step
  pipeline, not open-ended conversation)"*
- *"`project_type` MUST be `rag` (not `chat_app` — this is search, not conversation)"*
- *"`project_type` should be `agent` (not `rag` — this is generation, not search)"*

The three scenarios are chosen so that each one's most plausible wrong answer is a
*different* one of the others' right answers. That is the fixture set's actual design: not
three samples of the space, but three mutually-confusable cases pinned against each other,
which is what makes them a discriminating test of [[AI Project Archetypes]] rather than
three independent smoke tests.

The bullets also record the strength of each claim. `MUST` marks an assertion a failure
breaks the harness on; *"should"* marks a defensible-but-expected value. Scenario C uses
both in the same list — `deployment_target` **MUST** be `local`, while `project_type`
*should* be `agent` — encoding which failures are bugs and which are judgment calls worth a
friction-log entry.

## Negative space is part of the fixture

Each expected profile carries an explicit **Explicitly Out of Scope** list — *"not building
a full project management tool," "legal advice (the AI finds relevant law; attorneys advise
clients)," "multi-user system."*

These are assertions in the same sense as the positive fields: a pipeline that produces a
profile without them has failed, because the discovery conversation is specified to elicit
non-goals. Fixtures that only record what the system should produce cannot test a stage
whose job includes bounding scope.

## The derived-constraint chain

The scenarios show the hint table is not a flat mapping from utterance to parameter — values
constrain each other, and the fixture encodes the chain. Scenario C's *"free weekend"*
produces the weekend-sprint tier, which produces `deployment_target: local`, which the
validation points extend into an infrastructure-wide consequence: *"the weekend complexity
budget should steer away from heavy infrastructure (no Docker, no eval suite, no CI)."*

That is [[Complexity Floor]] reasoning appearing as a test assertion — the fixture asserts
not just the parameter but the downstream restraint it implies. Stage 3 of the harness
checks the same property syntactically, rejecting contradictory pairs like
`project_type=prototype` with `deployment_target=cloud`.

Data classification runs the same way: scenario A's transcripts *"may contain student
names/situations → `restricted`"*, and scenario B's memos *"may reference specific cases"*
despite the statutes themselves being public. In both, the sensitivity comes from a fact the
volunteer mentioned only in passing, and getting it right is what makes the observability
question non-optional downstream ([[Scope-POC Design Interview]]).

## See Also
- [[Skill Pipeline Dryrun Testing]] — part-of (the harness these fixtures feed)
- [[AI Project Archetypes]] — extends (the discrimination the fixture set is designed around)
- [[Specification by Example]] — instance-of (the artifact is the spec)
- [[Golden Set Mechanics]] — alternative-to (curated cases for a model rather than a pipeline)
- [[Project Discovery Conversation]] — prerequisite-for (the stage being fixtured)
- [[Complexity Floor]] — constrains (capacity implies infrastructure restraint, asserted)
- [[Asked vs Derived Scaffold Variables]] — extends (the hints table under test)
- [[Human-Participant Skill Test Protocol]] — complements (live participants rather than authored fixtures)
