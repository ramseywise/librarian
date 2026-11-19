---
title: "GLIGEN Grounded Text-to-Image"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "GLIGEN freezes a pretrained text-to-image diffusion model and adds gated self-attention layers that take grounding tokens (boxes, keypoints, reference images), so box grounding generalises to unseen concepts."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-li-2023-gligen.md
---

# GLIGEN Grounded Text-to-Image

Li and colleagues ask whether a pretrained text-to-image diffusion model, kept frozen, can take in new kinds of grounding (boxes, keypoints, reference images, spatial maps), retain its concept knowledge and still generalise to concepts it has not seen. Results are self-reported.

## Mechanism

- Every weight of the pretrained latent diffusion model (an LDM trained on LAION, or Stable Diffusion) is frozen. Each Transformer block gets a new trainable **gated self-attention** layer over the visual tokens concatenated with grounding tokens; its output is added back to v, scaled by beta and tanh(gamma).
- A **grounding token** is h = MLP(f_text(e), Fourier(l)): an MLP over an entity's text (or image) embedding and the Fourier embedding of its box.
- **Scheduled sampling:** beta is 1 for an initial fraction tau of the steps and 0 afterwards, which switches the gate off.
- Null-caption training uses the classifier-free guidance scheme with 10% token dropping.

## Findings

- GLIGEN-LDM trained only on COCO2014CD reaches a higher zero-shot LVIS AP than LAMA, which is fully supervised on LVIS. Scaling grounding data (GoldG, O365, SBU, CC3M) raises zero-shot LVIS AP to 11.1, with rare-class AP rising from 5.8 to 9.0 (upper bound 25.2). GLIGEN-Stable reaches 10.8; fine-tuning on LVIS gives 14.9.
- COCO2017 layout-to-image: GLIGEN-LDM is ahead of the strongest baselines on both FID and YOLO AP (22.4 against 13.40 for LAMA). On COCO2014, detection-only training gives YOLO AP 24.0 against 0.6 for the base LDM; pseudo-labelled GLIP data gives only 11.2.
- Pretraining on the large data, then fine-tuning on COCO2017, gives YOLO AP 30.8 (19.1 zero-shot) at FID 21.58.
- Ablations: Flamingo-style gated cross-attention grounds worse than gated self-attention at similar FID; replacing the Fourier box embedding with a plain MLP collapses grounding; a pseudo caption of noun entities worsens FID against a null caption.
- Where large objects (30-50% of the image) are inpainted with grounding, YOLO AP is higher YOLO AP than the plain LDM; keypoint-grounded GLIGEN beats pix2pixHD on keypoint AP and FID (27.34 against 142.4; COCO2017 val).
- The learned gate value peaks at roughly 60-70k iterations, around when the model begins learning spatial correspondence.

## Limits

- Keypoints learned for humans fail on non-human shapes (cat, lamp), and scheduled sampling does not rescue this.
- Sampling with beta fixed at 1 sometimes lowers image quality relative to the original model, so scheduled sampling is a compromise.
- Baseline text-to-image models cannot accept boxes; a fine-tuned LDM is the only reference with a YOLO score.
- The paper has no seeds, repeat runs or significance tests, and does not state the compute for the scaled runs.
- Early UNet attention maps are uninterpretable, attributed to missing positional embeddings in the visual tokens.

## See Also

- [[Latent Diffusion Models]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[ControlNet Spatial Conditioning]] — related
- [[Diffusion and GAN Image Generation]] — prerequisite-for
