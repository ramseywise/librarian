---
title: LLM Judge Biases
tags: [eval, llm, concept]
summary: "Position, verbosity, self-preference, leniency, format/authority and capability limits — the documented ways LLM judges go wrong, each with a mitigation (both-order pairwise, different model family, binary criteria with tricky-FAIL examples), plus the pairwise-vs-pointwise and Elo/Bradley–Terry choices."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--05-llm-as-judge.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--12-failure-modes.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--references.md
  - data/raw/papers/2026-11-05-whitehouse-2025-j1.md
  - data/raw/papers/2026-11-05-ye-2023-flask.md
  - data/raw/papers/2026-11-06-chen-2026-two-level-meta-rubrics-evaluating.md
  - data/raw/papers/2026-11-08-wang-2024-large-language-models-not-fair.md
  - data/raw/papers/2026-11-08-gu-2024-survey-llm-as-judge.md
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

## Measured examples (self-reported by the papers)

- **Position.** J1-Llama-70B, trained as a judge, flipped its verdict on 21.9% of PPE Correctness
  pairs when answer order was swapped; an untrained Llama-3.1-8B flipped on 44.1%
  ([[J1 Reinforcement-Learned Judge]]).
- **Position, pairwise order swaps.** On 80 Vicuna questions, ChatGPT as judge let Vicuna-13B beat ChatGPT on 66 queries by reordering alone; GPT-4 favoured the first position (51.3% win rate as Assistant 1, 23.8% as Assistant 2) and ChatGPT the second (2.5% against 82.5%) ([[Position Bias Calibration (MEC, BPC, HITLC)]]).
- **Survey meta-evaluation.** Gu et al. ran six standard judges at temperature 0 on swapped-position pairs (LLMEval2 and EvalBiasBench): position consistency was 80.31% for GPT-4-turbo, 68.78% for GPT-3.5-turbo and 38.85% for LLaMA3-8B. On the EvalBiasBench length subset (n=34) GPT-3.5-turbo scored 20.59% against 91.18% for GPT-4-turbo. Requesting an explanation alongside the verdict cut GPT-3.5-turbo's consistency under position swaps from 68.78% to 48.97%; a 5-round majority vote lifted it only to 70.11%. One run per cell, no intervals; the authors call the explanation result a speculation about deeper biases, and it was tested on GPT-3.5-turbo only (self-reported).
- **Length.** FLASK skill scores correlated 0.737 with response length for
  completeness but 0.147 for logical correctness ([[FLASK Skill-Set Evaluation]]).
- **Self-scoring.** In GAMUT, Qwen3-VL 235B as judge gave itself 44.0 against 33.0 from a Gemini
  judge, while Gemini and Claude Opus 4.8 judges produced identical rankings
  ([[GAMUT Meta-Rubric Benchmark]]).

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
- [[Shepherd Critic Model]] — related (GPT-4 Likert versus pairwise against human ratings)
- [[LLM-as-Judge Evaluation]] — extends (the failure modes of the judge primitive)
- [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] — related (measuring the residual error after mitigation)
- [[Specialist Verdict Panel]] — instance-of (one judge per criterion)
- [[Bradley-Terry Preference Model]] — prerequisite-for (the model behind Elo leaderboards)
- [[Reward Hacking and Overoptimization]] — related (optimizing against one judge)
- [[Positive-Only Judge Fixtures Measure Recall]] — extends
- [[Human Verdicts as Judge Fixtures]] — extends
- [[Human Agreement Ceiling Protocol]] — extends
- [[Output Length Confounds Reference Metrics]] — related (length control as a verbosity mitigation)
- [[Tool-Augmented Factuality Checking]] — related (outside evidence instead of a lenient self-check)
- [[J1 Reinforcement-Learned Judge]] — extends (a consistency reward aimed at position flips)
- [[FLASK Skill-Set Evaluation]] — related (length and grader-preference evidence)
- [[Prometheus 2 Evaluator Models]] — related (bias analysis not done there)
- [[Position Bias Calibration (MEC, BPC, HITLC)]] — instance-of (position bias, measured and calibrated)
- [[Self-Taught Evaluators]] — related (answer order alone swung one judge's RewardBench score by 5.6 points)
- [[Taste-Bench]] — related (both-orders scoring against position bias)
- [[FACTS Leaderboard]] — related (concedes judge self-preference and averages two judges to reduce it)
- [[HITL Annotation Pipeline]] — related (LLM annotators compared with crowd workers, with the Gilardi limits)
- [[Medprompt]] — related (a choice-shuffle ensemble that targets option-order bias)
- [[AlpacaFarm Simulated Human Feedback]] — related
- [[BBQ Bias Benchmark]] — related
- [[Chain-of-Thought Unfaithfulness Under Biased Context]] — related
- [[ChatEval Multi-Agent Debate Judges]] — related (diverse judge personas)
- [[Arena-Hard-Auto and BenchBuilder]] — related (measures self-preference and style effects)
