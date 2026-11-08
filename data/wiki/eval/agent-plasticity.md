---
title: Agent Plasticity
tags: [eval, concept]
summary: "A metric for self-improving agents defined as held-out score gain per unit learning cost; across board-game tasks one model had the highest fitted endpoint while another had the highest plasticity (298 points per $1,000 for GPT-5.6 Sol versus 57 for Claude Fable 5, self-reported), so endpoint score and learning efficiency can rank models differently."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-singh-2026-agent-plasticity.md
---

# Agent Plasticity

Singh et al. (arXiv 2610.08902, 2026) propose measuring an agent that learns from experience by its **plasticity**: held-out performance gain per unit of learning cost, P = (S_T − S_0) / C_T, in points per $1,000. The score can be negative, and falls once performance plateaus. Learning cost includes rejected reflection attempts and is priced in dollars at provider prices, which the authors call the closest available proxy; it is not a measure of physical computation.

## How it is measured

Agents play a task in checkpoints, reflect between checkpoints, and may write artifacts (tools, skills, memory) that carry forward, with model weights frozen. After each checkpoint the agent is scored on held-out games. A four-parameter saturating curve is fitted by binomial maximum likelihood, and the **saturation plasticity** (Psat) is the gain divided by cost at the first checkpoint where the fit reaches 90% of its rise. If the fitted rise is under 10 points, Psat is 0. If saturation is not seen within 3x the final cost, the paper reports "plasticity to date".

## Results (self-reported)

- **Endpoint and efficiency diverge.** Mean held-out in-distribution score over chess (Hard and Easy), Go (5x5) and Hex (6x6), 20 checkpoints: Psat was 298 for GPT-5.6 Sol, 233 for Claude Opus 5, 57 for Claude Fable 5 and 14 for Claude Opus 4.8, in points per $1,000. GPT-5.6 Luna showed no reliable rise (Psat 0). Fable 5 reached the highest fitted performance.
- **Hard chess.** Held-out in-distribution score, checkpoint 0 to the mean of checkpoints 16 to 20, against Stockfish 16 at 20k nodes: Fable 5 from 37.5% to 73.3%, Opus 5 from 25.0% to 66.4%, GPT-5.6 Sol from near 0% to 36.9%.
- **Other games.** Go and Hex gains were uneven: Opus 4.8 lost ground in Go while improving in Hex, and Opus 5 dropped sharply at the last Go checkpoint after a tool-making error.
- **NetHack.** Of six models over 41 checkpoints (10 seeded games per checkpoint), only Opus 5.5 showed a reliable gain, reaching saturation at checkpoint 11 with Psat 61.75 normalised points per $1,000 and a learning cost of $1,072.73 up to saturation. The extraction notes this figure is on a different scale from the board-game Psat values.
- **Artifact reuse.** Labelled offline by Gemini 3.1 Pro, the share of relevant chess decisions made without using an artifact was about 98% for Luna, 87% for Gemini 3.1 Pro, 51% for Opus 4.6 and 28% for GPT-5.5, against 2 to 6% for Fable 5, Opus 5, Opus 4.8 and Sol. For the strong improvers 83 to 99% of remaining failures happened while a relevant artifact was in use.
- **Local diagnostics can mislead.** In Go, Opus 4.8's share of successful reuse rose from 59 to 65% to 93% while its held-out score fell from 40% to between 10 and 25%.

## Limits

The authors state that plasticity belongs to an agent under a particular learning protocol, not to the model as an intrinsic scalar. Efficiency depends on provider pricing and on fit and extrapolation assumptions. The reuse and failure diagnostics are observational, and the design cannot separate environment feedback from the extra compute spent on reflection. Separate lineages do not show that artifacts transfer across tasks, held-out sets are finite, and in NetHack score changes mix learning with game difficulty (Opus 5.5's three best games give 69% of its checkpoint-10 total, and it scored 2.6 to 25 times the others at checkpoint 0). The extraction notes there is one lineage per model as far as the text says, no variance beyond bootstrap intervals, one LLM labeller with no human or second-judge check, feedback that differs by game (strong in chess, none in NetHack) so plasticity is not comparable across games, and that the abstract's "best need not be most efficient" rests on one pair of models.

Internal inconsistencies noted by the extraction: Psat units differ between figure and text and between board games and NetHack; Sol is the most plastic on board games but declines in NetHack (about 570 to 420); and the text says Sol surpasses Opus 4.8 in plasticity and eventual performance, although Sol's Hard chess score is 36.9%, which seems to rely on the combined three-game curve.

## See Also
- [[Self-Learning Agents]] — related (the learning mechanisms this metric scores)
- [[Eval Non-Determinism]] — related (repeat runs; here one lineage per model)
- [[Skill Lift Evaluation]] — related (another with-versus-without measure of what accumulated skills add)
- [[Agent Memory Types]] — related
