---
title: Shared Context Brief
tags: [llm, context-management, pattern]
summary: A structured brief the orchestrator fills in exactly once and passes to every dispatched subagent, so N parallel reviewers share one grounding pass instead of each re-deriving repository context from the same diff.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/skills/parallax-shared/templates/context-brief.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/templates/review-report.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/templates/interview-walkthrough.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/templates/github-comment.md
  - data/raw/claude-docs/Parallax/agents/parallax.md
---

# Shared Context Brief

Parallax's orchestrator fills in one `context-brief.md` during Stages 0–2 and hands the
same filled brief to every dispatched subagent. The template states the constraint twice:
it is "produced once by the orchestrator, passed to every dispatched subagent," and "a
subagent should never need to re-derive any of this itself."

This is the grounding half of fan-out review. [[Parallel Dimension Scanner Architecture]]
splits *judgment* across agents; the brief keeps *context acquisition* unsplit.

## Why build-once matters

Without it, seven subagents each independently read `CLAUDE.md`, walk the repo structure,
resolve callers of changed symbols, and skim CI config — seven times the token cost for
work with one correct answer, and seven chances to derive it slightly differently. Two
subagents disagreeing because they reconstructed the change map differently produces a
conflict the orchestrator cannot resolve, since neither disagreement is about the code.

Centralizing it also means the expensive context is gathered by the one agent that has to
hold the whole picture anyway.

## The three sections

| Section | Stage | Captures |
|---|---|---|
| Review Contract | 0 | Intended change, expected behavior, scope/out-of-scope, constraints, confirmed facts vs inferred assumptions vs unknowns, initial risk areas, review profile, time budget |
| Repository Context | 1 | Repo structure; `CLAUDE.md`/`AGENTS.md`/`CONTRIBUTING.md`/`README.md` summaries; PR template fields; CI summary; changed files; nearby files; callers and callees of changed symbols; relevant historical changes; static analysis tool and result |
| Change Map | 2 | Input, validation, transformation, state transition, external systems, tools, side effects, persistence, output, error path, human handoff, evaluation path, memory write-back |

The Change Map's last four fields — human handoff, evaluation path, memory write-back, and
tools — are agent-system concerns rather than general-PR ones. The brief carries them for
every review, so the gated agent-system dimensions have their grounding already present
when they are dispatched, including on a [[Corrective Follow-Up Dispatch]] second round
where no fresh context pass happens.

## Unknown is a value

The Review Contract separates **confirmed facts**, **inferred assumptions**, and
**unknowns** into three distinct fields, and the template closes with the rule: "Missing
context is not a code defect — if a field above is unknown, write 'unknown' rather than
guessing, and let the general review's Intent dimension raise it as a question."

Recording absence explicitly is what stops a gap from being silently filled by a plausible
guess that then propagates to all seven subagents as though it were established. It is the
same discipline [[Evidence Classification Model]] applies to findings, applied one stage
earlier to inputs — and it routes the gap to a dimension that handles questions rather than
letting it become a fabricated premise.

## Output templates mirror the same ownership rule

Three of the four templates are orchestrator-only, for the same reason the brief is:

- **`review-report.md`** — assembled once over every subagent's combined findings. Its
  Subagent Dispatch block records each of A–G as `dispatched / completed`,
  `failed after retries`, or `skipped` with the reason (`Agent-System Extension not
  active`, `no SANYI.md`). A dimension that did not run is visible as a distinct state from
  one that ran and found nothing.
- **`interview-walkthrough.md`** — the three "Main Concern" slots are "the top three
  findings by merge impact **across all dispatched subagents, not per-subagent** — this is
  why only the orchestrator assembles this document." Any ranking that spans dimensions
  requires the merged view by definition.
- **`github-comment.md`** — one finding, one comment, rendered from the canonical finding's
  `communication` fields. Used only under explicit authorization (review is read-only by
  default). Two rules bind it to the evidence model: never post a `blocker` as anything
  other than `request_change`, and never post a hypothesis or question phrased as a
  confirmed defect — "the template's evidence_state tag exists specifically so the reader
  can see this at a glance."

The report's Static Analysis section is likewise reserved for raw tool output or the
literal string "no static analysis tool detected" — see [[Deterministic Review Substrate]].

## See Also
- [[Parallel Dimension Scanner Architecture]] — extends
- [[Evidence Classification Model]] — extends
- [[Deterministic Review Substrate]] — extends
- [[Corrective Follow-Up Dispatch]] — prerequisite-for
- [[Merge Impact and Evidence State]] — extends
- [[ADK Context Engineering]] — instance-of (context assembled once, reused across calls)
- [[Skill Preloading via Agent Definition]] — alternative-to (startup-preloaded vs. per-run context)
