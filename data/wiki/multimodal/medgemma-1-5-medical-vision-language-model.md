---
title: MedGemma 1.5 Medical Vision-Language Model
tags: [multimodal, concept]
summary: "MedGemma 1.5 4B keeps the Gemma 3 architecture and 400M MedSigLIP encoder but adds 3D CT/MRI via capped slice stacks, whole-slide pathology via capped patch sets, localization and lab-report extraction; gains on new tasks came with regressions on some older ones (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-sellergren-2026-medgemma-1-5-technical-report.md
---

# MedGemma 1.5 Medical Vision-Language Model

The MedGemma 1.5 technical report (Google Research and Google DeepMind, arXiv 2604.05081) describes a single 4B model that handles 3D CT and MRI as well as whole-slide pathology, and also bounding-box localization, chest X-rays taken at several timepoints and lab-report extraction. The architecture is unchanged from Gemma 3, and the vision side is the 400M MedSigLIP encoder.

## Mechanism

- **Volumes:** 3D scans are cut into 2D axial slices at 896x896, at most 85 per query (21,760 vision tokens) so the prompt stays under 32K tokens; longer scans are sampled equidistantly along z and slice indices are interleaved in the prompt. CT uses three windowed channels (-1024 to 1024, -135 to 215 and 0 to 80 HU); MRI is min-max normalised with no windowing.
- **Slides:** tissue-masked patches at one randomly chosen magnification per slide (5x 0.34, 10x 0.33, 20x 0.33), 896x896, with a cap of 126 per slide (32,256 tokens), kept in spatial order. That cap exceeds the CT one since slide captions run shorter.
- **Training:** the vision encoder stays frozen; the LLM receives further pretraining, followed by distillation (256 teacher logits per token) and RL as in Gemma 3, plus domain teachers for CT, MRI and histopathology. Whole-slide RL uses token-level ROUGE-L as reward.
- Localization output is a JSON list of labelled boxes [y0, x0, y1, x1], normalised to 0-1.

## Results (self-reported; temperature 0, single run)

- Against MedGemma 1 4B: CT condition classification moves 58.2 to 61.1; whole-slide ROUGE-L 2.2 to 49.4; Chest ImaGenome IoU 3.1 to 38.0; and for MS-CXR-T the macro accuracy goes from 61.1 up to 65.7. Internal sets are class-balanced yes/no per condition. MRI 51.3 to 64.7 is flagged below.
- The 4B whole-slide score is near the specialist PolyPath (49.8) and well beyond both Gemini 3 Flash at 13.9 and Pro at 12.2; on ImaGenome it sits near Gemini 3 Flash (38.5) and Pro (39.1).
- Lab-report extraction macro F1 rises on three internal sets (78 to 91, 50 to 71, 25 to 64) and stays at 85 on Mendeley, which has 14 images.
- Text benchmarks improve too. MedQA rises from 64.4 to 69.1; EHRQA from 67.6 to 89.6; multimodal MedXpertQA from 18.8 to 26.4.
- Using the public CT-RATE validation split (each of 18 conditions asked separately), macro F1 is 26.9, against 23.5 for MedGemma 1 and 8.5 for Gemini 3 Flash.
- Against Qwen3 VL 4B it is stronger on specialised vision tasks but weaker on general biomedical text such as MedQA (69.1 vs 76.8).
- Some scores went down. MMLU-Pro fell from 39.1 to 33.8 (for comparison, Gemma 3 4B is at 43.6). SlakeVQA dropped to 59.8 from 72.3. VQA-RAD slipped from 49.9 to 48.1, and PubMedQA from 73.4 to 67.6. The authors attribute the SLAKE and VQA-RAD drops to benchmark quality.

## Limits

- According to the authors, the model should not be deployed before clinical fine-tuning, and its capabilities are data-processing tools, not clinical decision-making.
- The CT, MRI, whole-slide and lab-report evaluations run on internal data, so outsiders cannot reproduce them; the only public ones are CT-RATE, MS-CXR-T and ImaGenome. CT and MRI labels were derived by regex plus Gemini extraction from reports, with a manual check on a random sample only. No per-dataset confidence intervals; prompts were hand-tuned for this model.
- Coverage is sparse: 85 slices, 126 patches, and only single slide-text pairs were tested. Some Qwen3 VL evaluations are missing.
- Internal inconsistencies noted by the extraction: concatenated table cells leave the MRI 64.7 and lab-extraction 64 values uncertain, the abstract's MRI "11%" does not match 51.3 to 64.7, its "47% macro F1" for slides is a ROUGE-L gain, and its "18% macro F1" for lab reports does not match the table cleanly. Treat 64.7 as unverified.
- Parts of the report were drafted with Gemini models and then human-edited; the extraction notes that its baselines (Gemini 3, Qwen3 VL, Gemma 3) date it.

## See Also
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[Vision-Language Model Training Families]] — prerequisite-for
