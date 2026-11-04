---
title: "Data Incident Playbook: Contain Before Diagnosing"
tags: [foundations, pattern]
summary: "A data incident runs detect, triage, contain, repair, verify and postmortem in that order, because wrong data persists and spreads after the cause is fixed; contain first, never fix raw in place, and close only when the checks that fired are quiet."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--03-incident-playbooks.md
---

# Data Incident Playbook: Contain Before Diagnosing

Data incidents differ from service incidents in one way: **the damage persists**. An outage ends when the service returns; wrong data stays wrong, keeps being read, and spreads to every table built from it. Detection only starts the job, and repair has a second half services lack, a backfill ([[Idempotent Backfills and Dated Corrections]]). The role split and severity levels below are adapted from service-incident practice; the severity table is engineering judgment, not a standard.

## The order

Detect, triage (how bad, how far), contain (stop the spread), repair (fix and backfill), verify against the same checks, postmortem with a new check. Priority: stop the bleeding, restore service, preserve evidence. Containment needs no diagnosis: you can stop a dashboard showing a number without knowing why it jumped. Preserving evidence means **never overwriting the raw partition**; correct in a layer above.

## Roles and declaring

| Role | Job |
|---|---|
| Commander | Holds state, assigns work, holds any undelegated role; decides whether to pause publishing |
| Operations | The only people changing the system |
| Communications | Periodic updates to dashboard and model owners |
| Planning | Tracks hand-applied changes so they can be reverted |

One person may hold several roles; what matters is that only one group changes tables. Keep a living incident document. Treat it as an incident if a second team is needed, customers can see it, or it is unsolved after an hour of focused work; declare early, since closing a small one is cheap. Example severities: SEV1 wrong data reached customers, regulators or billing (page now, updates every 30 minutes); SEV2 wrong numbers in an executive report or a production model's inputs (pause publishing); SEV3 internal dashboard stale with a workaround (ticket); SEV4 a monitor fired and the data was correct (tune it).

## Triage: cheap questions first

Most incidents are boring, so check in order: did data arrive, did it arrive once, are fields present, do correlated columns still move together, is the row count plausible. Distance up 59% while fares are flat cannot be longer trips, since fares would rise too: it is a unit fault, not behaviour, which is the difference between a repair and a retrain. Find the first and last bad day from a metric, not memory; the span is the backfill window, and the downstream half comes from [[Lineage for Blast Radius and Rebuild Lists]].

## Contain

The cleanest containment is built before the incident: the [[Write-Audit-Publish Gate]], where readers see a gap, which is visible and honest, instead of a wrong number. Without a gate: pause the downstream DAG, restore a previous table version if the format supports it, or put a warning on the dashboard. A model can be rolled back separately from code, but not when the inputs are what is wrong.

## Verify and communicate

Done means the checks that fired are quiet and open items are written down, not that the job went green (green is how the incident started). In the synthetic feed three checks cleared and two items stayed open: one day never sent, and one day with 19.9% null fares whose revenue stays understated. Neither can be repaired from this side; re-request from the source, or publish a labelled estimate. Never fill the gap with an average and call it repaired. Say what is wrong before stakeholders find it, or they stop trusting all the numbers.

## Per-fault playbooks

| Fault | Contain | Repair |
|---|---|---|
| Null spike | Quarantine the day | Re-request, rebuild the day |
| Dropped day | Mark missing, do not interpolate | Re-export, audit, publish, rebuild downstream |
| Late partition | Tell consumers | Trigger on arrival; rebuild marts older than their input |
| Duplicates | Quarantine the day | Deduplicate on key in staging, rebuild |
| Unit change | Quarantine from onset; check models | Dated correction, full backfill of the window; retrain only if the model trained on it |

## Postmortem

Triggers: user-visible degradation, any data loss, on-call intervention, long resolution, or a monitor failure (a stakeholder finding it first means a monitor failed). Blameless: look for contributing causes and assume everyone acted well with what they knew, because punished people stop surfacing errors and silent wrong numbers sit for weeks. Record impact, timeline, detection, causes, what went well and badly, and actions with owners and dates. Every postmortem adds at least one test or monitor.

## Pitfalls

Fixing raw in place; non-idempotent repair jobs; diagnosing before containing; backfilling without the blast radius; filling gaps silently; retraining as the reflex (it bakes the fault in); closing at the first green; no communication.

## See Also
- [[Write-Audit-Publish Gate]] — prerequisite-for
- [[Idempotent Backfills and Dated Corrections]] — extends
- [[Lineage for Blast Radius and Rebuild Lists]] — prerequisite-for
- [[Freshness Alerts Need a Date Spine]] — related
- [[Silent Failure Catalogue]] — related
