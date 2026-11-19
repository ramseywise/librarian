---
title: On-Policy Correction for Harness-Model Co-Evolution
tags: [harness, llm, pattern]
summary: "After a harness has been evolved around a weaker model, fine-tuning that model on a stronger model's full trajectories lowered its success on all seven tasks (78.0% to 63.1%), while having the expert rewrite only the failing turn of the model's own rollouts did not (79.7%) (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-yu-2026-co-evolving-harnesses-models.md
---

# On-Policy Correction for Harness-Model Co-Evolution

Yu and colleagues (Salesforce AI, arXiv September 2026) study what happens when a harness has already been evolved around a weaker model and that model is then fine-tuned. The co-evolution loop they propose evolves a harness around model M_t, then trains the model inside that harness to obtain M_(t+1), and so on. One correction round is all that is reported; the repeated loop is proposed but not shown.

## Mechanism

- **Harness evolution** follows the GEPA pattern, with gemini-3.1-pro-preview reflecting and the Qwen student as the only executor during evolution (see [[GEPA Reflective Prompt Evolution]]). Budget was $20 per task per seed, 3 seeds, 600 s rollout limit.
- **Imitation baseline.** LoRA-SFT of the student on expert trajectories that scored a full 1.0, together with the student's own passing rollouts.
- **On-policy correction (SFT-corr.).** A meta-level agent localises the failing turn in each of the student's own rollouts, and the expert rewrites only that turn, leaving the student's planning distribution intact. Given the task, the trajectory so far and the failed checkpoint, the expert writes a one-sentence strategy and the repaired tool call. It produces three candidates and a quality judge picks one. The data is around 400 correction rows and about 50 rows the student passed on its own.
- **Training.** LoRA rank 16 or 64 (the best scores are reported), two epochs, learning rate 1e-4, bf16, batch size 8, sequence length 49,152, and under an hour per run.

## Results (self-reported)

Setup: the student is qwen3-coder-30b-a3b (3B active of 30B), the expert is gemini-3.1-pro-preview, and the benchmark is seven enterprise tasks from Yang et al. 2026, scored on the test split as a mean of three runs.

- Harness evolution alone is the largest lever: Qwen 29.2% to 78.0% (+48.8) and Gemini 84.4% to 93.6% (+9.2).
- Imitation under the evolved harness lowered Qwen's mean from 78.0% to 63.1% (−14.9), on all seven tasks (from −4.2 up to −29.9; the largest were payroll at −29.9, website at −20.3 and browser at −16.0).
- Correction lifted the score by 1.7 points, 78.0% to 79.7%, with improvements on five of the seven tasks. The table's standard error is about 0.67 to 0.97, so the gain is roughly 1 to 2 SEM with no significance test.
- Imitation under the unevolved harness h0 helped: 29.2% to 35.5% (+6.3). The regression is therefore tied to the evolved harness, not to imitation itself.
- Under imitation on the evolved harness, planning failures grew from 1.1% to 14.6% of all failures; under correction they reached only 1.8%. The authors read this as the student adopting the expert's planning style without the competence to execute it. In a payroll case the imitated model gives the right answer but re-issues the same view 29 times and never finishes in 78 steps.
- Second family, one task: Gemma-4-26b-a4b-it on Webarena went 46.7% to 55.6% with the evolved harness and fell to 41.1% after imitation.

## Limits

- One student family covers the seven tasks, with Gemma on one task, and there is one expert and LoRA only; full fine-tuning is untested.
- The size of the imitation data is not given, so the two arms are not matched (correction used about 500 rows) and a data-quantity confound stays open. LoRA rank was picked by the best score.
- The planning-style explanation rests on an LLM judge sorting failures plus two case studies, with no intervention on planning style. Failure shares are shares of failures, not absolute rates.
- Correction does not fully close the gap to the expert. The paper has no RL arm, no on-policy distillation arm and no correction run under h0.
- The paper's environment changes make its absolute numbers not comparable with Yang et al. 2026.

## See Also
- [[Harness Engineering]] — prerequisite-for
- [[VERA Co-Evolving Model and Harness]] — alternative-to (RL on the model rather than expert-corrected SFT)
- [[GEPA Reflective Prompt Evolution]] — prerequisite-for
- [[Post-Training for Agents]] — prerequisite-for
