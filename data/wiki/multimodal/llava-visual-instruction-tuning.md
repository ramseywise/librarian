---
title: LLaVA Visual Instruction Tuning
tags: [multimodal, pattern]
summary: "LLaVA connects a CLIP vision encoder to Vicuna through a small trained projector, aligns it on caption pairs, then instruction-tunes it on GPT-4-written image conversations; LLaVA-1.5 swaps in an MLP connector, VQA data with format prompts and 336px input (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-liu-2023-visual-instruction-tuning.md
  - data/raw/papers/2026-11-07-liu-2024-improved-baselines-visual-instruction-tuning.md
---

# LLaVA Visual Instruction Tuning

Liu et al. (arXiv 2304.08485, NeurIPS 2023) ask whether instruction tuning can move into the language-image space when a language-only GPT-4 writes the training data. **Visual instruction tuning** is their name for that extension. The follow-up (arXiv 2310.03744) asks which design choices (the connector, the blend of training data, prompt wording that fixes answer format, image resolution, the language model) matter in a controlled LLaVA-style setting.

## Mechanism

- One trainable linear layer projects grid features from a CLIP ViT-L/14 encoder into the Vicuna word-embedding space.
- Stage 1 updates just that projection, using 595K caption pairs filtered from CC3M. Stage 2 updates the projection and the LLM together, using 158K instruction samples that GPT-4 generated (or using ScienceQA instead).
- When GPT-4 writes the data it is shown captions plus bounding boxes only, never the pixels.

## LLaVA results (self-reported)

- On LLaVA-Bench (COCO; 30 images, 90 questions), full-data training reaches 85.1% relative to text-only GPT-4; no instruction tuning gives 21.5%; conversation-only data gives 73.8%.
- On LLaVA-Bench (In-the-Wild; 24 images with 60 questions, averaged over 3 runs), the model gets 67.3% overall, which is 29 points above BLIP-2 and 48 above OpenFlamingo, and 81.7% on the complex-reasoning slice.
- Fine-tuned on ScienceQA (13B, 12 epochs), LLaVA alone gets 90.92%. Re-prompting GPT-4 as a judge when the two disagree gives 92.53%; the GPT-4 complement scheme that falls back to LLaVA gives 90.97%.
- Ablations on ScienceQA: no stage-1 pretraining 85.81%; a 7B model 89.84%; last-layer CLIP features 89.96%.
- Cost: stage 1 finishes within 4 hours and stage 2 within 10 hours, both on 8 A100s.
- The authors report an early observation, without numbers, that text-only GPT-4 gave better instruction data than ChatGPT. They also note that the model at times handles an image like an unordered set of patches.

## LLaVA-1.5 changes (self-reported)

The projector becomes a two-layer MLP, the encoder CLIP-ViT-L-336px, and the instruction mix grows to 665K samples (academic VQA, OCR and region data, plus ShareGPT text) after 558K pairs of alignment pretraining. A **response-format prompt** is a single clause appended to a VQA question that fixes the output form.

- On 7B at 224px with a subset of InstructBLIP data, adding VQAv2 moves the MME score up from 809.6 to 1197.0, and the format prompt lifts it to 1323.8 (InstructBLIP: 1212.8).
- With the format prompt, accuracy on VizWiz's unanswerable questions climbs from 11.1% to 67.8%.
- At 13B and 336px: MME 1531.3, GQA 63.3, MM-Vet 36.1, VQAv2 80.0, MMBench 67.7, SEED 61.6, POPE 87.1/86.2/84.5.
- Training the 13B model takes about 6 hours of pretraining plus 20 hours of instruction tuning on 8 A100s, roughly twice the original because of the larger input.
- LLaVA-1.5-HD splits the image into 224px grid cells and adds a downsampled global view, reaching VQAv2 81.8 and GQA 64.7; the global view helps GQA, MME and MM-Vet in a 7B ablation.
- Sampling half of the instruction data at random keeps more than 98% of the full-data result (read from a plot).

## Limits

- The judge in the first paper is text-only GPT-4 given captions, so it never sees the image, and its robustness is untested. LLaVA-Bench is tiny, and each data-mix ablation is a single run.
- Training images are COCO and CC3M only; only a single linear projection was explored, with gated cross-attention and Q-former left open.
- LLaVA-1.5 uses all 576 patches at 336px, which lengthens training; it has no multi-image understanding, still hallucinates and is not meant for critical use.
- Cells marked with an asterisk (GQA, VQAv2 and others) saw training images or annotations, so they are not zero-shot. Runs are single, with no seeds.
- The hallucination-versus-resolution claim has no reported metric. The extraction notes the follow-up says 11 benchmarks in places and 12 in others.
- Hyperparameters and decoding settings of the first paper are not fully stated.

## See Also
- [[Vision-Language Model Training Families]] — prerequisite-for
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[MMBench]] — related (evaluates LLaVA-1.5)
- [[POPE Object Hallucination Probing]] — related (evaluates LLaVA)
- [[MoE-LLaVA and MoE-Tuning]] — extends
- [[InstructBLIP Instruction-Aware Query Transformer]] — alternative-to
- [[MultiInstruct Multimodal Instruction Benchmark]] — related
- [[DreamLLM Interleaved Comprehension and Creation]] — related
- [[Vision-Language Model Architectures]] — related
- [[MiniGPT-4 Linear Projection Alignment]] — related
- [[Video-ChatGPT Video Conversation Model]] — extends
- [[ShareGPT4V Detailed Caption Data]] — related
- [[LLaMA-Adapter V2 and MultiModal-GPT Parameter-Efficient Visual Tuning]] — related
