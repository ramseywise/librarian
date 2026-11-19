---
title: Image Prompting Practices for Diffusion Models
tags: [multimodal, diffusion-and-image-generation, reference]
summary: Practitioner advice from Phoenix and Taylor for prompting Midjourney, DALL-E and Stable Diffusion (format and style modifiers, weights, negative prompts, inpainting, upscaling, consistent characters) and for the Stable Diffusion tooling around them; every setting is the authors' experience, not a measurement.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-prompt-engineering-for-generative-ai-ch07-diffusion-models-image-generation.md
  - data/raw/papers/2026-11-07-prompt-engineering-for-generative-ai-ch08-standard-practices-image-generation-mi.md
  - data/raw/papers/2026-11-08-prompt-engineering-for-generative-ai-ch09-advanced-image-generation-stable-diffu.md
  - data/raw/papers/2026-11-07-prompt-engineering-for-generative-ai-ch01-five-principles-of-prompting.md
  - data/raw/papers/2026-11-07-prompt-engineering-for-generative-ai-ch10-building-ai-powered-applications.md
---

# Image Prompting Practices for Diffusion Models

Phoenix and Taylor (*Prompt Engineering for Generative AI*, chapters 7 to 9) describe prompting a diffusion model as a search through latent space for the picture you have in mind, and they connect each technique to their five principles of prompting. Nothing here is tested: each technique comes with a picture or two and the authors' opinion.

## Choosing a model

By the authors' own experience, DALL-E 3 composes best and integrates with ChatGPT, Midjourney looks best, and Stable Diffusion is the most flexible and the one to build products on. The comparison is a single prompt (their Figure 7-12) and no metric. Chapter 7 also repeats figures from other sources. Parameter counts cited are 6.6 billion for SDXL 1.0 and, for Stable Diffusion v1.5, 0.98 billion. Running Stable Diffusion locally needs a GPU with 8GB of VRAM. Only a small share of its training images could be reproduced by researchers, which the chapter offers as evidence that the model keeps no copies (see [[Diffusion Model Training-Data Extraction]]). The controls it exposes include classifier-free guidance, denoising and seed (see [[Classifier-Free Diffusion Guidance]]).

## Text-prompt techniques (Midjourney v5)

- **Format and style.** Name the format (stock photo, oil painting, hieroglyph). It shifts both style and content, drags in whatever the training data associates with it, and so works best paired with other techniques. An artist or art movement acts as a shortcut into one area of latent space. The authors lean towards artists dead for more than a year rather than living ones, and recommend legal advice before commercial use. Breaking a style into parts only works for artists well known enough to be describable from training data.
- **Quality boosters.** Add one or two after the subject, separated by commas (for example 4k, very beautiful, trending on artstation).
- **Weights.** Each word starts at weight 1, with earlier words counting for more, which is why the subject comes first. The `::` syntax blends concepts. In the two-artist example (Golden Gate Bridge, Van Gogh against Dali) the weights move in steps of 0.2 across 0 to 1, like a grid search without a quality score. The authors also suggest giving Van Gogh weight -1 beside Dali at 5 to remove his influence, shown on one image.
- **Negative prompts.** The `--no` flag amounts to weight -0.5 for that part of the prompt; for tangled concepts such as oil painting and its frame, list them with commas. If that fails, raise the negative weight. The authors report that newer versions (Midjourney v5, Stable Diffusion XL) rarely need negative prompts aimed at hands, eyes or bodies, and that strongly correlated concepts defeat negation at times.
- **Reverse engineering and pruning.** `/describe` turns an image back into a prompt. `/shorten`, with token weights, trims a prompt, because each extra word adds noise.
- **Rewriting and unbundling.** Another model can rewrite a user's prompt, for example by finding the artist's medium and filling a medium-subject-artist template. To unbundle a style, have a text model describe a work without naming the work or its artist, shorten that description, add your own subject and recombine the parts. Meme mapping gathers prompts from communities (Lexica.art, Discord) and finds repeated patterns by hand, with NGram analysis or with image labels. On trained prompt-writing models, the authors say they lift quality only to average, short of an expert. Chapter 10 has one model write another's image prompt (meta-prompting).
- **Base image.** For img2img, begin the prompt with a link to the base image and keep the text short.

