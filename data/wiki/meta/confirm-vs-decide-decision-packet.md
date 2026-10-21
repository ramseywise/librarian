---
title: Confirm vs Decide Decision Packet
tags: [meta, pattern]
summary: A format for asking an executive for answers. Tag every open question (confirm) for a fact they can answer or delegate, or (decide) for a call that comes with If YES / If NO consequences and a recommendation, so "agreed" is a complete reply. Keep architecture decisions apart from product decisions, and make resolved calls reopenable only on new evidence.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/dssg/docs/overview/exec-summary.md
  - data/raw/claude-docs/dssg/docs/overview/tooling.md
  - data/raw/claude-docs/dssg/docs/overview/roadmap.md
  - data/raw/claude-docs/dssg/docs/overview/design.md
  - data/raw/claude-docs/dssg/docs/overview/portfolio.md
---

# Confirm vs Decide Decision Packet

Built in 2026-07 for a proposal to a time-poor executive covering four workstreams on a shared
platform. The bottleneck was the executive's *response time*, not engineering effort, so the
packet was shaped to minimise the work of answering.

## The format

- **Per-project question IDs** by prefix (platform foundation, portal, PM, KB, template), so
  every downstream doc can cite `pending PF-2` instead of silently assuming an answer.
- **Two question kinds:**
  - **(confirm)**: a fact the reader can answer or delegate ("Is the portal deployed today,
    and where?").
  - **(decide)**: an exec call, always with *the layer it touches*, *why it matters / what it
    blocks*, **If YES** and **If NO** consequences, and a **Recommendation**. "Agreed" is a
    complete answer. For a budget question, "name any number, even $0 unblocks design" turns
    an open-ended ask into a pick-one.
- **One block per project, same shape every time:** goal → where it stands → product
  requirements → technical requirements → open questions. Product requirements shape the
  technical ones.
- **Architecture decisions are kept apart from product decisions.** "Which database and
  identity provider?" is decided once for the whole org. "What is the portal's first AI
  feature?" is scoped to one product. They sit in different sections. A whole-org call is
  repeated under each project it touches, with its blast radius flagged.
- **Rank by downstream rework**, not by importance. The highest-leverage question
  (identity/data-model standardisation) is marked as gating nearly every plan.

## The surrounding doc set

| Doc | Role |
|---|---|
| Exec summary | the only doc that needs a response |
| Portfolio | current-state evidence layer: what is real vs. proposal-only; findings point to where they are tracked |
| Design | target architecture; each tech decision as Context → Requirements → Alternatives → Recommendation → Rationale |
| Roadmap | the reasoning behind each question; every section is *exists today → needs agreeing → tasks* |
| Tooling lookup | re-cuts the design decisions by project: *gating Q → decision → why this → why not the alternative → build status* |

## The decision log clause

A dated decision log records resolved calls "so they aren't re-litigated by default.
Reopening one requires new evidence, not new enthusiasm." The tooling lookup cites settled
conventions explicitly, so a downstream "why not X?" does not reopen them.

## See Also
- [[Deferred Decision Status]] — related (Resolved / Open / Deferred status for the same decision rows)
- [[Four-Stage Design Pipeline with Backflow]] — related (the initiative → product → system → roadmap stages that produce such a packet)
- [[DESIGN.md Artifact]] — related (the per-project design record the decisions land in)
- [[Decision-ID Reservation Across Concurrent Plans]] — related (stable IDs for decision rows)
