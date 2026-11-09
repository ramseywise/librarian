---
title: BLIP Bootstrapped Captioning and Filtering
tags: [multimodal, concept]
summary: "BLIP pretrains one mixture of encoder-decoder (MED) for understanding and generation, then uses CapFilt, a captioner plus a filter, to clean noisy web image-text pairs before pretraining a new model."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-li-2022-blip.md
---

# BLIP Bootstrapped Captioning and Filtering

BLIP addresses two limits at once: models tend to suit either understanding or generation, and web alt-text is a noisy supervision source. Its answer is a multimodal mixture of encoder-decoder (MED) and a data bootstrapping step called CapFilt.

## Mechanism

- MED works as a unimodal encoder, an image-grounded text encoder or an image-grounded text decoder. A ViT image encoder pairs with a BERT-style text transformer, trained jointly with contrastive (ITC), matching (ITM) and language-modeling losses.
- CapFilt fine-tunes two copies of the pretrained MED on COCO: a captioner (language-modeling head) and a filter (ITC plus ITM heads). The captioner writes one nucleus-sampled caption for each web image, and the filter discards texts that do not match, whether scraped or synthetic. A fresh model is then pretrained on the cleaned texts together with the human-annotated pairs.

## Reported results (self-reported)

- Setup 14M images (COCO, VG, CC, CC12M, SBU), ViT-B/16, single run: CapFilt raises COCO text-retrieval recall@1, zero-shot NoCaps CIDEr and COCO caption CIDEr over raw web text. Captioner alone and filter alone each help (text-retrieval R@1 79.1 and 79.7), and the effects are complementary.
- At 129M images (115M LAION added), a ViT-L captioner and filter lift a ViT-B student further (self-reported).
- Nucleus sampling with p=0.9 outperforms beam search for synthetic captions; the filter rejects 25% of nucleus-sampled texts versus 19% of beam-search texts (self-reported).
- Sharing all text layers except self-attention is best at 252M parameters (77.5 against 77.3 for all shared and 78.3 for none shared at 361M, 14M images, no CapFilt). Sharing parameters between captioner and filter drops the noise ratio to 8% from 25% and lowers scores, which the authors read as confirmation bias.
- Continuing to train on the bootstrapped data is worse than training a fresh model, and simply replicating web text does not match CapFilt (self-reported).
- At 14M images BLIP beats ALBEF on COCO retrieval average recall@1 and on VQA test-std. NLVR2 gains little from extra web images.

## Limits

- The captioner and filter are finetuned on COCO only.
- Results are single runs with no seeds; the noise ratio is just the share the filter rejects, with no human audit, and the explanation the authors offer for why nucleus sampling helps (diversity) is only a hypothesis.
- Multiple bootstrapping rounds, several captions per image and ensembles are suggested but untested.
- Video transfer ignores temporal information; SNLI-VE is left out because its test data is reported as noisy.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[ALBEF Align Before Fuse]] — prerequisite-for (the main baseline BLIP extends)
- [[SimVLM PrefixLM Pretraining]] — alternative-to (generation-capable pretraining on larger data)
- [[InstructBLIP Instruction-Aware Query Transformer]] — extends
