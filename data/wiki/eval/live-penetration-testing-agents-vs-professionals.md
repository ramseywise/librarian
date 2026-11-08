---
title: Live Penetration Testing of Agents and Professionals
tags: [eval, comparison]
summary: "Lin et al. ran AI agents and 10 professionals on a live university network (about 8,000 hosts); the authors' own ARTEMIS scaffold ranked second of 15 entries, scoring 95.2 against 111.4 for the best human, with one run each and no statistical testing (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-lin-2025-comparing-ai-agents-cybersecurity-professionals.md
---

# Live Penetration Testing of Agents and Professionals

Lin et al. (arXiv 2512.09882, 2025; ICLR 2026 is listed in the extraction header but the
paper prints no venue) compared agents with people on a real target: a university network of
about 8,000 hosts across 12 subnets. Ten recruited professionals (self-reported credentials)
each used an identical Kali VM, a student-level account and a flat fee of $2,000, and were asked
to commit at least 10 working hours. The research group triaged findings with IT staff, who
were aware of the exercise and approved flagged actions by hand.

## Scoring

Each valid finding scores its technical complexity plus a severity weight (8, 5, 3, 2 and 1
from Critical to Informational); verified-but-unexploited findings are penalised. The authors
wrote the rubric from industry standards and consultation with the target organisation, and state
that assessing penetration-test quality is inherently subjective.

## Results (self-reported, one run per agent)

- **Ranking.** The authors' scaffold, ARTEMIS (variant A2, an ensemble of supervisor models),
  placed second of 15 entries: a total of 95.2 points against 111.4 for the top human, 9 valid findings
  from 11 submissions (82% valid), first 10 of 16 hours scored. It outperformed 9 of 10 humans.
- **Scaffold over model.** GPT-5 beat 5 of 10 humans inside ARTEMIS (variant A1), 2 inside
  Codex, and was beaten by every human inside CyAgent.
- **Cost.** A1 cost $291.47 over the 16-hour window ($18.21 an hour) and A2 $944.07 ($59 an
  hour); the human comparison figure is a salary from a job site. The headline "$18 against $60"
  takes the cheaper configuration's cost but the second-ranked one's placement.
- **Validity and gaps.** A1 had 55% valid submissions and A2 82%, against 100% for eight of ten
  humans. 80% of humans found a remote-code-execution flaw on a Windows machine reached through a
  GUI tool, an interaction ARTEMIS struggled with.
- **Zero scores.** Claude Code and MAPTA refused the task and Incalmo stalled in early
  reconnaissance, each finding nothing.

## Limits

The authors concede sample sizes were too small for hypothesis testing and that time frames were
compressed. There are no repeated runs or intervals; Codex and CyAgent stopped early. Nobody
reports inter-rater agreement or blinding, and the authors scored their own agent. By
severity score alone another human leads and A2 is second, and the ranking depends on the
complexity term. Costs omit the researcher who supervised every agent session and the IT monitor. Time budgets are stated inconsistently, one human did reconnaissance before the clock
started, and the paper does not say whether the agents ran before or after the humans' findings were
fixed. The models are all from 2025 (o3, Gemini 2.5 Pro, GPT-5 and two Claude 4 models). The
authors' funding includes an unrestricted gift from OpenAI.

## See Also
- [[Extreme-Risk Model Evaluation]] — related (cyber-offense is one of its listed dangerous capabilities)
- [[Holistic Agent Leaderboard (HAL)]] — related (scaffold changed outcomes there too)
- [[Eval Error Bars and Sample Size]] — related (one run each, no intervals)
