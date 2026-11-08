---
title: MetaCrit Adaptive Critique
tags: [prompting, pattern]
summary: "A four-call pipeline (generator, read-only monitor, controller, synthesizer) that scales critique to the answer instead of always critiquing; in its paper, appending a plain critique instruction to every baseline made accuracy collapse, while the graded pipeline reached 94.12 on TruthfulQA with GPT-3.5-Turbo (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-hou-2025-knowing-when-critique.md
---

# MetaCrit Adaptive Critique

MetaCrit (Hou et al., arXiv 2507.15015, a preprint now at v4) asks whether critique helps a model reason or only changes answers that were already right. It runs four calls on every input. A generator answers. A monitor, which only reads, questions whether the answer is valid; its prompt asks, in effect, whether the question has one objective answer settled by science or fact. A controller then critiques, and a synthesizer merges the results. "Adaptive" here means the strength of intervention varies inside a fixed pipeline: nothing is gated and no stage is skipped.

All figures below use GPT-3.5-Turbo unless stated, with one run per cell and no seeds reported. TruthfulQA (n=817) is scored by a GPT-4o judge and CIAR (n=50) by two human annotators.

- **Raw critique hurts.** Appending a one-sentence critique instruction ("distinguish trick questions if needed") to eight baselines lowered all of them. Self-refine fell from 75.89 to 18.23 on TruthfulQA (-76.0%) and Multi-Expert Prompting (MEP) from 89.35 to 27.66 (-69.0%) (self-reported). The authors attribute this to critique that fires on every input whether or not the answer was sound, so it over-corrects.
- **Headline accuracy.** MetaCrit scored 94.12 on TruthfulQA and 84 on CIAR, against 70.38 and 24 for zero-shot chain-of-thought, 89.35 and 82 for MEP, and 94.97 and 84 for o1 (self-reported).
- **Other monitor-and-control loops.** Baselines scored (TruthfulQA, then CIAR): Metacognitive Prompting 67.73 and 44, MGV 51.83 and 32, ReMA 52.32 and 32, SOFAI-LM 64.79 and 40. On GPT-4o these baselines are far closer to MetaCrit, and the authors concede its margin is largest where regulation has work to do.
- **Ablation (TruthfulQA).** Without the monitor 75.28; without the controller 76.62; full pipeline 94.12 (self-reported). When only the monitor flags a problem, accuracy is 64.0, against 94.12 when both flag it.
- **Significance.** On TruthfulQA the 94.12 has a 95% interval of 92.3 to 95.5 and beats MEP at p<.001. On CIAR the 84 against 82 is not significant (n=50, p=.79), so there it matches MEP rather than beating it.
- **Cost.** About 4,000 tokens, about 10 s and $2.00 per 1,000 queries, against $0.40 for zero-shot chain-of-thought, $1.60 for MEP and $12.00 at about 30 s for o1. These are estimates averaged over 100 TruthfulQA queries.
- **What it cannot fix.** Of 48 TruthfulQA errors, 27 (56.3%) were "consensus collapse", where every agent converged on the same wrong answer, and 13 (27.1%) were knowledge gaps.

## Limits

By the authors' own account, the TruthfulQA scoring uses a GPT-4o judge, CIAR has just 50 items, the safety evaluation covers English only, and the baselines are limited to training-free methods on closed-weight models. The extraction adds that GPT-3.5-Turbo is a weak, dated backbone, that the raw-critique baseline is a single sentence (it tests where critique is placed, not how good it is), and that Table 1 mixes numbers reproduced from earlier papers with the authors' own runs while its caption says all rows share one setup. It contains no evaluation of agents, tool use or trajectories.

Internal inconsistencies found by the extraction: the CrowS-Pairs ablation text says removing the controller improves accuracy (82.07 against 79.08), but the table gives 82.07 for the full pipeline and 79.08 without it. In the drop-in table, MEP plus the controller gets 94.24 for TruthfulQA and 96 for CIAR, above full MetaCrit on CIAR (84), which does not square with "highest of all twelve baselines". In the failure-analysis table the TruthfulQA rows add up to n=204 rather than 817, and the CIAR rows to 12 rather than 50. The text says general models reach 24 to 60% on CIAR, while the model table gives gpt-4o 74 and Claude-3.5-Sonnet 76. The extraction's weighted reading of those rows gives about 80%, not 94.12. The table gives 94.12 for the both-flag row, whereas the text gives 95.12.

The extraction also notes that the preference rates in Appendix L.2 do not match Table 4, that the worked CIAR failure cases in Appendix H have garbled arithmetic, that the survey repeats questions (Q25 matches Q22, and Q26 and Q27 match Q23 and Q24), and that the paper calls MetaCrit preferred overall although it is preferred on only two dimensions. It also records that the reading ledger files this paper's arXiv id under a different title (MCPEval) with a rationale the paper cannot support.

## See Also
- [[Reflexion]] — related (another critique-then-revise loop; Reflexion relies on an external evaluator)
- [[Chain-of-Verification]] — related (a verification pass over the model's own answer)
- [[RLMF Metacognitive Advantage Scaling]] — related
