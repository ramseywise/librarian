---
title: PaLM-E Embodied Multimodal Language Model
tags: [multimodal, concept]
summary: "PaLM-E injects continuous sensor inputs (state vectors, ViT features, object-centric scene representations) into a pretrained PaLM's embedding space as multimodal sentences, so one model handles robot planning, VQA and language tasks (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-driess-2023-palm-e.md
---

# PaLM-E Embodied Multimodal Language Model

Driess et al. (2023, arXiv 2303.03378) ask whether continuous observations can be fed into the embedding space of a pretrained LLM, letting a single model handle embodied reasoning plus vision-language and pure language tasks, with transfer between them. They hypothesise that training jointly on web-scale and embodied data carries across tasks and robot embodiments, and that bigger LLMs lose less of their abilities during multimodal training.

## Mechanism

- Encoders (a state MLP, a ViT, a ViT with TokenLearner, and OSRT, an object scene representation transformer) map observations to vector sequences in the PaLM token-embedding space. A **multi-modal sentence** interleaves these vectors with text embeddings.
- The decoder-only LLM is trained on text targets with a cross-entropy loss, and its weights are either frozen or updated. Evaluation spans TAMP planning, Language-Table and mobile manipulation, alongside VQA, captioning and language benchmarks.
- The full training mixture is 8.9% embodied data.

## Results (self-reported)

- A single generalist PaLM-E-562B checkpoint reports the best OK-VQA score of those listed, ahead of task-finetuned models and without any task-specific finetuning; the extraction lists PaLI finetuned at 64.5 and Flamingo at 57.8 (32-shot) (self-reported).
- With a frozen LLM, PaLM-E-12B gets 70.3 on VQAv2 test-dev against 48.4 for Frozen (self-reported).
- Unfrozen PaLM-E-84B has an NLG average of 18.4 against 47.8 for PaLM-62B, so it lost much of its language performance (1-shot, NLG average over TriviaQA, NQ, WebQuestions and Lambada); the paper reports that the loss shrinks with scale, for 562B against PaLM-540B (self-reported).
- On mobile-manipulation failure detection PaLM-E-12B scores F1 0.91 against 0.73 for zero-shot PaLI and 0.89 for CLIP-FT-hindsight; affordance prediction F1 is 0.91 against 0.62 for PaLI and 0.63 for QT-OPT (self-reported).
- On TAMP planning with 1% of the data (320 examples per planning task), the OSRT input gives the best planning, and a ViT-4B co-trained on the full mixture lifts planning success to more than twice that of a model trained on a single robot (LLM frozen) (self-reported).
- PaLI used zero-shot gets 0.0 on TAMP questions q2 and q3; on Language-Table Task 1, zero-shot SayCan and PaLI both get 0.0 (self-reported).
- Real-robot long-horizon planning is evaluated qualitatively, trained on 2912 SayCan sequences.

## Limits

- The main models come with no training hyperparameters: optimizer, learning rate, batch size, steps and hardware are all unstated.
- Real-robot findings are only qualitative, with no seeds or variance.
- A frozen LLM struggled on some robotics tasks.
- Generalist numbers trail finetuned PaLI on COCO (138.7 against 149.1) and VQAv2 (80.0 against 84.3).
- Language-Table Task 1 is scored on a test set, while Tasks 2 and 3 rely on 80 rollouts.
- Several extracted result lines carry no number; the figures above are only those the extraction states.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[RT-1 Robotics Transformer]] — related (RT-1 supplies PaLM-E's low-level policies)
- [[SayCan Affordance-Grounded Skill Selection]] — prerequisite-for
- [[Frozen Visual Prefix Few-Shot Learning]] — prerequisite-for
- [[PaLI and PaLI-X Jointly Scaled VLMs]] — related
