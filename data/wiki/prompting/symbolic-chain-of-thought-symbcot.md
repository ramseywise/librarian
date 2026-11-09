---
title: Symbolic Chain-of-Thought (SymbCoT)
tags: [prompting, pattern]
summary: Four LLM-run modules (translator, planner, solver, verifier) translate premises to first-order logic and reason over them with named inference rules, with no external solver.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xu-2024-faithful-logical-reasoning-symbolic-chain.md
---

# Symbolic Chain-of-Thought (SymbCoT)

SymbCoT runs one LLM through four few-shot-prompted modules. The translator rewrites premises into first-order logic, paired with the original text. The planner writes a step-by-step plan using the premises and inference rules. The solver executes the plan, naming the rule used at each step. The verifier checks that the symbolic context matches the natural language and that each solving step is valid. Nothing external is called, unlike pipelines that translate with an LLM and then hand off to a solver such as Prover9.

## Reported results (self-reported)

- GPT-4, first-order-logic sets (PrOntoQA 500, ProofWriter 600, FOLIO 204): average 88.47 against 79.16 for CoT and 80.59 for the external-solver approach. Per set: PrOntoQA 99.60 (CoT 98.79), ProofWriter 82.50 (CoT 68.11), FOLIO 83.33 (CoT 70.58).
- GPT-3.5: average 64.22 against 58.11 for CoT, but FOLIO 57.84 trails the external-solver approach (62.74).
- Constraint-optimisation form, GPT-4: LogicalDeduction 93.00 (CoT 75.25), AR-LSAT 43.91 (CoT 35.06).
- Ablation (GPT-4, five datasets): planner plus solver added 10.4% on average, the translator 6.3%, with a further gain from the verifier; the extraction says the bar labels were inferred.
- Execution: 100% of items ran, against an average 17.7 points lower for the external-solver baseline. On FOLIO, 55.6% of that baseline's wrongly predicted "unknown" cases were translation faults.
- Faithfulness audit on FOLIO by five graduate students: 6% of correct CoT answers came from flawed reasoning, 2% without the verifier, 0% with it (sample size not stated).
- Cost: average output tokens per module on AR-LSAT were 323, 627, 654 and 726 (about 2,330 in total by the extraction's arithmetic).

## Limits

- The authors name two limits: only two symbolic forms were tested, and the long generation chain is costly.
- The authors state it does not improve planning; the main failure is choosing the wrong reasoning path, and a hybrid with an external solver is untested.
- Baselines were copied from earlier papers rather than re-run; several lack figures for PrOntoQA or AR-LSAT. Only 2023 snapshots of GPT-3.5 and GPT-4. No cost-matched baseline.
- The faithfulness audit is small, done by hand and covers one dataset. Ablation and depth results are mostly in figures; the extraction could not assign the depth labels and did not state whether the gains quoted in the text are absolute or relative.
- Closed-world true, false, unknown tasks only; transfer to general prompting is not shown. The venue is not printed in the extraction.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[PrOntoQA]] — prerequisite-for
- [[Logic-of-Thought]] — alternative-to
- [[Program-Aided Language Models (PAL)]] — alternative-to
- [[SelfCheck Step Verification]] — related
