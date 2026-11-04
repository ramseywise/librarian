---
title: "Rolling Out a Decision Router: Partial Shadow and an Audit-Sized Canary"
tags: [foundations, pattern]
summary: "A router that pays, reviews or rejects can shadow only where the champion produced outcomes, so it needs a canary with a stable unit, action limits and a clock set by label arrival, with an audit sized to the error jump it must detect."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--06-ml-system-framing-to-monitoring.md
---

# Rolling Out a Decision Router: Partial Shadow and an Audit-Sized Canary

[[Model Rollout: Shadow, Canary and A/B]] gives the mechanics; this page covers a model whose output is a decision with money attached.

## What shadow can and cannot show

An upstream extractor can shadow fully: a new reader takes a copy of each page, only the champion's fields go downstream, differences appear with no labels. Treat a difference as an alarm, and send disagreeing documents to a person to get labels where they are most useful.

A router can only partly shadow. Outcomes exist only where the champion produced them:

| Champion | Challenger | Outcome available |
|---|---|---|
| Review | Pay | yes, the clerk's decision (what you most want) |
| Pay | Review | only if audited or a problem surfaces later |
| Pay | Pay | only through the audit |

It also cannot see how clerks would behave given different suggestions. Hence a real canary.

## Canary: unit, limits, clock

- **Unit:** hash a stable key. Hashing the supplier keeps one supplier on one policy, but a few big suppliers make the real share lumpier than a nominal 5%, so count what you got.
- **Limits:** when a system acts in the real world, set and enforce action limits as a sanity check: a cap on money paid without review per day and per supplier. Hard rules stay above the model during and after the canary.
- **Clock:** a canary cannot end before its labels arrive. Size an audit first. At 50,000 invoices a month, a 5% canary gets 2,500 invoices and pays about 1,525 (paid share 0.61). Auditing 100 gives a 0.421 chance of catching an error jump from 1.3% to 3.3% at a 5% false-alarm rate; auditing 300 gives 0.775. Three hundred of 1,525 is about 20%, against 2% to 5% audits in steady state, so a real canary audits a far larger share.

Also needed: a canary because a model artifact and the serving system can mismatch (catching it earlier is better), and a rollback practised as normal operation, back to the previous version or to review-everything, checking the queue can take it. Do not stop a canary because the dashboard looks fine; labels have not arrived.

## See Also
- [[Model Rollout: Shadow, Canary and A/B]] — prerequisite-for
- [[ML System Design: Stages and Handoffs]] — related
- [[Learning From Corrections and the Audit Sample]] — related
- [[Review Route Thresholds From Priced Costs]] — related
