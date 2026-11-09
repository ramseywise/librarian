---
title: LLaMA-Adapter V2 and MultiModal-GPT Parameter-Efficient Visual Tuning
tags: [multimodal, concept]
summary: "Two cheap routes to a visual instruction model: LLaMA-Adapter V2 early-fuses visual tokens into a frozen LLaMA with bias tuning (about 14M trainable parameters), and MultiModal-GPT trains LoRA adapters on OpenFlamingo (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-gao-2023-llama-adapter-v2.md
  - data/raw/papers/2026-11-07-gong-2023-multimodal-gpt.md
---

# LLaMA-Adapter V2 and MultiModal-GPT Parameter-Efficient Visual Tuning

Both papers turn a frozen language model into a visual instruction follower by training a small set of parameters.

## LLaMA-Adapter V2 (Gao et al., 2023)

The authors hypothesise that fusing visual tokens early, and training separate parameter groups jointly on captions and on text-only instructions, stops image-text alignment and instruction following from interfering with one another.

- It starts from LLaMA-Adapter (zero-initialised gated prompts in a frozen LLaMA) and adds a learnable scale and bias to each linear layer so that y = s(Wx + b), with b starting at 0 and s at 1, and unfreezes the norms. This is called **bias tuning**; the extraction lists BitFit and SSF as related precedents.
- **Early fusion** injects visual tokens at the first Transformer layer instead of only into prompts in the last layers. Two separate parameter groups are trained, one on COCO captions and the other on GPT-4-LLM instructions; no visual instruction data is used. At inference time a caption or OCR expert can supply extra text context.
- About 14M parameters are tuned; the paper's own comparison lists 13B for each of MiniGPT-4 and LLaVA, counting every tuned parameter needed to convert the pretrained models (self-reported). Bias tuning adds about 0.04% (self-reported).
- Fine-tuned on COCO alone, it reaches 122.2 CIDEr on COCO Caption, above ClipCap and below BLIP and BLIP-2 (self-reported).
- GPT-4 judged the 65B-based V2 at 118% of ChatGPT on total score, winning 50 of the 80 questions, with 7 ties and 23 losses read off a figure, against a 13B Vicuna baseline (self-reported).

## MultiModal-GPT (Gong et al., 2023)

OpenFlamingo, built from a CLIP encoder, a perceiver resampler and a LLaMA decoder with gated cross-attention, stays frozen, and LoRA adapters train in the decoder's self-attention, cross-attention and FFN. One instruction template covers both language-only and vision-language data, and the loss falls on the response and the EOS token alone.

- The extraction reports that datasets whose answers run one or two words (VQA v2.0, OKVQA, GQA, CLEVR, NLVR) pushed the model to reply briefly to everything, which is why they were dropped; this rests on preliminary runs that are not reported.
- Adding Dolly 15k and Alpaca GPT4 to the vision-language mix is said to help dialogue, but only demos show it.
- Batch size 256 aggregate on 8 A100 GPUs, one epoch.

## Limits

- LLaMA-Adapter V2 reports no visual QA or multimodal benchmark; visual ability rests on hand-picked examples. It fails on an out-of-distribution cartoon image, lags LLaVA in visual understanding (no number) and is sensitive to wrong expert output. The chat comparison pits a 65B-based model against a 13B one.
- MultiModal-GPT has no quantitative evaluation or ablation. LoRA rank, optimizer, schedule and seeds are not stated.
- For V2 the extraction records no optimizer, learning rate, batch size, epochs, hardware or seeds. MultiModal-GPT does state 8 A100 GPUs and a batch of 256.
- Table 1's parameter comparison counts data and tuning parameters, including Vicuna's own tuning in the MiniGPT-4 row, and the paper does not say why that row is 13B.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[Bottleneck Adapters for Parameter-Efficient Transfer]] — prerequisite-for
- [[Flamingo Gated Cross-Attention VLM]] — prerequisite-for
- [[MiniGPT-4 Linear Projection Alignment]] — alternative-to
- [[LLaVA Visual Instruction Tuning]] — alternative-to
