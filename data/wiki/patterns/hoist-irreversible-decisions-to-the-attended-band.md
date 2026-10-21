---
title: Hoist Irreversible Decisions to the Attended Band
tags: [langgraph, llm, pattern]
summary: "When a stretch of an agent pipeline must run unattended, move every irreversible decision into the attended band before it. Where something irreversible still comes up, stop, rather than deferring or proceeding. An async confirmation channel nobody watches is a timeout with extra steps. Budgets with no measurement behind them are labelled unmeasured, and elapsed time is recorded beside stopped-versus-completed."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-27-band-contract-hitl-gates.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-27-band-contract-hitl-gates.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-fast-loop-borrowables.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-fast-loop-borrowables.md
---

# Hoist Irreversible Decisions to the Attended Band

From the galactus "fast loop": a ~60-minute pipeline in four bands. In band 1 (triage,
5–10 min) the operator confirms a decision tree. Band 2 (prototype, 20–30 min) runs
**while the operator is working in notebooks**, so it must be *non-blocking*, not just
fast. Bands 3 and 4 optimize and harden. One hard rule cuts against the band-2
requirement: `human_approval` may never be derived silently, because a silent default
there fails in an irreversible way (an autonomous external write that nobody sanctioned).

## Three options, one adopted

| Option | Verdict |
|---|---|
| Async confirmation channel (a status file band 2 polls) | **Rejected.** A channel the operator is not watching is not a confirmation. It is a timeout with extra steps. Building it forces a decision about what happens when nobody answers. Blocking defeats the band, and proceeding without approval is the exact irreversible failure the carve-out forbids. |
| Defer approvals to the last band | **Rejected.** Band 2 writes artifacts. An approval that arrives after the write approves nothing. |
| **Hoist every irreversible decision into band 1** | **Adopted.** |

Hoisting works because of a reversibility rule: **a default is safe to apply silently in
proportion to how cheaply it can be reversed.** What band 2 does, such as fitting a model,
writing under `runs/`, or writing a plan doc, can be undone with rerun, delete or
`git checkout`. The thing that decides what interrupts the human is blast radius, not
importance.

**The carve-out:** if band 2 ever needs an irreversible action, it **stops**. It does not
defer and does not proceed. The run is recorded as blocked at that point, and a
checklist item makes the block a legible outcome rather than a crash. If stopping turns
out to be common, that is the evidence an async channel is genuinely needed, and it can be
built then, against real cases.

## The hole a failure pass found

Band 2 owns the execute phase, and execute dispatches worktree agents that **commit**. A
commit is not in the enumerated "rerun, delete, checkout" set. So stopping may be the
*usual* case, not the exception. The hidden risk is in the measurement: **a band budget
averaged over runs that stopped early looks like evidence the budget holds.** The
mitigation applies from day one. The dispatcher records stopped-versus-completed next to
elapsed time, so the budget is never computed over a contaminated population. Waiting for
the stop frequency to show itself is exactly what would corrupt the figure.

## Unmeasured budgets stay labelled unmeasured

Bands 1 and 2 had evidence. A conversational intake measured at ~2 min against ~12 min
for a scaffolding tool. A one-hour claim had been tested once and failed, because fit time
for the *baseline* dominated (the winning model fit in 11.6 s). Band 2's budget is
therefore **conditional on fold and model capping as a declared default, not an available
flag**. Bands 3 and 4 had no measurement at all, in either repo.

The tempting move is to write "10–15 min" into the contract. That was refused: **a target
with no measurement behind it, once written into a contract, becomes an estimate the next
reader trusts.** The contract instead records `Budget: unmeasured (target 10–15 min, no
evidence)`, and every band **emits its elapsed time**. Evidence then accumulates as a side
effect of normal use (see [[Budget Without a Meter Is a Preference]]).

## Supporting decisions from the same design

- **Bands are a view over the status machine, not a replacement.** Bands are derived by
  lookup from the existing `Status:` field, so neither validation hook changes. A terminal
  `SUPERSEDED` state belongs to no band: it is an escape from the sequence. A band with no
  owner skill cannot have a release checklist, and a "no band is empty, every band names an
  existing owner" check exposed one such band.
- **A backward transition needs a reader, not a new field.** The transition ledger already
  logged `{from, to}` for every accepted edge, so a regression is an entry whose `from`
  comes after its `to`. What was missing was a band-aware reader that counts loop-backs
  per run. That is the cheapest resolution, and it was only available because the ledger
  had landed first.
- **Propose-and-confirm intake can drift into leading the witness.** Record each
  confirmation as confirmed or overridden. **An override rate of zero is itself the
  warning sign** (see [[Asked vs Derived Scaffold Variables]]).
- **"Serial by default" was scoped, not inherited.** A rule written for a watched,
  recorded exercise ("parallel agents are faster and unwatchable") would have forbidden
  the parallelism band 2's budget depends on. It applies to the attended bands only.

## See Also
- [[Reversibility Cliff]] — extends
- [[Decision-Seat Inventory for a Control Plane]] — extends (which seats stay human)
- [[Audit-Don't-Assert Release Checklist]] — extends (the per-band gate that makes a stop legible)
- [[HITL Gradient]] — extends
- [[Budget Without a Meter Is a Preference]] — extends
- [[Asked vs Derived Scaffold Variables]] — extends (the propose-and-confirm triage intake)
