---
title: PEZ Gradient-Based Hard Prompt Discovery
tags: [prompting, pattern]
summary: "PEZ finds discrete text prompts by gradient descent on a continuous iterate that is projected to the nearest token embeddings at each forward pass; it needs white-box gradients, yields often unreadable prompts, and was tested only on small models and narrow classification."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wen-2023-hard-prompts-made-easy.md
---

# PEZ Gradient-Based Hard Prompt Discovery

PEZ learns a **hard prompt**, meaning a string of real vocabulary tokens, with gradients. It keeps a continuous (soft) iterate. On every forward pass it projects that iterate onto the nearest vocabulary embeddings, evaluates the loss gradient there, and uses that gradient to update the continuous iterate. The authors offer this as a simpler option than AutoPrompt and FluentPrompt, both of which re-project after every step; the paper says re-projection baselines can stall when nearest tokens are far from the embedding and the learning rate is untuned. It is white-box: it needs the embedding matrix and gradients. Text runs add a fluency term to the loss, weighted 0.003 for the transfer table and 0.03 for few-shot runs.

## Results

All numbers are the paper's own (self-reported). Setups differ per row.

- **Text transfer.** Ten-token prompts optimised on GPT-2 Large for 5000 steps, best five per method tested unchanged on other models, SST-2 validation accuracy over 5 prompts. PEZ with fluency scored 79.72 on GPT-2 XL, 63.30 on T5-LM-XL, 77.18 on OPT-2.7B and 72.39 on OPT-6.7B, against 58.72 for the empty template on OPT-6.7B; the text cites about a 14% boost there. On the source model PEZ did not beat the baselines (FluentPrompt 88.33 against 88.05).
- **Source model versus soft prompts.** GPT-2 Large, 10 prepended tokens: soft prompts scored 93.35, 92.76 and 94.65 on SST-2, AGNEWS and Amazon, while PEZ scored 88.05, 76.94 and 87.78. PEZ was about 2 points better than the other hard-prompt methods on AGNEWS only.
- **Few-shot discovery.** AGNEWS, GPT-2 Large, 3 appended tokens, 100 seeds, about 5 minutes per run: PEZ with fluency scored 70.93 at 2 shots per class and 74.15 at 4, against a soft prompt's 74.92 and 79.93.
- **Image prompts.** Stable Diffusion v2, 8 PEZ tokens, CLIP similarity scored by a separate model, 100 images per dataset over 5 seeds: PEZ scored 0.697 on LAION against 0.707 for a roughly 77-token CLIP Interrogator prompt; soft prompts transferred poorly (0.408).
- **Length.** The paper reports longer prompts overfit and finds 16 tokens most generalisable for images.
- **Filter evasion.** PEZ can build a prompt that avoids a banned word yet reproduces the concept; the authors show it on Midjourney.

## Limits

- White-box only; the "API-only" benefit applies to deploying a found prompt, not finding it. For images, the CLIP encoder supplies the loss, so no backpropagation through the diffusion model is needed.
- The authors concede that the learned prompts are frequently unreadable.
- Only small, older models: GPT-2 Large was the source model, with GPT-2 XL, T5-LM-XL and OPT as targets. No instruction-tuned chat models.
- Narrow classification tasks (SST-2, Amazon Polarity, AGNEWS), with hard prompts far below soft ones.
- Standard errors of about 2-4 points make several margins over baselines inconclusive; some hyperparameters were best-of-learning-rates.
- No human evaluation of images, only CLIP similarity.
- The extraction flags internal inconsistencies: GPT-2 Large is 774M in the text and 755M in table headers; the paper's 16-token optimum conflicts with a 2-6 token axis on Figure 5, whose labels were garbled; Table 6 reports standard deviation where other tables give standard error.
- The paper predates LLM-as-optimizer methods and optimises tokens through gradients, not instructions.

## See Also
- [[Prompt Optimization]] — prerequisite-for
- [[Fine-Tuning as Prompt Compression]] — related (soft prompts as the contrast)
- [[GCG Adversarial Suffix Attack]] — related (lists PEZ as a baseline that got 0% exact match)
