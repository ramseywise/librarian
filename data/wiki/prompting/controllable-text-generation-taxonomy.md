---
title: Controllable Text Generation Taxonomy
tags: [prompting, reference]
summary: "A 2024 survey sorts control of LLM output into content (hard) and attribute (soft) tasks, and into training-stage and inference-stage methods; prompting, latent steering and decoding-time edits sit on the inference side. It ran no experiments, so it ranks nothing."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-liang-2024-controllable-text-generation-large-language.md
---

# Controllable Text Generation Taxonomy

Liang, Wang, Wang et al. (preprint, 2024) survey **controllable text generation (CTG)**: generation that obeys set control conditions (safety, sentiment) and stays fluent and varied. The survey states every claim below as a literature statement; the authors ran no experiments and report no comparative numbers.

## Two axes

**By task.** *Content control*, also called hard or linguistic control, targets structure and vocabulary. *Attribute control*, also called soft or semantic control, targets abstract properties such as sentiment, style, topic and safety. Control is *explicit* when given through instructions such as a prompt and *implicit* when a standard must hold without being requested.

**By stage.**

- Training stage: retraining (a new or restructured model), fine-tuning on a smaller dataset, and reinforcement learning. The survey says retraining is impractical for modern LLMs, and fine-tuning depends on dataset quality.
- Inference stage: prompt engineering, latent space manipulation and decoding-time intervention. These need no retraining and allow real-time adjustment.

## Inference-stage methods

- **Prompting** controls output through the input only, as `Model(control prompt + input)`. A **hard prompt** is discrete natural language; a **soft prompt** is a trainable continuous vector. The survey says hard prompts are simple but sensitive to word choice and may give limited fine-grained control, while soft prompts fix that at a cost in interpretability and initial tuning. Success depends on the model following instructions.
- **Latent space manipulation** (activation engineering) adds a guiding vector to activations in some layers. The survey says results differ with the model and the task, which makes it harder to predict.
- **Decoding-time intervention** adjusts logits or the next-token distribution. It is plug-and-play but adds inference time and can harm fluency by forcing less likely tokens. Examples it describes: DExperts adds a scaled difference of two logit sets to the base logits (z_t + alpha(z'_t - z''_t)), and PREADD contrasts log-probabilities with and without a prefix, weighted by a multiplier.

## Evaluation and open problems

For evaluation it names automatic metrics (overlap, LM-based, distance-based, attribute classifiers or APIs), human A/B or Likert ratings, and LLM judges that it calls cheaper than humans. Open problems it lists: lost fluency (attribute collapse), controlling several attributes at once, attributes that stay entangled, slower decoding, and loose control of content. A refusal is safe but unhelpful, so control and helpfulness trade off. The authors ask that CTG papers include prompt baselines.

## Limits

- No experiments, so no method is ranked; the cutoff is August 2024.
- Prompting gets roughly two pages, which cover AutoPrompt, DAs, PCFG and soft-prompt tuning. The extraction notes that the survey does not treat system prompts, few-shot examples or structured-output modes as control methods.
- Most surveyed methods target GPT-2 or T5 scale models, and the extraction notes the survey does not say which carry over to chat LLMs.

## See Also
- [[Prompt Engineering]] — prerequisite-for
- [[Structured Output]] — related (hard control by format)
- [[Sampling Parameters]] — related (decoding-time knobs)
- [[Prompt Optimization]] — related
