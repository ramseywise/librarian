---
title: Hugging Face Transformers Library and Model Hub
tags: [infra, concept]
summary: "Wolf et al. (EMNLP 2020 demo) describe the Transformers library, in which every model is a tokenizer, a transformer and a task head loaded through Auto classes, plus a community Model Hub and export paths such as ONNX; the paper reports nearly a 4x ONNX speedup (self-reported, no setup)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-wolf-2020-transformers.md
---

# Hugging Face Transformers Library and Model Hub

Wolf, Debut, Sanh et al. (EMNLP 2020, Systems Demonstrations, arXiv 1910.03771) describe an open-source library that makes Transformer architectures accessible, extensible and deployable through one unified API, together with a community hub for sharing pretrained and fine-tuned models. It is a systems description; the authors train no model and run no controlled experiment.

## Design

Every model in the library is three parts:

- **Tokenizer.** Turns raw text into sparse index encodings and back. It keeps the vocabulary map from token to index, follows the model's own tokenisation process, and deals with special tokens, token type indices and cutting inputs to a maximum length.
- **Transformer.** The attention architecture the library implements (its lineage names Vaswani et al.). The paper says the library's structure was inspired by tensor2tensor and the original BERT code, and that the idea of easy caching of pretrained models came from AllenNLP.
- **Head.** A wrapper class that puts an output layer (and optionally a loss) over the contextual embeddings the transformer produces, so the model can make a task-specific prediction.

**Auto classes** pick and build the matching model or tokenizer from whichever pretrained configuration the user names, so a user can swap models and frameworks. The paper's example loads a tokenizer and a model from the same checkpoint name with `AutoTokenizer.from_pretrained` and `AutoModel.from_pretrained`.

## Model Hub and deployment

The **Model Hub** distributes pretrained and fine-tuned checkpoints, with model cards and live inference (see [[Model Cards]]). The paper lists deployment paths through PyTorch and TensorFlow interoperability, TorchScript, ONNX and CoreML.

## Reported figures (self-reported)

- Exporting BERT, RoBERTa and GPT-2 to ONNX gave close to a 4x speedup, in work done with the ONNX team (self-reported); the text names no hardware or baseline.
- At the time of writing (2020) the hub held 2,097 user models (self-reported), and the library was released under Apache 2.0 and counted more than 400 contributors from outside (self-reported).

## Limits

- A technical report: it covers the core modelling specification and sends readers to the documentation for training and development tooling.
- The one quantitative result (ONNX) lacks hardware, baseline and sequence length in the text, and the figure values are not given there.
- The hub count, contributor count and model list date from 2020.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Model Cards]] — related (the hub attaches a model card to shared models)
- [[TurboTransformers Variable-Length Serving]] — related (another Transformer serving system)
