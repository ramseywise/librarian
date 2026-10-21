---
title: Control Plane Owns the Join, Not the Truth
tags: [patterns, infra, pattern]
summary: "A work item is spread across authoritative subdomains (issue, plan doc, git, PR, sessions) that are each locally true; a control plane must own the reconciliation join and report agree / disagree / could-not-join, never cache or override the subdomain truths, and must land before any orchestrator acts on its view."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-14-control-plane-design.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-15-gua-113-board-contract.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-12-wake-consistency-check.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-15-gua-118-install-the-clock.md
---

# Control Plane Owns the Join, Not the Truth

Design finding from guacamayo's control-plane work (2026-08). There are two kinds of
agent-workflow system. A planner such as galactus asks "what should happen next?". An
observer such as guacamayo has to ask "what is actually happening?" first. The second
question is harder than it looks, because no single store holds the answer.

## The work item is a join, not a record

One unit of work has several authoritative subdomains. Each one owns one fact:

| Subdomain | Owns |
|---|---|
| Issue | wanted / open / closed |
| Plan doc | the plan and its lifecycle status |
| Git | what code exists |
| PR | what merged |
| Sessions | what was decided |

The observed failure was a six-surface contradiction on one issue. Label, plan status,
branch, PR, board column and session notes all disagreed, and **every row was locally
true**. No single surface was wrong, so a fix to any one surface could not clear it. The
rule that came out of it: *the control plane owns the join, not the truth.* It reads each
subdomain, joins them, and reports on the join. It never becomes a second copy of any
subdomain's fact.

## Three tiers of state

- **Session**: ephemeral, dies with the conversation.
- **Workflow**: persistent and owned by the tooling (plan status, labels, ledgers).
- **World**: externally authoritative (git, the PR host). Always re-read it, never cache it.

A status report (`/wake`) that skips reconciliation against the world tier reports
*belief as fact*. See [[Re-Derive, Never Re-Read]].

## Report three ways, not two

Each joined fact gets one of three verdicts: **agrees**, **disagrees**, or **could not
join**. The third verdict is the one that gets dropped. In the first consistency check,
the join regex matched only `#N` issue references. Every plan header that followed the
newer URL convention therefore joined to nothing, so the docs that followed the convention
were exactly the ones that failed. An `unmatchable=106` footnote looked normal. Unmatchable
has to be a first-class finding row, not a footnote (see [[Silence Reads as Clean]]).

## Board contract rules that fall out

- **A contract with no producer cannot be tested.** The schema and its only producer land
  in the same change.
- **A truncated view must not pass as complete.** `skipped_repos` is a required key, so a
  board that skipped a repo says so.
- **Undetermined is never the default bucket.** A column that cannot be derived renders as
  `?`, never `backlog`. A default bucket silently absorbs failed joins.
- **Carry the label next to the derived column.** When the two disagree, that disagreement
  is the signal, so show both and keep both.
- **Freshness is per record.** Each record has its own `collected_at`. A banner appears past
  30 minutes, and a missing file reads "the clock has never run" rather than showing an
  empty board.
- **Keep independent checks in separate commands** (`--board` and `--consistency`), so each
  can fail on its own.
- **An empty fetch is an error** (`EmptyInputError`). It must not render as a clean board.

## Derived sync axis, earned by failure

The design proposed a `Sync:` axis on plan docs (SYNCED / DRIFTED / STALE / UNRESOLVED).
It is *derived*, never hand-written, and it carries provenance (`Sync-at`, `Sync-against`).
The plan called it "earned by observed failure": it was added only because the
contradictions above were observed, not on speculation.

## Sequencing

Reconciliation comes before orchestration. An orchestrator that dispatches work from an
unreconciled view automates the drift. The same design kept data flowing one way between
repos: the session corpus stays authoritative in its home repo, and the control plane owns
only state it derives itself.

## See Also
- [[Decision-Seat Inventory for a Control Plane]] — extends
- [[Map Every State to Its Writer]] — prerequisite-for
- [[Re-Derive, Never Re-Read]] — extends
- [[Silence Reads as Clean]] — extends
- [[Unit Tests Encode the Checker's Assumption]] — extends
- [[Plan Epistemic State Axis]] — extends
