---
title: LLM-as-Judge Evaluation
tags: [eval, llm, pattern]
summary: A separate LLM scoring outputs against a rubric — the approach for subjective quality where exact matching fails, requiring calibration against human grades and recommended as a complement to golden-set grading rather than a replacement.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-luong-2025-towards-robust-mathematical-reasoning.md
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-divergence-since-diskoe-mvp.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-divergence-since-diskoe-mvp.md
  - data/raw/claude-docs/akira/docs/technical-feasibility.md
  - data/raw/claude-docs/diskoe/docs/technical-feasibility.md
  - data/raw/claude-docs/playground/docs/technical-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/technical-feasibility.md
  - data/raw/claude-docs/akira/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-26-venue-dataset-review-findings.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--05-llm-as-judge.md
  - data/raw/papers/2026-11-05-you-2026-agent-as-judge.md
  - data/raw/papers/2026-11-05-li-2026-jev-as-judge.md
  - data/raw/papers/2026-11-08-chiang-2023-can-large-language-models-be.md
  - data/raw/papers/2026-11-08-gu-2024-survey-llm-as-judge.md
---

# LLM-as-Judge Evaluation

A separate LLM call evaluates output against criteria (relevance, accuracy, helpfulness,
tone), scoring on a scale or pass/fail. More flexible than heuristic grading, but more
expensive and more variable.

**Use when** output quality is subjective (summaries, drafts, recommendations); you need
to evaluate tone, completeness, or style; you want automated scoring but can't define
correctness by string match; you're evaluating *generation* rather than *retrieval*.

**Avoid when** correctness is objectively definable — use [[Golden Set Mechanics]] instead,
cheaper and more reliable; budget is tight; or you need deterministic results.

## Calibration is the setup cost

The step that distinguishes a working judge from a plausible one:

