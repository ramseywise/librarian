---
title: Prompt Optimization
tags: [prompting, eval, concept]
summary: Treat the prompt as a versioned artifact searched against a fixed eval set and metric — by hand (cheapest layer first, one change at a time), by an LLM proposer (APE, OPRO, meta-prompting) or by a framework (DSPy, TextGrad); an optimizer without a metric is just a rewriter.
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--07-prompting-reasoning-models.md
  - data/raw/papers/2026-11-06-ramnath-2025-systematic-survey-automatic-prompt-optimization.md
  - data/raw/papers/2026-11-06-lakshmanan-hapke-genai-design-patterns-ch06-improving-reliability.md
  - data/raw/papers/2026-11-07-yang-2023-large-language-models-as-optimizers.md
  - data/raw/papers/2026-11-08-ein-dor-2024-conversational-prompt-engineering.md
  - data/raw/papers/2026-11-07-zhou-2022-large-language-models-human-level.md
  - data/raw/papers/2026-11-06-wen-2023-hard-prompts-made-easy.md
  - data/raw/papers/2026-11-07-agrawal-2025-gepa.md
  - data/raw/papers/2026-11-07-singh-2026-coding-agents-strong-prompt-optimizers.md
  - data/raw/papers/2026-11-08-shin-2020-autoprompt.md
---

# Prompt Optimization

```
template v1 → run on eval set → score → propose changes → template v2 → keep if it beats …
```

The proposer can be a human, an LLM, or a framework. What matters is the same in every
case: **a fixed eval set, a metric, and a record of every version** ([[Evaluating Prompts]]).

## Prompts as versioned artifacts

- Version the **template**, not the rendered string ([[Prompt Templates and Variables]]).
- Store it like code (repo or registry) with ID, version, the model it was tuned on and its
  eval score. **Pin the model version** — prompts are not portable across models.
- **Diff behaviour, not text**: a one-word change can move scores; regression-test every edit.
- Log production I/O per prompt version — tomorrow's eval set and optimizer training data.

## LLM as proposer

- **APE** (Zhou et al., 2022): an LLM drafts candidate instructions from input/output
  demonstrations, each is scored on the target model (e.g. by log-probability of correct
  outputs), winners are resampled. It found a zero-shot CoT trigger that beat "Let's think
  step by step" on arithmetic benchmarks.
- **OPRO** (2023): the LLM optimizer sees past prompts and their scores in context.
- **Prompt-OIRL**: offline inverse RL to pick query-dependent prompts.
- Gradient-based search (AutoPrompt, prefix and prompt tuning) needs model access and
  borders on [[Fine-Tuning as Prompt Compression]]. [[PEZ Gradient-Based Hard Prompt Discovery]]
  finds discrete vocabulary tokens (often unreadable) by projecting a continuous prompt onto the vocabulary.
- **Reflective evolution:** [[GEPA Reflective Prompt Evolution]] has a model read run traces in
  natural language and keeps a Pareto frontier of candidates; [[Coding-Agent Skill Distillation (CASD)]]
  uses a coding agent as the optimizer and compares itself against GEPA.

The lesson is not the magic phrases — model-specific and dated — but that **search
against a metric beats intuition** once you have one.

## Meta-prompting (two senses)

1. **Structure-oriented prompting** (Zhang et al., 2024): give an abstract solution
   *template* for a class of problems instead of worked examples. Token-efficient, avoids
   example anchoring ([[Few-Shot Prompting]]), behaves like zero-shot; degrades on
   genuinely novel domains.
2. **A model writing prompts** — the common sense in practice: a strong (often reasoning,
   [[Prompting Reasoning Models]]) model drafts a system prompt or critiques and rewrites
   one given failing cases; vendor prompt generators/improvers do this. The
   evaluator–optimizer loop automates it: a judge scores and writes feedback, a meta-prompt
   turns feedback into a revised prompt. Generated prompts are **a first draft, not a
   result** — they must still win on the eval.

## Frameworks

