---
title: Visual Instruction Tuning and Tool-Using VLMs
tags: [multimodal, comparison]
summary: "Four ways to give an LLM vision compared by what is trained: LLaVA and Emu train a connector or the whole model, SPAE trains only a tokenizer into a frozen LLM's words, and ViperGPT and Visual ChatGPT train nothing and call tools; benchmarks and a medical and a planning variant round out the family."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-liu-2023-visual-instruction-tuning.md
  - data/raw/papers/2026-11-07-liu-2024-improved-baselines-visual-instruction-tuning.md
  - data/raw/papers/2026-11-06-sun-2023-emu.md
  - data/raw/papers/2026-11-06-yu-2023-spae.md
  - data/raw/papers/2026-11-07-suris-2023-vipergpt.md
  - data/raw/papers/2026-11-07-wu-2023-visual-chatgpt.md
  - data/raw/papers/2026-11-06-sellergren-2026-medgemma-1-5-technical-report.md
  - data/raw/papers/2026-11-06-xu-2025-visual-planning.md
  - data/raw/papers/2026-11-07-liu-2024-mmbench.md
  - data/raw/papers/2026-11-07-li-2023-seed-bench.md
  - data/raw/papers/2026-11-07-li-2023-evaluating-object-hallucination-large-vision.md
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch01-introduction.md
---

# Visual Instruction Tuning and Tool-Using VLMs

The papers here answer one question in different ways: how does a language model come to work with images? The comparison axis is what gets trained. All figures belong to the papers' own setups and are self-reported; the per-paper pages carry the setups and limits.

The book chapter *Multimodal Deep Learning, Chapter 1* (arXiv 2301.04856) presents the field as a meeting of NLP and computer vision and lays out a four-part book; it contains no experiments or numbers.

## What is trained

| Approach | Trained | Frozen or unchanged | How images enter |
|---|---|---|---|
| [[LLaVA Visual Instruction Tuning]] | a projector, then projector plus LLM | CLIP encoder (stage 1 also freezes the LLM) | projected grid features |
| [[Emu Generative Pretraining in Multimodality]] | the whole 14B model end to end, then a diffusion decoder | decoder training freezes encoder, LLM and VAE | regressed visual embeddings, interleaved with text |
| [[SPAE Semantic Pyramid AutoEncoder]] | only the tokenizer | the LLM (PaLM 2-L or GPT-3.5) | words from the LLM's vocabulary in a pyramid |
| [[ViperGPT Visual Inference via Python Execution]] | nothing | all modules and the code LLM | calls from generated Python |
| Visual ChatGPT | nothing | ChatGPT and 22 visual foundation models | text descriptions and filenames |

## Trained connectors: LLaVA and Emu

LLaVA uses a language-only GPT-4 to write instruction data from captions and boxes, and trains in two stages. Its follow-up finds that adding academic VQA data with a one-clause response-format prompt moved MME from 809.6 to 1323.8 on a 7B model at 224px (self-reported), and that a 13B model trained on 1.2M public samples ran in about a day on 8 A100s. Emu spends more (128 A100s for about 2 days of pretraining) to also generate images, then instruction-tunes with light LoRA and reuses a filtered LLaVA subset in its data. Emu's generation lags a plain diffusion model on FID (zero-shot FID on 30K COCO prompts, 11.66 against 9.93 for SD1.5; self-reported), which its authors suspect comes from the mismatch between the decoder's conditioning space and the original text one.

## Frozen LLM, translated images: SPAE

SPAE keeps the LLM untouched and moves the work to a tokenizer that writes an image as words. Its result runs against intuition: understanding accuracy peaks at 21 tokens and falls at 597, while captioning and reconstruction need the longer sequences. That makes the token budget a per-task choice.

## No training, tool composition: ViperGPT and Visual ChatGPT

