---
title: Spaced Repetition and Self-Quizzing From a Knowledge Base
tags: [foundations, concept]
summary: "Retrieving material beats rereading it at a delay but not immediately, and the best gap between sessions grows with how long you need to keep it; this wiki infers that a KB should ask recall questions and grade them later, with no credit for how a quiz scores straight after reading."
updated: 2026-11-05
sources:
  - data/raw/web/2026-11-05-testing-effect-and-spacing-research.md
  - data/raw/web/2026-11-05-citation-check-corrections.md
  - data/raw/web/2026-11-05-citation-check-corrections-third-pass.md
---

# Spaced Repetition and Self-Quizzing From a Knowledge Base

Two findings from learning research carry the idea. Testing yourself holds up better than rereading,
and spreading sessions out holds up better than massing them. Dunlosky et al. (Psychological Science in the
Public Interest, 2013) gave practice testing and distributed practice high utility ratings in a monograph on
learning techniques.

## The testing effect

Roediger & Karpicke (Psychological Science, 2006) had students study prose passages, then restudy or take a recall test.

| Test delay | Tested or repeatedly tested | Restudied | Effect |
|---|---|---|---|
| 2 days (Exp 1) | 68% | 54% | d=0.95 |
| 1 week (Exp 1) | 56% | 42% | d=0.83 |
| 1 week (Exp 2) | 61% | 40% | d=1.26 |

Five minutes after study the order flips. In Experiment 2, repeated study (SSSS) reached 83%, one test (SSST) 78% and
repeated testing (STTT) 71%. In Experiment 1 restudy reached 81% against 75% for testing (d=0.52). Karpicke & Roediger
(Science, 2008) sharpened the point with foreign-language vocabulary: once material had been learned, more study did
nothing for delayed recall, and more testing helped a lot. Rowland's 2014 meta-analysis (Psychological Bulletin) found
recall tests give larger benefits than recognition tests.

## The spacing effect

Across 839 assessments in 317 experiments, Cepeda et al. (Psychological Bulletin, 2006) found the gap that maximises
retention grows as the retention interval grows. Cepeda et al. (Psychological Science, 2008), with more than 1,350 people,
added the proportion: the best gap drops from roughly 20–40% of the delay when the test is a week away to roughly
5–10% when it is a year away. So the best single gap gets longer in absolute terms and shorter relative to the horizon.

That result picks one gap per learner for a given horizon. It is not evidence for successive gaps that widen. A
[[Flashcard Schedulers: Leitner, SM-2 and FSRS|scheduler]] widens gaps by design, on this wiki's reading, and the abstracts read here do not
establish that choice.

## Applied to a knowledge base

This section is this wiki's inference from the findings above, not a tested result.

- **Prefer recall to recognition.** Typed or self-graded answers from a page fit better than multiple
  choice, as in the [[Graded Rehearsal Drill Harness]], where the learner types every character.
- **Do not judge by the same-day score.** At five minutes restudy wins, so a quiz straight after reading
  scores worse than rereading while doing more for next week. The comparison that counts comes later.
- **Quiz again later.** Set the gap from how long the material must last. Widening the gaps across repeated
  reviews is, on this wiki's reading, the common scheduler design, not something shown here.
- **Separate durable from performative content.** Material for a date-bound round has a shorter horizon
  than durable knowledge, so it needs shorter gaps. See [[Durable vs Performative Knowledge Split]].

## What argues against it

The evidence is about people learning set material, in the 2006 paper students with prose passages. Only
that paper's text was read here; the others were read as abstracts. None of it tests questions generated from a personal wiki,
so the application above has no direct support. The 2006 paper also shows study beating testing at
five minutes, so this wiki infers that cramming is a real choice when the test is minutes away.

## See Also
- [[Flashcard Schedulers: Leitner, SM-2 and FSRS]] — extends (turning the spacing finding into due dates)
- [[Graded Rehearsal Drill Harness]] — instance-of (typed recall under a rubric)
- [[Durable vs Performative Knowledge Split]] — related (the horizon differs by kind of knowledge)
- [[Technical Breadth Round Playbook]] — related (one use of recall cards)
