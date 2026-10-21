---
title: Customer Simulation Interview Study Guide
tags: [interview, reference]
summary: "Method guide for the FDE customer/stakeholder role-play round — six habits that survive improvisation (discover first, mirror, translate by altitude, bad news straight with a path, yes-and-here's-what-it-displaces, dated next step), the Problem → Ownership → Options → Recommendation → Next-step frame, and why discovery often reveals the stated target is a proxy for a different constraint."
updated: 2026-10-17
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation--study-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation--questions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation--sources.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation--examples--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation--examples--bad-news-delivery.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation--examples--incident-response.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--customer-simulation--examples--scope-negotiation.md
---

# Customer Simulation Interview Study Guide

The forward-deployed engineer's signature round, distinct from behavioral: 30–60 minutes of
live role-play where the interviewer plays a skeptical exec, confused domain expert, or
frustrated champion, and scores empathy, discovery, expectation-setting, and technical
translation under social pressure. Prep sources (medium confidence) report that in at least
one frontier-lab loop a majority of candidates who pass coding fail here, and that FDE loops
weight this round plus the case study at about half the evaluation — the engineering bar
filters, the customer bar decides. AIE/MLE rarely get it as a dedicated round, but the same
habits carry the project deep-dive.

**The consistent failure mode:** reverting to engineering mode under pressure — defending
the architecture, deploying jargon, solving before listening. The interviewer improvises
off your responses, so scripts break immediately; only *habits* pass.

Scenario families: kickoff discovery, bad news (model underperforms, timeline slips),
scope creep from a competitor demo, the demo failed in front of their CEO, "why is this
taking so long?", IT says no external APIs, data-privacy concern mid-engagement, in-house
build threat, hostile new contact after the champion left.

## The six habits

1. **Discovery before prescription.** The first two or three turns are genuine questions
   (workflow today, pain ranking, success definition, who decides). Self-test: after two
   minutes of only questions, does your recommendation differ from what you would have
   said immediately? If not, the questions were not real discovery.
2. **Listen and mirror.** Restate the core problem in their words plus a brief
   acknowledgment of what it means for them, *then* respond. Mirroring captures the
   feeling, not just the fact. If they repeat a concern in new words, they don't feel heard
   yet — mirror harder before moving on.
3. **Translate, don't dumb down.** Pick the altitude for the decision this person makes:
   C-suite → outcomes and risk; VP → trade-offs and timelines; manager → adoption and team
   change; technical team → architecture and constraints. Analogies follow
   familiar concept → structural parallel → *say where it breaks* (e.g. fine-tuning as
   accent training vs RAG as a reference library — most companies need the library).
4. **Bad news straight, with a path** — see the frame below.
5. **Boundaries without "no".** "Yes — and here's what it displaces. Which matters more to
   you?" turns your limitation into their priority choice. Never "that's out of scope"
   (no path), "that's not what you asked for" (relationship damage), or "we can try to fit
   it in" (false commitment).
6. **Next step always.** Specific deliverable, dated, one named owner. Ending without one
   leaves the relationship in their hands.

## Bad-news frame: Problem → Ownership → Options → Recommendation → Next step

- **Problem** in the first sentence, with the number ("we're at 71% against an 85% target").
- **Ownership** of what was in your control — neither over-own nor deflect; separate owned
  causes from external ones without using the latter as cover.
- **Options** — two or three with honest trade-offs, *including the hard one* (reduced scope
  or a clean wind-down). Naming wind-down signals alignment with their success over your
  revenue.
- **Recommendation** — one, with the reason. Hedging is a red flag. Under pushback, hold it
  if it was only pressure; adjust if they surfaced new information.
- **Next step** — written, dated.

Rushing to options before owning sounds like deflection.

## What the worked examples teach

- **The stated target is often a proxy.** In the pilot-miss scenario, discovery reveals the
  85% target was the confidence threshold a compliance team needed before cutting manual
  review — which changes what you are solving for. Ask what the number *gates* before
  proposing recovery paths.
- **Defend estimates with mechanism, not assurance.** "68% of misclassifications come from
  one document subset with a known cause" earns belief in a recovery range; "we're
  confident" does not.
- **Convert an opaque gamble into a checkpoint.** Commit to an early-warning date (day 45 of
  a 60-day extension) at which you will surface a miss instead of waiting for the deadline.
- **Honest uncertainty in an incident.** "I don't know the cause yet and won't guess before
  I've seen the logs" plus a dated root-cause commitment beats a speculative explanation.
  Ask first what happened to *their* customer; write their customer-facing message at
  their altitude.
- **Live ROI arithmetic on their numbers.** "Two people, three hours, every morning" →
  ~130 hours/month makes the value of the ask concrete and anchors the scope trade-off
  (see [[Product and Delivery Interview Study Guide]] for the ROI templates).
- **Branch honestly on unknowns.** "If the tickets carry queue labels, 4–6 weeks; if not, a
  different timeline" — and put dependencies that sit on the customer in writing.
- **Know your escalation line** — what you commit to in the room vs take back to the team.
  Overpromising in the sim is scored as overpromising to a client.

## Emotional signals

"I can see why that's frustrating" followed by silence — no "but". Short yes/no answers
mean disengagement: ask what's on their mind. "That's fine" in a flat tone is not fine.
Pausing 2–3 seconds before responding signals processing rather than queuing.

## Anti-patterns

Defending ("the model performed within spec"), jargon-dumping, overpromising, solution
first, no follow-up, claimed empathy ("I totally understand") followed by a pivot, blame
transfer (even when true), hedging the recommendation.

## Practice

Mock scenarios out loud with a peer or an LLM playing the customer and improvising; record
at least three sessions. In playback check the first word out of your mouth (solution or
question), jargon density under time pressure, tone shift when challenged, and whether
every conversation ended with a dated next step.

## See Also
- [[AI Role Interview Loop Map]] — extends (customer simulation is one of the rounds self-made lists miss)
- [[Product and Delivery Interview Study Guide]] — prerequisite-for (ROI arithmetic, three-audience pitch, framing habit)
- [[Behavioral Interview Study Guide]] — alternative-to (past behavior narrated vs behavior performed live)
- [[Case Study Interview Study Guide]] — extends (the other half of the FDE evaluation weight)
- [[Project Deep-Dive Interview Study Guide]] — extends (same translation habits, applied to your own systems)
- [[Durable vs Performative Knowledge Split]] — instance-of (performance technique that transfers to real client work)