Both systems compose existing models rather than training a new one, but the composition differs. ViperGPT asks a code model for a whole program per query and runs it once. Visual ChatGPT drives ChatGPT (text-davinci-003) through LangChain in a multi-step loop: a Prompt Manager assembles the prompt from system principles, per-tool descriptions (name, usage, inputs and outputs, and optionally an example), together with filenames for unique and chained images and a closing suffix that makes the model first ask itself whether a tool is needed. It exposes 22 visual foundation models, including Stable Diffusion, InstructPix2Pix, ControlNet and BLIP, and needs four V100 GPUs to host them all. Its only evidence is one qualitative dialogue of 16 rounds plus case studies that ablate the prompt; no benchmark, baseline or metric appears. The authors list heavy prompt engineering, slow chains of models, a token limit on how many tools fit, security and privacy concerns for remote plug-in models, and unsatisfying outputs from tool failure and prompt instability as limits.

ViperGPT does report numbers: on GQA test-dev it leads the zero-shot field by 3.4 points over BLIP-2, yet on GQA its 48.1 sits far under the 72.1 of the supervised CRF model (self-reported). The tool-calling idea itself is covered in [[Toolformer Self-Supervised Tool Use]] and [[ReAct Pattern]].

## Variants of the recipe

- **Domain adaptation:** [[MedGemma 1.5 Medical Vision-Language Model]] keeps a general VLM architecture and adapts input handling (capped slice and patch sets) to medical volumes and slides. It gained on the new tasks but lost general knowledge: MMLU-Pro fell from 39.1 to 33.8 versus MedGemma 1 4B, single run at temperature 0 (self-reported).
- **Visual reasoning without text:** [[VPRL Visual Planning with Reinforcement Learning]] plans by generating image sequences and beat text SFT on grid navigation (80.6 against 53.6 average exact match, on synthetic FrozenLake, Maze and MiniBehavior grids, against Qwen2.5-VL-7B supervised on the same data; self-reported), while staying weak on larger unseen grids.

## Evaluating these models

Benchmarks disagree about how to score. [[MMBench]] requires correct answers under every circular shift of the options and uses an LLM to extract the chosen option; [[SEED-Bench]] scores option likelihood and criticises that extraction step. [[POPE Object Hallucination Probing]] polls yes/no object questions and varied less across prompts than caption-based CHAIR in its authors' tests. All three evaluate LLaVA-family models, and the checks in [[VLM Benchmark Shortcuts]] apply to each.

## What argues against it

The comparison is across papers with different data, backbones and eras, so it ranks nothing. The extractions flag that the zero-shot tool systems depend on deprecated models (ViperGPT) or have no quantitative evaluation at all (Visual ChatGPT), and that Emu, SPAE and SEED-Bench report mid-2023 results.

## Limits

This page compares reports from single papers, mostly single runs with no variance. Visual ChatGPT's description comes from an extraction with no results table; its claims are method descriptions, not measurements.

## See Also
- [[LLaVA Visual Instruction Tuning]] — instance-of
- [[Emu Generative Pretraining in Multimodality]] — instance-of
- [[SPAE Semantic Pyramid AutoEncoder]] — instance-of
- [[ViperGPT Visual Inference via Python Execution]] — instance-of
- [[MedGemma 1.5 Medical Vision-Language Model]] — instance-of
- [[VPRL Visual Planning with Reinforcement Learning]] — instance-of
- [[MMBench]] — instance-of
- [[SEED-Bench]] — instance-of
- [[POPE Object Hallucination Probing]] — instance-of
- [[Microsoft COCO]] — related
- [[Food-101 and car-197 Fine-Grained Datasets]] — related
- [[Vision-Language Model Training Families]] — prerequisite-for
- [[VLM Benchmark Shortcuts]] — related
- [[Vision-Language Model Architectures]] — related
- [[Qwen-VL Fine-Grained Perception VLM]] — related
- [[Kosmos-2 Grounded Multimodal LLM]] — related
- [[InternVL Scaled Vision Encoder with QLLaMA]] — related
- [[Video-ChatGPT Video Conversation Model]] — related
