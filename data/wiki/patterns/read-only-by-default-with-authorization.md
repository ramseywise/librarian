---
title: Read-Only by Default with Explicit Authorization
tags: [llm, pattern]
summary: A review agent's safety model built from an enumerated safe-command allowlist plus a single authorization gate placed at the write boundary — so subagents get real shell access for verification while every mutating action, including writing a draft the system itself produced, stops at proposing.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/Parallax/docs/documents/Evidence_Driven_PR_Review_System_Spec.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-10-dis222-b93-kulturdaten-backfill.md
---

# Read-Only by Default with Explicit Authorization

[[Parallax]] is read-only by default, but not by withholding tools. All seven of its
subagents have `Bash`, because [[Evidence Classification Model]] requires them to run tests
and reproductions before claiming a finding is verified. The safety property is enforced
instead by **one authorization gate placed at the write boundary**, with an enumerated list
on each side.

## The gate is a list, not a judgment

Explicit user authorization is required before: editing files, applying patches, running
SANYI `--fix`, committing, pushing, posting GitHub comments, approving, requesting changes,
deleting files, and modifying configuration. Safe without authorization: reading files,
grep/search, `git diff`, `git status`, test discovery, and known project checks.

The two lists are the whole mechanism. An agent does not reason about whether an action is
safe — it checks membership. The residual case is handled by a rule rather than by
inference: **"unknown scripts must be inspected before execution."** A script the agent has
not read is neither on the safe list nor obviously on the gated one, and the resolution is
to read it first rather than to guess from its name or location.

Granting `Bash` and then constraining it by allowlist is the deliberate inverse of the
usual "read-only means read-only tools" arrangement. The design needed verification power
([[Evidence Classification Model]] treats an unverified claim as a hypothesis, not a
finding), so the tool stayed and the boundary moved. Every subagent's `Bash` access is
scoped "to the same safe-commands list Section 24 already defines" — one list reused, not a
second policy invented per agent.

## Drafting is free; writing is gated

The most instructive placement is where the gate falls on Parallax's own output. When the
system detects an undeclared invariant, it can draft a candidate `SANYI.md` contract entry.
The spec splits that into two actions with different authorization:

- **Drafting one and surfacing it in the report** requires no authorization.
- **Writing it into `SANYI.md`** does.

Producing a proposal is not a mutation regardless of how finished the proposal looks, and
routing it through the report rather than the filesystem keeps it a recommendation. The
draft is "only ever a recommendation inside Parallax's own report" — and notably this reuses
"the same authorization mechanism Section 24 already applies to every other write action…
not a new bespoke rule." A system that invents a special-case gate for its own outputs has
two policies to keep consistent; this one has a single boundary that the new capability
simply falls on the far side of.

The same split governs who may draft at all: only the subagent with SANYI's contract format
preloaded drafts the entry; the subagent that *found* the gap reports it but does not draft.
See [[SANYI Change-Contract System]].

## Automate coverage, not accountability

The policy is stated as principle rather than only as a list. Two of the design's fifteen
final principles carry it: **"the final decision belongs to the human"** and **"automate
coverage, not accountability."**

That phrasing draws the line by *kind* of work rather than by risk level. Coverage —
reading every changed file, checking every dimension, tracing every caller — is exactly what
scales badly for a human reviewer and well for parallel agents. Accountability for the merge
is what does not transfer, so the pipeline's terminal action is a recommendation and never
an approval; auto-approve and auto-comment are both explicit non-goals, and safety tests
exist specifically to verify the system does not auto-edit, auto-comment, auto-approve, or
run SANYI `--fix` without authorization.

This is why [[Parallax]]'s eight stated obligations end at "preserve human responsibility for
approval" rather than at producing a verdict, and why a review that could mechanically block
a merge instead produces a merge *impact* classification for a human to act on
([[Merge Impact and Evidence State]]).

## Test the default, not the flag parser (akira backfill, 2026-09)

A backfill script's tests covered the `--write` flag parser and nothing else. Review asked
for tests of the behaviour behind the flag. One test calls `main()` with write disabled and
asserts that no `.update` call happens. Another asserts that a write touches only the
columns it is scoped to. The reviewer mutation-tested both by inverting the dry-run guard
and widening the update, and each test went red. A parser test passes even when the guard
it feeds is deleted.

## See Also
- [[Parallax]] — instance-of
- [[Evidence Classification Model]] — prerequisite-for (why `Bash` had to stay)
- [[Merge Impact and Evidence State]] — extends (recommendation, not verdict)
- [[SANYI Change-Contract System]] — extends (the drafted candidate entry)
- [[Verified Runtime Capability Constraint]] — alternative-to (an enforceable control vs. an abandoned one)
- [[Agent Quality Review Checklist]] — extends (human-approval and permission checks)
- [[Production Write Guard: Explicit Override, Never Ambient]] — instance-of (operator CLIs refuse non-local writes without a deliberate flag)
