---
title: Role Anchor and Role Drift
tags: [foundations, concept]
summary: Role drift is the loss of a module's assigned job when a compound LLM pipeline is trained end to end with a final-answer reward; the Role Anchor penalty on a role-utility measure kept a RAG reader evidence-following (0.869 against 0.589) in a small study (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-cao-2026-do-modules-stay-their-lane.md
---

# Role Anchor and Role Drift

Cao, Srinivasan and Bakker (arXiv 2607.21627, July 2026 preprint) study what happens to the modules of
a compound system when reinforcement learning rewards only the final answer. Accuracy can rise while
a module stops doing the job it was given. The authors frame this as surviving verifiable rewards,
since the verifier checks only the end result.

## The role anchor

Role utility is the log-probability of a token given the history and the role prompt, minus the
same under a neutral prompt, mean-centred over the top five tokens. The anchor adds a penalty on the
squared change of that utility from the pre-RL reference model, weighted by a coefficient lambda,
to the policy-gradient loss. It needs log-probabilities under both prompts, from a frozen reference as well as
the trainable weights, and costs about 22% (RAG) and 18% (decomposer-solver) extra wall-clock time.

## Results (self-reported)

- **RAG pipeline.** Query generator, a frozen term-matching retriever and a reader, both Qwen2.5-3B-Instruct,
  176 HotpotQA yes/no evaluation questions, REINFORCE with a group baseline (k=8) and LoRA rank 16, run for 10
  epochs over 3 seeds, starting from an SFT checkpoint. Evidence-following accuracy (answering as the
  passage implies) fell from 0.86 to 0.54, against a chance floor of 0.506. At epoch 9, with no anchor
  against the anchor, accuracy was 0.447 without and 0.380 with it, evidence-following 0.589 without and 0.869 with it, and accuracy with a
  random passage 0.187 without and 0.030 with it. Anchor lambda 0.05 gave up 0.067 accuracy to gain 0.280 in evidence-following;
  in a sweep, lambda 0.02 lifted evidence-following (0.75 before, 0.90 after).
- **Decomposer-solver pipeline.** Decomposer Qwen2.5-7B, deliberately weak Solver Qwen2.5-0.5B,
  200 MuSiQue-Ans dev questions, k=4, 3 seeds, lambda 1.00. 86% (plus or minus 19%) of the
  apparent RL gain vanished under the anchor (+0.310 unanchored against +0.057). Epoch-9 accuracy 0.550
  against 0.297; decomposer insertion rate 0.596 against 0.143. Drift began abruptly after epoch 4.
- **Mechanism check.** The anchor reduced the update's projection onto the drift direction (decomposer:
  +0.50 became -0.06; RAG: +0.22 became +0.006). The direction was defined from the unanchored run itself, so the
  authors hedge with "suggests".

## Limits

- Two small pipelines (0.5B to 7B Qwen2.5, LoRA, 3 seeds). The RAG slice is 176 yes/no questions
  with chance near 0.5. The authors concede the anchor does not apply to API-only modules,
  non-probabilistic components such as the retriever, or prompt-optimised systems. They do not claim
  it improves accuracy in general; whether the corpus beats memory is a deployment choice.
- Part of the RAG drift reflects an imperfect retriever, as the authors say. The benefit under a
  corpus update is argued from a counterfactual passage swap, not a real update. No comparison with
  other grounding methods.
- Internal inconsistency noted by the extraction: the unanchored RAG accuracy is 0.34 in the lambda
  sweep and 0.447 in the main table, unexplained.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Multi-Agent Failure Modes at Scale]] — related (a module-level failure that outcome scores hide)
- [[Verification Loops]] — related
