---
title: SAM 3 Promptable Concept Segmentation
tags: [multimodal, concept]
summary: "SAM 3 detects, segments and tracks every instance of a noun-phrase or exemplar concept using a presence head and a human-plus-AI-verifier data engine; it reports cgF1 54.1 on SA-Co/Gold and LVIS mask AP 48.8 zero-shot (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-sam-3-2025.md
---

# SAM 3 Promptable Concept Segmentation

The SAM 3 paper (preprint) introduces Promptable Concept Segmentation (PCS). For an image, or a video no longer than 30 seconds, the task is to find, segment and track every instance of a concept, which is specified by a short noun phrase, by image exemplars, or by both. That contrasts with the previous task of segmenting a single object per point, box or mask prompt.

## Mechanism

- The model has about 850M parameters. One Perception Encoder backbone is shared and feeds a DETR-style detector conditioned on text and exemplars. The detector has a fusion encoder, a decoder of 6 layers, 200 object queries and a MaskFormer-style mask head. For video, a memory tracker is inherited from the previous model.
- A learned global presence token predicts whether the phrase appears at all, while each query only judges whether it matches given presence; the final score is their product. This separates recognition from localization.
- The data engine pairs humans with AI verifiers, Llama 3.2 fine-tuned to check masks and exhaustivity, across four training stages with hard-negative phrases. SA-Co/HQ contains 4M unique phrases, and the benchmark has 207K concepts.
- The cgF1 metric is classification-gated F1, 100 times pmF1 times image-level Matthews correlation.

## Results (self-reported)

- Zero-shot on LVIS, mask AP is 48.8 against 38.5 for the best earlier system. On SA-Co/Gold instance segmentation, using the oracle protocol across 3 annotations at threshold 0.5, cgF1 is 54.1, which is 74% of the estimated human level of 72.8. Other splits give Silver 49.6, Bronze 42.6 and Bio pmF1 55.4. Under a random-pair protocol, human agreement drops to 55.5.
- Ablations use lighter models and shorter schedules, so tables do not compare with each other. The presence head adds 1.5 cgF1. Hard negatives lift image-level MCC from 0.44 to 0.68, and cgF1 from 28.3 to 43.0. Using the exhaustivity verifier instead of the presence score adds 7.2 cgF1, with the mask verifier adding 1.1 beyond that (62.3 against human 72.8). The PE encoder gets 43.2 where Hiera-L gets 32.8.
- Verifiers roughly double the throughput of the data engine, with negative phrases going 5x faster and positive ones 36% faster. Given three simulated exemplar clicks, PCS outperforms text-only prompting by 21.6 cgF1. One exemplar beats T-Rex2 by margins of 18.3 (COCO), 10.3 (LVIS) and 20.5 (ODinW13). With 10 shots on ODinW13, AP is 71.8 versus 67.9.
- Video: SA-Co/VEval SA-V cgF1 30.3 and pHOTA 58.0 (human cgF1 53.1); MOSEv2 J&F 60.3 against 53.8. With an MLLM calling it as a tool, ReasonSeg val gIoU 77.0. CountBench accuracy 93.8%. 30 ms per image with 100+ objects on an H200. Training took 172k A100 and 86k H200 GPU hours.

## Limits

- Weak on fine-grained out-of-domain concepts (aircraft types, medical terms, thermal imagery) zero-shot; prompts are simple noun phrases, with no referring expressions without an MLLM; video cost grows linearly with tracked objects; concept and instance prompting do not interleave.
- PCS is ambiguous by nature. Each hard negative has a single label, so human image-level MCC is extrapolated. The authors tuned the baselines themselves, and some ran zero-shot outside their training distribution. On Roboflow100-VL the model trails Grounding DINO, at 15.2 AP versus 15.7.
- No seeds or confidence intervals for main results. The annotation pool does not represent all user communities; the benchmark is not for training. Mid-2025 baselines have likely dated.

## See Also
- [[SAM 2 Promptable Video Segmentation]] — prerequisite-for
- [[Segment Anything SAM and SA-1B]] — prerequisite-for
- [[LLM-as-Judge Evaluation]] — related (AI verifiers filter training masks)
