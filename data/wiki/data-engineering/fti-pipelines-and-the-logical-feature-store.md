---
title: "FTI Pipelines and the Logical Feature Store"
tags: [data-engineering, ml-platform, pattern]
summary: "The FTI pattern reduces an ML system to a feature pipeline, a training pipeline and an inference pipeline that meet only at a feature store and a model registry; the LLM Engineer's Handbook applies it to an LLM product with a vector DB plus versioned artifacts standing in for the feature store."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch01-llm-twin-concept-and-architecture.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch03-data-engineering.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch04-rag-feature-pipeline.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch10-inference-pipeline-deployment.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch11-mlops-and-llmops.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch12-mlops-principles.md
---

# FTI Pipelines and the Logical Feature Store

Iusztin and Labonne (*LLM Engineer's Handbook*, 2024) build their LLM product, the "LLM Twin", on the feature/training/inference (FTI) architecture, which they credit to Dowling. The claims below are the authors' design arguments; the chapters report no experiment that compares architectures.

## Why not one pipeline

A monolithic batch pipeline avoids training-serving skew, meaning a mismatch between how features are made for training and for serving, because the same feature code runs in both places. The authors list its costs: the features are not reusable and the design cannot move to streaming. They also say model training is the easy part of an ML system and the engineering around it is the hard part.

## The three pipelines

- **Feature pipeline:** turns raw data into versioned features written to the feature store. Versioning keeps the features used in training and in inference matched, which is the authors' route to avoiding skew.
- **Training pipeline:** reads versioned features, trains, and writes models to a model registry. The authors advise storing the best hyperparameters after experimentation so training can be repeated continuously, and keeping a manual approval step before a new model reaches production even in a fully automated system.
- **Inference pipeline:** reads features and the registered model to serve requests. The authors log queries, the prompts built by RAG and the answers to a prompt monitoring system.

The pipelines communicate only through the feature store and the registry. Scaling then differs per pipeline: data and feature work scale horizontally, training scales vertically by adding GPUs, and inference scales horizontally with request volume.

## Applying it to the LLM Twin

- **A fourth component.** Data collection is a separate pipeline owned by data engineering, ahead of the three FTI pipelines. The collected data is grouped by category (article, repository, post) rather than by source platform, so a new crawler needs no downstream change. It talks to the feature pipeline only through the MongoDB store, so the two run on independent schedules.
- **A logical feature store.** Instead of a specialised feature store, the authors use a vector DB plus versioned artifacts. The feature pipeline writes two snapshots: one after cleaning (for fine-tuning) and one after chunking and embedding (for RAG). They advise not shaping warehouse data for one use case.
- **Same code at both ends.** The RAG retrieval path reuses the feature pipeline's cleaning, chunking and embedding functions and model for the user query, and the inference chapter asks for identical pre- and post-processing in training and inference, both to avoid skew. See [[Train-Serving Skew and the Shared Feature Function]].
- **Training requirement.** The stated requirement is support for 7B, 14B, 30B or 70B parameter LLMs and several instruction-dataset sizes. This is a design requirement, not a measurement.

## What it buys for automation

The authors credit two choices for making continuous training (CT) simple: the FTI split and adopting an orchestrator from day 0. In the appendix, CT automates the FTI pipelines while CI/CD ships new pipeline code, and CT can be triggered on a schedule, on new data or on a monitoring drop. In the LLM Twin the trigger is manual because the data are static links; the authors name manual, REST API and scheduled triggers as the initial options. They also say a single end-to-end pipeline is not the best approach, and that each pipeline should run alone and start the next by trigger. See [[MLOps Maturity Levels and CT vs CI/CD]].

## Limits

- Chapter 1 has no experiments, data or numbers; it is product planning and architecture for a three-person-team thought experiment, with figures absent from the text copy.
- Pretraining is out of scope; the model is a fine-tune of an open-weight LLM picked in a later chapter.
- In the deployed example the CT pipeline is a single monolith because a free-trial limit allows only three pipelines, which the authors say is not the approach to copy. CI contains only a dummy test, CT starts only by hand and has no drift detection, and CD pushes to main with no staging.
- The data collection chapter works at hundreds of documents, and the RAG feature pipeline uses a naive full pull with no deletes handled and change data capture only discussed. Scale, cost and skew are never measured.
- Tools and versions date from 2024.

## See Also
- [[Train-Serving Skew and the Shared Feature Function]] — prerequisite-for
- [[Feature Stores: Parts and When You Need One]] — alternative-to (a specialised store is the heavier option the authors decline)
- [[MLOps Maturity Levels and CT vs CI/CD]] — related
- [[Model Registry Aliases and the Run Record]] — related (the registry both training and inference touch)
- [[Orchestrator Design Rules and Tool Choice]] — related
- [[Advanced RAG Retriever: Self-Query, Query Expansion, Filtered Search and Rerank]] — related (the inference-side retrieval step)