1. Write 3–5 quality criteria (*"Is the summary under 200 words? Does it include all
   action items? Is the tone professional?"*).
2. Create 5–10 sample inputs with human-graded "good" outputs.
3. Write a judge prompt scoring against the criteria.
4. **Run the judge on the sample set and calibrate until it agrees with human grades.**

Step 4 is what makes the scores mean anything. An uncalibrated judge produces numbers that
look like measurements but track the judge's priors — see
[[LLM Grader Calibration Insights]].

## Complexity

**Multi-sprint** — needs a rubric, a judge prompt, calibration samples, and eval-runner
integration.

## Scaffold mapping

| Parameter | Value | Rationale |
|---|---|---|
| `optional_features` | `[ragas]` | RAGAS provides LLM-judge grading infrastructure |
| `optional_features` | `[promptfoo]` | Promptfoo supports LLM-as-judge via config |

Both integrate *alongside* — not replacing — heuristic golden-set grading.

## Trade-offs

**Pro:** evaluates subjective quality; flexible criteria; catches subtle tone/style
regressions.
**Con:** costs money per run; non-deterministic (identical input may score differently);
requires calibration; **the judge can simply be wrong**.

**Recommendation:** *"Use as a complement to golden-set, not a replacement. Run heuristic
grading (free, fast) in CI; run LLM-judge on demand for quality audits."* The cost and
non-determinism make it a poor fit for a per-PR gate.

## The trust ceiling is human–human agreement

A decision log from an LLM-ranked consumer product (akira) states the limit precisely: a
judge's agreement with human raters cannot be trusted above the agreement measured *between*
those raters on the same instrument. If humans agree at kappa 0.6, a judge reporting 0.8
against one rater is measuring that rater, not the truth. Consequences adopted there:

- the judge is a **regression detector, never a launch gate** — it flags movement between
  prompt versions; humans decide whether the movement is real;
- items the judge cannot classify fail safe to `needs_human_review` rather than to a score;
- a fixed fraction (~25%) of judge critiques is sampled for human review on an ongoing basis,
  so the ceiling itself is re-measured rather than assumed.

The storage side of that measurement — keeping every human rating so agreement stays
computable — is [[Append-Only Human Labels]].

## Judge Choice Can Dominate the Number

In a venue-enrichment dataset review (repo akira, 2026-09-26), **the same 200 probe
outputs passed at 0.96 under one judge model and 0.25 under another**. The judge choice
moved the pass rate about four times more than swapping the probe model did. A third
judge run failed outright (1 of 200 rows ok), and cheaper probe models invented
attributes on 60–75% of rows under any judge. Consequence: **no judge threshold may be
written until one judge is calibrated against a human-anchored set** (see
[[Human Agreement Ceiling Protocol]]). Before then, judge pass rates across models are
not comparable, and quoting one as quality is meaningless.

## Calibration and bias (course synthesis, 2026-10)

The 06-eval course treats a judge as a classifier to be measured: 100–200 human labels split
train/dev/test, TPR and TNR on the held-out split, and a bias-corrected pass rate — see
[[Judge Calibration (TPR, TNR and Corrected Pass Rate)]]. Known judge biases (position, verbosity,
self-preference) and their mitigations are on [[LLM Judge Biases]]. Under that procedure a judge in the
`calibrated` state may gate a release at its calibrated threshold.

The two bars apply at different stages. The 5–10-sample calibration above is a
**discovery-stage smoke test** for a rubric, and a judge at that stage is a regression
detector only. Before a judge may gate a release it needs the full procedure: 100–200 human
labels, TPR/TNR on a held-out split, and a human inter-rater agreement measured high enough
that the judge's agreement means something ([[Human Agreement Ceiling Protocol]]). Where
that ceiling is low — as in the product above — the judge stays ungated whatever its
calibration says.

## Agent-as-a-Judge (survey)

You et al. (arXiv 2601.05111, 2026) is a survey with no experiments or numbers of its own. The
authors argue that a single-pass LLM judge has three weaknesses: bias from its own parameters
(verbosity, favouring patterns like its own output), no way to check a claim against the world,
and coarse scores when a rubric has many dimensions. Their remedy is a judge that plans, calls
tools (code execution, search, provers), keeps memory and may use several cooperating agents. They
sort such judges into three stages: procedural (a fixed workflow or debate between fixed roles),
reactive (tool calls and routing chosen from interim feedback) and self-evolving (rubrics
and memory that change as the judge runs). They also say agentic judging costs more, is slower, opens more
room for attack and can magnify judge bias if its output is used as a reward. Limits: the survey offers no
evidence that agentic judges match humans better than single-pass ones, states no inclusion criteria, concedes
that many "agent" judges are fixed role-play prompts, and does not say how to validate an
agentic judge itself. Trained and cheaper variants are on [[J1 Reinforcement-Learned Judge]],
[[Prometheus 2 Evaluator Models]] and [[JEV-as-a-Judge Cascade]]; a logprob-weighted scorer is
[[LLM-as-a-Verifier]].

## Human-evaluation replacement and a survey's own experiment (2023-2025)

Chiang and Lee (ACL 2023) gave text-davinci-003 and ChatGPT the same instructions, samples and 1-5 Likert questions that human evaluators get, and compared them with three English teachers on 200 human-written and 200 GPT-2-medium stories (WritingPrompts) and on adversarial-attack text. In their setup text-davinci-003 gave human-written stories higher grammaticality ratings than GPT-2 stories, as the teachers did, and cost less (self-reported). Its per-story agreement with teachers was strongest on relevance and weakest on grammaticality. Lowering temperature to 0 slightly lowered ratings but kept the ordering, and a persona or an explain request changed grammaticality and cohesiveness ratings by under 0.1. Limits: only two tasks, English, three teachers, two instruction variants; ChatGPT ran through its web interface, one sample each, with scores read manually; Kendall tau against the teachers was only 0.12 to 0.22 on grammaticality, cohesiveness and likability; the models are deprecated, and the authors call LLMs unsuitable for factual tasks.

Gu et al. (arXiv 2411.15594, a survey) frame a judge as E <- P_LLM(x (+) C) and add a small meta-evaluation of their own: one run per cell at temperature 0, on LLMEval2 (2,553 samples with swapped positions) and EvalBiasBench (80 samples in all, with 24 to 34 for each bias). GPT-4-turbo reached 61.54% agreement with human labels there, and all judges were weak on human-tie labels (self-reported). Numbers by bias are on [[LLM Judge Biases]]. Their recipe for pairwise judging is a stronger model, swapped positions and a majority vote over several rounds. Limits: the experiment has no intervals or significance tests, uses percentage agreement only (no kappa) and prints no judge prompts; text and tables differ in a few decimals; the authors give causes for the explanation and self-validation results as speculation, and say current meta-evaluation is insufficient.

Judges that score by token probability instead of a generated verdict are [[GPTScore]]; prompted translation scoring is [[GEMBA Translation Quality Prompting]]. Trained open judges are [[PandaLM]], [[Self-Taught Evaluators]] and [[TIR-Judge]] (a judge that runs code). Running a judge in production is [[Judge Lifecycle with RART and a Drift Band]], and the calibration for order flips is [[Position Bias Calibration (MEC, BPC, HITLC)]].

## See Also
- [[Generative Search Engine Verifiability Audit]] — related (human audit of citation support)
- [[PaperBench]] — related (a judge validated against human leaf labels)
- [[DataSpace]] — related (a model-free table comparison used instead of a judge)
- [[FINDER and DEFT (Deep Research Agent Failures)]] — related (judge and reference report from the same vendor)
- [[Gaia2]] — related
- [[SAFE Long-Form Factuality Scoring]] — related (an LLM-plus-search judge validated against human labels)
- [[Shepherd Critic Model]] — related
- [[Eval vs Test Distinction]] <!-- auto-linked -->
- [[Eval Ladder]] — related (part of; rung 3)
- [[Golden Set Mechanics]] — related (heuristic in CI, judge on demand)
- [[LLM Grader Calibration Insights]] — extends (calibration failure modes)
- [[Manual Review as Eval Bootstrap]] — prerequisite-for (human grades calibrate the judge)
- [[Eval Maturity Ladder]] — related (part of; one of four layered grader types; source of the three judge biases)
- [[Online Eval Sampling]] — extends (the judge as layer 2 over production traces)
- [[Eval Harness Anatomy]] — related (part of; one of the three grader types under the simplest-reliable rule)
- [[Constitutional AI and RLAIF]] — instance-of (the same judge primitive used to generate training labels)
- [[Bradley-Terry Preference Model]] — related (pairwise comparison formalized as a scalar)
- [[Append-Only Human Labels]] — prerequisite-for (human labels set the judge trust ceiling)
- [[IMO-Bench]] — related (autograders for answers and proofs checked against expert grades)
- [[Human Agreement Ceiling Protocol]] — prerequisite-for (κ_judge ≥ 0.8 × κ_HH, not an absolute target)
- [[Synthesize the Cheap Half]] — related (gold-set calibration, closed-loop and stratum-bias rules for synthesized labels)
- [[Confidence That Is Not a Probability]] — related (another score that needs independent labels before it can gate)
- [[Specialist Verdict Panel]] — extends (one judge split into single-dimension specialists with structured verdicts)
- [[Answer Criteria with Named Wrong Answers]] — extends (per-topic fail-if lists as the rubric)
- [[Positive-Only Judge Fixtures Measure Recall]] — extends (recall vs precision of a judge fixture set; one calibration pass)
- [[Closed Judge Vocabulary, Tolerant Parse]] — related (closing a judge's free-text issue list without brittle enum parsing)
- [[Demote Judge Findings to Keyless Gates]] — extends (regex-catchable findings leave the judge for a keyless 1.0 gate; missing-verdict re-ask; calibration floor)
- [[Judge Sees the Drafter's Facts]] — extends (reference facts so restating a given score is not scored ungrounded)
- [[Grader States (Heuristic, Calibrated, Experimental)]] — extends
- [[SOMA Judge Rubric]] — extends (specific, ordinal, multi-aspect rubric; never reveal self-grading)
- [[Verification Loops]] — instance-of
- [[HITL Annotation Pipeline]] — related (LLM annotators against crowd workers on text-annotation tasks)
- [[Silicon Sampling and Algorithmic Fidelity]] — related (an LLM standing in for human respondents)
- [[MetaCrit Adaptive Critique]] — related (a monitor and controller that decide how hard to critique)
- [[LLM-as-a-Verifier]] — extends (score-token expectation instead of a discrete verdict)
- [[J1 Reinforcement-Learned Judge]] — extends (a judge trained with RL)
- [[Prometheus 2 Evaluator Models]] — extends (an open trained evaluator)
- [[JEV-as-a-Judge Cascade]] — extends (a cheap judge that escalates when unsure)
- [[FLASK Skill-Set Evaluation]] — extends (per-skill rubrics)
- [[GAMUT Meta-Rubric Benchmark]] — extends (structured rubrics compiled to binary checks)
- [[GPTScore]] — alternative-to (a probability score instead of a generated verdict)
- [[GEMBA Translation Quality Prompting]] — instance-of (an LLM judge scoring translations)
- [[PandaLM]] — extends (an open judge trained on distilled labels)
- [[Self-Taught Evaluators]] — extends (a judge trained on synthetic pairs)
- [[TIR-Judge]] — extends (a judge that runs code)
- [[Judge Lifecycle with RART and a Drift Band]] — extends (judge in production, with a drift trigger)
- [[Position Bias Calibration (MEC, BPC, HITLC)]] — extends (calibrating the pairwise judge for answer order)
- [[Ragas Reference-Free RAG Metrics]] — instance-of (reference-free LLM-prompted RAG metrics)
- [[LiveMCP-101]] — related (a judge checked against humans and other judges)
- [[UQ Unsolved Questions Benchmark]] — related (validators used as judges where no gold answer exists)
- [[Knowledge Index and Information Gain]] — related (an LLM judge splits and scores reasoning steps)
