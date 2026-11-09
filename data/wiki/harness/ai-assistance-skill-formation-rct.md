---
title: AI Assistance Skill Formation RCT
tags: [harness, pattern]
summary: "A randomized trial with 52 Python developers learning an unfamiliar library found that those given a GPT-4o chat assistant scored 4.15 of 27 points lower on a follow-up quiz (about 17%) with no significant speed-up (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-shen-2026-how-ai-impacts-skill-formation.md
---

# AI Assistance Skill Formation RCT

A 2026 preprint tests whether AI help during learning costs the learner skill. Setup: 52 Python developers (26 per arm) learned the Trio asynchronous library in a task with a 35-minute cap; one arm had a GPT-4o chat assistant, the control had none. A quiz of 27 points followed.

## Results (self-reported)

- Quiz gap of 4.15 points of 27 (about 17%) against the assistant arm (Cohen's d = 0.738, p = 0.010).
- Completion-time speed-up was not significant (p = 0.391).
- Exploratory: the gap was largest on debugging questions and smallest on code reading.
- Six interaction patterns were identified: three scored under 40% on the quiz and three scored 65% or more. Clusters are tiny (n = 2 to 7).

## Limits

- Small sample, one library, one short session, one assistant model.
- Pattern clusters are too small to support the pattern claims; the extraction notes the pair-to-pattern mapping is its own inference.
- The extraction notes inconsistent figures: "up to 15 queries / more than 30% of time" against "up to 11 minutes" in one section and "10 minutes" in another; only 4 control-arm comments are legible.
- The paper reports errors, pilot studies and a recruitment-platform compliance issue.

## See Also

- [[Prompt Injection]] — related
