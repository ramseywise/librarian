---
title: RoboCat Self-Improving Robot Generalist
tags: [foundations, llm, pattern]
summary: "RoboCat trains one vision-based goal-conditioned policy across robot arms and tasks, fine-tunes it on a few hundred demonstrations, lets it collect its own data and retrains; the appendix evidence shows self-generated data is mostly failures and matches the data's success rate (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-bousmalis-2023-robocat.md
---

# RoboCat Self-Improving Robot Generalist

RoboCat (Google DeepMind, TMLR 2023) is a transformer policy for robot manipulation trained on many embodiments. The extraction covers only the appendix (pages 23 to 60) of the paper.

## Self-improvement loop

1. Humans supply a few demonstrations for a new task.
2. An existing RoboCat agent is fine-tuned on either 500 or 1,000 successful episodes; failed episodes are left out at this stage.
3. That specialist collects more episodes autonomously.
4. The final generalist trains on the demonstrations plus the self-generated data, sampling tasks and successes versus failures equally.

Each self-improvement task used an earlier RoboCat version, not the final one. Self-generated data is mostly failures and often outweighs the human data; for example the Panda apple task has 1,956 human successes and 8,117 agent successes with 6,058 agent failures.

## Findings (self-reported, real robots unless noted)

- The generalist roughly matches the success rate of its own training data and beats it on some tasks (banana, peach, strawberry, potato). Where the data-generating expert used privileged state in simulation, the vision-based policy fell short of the experts by at most 10%, tower building being the exception.
- More fine-tuning demonstrations generally help (gear lift 56% to 86%, 500 to 1,000 demos) but insertion stays hard (shape insertion 4% to 19%), and two of three bowl insertions got worse.
- Predicting future tokens five steps ahead gave a 50% relative gain in held-out generalisation over none; predicting pixels gave zero held-out success. A 1.18B model beat a 364M one by 6 to 21% in success.
- Gear insertion failures fell by about two thirds from the 364M model to the full agent.

## Limits

- Single model per setting with no variance; 100 evaluation episodes, with checkpoints chosen on 25-episode runs; real-task success counted visually.
- The appendix shows one round of self-improvement, with no per-round numbers and no comparison against demonstrations alone, so the extraction cannot show that self-generated data helped. The model card says it is not evaluated for deployment and safety.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Rejection Sampling Fine-Tuning]] — related (success-filtered fine-tuning versus RoboCat's mixed data)
- [[DreamGym Synthetic Experience RL]] — related
- [[RT-1 Robotics Transformer]] — related
- [[PaLM-E Embodied Multimodal Language Model]] — related