[[DSPy]] compiles signature-and-module programs against a metric (few-shot selection,
instruction search, distillation); TextGrad propagates LLM-written critiques ("textual
gradients") back through a pipeline. Worth it for multi-step pipelines with a scorable
metric and dozens to hundreds of labelled examples; skip for one-off prompts.

## Manual checklist

1. Find the **failure category** in eval results — format, missing context, wrong
   reasoning, instruction ignored.
2. Fix the **cheapest layer first**: instruction clarity → missing context → ordering →
   examples → CoT → splitting the task ([[Prompt Chaining]]) → stronger model → fine-tuning.
3. **Change one thing at a time** and re-score.
4. **Keep the losers** so you don't retry them.

## Survey taxonomy (Ramnath et al.)

A 2025 survey from AWS authors (arXiv 2502.16923, preprint) frames automatic prompt optimisation as choosing the prompt that scores best on average over a validation set, for a task model reachable only as a black box; it calls exact search over discrete tokens intractable, so methods approximate. It reports no experiments of its own; every method result belongs to the primary papers. It splits a method into five choices:

1. **Seed prompts:** hand-written instructions, or instructions induced by an LLM from input-output demonstrations.
2. **Evaluation and feedback:** numeric (task accuracy, reward-model score, entropy, output log-likelihood), LLM-written feedback on one or several candidates, or human feedback.
3. **Candidate generation:** heuristic edits (Monte Carlo sampling, genetic algorithms, word-level edits, vocabulary pruning), an auxiliary trained network (RL, fine-tuned rewriter, GAN), metaprompt design (OPRO), coverage-based expansion or ensembles, and program synthesis (DSPy).
4. **Filter and retain:** top-K greedy, bandit selection such as UCB, region-based search, or a metaheuristic ensemble.
5. **Iteration depth:** a fixed number of steps in most methods, or variable with a patience or reward threshold.

Its only cost figure compares optimising a system prompt (about 60 hours for SPRIG, given without model or hardware) with about 10 minutes per task for ProTeGi (self-reported). It credits APE with showing a few hundred examples can be enough to seed optimisation. Failure modes it lists: LLM self-reflection can misidentify errors and fail to improve a prompt; uninterpretable "evil twin" prompts can recover some of a good prompt's performance; entropy and likelihood scoring need output probabilities that black-box APIs often withhold; and feedback adds an LLM call per step. On theory, only an upper bound on the gain exists, no lower bound. Open problems it names: task-agnostic optimisation (methods assume a known task and an eval set), system prompts and agents, and multimodal prompts.


## A book example: best-of-N and a reference-comparison judge

Lakshmanan and Hapke (Generative AI Design Patterns, 2025) describe the optimiser as a pipeline, a dataset (possibly one example), an evaluator and an optimiser that returns the best-scoring prompt per step, rerun each time the model or some other dependency changes. Their illustration is one run rewriting a book blurb with DSPy on claude-3-7-sonnet: the baseline rewrite scored 0.63 and best-of-10 reached 0.74 (self-reported), both from an LLM judge of the same style with no human check, and best-of-N costs N inference calls. They recommend a judge that compares the rewrite with the original as a reference, because separate absolute scores such as 0.89 and 0.90 (self-reported) cannot be trusted to rank (an anecdote, not a measurement). A few-shot variant (BootstrapFewShot) is described but not scored.

## OPRO and conversational prompt building

Yang et al. (2023) give an LLM optimizer a meta-prompt holding the best 20 solutions so far with their scores, and sample 8 candidates per step. With a PaLM 2-L scorer on GSM8K, an instruction beginning "Take a deep breath" scores 80.2, where "Let's think step by step" gets 71.8; the best instructions transfer to MultiArith (95.3) and AQuA (54.3) (self-reported). Training accuracy runs 5 to 20 points above test, text-bison shows no clear win, and the extraction notes the best instructions were chosen by test accuracy. On travelling-salesman instances at n=50, gpt-4 reaches a gap of 11.0 against 9.8 for farthest insertion (self-reported).

Ein-Dor et al. (2024) build a prompt through chat from unlabeled data with Llama-3-70B. Across 12 sessions participants ranked the zero-shot summaries best on 53% of the 112 test instances and the few-shot summaries best on 47%, not a significant difference (self-reported); these are ranking shares, not prompt scores. Convergence took about 25 minutes and 32 turns, with satisfaction 4.6 of 5. See also [[SkillOpt Agent Skill Optimization]] for a gated optimizer over skill documents.

## APE (Zhou et al., 2022)

APE has an LLM propose candidate instructions from five demonstrations of the task, scores each on the target model (execution accuracy by default, with adaptive multi-stage subset evaluation) and keeps the best; nothing is trained. With InstructGPT it reached human-level zero-shot accuracy on 24 of 24 Instruction Induction tasks and 17 of 21 BIG-Bench tasks, and on TruthfulQA its instructions gave over 40% true-and-informative answers against 30% for a human prompt (self-reported; the instructions were tuned on the evaluation data). Human-level results needed about 64 sampled instructions, and iterative resampling gave marginal gains. Instructions did not transfer across models (InstructGPT to GPT-3 and back), and one task showed scorer overfitting (rhymes: echo the input). Everything ran on retired 2022 OpenAI models; sampling temperature and filter thresholds are not stated.

## AutoPrompt: gradient-searched trigger tokens

Shin et al. (EMNLP 2020) build prompts for frozen masked language models (BERT-base, RoBERTa-large) without writing them by hand. Each input goes into a template with a mask slot plus trigger tokens shared across all inputs. The trigger tokens begin as mask tokens, get candidate replacements from a first-order gradient search, and the candidates are re-scored with forward passes. A logistic classifier on the mask embedding supplies the label tokens. The model is never fine-tuned.

- RoBERTa-large with AutoPrompt reaches 91% on SST-2 test with no fine-tuning (self-reported).
- On fact retrieval (LAMA, BERT-base, one prompt per relation), a 7-token AutoPrompt beats the best single mined prompt; the extraction leaves the point values blank (self-reported).
- With 10 to 1000 training examples on SST-2 and three-way SICK-E, AutoPrompt matches fine-tuned BERT on average and beats fine-tuned RoBERTa at hundreds to thousands of examples; the extraction notes these values are read only from a figure (self-reported).
- A relation-extraction probe on perturbed sentences, with objects replaced at random, drops sharply; the authors read this as much of the accuracy coming from stored facts.

The authors' limits: on QQP and RTE the prompts stayed close to chance, labelled training data is needed, the prompts are not interpretable, and the greedy search over a large discrete space is sometimes brittle and mostly raises the majority label on imbalanced data. Only masked models were tested; the SST-2 search took two days on eight GPUs.

## Limits

- OPRO: best instructions picked on test accuracy; Ein-Dor: researcher participants and no comparison with an automatic optimizer.
- Ramnath et al. (survey): black-box discrete prompts only, so soft prompts, gradient-based AutoPrompt, Reflexion and similar are excluded; single-category labels are forced; the 57-method comparison is in the appendix with asymptotic complexity formulas, not measurements; it covers work to about early 2025.
- Lakshmanan and Hapke (book): framework lists in the chapter are dated 2025, and all figures are single illustrative runs.

## See Also
- [[Evaluating Prompts]] — prerequisite-for
- [[DSPy]] — extends
- [[Fine-Tuning as Prompt Compression]] — alternative-to
- [[Prompt Templates and Variables]] — extends
- [[Principled Instructions (26 Prompt Principles)]] — related (hand-written prompt rules, the manual alternative to search)
- [[Dependency Injection for LLM Chains]] — related (swappable chain steps)
- [[GATE Generative Active Task Elicitation]] — related (elicits the task from the user instead)
- [[GEPA Reflective Prompt Evolution]] — instance-of (reflective evolution with a Pareto frontier)
- [[Coding-Agent Skill Distillation (CASD)]] — instance-of (coding agent as optimizer)
- [[PEZ Gradient-Based Hard Prompt Discovery]] — instance-of (gradient-based hard prompts)
- [[SkillOpt Agent Skill Optimization]] — instance-of (gated edits to a skill document)
- [[ACE Agentic Context Engineering Playbooks]] — alternative-to (delta-updated playbook instead of rewriting prompts)
- [[LM-BFF and PET Prompt-Based Fine-Tuning]] — related (searched templates and label words)
- [[Controllable Text Generation Taxonomy]] — related
