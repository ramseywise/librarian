---
title: LLM Judge Biases
tags: [eval, llm, concept]
summary: "Position, verbosity, self-preference, leniency, format/authority and capability limits — the documented ways LLM judges go wrong, each with a mitigation (both-order pairwise, different model family, binary criteria with tricky-FAIL examples), plus the pairwise-vs-pointwise and Elo/Bradley–Terry choices."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--05-llm-as-judge.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--12-failure-modes.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--references.md
---

# LLM Judge Biases

Zheng et al. (*Judging LLM-as-a-Judge*, MT-Bench, 2023) documented the biases that matter
most, and found strong judges agree with human preferences about as often as humans agree
with each other (over 80%) **once these are controlled**.

| Bias | What happens | Mitigation |
|---|---|---|
| **Position** | Pairwise judges favor the first (or second) answer | Run both orders; count a win only if it holds both ways, else a tie |
| **Verbosity** | Longer answers score higher, even padded | Rubric says length is not quality; include a short correct PASS example; track score vs. length |
| **Self-preference** | A model favors its own family's outputs | Judge with a different model family from the system under test |
| **Leniency** | Borderline cases pass | Binary criteria with explicit FAIL conditions; tricky-FAIL few-shot examples |
| **Format / authority** | Confident tone, markdown and citations look correct | Check citations in code; judge content, not style |
| **Limited capability** | Cannot verify what it cannot do (hard math, niche code) | Reference answer, code check, or a stronger judge |

Self-grading leans lenient: frame the prompt as grading a third party's work, never the
model's own.

## Judge prompt structure that resists them

**One judge, one criterion, binary verdict.** A judge asked about "quality" switches criteria
row to row. Structure: role (grading a third party) → precise PASS/FAIL definition → 2–4
labeled few-shot examples near the boundary (from human-labeled data, never the test split)
→ delimited inputs → **critique, then verdict** in a fixed format → a `CANNOT_GRADE` escape
for missing inputs, without which the judge guesses. Hard criteria (grounding, completeness)
are decomposed into per-claim or per-sub-question checks; G-Eval (Liu et al. 2023) has the
judge write its own evaluation steps first.

## Pointwise, pairwise, reference-guided

| Shape | Good for | Watch for |
|---|---|---|
| Pointwise (output + rubric) | Absolute gates, production monitoring | Drift in what "pass" means |
| Pairwise (A vs B) | Version comparison, model selection | Position bias |
| Reference-guided (output + gold) | Factual correctness | Accepting subtly wrong paraphrases |

Relative judgments are easier than absolute ones, so pairwise is more reliable for "which is
better" — but production has no second answer, so most systems use **pointwise for gates and
pairwise for A/B decisions**.

## Optimization amplifies self-preference: multi-family panels

When an agent is optimized against a judge it learns that judge's blind spots. The
mitigation is several judges from **different model families** on the same rubric; their
biases tend to be orthogonal, so the agent rarely fools all at once. Aggregate by weighted
average or required agreement; to cap cost, run one judge on every case and the full panel
as a periodic audit. This is the eval-side face of
[[Reward Hacking and Overoptimization]].

## Pairwise ranking: Elo and Bradley–Terry

With no absolute standard, many "A or B?" votes become a ranking.
[[Bradley-Terry Preference Model]] gives each system a latent strength; Elo is its online
update (start at 1000; a 1200-rated system is expected to beat a 1000-rated one ~76% of the
time; upsets move ratings more). Chatbot Arena ranks this way from blind human votes — and
the ranking reflects what users happened to ask. With an LLM voting, **swap order on every
pair**; and since Bradley–Terry assumes transitivity that judges often violate, check for
cycles before trusting the ranking.

## Beyond text

The pattern extends to other modalities — TTS via an audio model (or ASR then a text judge),
UI agents from screenshots, video from sampled frames — each with its own calibration set.

## See Also
- [[LLM-as-Judge Evaluation]] — extends (the failure modes of the judge primitive)
- [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] — related (measuring the residual error after mitigation)
- [[Specialist Verdict Panel]] — instance-of (one judge per criterion)
- [[Bradley-Terry Preference Model]] — prerequisite-for (the model behind Elo leaderboards)
- [[Reward Hacking and Overoptimization]] — related (optimizing against one judge)
- [[Positive-Only Judge Fixtures Measure Recall]] — extends
- [[Human Verdicts as Judge Fixtures]] — extends
- [[Human Agreement Ceiling Protocol]] — extends
