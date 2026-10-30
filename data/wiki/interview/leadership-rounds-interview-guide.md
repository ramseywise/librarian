---
title: Leadership Rounds Interview Study Guide
tags: [interview, reference]
summary: "Method guide for the CTO / Head of Product / founder rounds and the reverse interview — interviewer-centric rounds graded on alignment and trust, where 'it depends' without the branches fails, agreeing under pressure is a negative signal, the 90-day answer must avoid hero and passive mode, and your questions back are evaluated signal plus your own due diligence."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--leadership-rounds--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds--study-guide.md
  - data/raw/repos/sisyphus/interviewing--rounds--leadership-rounds--study-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds--questions.md
  - data/raw/repos/sisyphus/interviewing--rounds--leadership-rounds--questions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds--sources.md
  - data/raw/repos/sisyphus/interviewing--rounds--leadership-rounds--sources.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds--examples--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--leadership-rounds--examples--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds--examples--90-day-sketch.md
  - data/raw/repos/sisyphus/interviewing--rounds--leadership-rounds--examples--90-day-sketch.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds--examples--cto-judgment-thread.md
  - data/raw/repos/sisyphus/interviewing--rounds--leadership-rounds--examples--cto-judgment-thread.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--leadership-rounds--examples--reverse-interview.md
  - data/raw/repos/sisyphus/interviewing--rounds--leadership-rounds--examples--reverse-interview.md
---

# Leadership Rounds Interview Study Guide

Late-stage, 30–60 min, low structure, near-certain in startup loops. Unlike syllabus rounds,
the content is **alignment**: what is tested depends on who is interviewing. They are also
selling to you, so engaged, specific questions from you are scored as seriousness.

## What each interviewer is actually asking

| Interviewer | Underlying question | Prep move | Common failure |
|---|---|---|---|
| **CTO** | Would I trust this person's technical decisions unsupervised? | Opinions with reasons on *their* likely stack tensions (build-vs-buy, vendor strategy, eval discipline, tech debt) | Too agreeable — no pushback from a candidate predicts none from an employee |
| **Head of Product** | Thought partner, or builds whatever I spec? | Problem-first reflex; one product decision of theirs you'd have made differently; one feature you'd have killed and the signal that drove it | "I'll build whatever you need" — reads as low value |
| **Founder / CEO** | Do they care about *this* mission, and can they operate at several layers at once? | Specific conviction about their bet; a 90-day sketch for *their* company; known deal-breakers | Generic enthusiasm ("I've always been passionate about AI") |

## Running a technical judgment thread

CTO rounds often center on one deep thread, a conversation not a quiz:

1. State a default with the reason ("my default is X because…").
2. Name the variable that flips it ("if Y is true I'd move to Z").
3. Steelman the other side.
4. Update on *new information*; hold on mere pressure — the distinction is the signal.

In the worked build-vs-buy-for-model-serving thread, the default is "rent what isn't
competitive differentiation"; when the CTO reveals a self-hosted small model failed on
quality, the recommendation shifts to tiered routing (cheap model for a classification
step) — validated by a **shadow-mode evaluation** routing real sampled traffic through both
paths before any production change. "It depends" is an answer only when followed by what it
depends on and what you'd do in each branch.

Before every round write the **two-stance exercise**: a technical bet you're confident in
and why; a hype you'd push back on, why, and what evidence would change your view.

## The 90-day answer

It asks how you operate somewhere new. Two failure modes: **hero mode** (a full platform in
90 days — signals you don't know how long things take or will bulldoze process) and
**passive mode** (just observe — defers output indefinitely). Also weak: the template
recited without being applied to their company, and promising to solve a problem you don't
yet understand.

- **Days 1–30, listen and map** — cross-functional interviews about friction with
  engineering, read ADRs and post-mortems, find silent breakages; deliver a one-pager
  *shared for feedback*, not declared as a plan.
- **Days 30–60, ship something small** — unblocks someone, fits inside current process,
  reviewable by the existing team.
- **Days 60–90, offer one improvement** — framed as a proposal tied to observed pain, not
  "how we did it at my last company".
- **Success** — you know how decision-makers think, you've shipped, and people tell you the
  real problems rather than the diplomatic version.

## The reverse interview is evaluated

Good questions show research (specific, not answerable from the website), altitude
(strategy, risk, culture — not perks), and standards (you are evaluating them). Pick 2–3 per
interviewer, write them down (reading from notes reads as prepared), and include at least
one due-diligence question. **Every good answer gets a follow-up** — that is where the
information is ("line-of-sight from signed contracts or active pipeline?"). Listen for what
isn't said: a CTO candidly admitting an eval-infrastructure gap is a culture signal and a
potential high-impact opportunity, not just a red flag.

High-yield questions: "What's the most expensive technical decision you'd revisit?"; "Is
there an eval gate for model or vendor changes?" (reveals eval maturity); "Where does
AI-generated code sit in review?"; "How do you decide what *not* to build?"; "What would
make the person in this role fail in the first year?"; "What's the runway, and what
milestone does the next raise depend on?"; "Who left recently, and why?" (asked kindly —
texture matters more than content).

## Due diligence before a startup offer

Runway at current burn and the specific milestone gating the next raise; leadership
departures in the last 12 months and stated reasons; engineering tenure; how the founder
handles strong internal disagreement; whether strategy changed in 12 months and why; what
investors and founders disagree on. Decide deal-breakers (comp floor, remote, mission fit)
*before* the round so answers register instead of washing past.

## Anti-patterns

No opinions; generic mission alignment; questions answered on their website; "I think I've
covered everything" (always have questions); capitulating under pushback; the
last-company reflex as the answer to everything; treating the founder round as a formality
when founders are usually the most candid source for evaluating the opportunity.

## See Also
- [[AI Role Interview Loop Map]] — extends (the reverse interview is one of the rounds self-made lists miss)
- [[System Design Interview Study Guide]] — prerequisite-for (judgment threads run on the design-round method)
- [[Product and Delivery Interview Study Guide]] — prerequisite-for (problem-first framing and metric trees for the HoP round)
- [[Customer Simulation Interview Study Guide]] — extends (FDE leadership rounds add a customer-executive flavor)
- [[Behavioral Interview Study Guide]] — alternative-to