## Editing an image

- **Inpainting.** In the DALL-E inpainting example, describing just the erased area gave better results than describing the entire picture. The authors also suggest combining several models, each used where it is strongest.
- **Outpainting.** Zoom Out and Custom Zoom widen the context or alter the aspect ratio.
- **Consistent characters.** Produce a 2:1 image holding two views, then inpaint one half to get each further angle.

## Open-source Stable Diffusion tooling (chapter 9)

The settings below are what the authors recommend "in our experience", with the warning that you must experiment yourself.

- **Sampling.** DPM++ 2M Karras or UniPC, 20 to 30 steps, CFG 7. To reproduce an image, keep its seed and read the PNG Info tab; parameter grids help with sweeps. Weights are written `(word:1.5)`, `[word]` lowers emphasis, and prompt editing turned out only marginally useful for them.
- **Img2img.** Euler at 50 steps, CFG 20 to 30, comparing denoising strengths in an X/Y/Z plot.
- **Upscaling.** Use a generic prompt instead of the original one, 150 to 200 steps or more, CFG 8 to 15 and denoising 0.1 to 0.2. On an M2 MacBook Air, 512 to 1024 took around 10 to 30 minutes.
- **Inpainting in AUTOMATIC1111.** Describe the full image, choose the whole picture as the inpaint area and repair a single artifact each time. Small edits suit denoising between 0.2 and 0.4; past 0.4, the authors saw inconsistent elements across the image and hallucinations. In their tests, feeding masks from [[Segment Anything SAM and SA-1B]] into inpainting was unreliable.
- **ControlNet.** The preprocessor must fit both the model and the Stable Diffusion version; begin with Canny. The ControlNet models in the chapter target SD 1.5 alone (see [[ControlNet Spatial Conditioning]]).
- **DreamBooth.** Train one concept, tied to a rare token (zwx and ukj are examples), from 20 to 30 images, though 5 may be enough. On one GPU the fine-tune takes roughly 45 to 60 minutes, whereas the chapter cites 150,000 GPU hours and $600,000 for the original model (see [[Textual Inversion and DreamBooth Personalization]]). The authors add that when they wrote, LoRA and Hypernetwork models were fewer than 10% of Civitai's models and tended to rate lower.
- **SDXL refiner.** Hand over at 0.6 of 30 steps: 18 for the base, 12 for the refiner.
- **Hosted API.** When written, $10 bought 1,000 Stability AI credits, enough for about 5,000 images. The chapter reserves local or Colab use of diffusers for custom pipelines.

## Limits

- Chapters 7 to 9 contain no experiment and no image-quality metric. Settings reflect the authors' experience, and the models date from late 2023 and early 2024 (Midjourney v5 and v6, SD 1.5 and SDXL 1.0, diffusers 0.11.1, AUTOMATIC1111). Midjourney features such as Zoom Out, Vary Region, `/describe` and `/shorten` belong to the product and may since have changed.
- Chapters 8 and 9 disagree on inpainting: chapter 8 says to prompt for the erased region only, while chapter 9 says to describe the whole image.
- Chapter 7's cost, popularity and revenue numbers come from others and are dated. Its account of the diffusion mechanism is a few paragraphs with no noise schedule or sampler detail, and its idea that Midjourney upscale clicks serve as feedback data has no source.
- How far the law permits imitating living artists is unsettled. Chapter 9's text prints no authors or year; they were taken from the repository's references.

## See Also
- [[Diffusion and GAN Image Generation]] — prerequisite-for
- [[Latent Diffusion Models]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[ControlNet Spatial Conditioning]] — related (the spatial-conditioning add-on used in the tooling section)
- [[Textual Inversion and DreamBooth Personalization]] — related (DreamBooth settings)
- [[Segment Anything SAM and SA-1B]] — related (SAM masks for inpainting)
- [[Prompt Engineering]] — related (the five principles applied to images)
