---
title: Clipper Prediction Serving
tags: [infra, concept]
summary: "Clipper is a 2016-17 serving layer that sits between applications and unmodified ML frameworks, adding per-model caching, AIMD adaptive batching against a latency target, and bandit-based model selection; batching raised throughput up to 26x under a 20 ms target (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-crankshaw-2016-clipper.md
---

# Clipper Prediction Serving

Crankshaw et al. describe Clipper, written in Rust, as two layers between applications (REST or RPC) and models running in Docker containers. The model abstraction layer provides a cache of predictions for each model (CLOCK eviction), adaptive batching in each container and container replication. The model selection layer picks models online using bandit policies, Exp3 for a single model or Exp4 for a linear ensemble, plus straggler mitigation and per-user state kept in Redis.

## Adaptive batching

The batch size is found by AIMD against a latency target: it grows until a batch misses the target, then backs off by 10%. The paper reports AIMD performing nearly identically to quantile regression and being simpler. A small deliberate delay can help when load is bursty.

## Results (self-reported)

- MNIST models in Scikit-Learn and Spark, 20 ms latency target: batching raised the Scikit-Learn SVM's throughput by up to 26x. The maximum batch size within the target differs 241x between the linear and the kernel SVM, giving nearly 30,000 queries/s against 200.
- Adding a 2 ms batch delay lifted the Scikit-Learn SVM's throughput 3.3x and did nothing for the Spark SVM.
- GPU containers replicated across four nodes on 10Gbps: 3.95x throughput (19,500 to 77,000 queries/s); a 1Gbps link saturated at the second remote machine.
- Combining five CNNs in a linear ensemble lowered ImageNet error by a relative 5.2%.
- Against TensorFlow Serving on MNIST, 23,138 against 19,537 for Clipper's Python TensorFlow container (unit assumed queries/s); Python containers lost 15-18% and C++ ones were nearly identical.

## Limits

- Models are black boxes: slow models stay slow, and training or retraining is out of scope.
- With large inputs on 1Gbps links, the network becomes the bottleneck.
- The paper gives no seeds, number of runs or variance, and omits the cache size and Exp3 parameters. The TensorFlow comparison covers three models, with batch sizes tuned by hand for TensorFlow Serving.
- Hardware and models date from 2016-17, and no LLM or token-level workload is tested.

## See Also
- [[LLM Inference Economics]] — prerequisite-for (batching trades throughput against first-token latency)
- [[S-LoRA Multi-Adapter Serving]] — related (batching shared work across many models)
- [[Cheap-First Gating and Model Cascades]] — related (online model selection in front of several models)
- [[TurboTransformers Variable-Length Serving]] — related (length-aware batching for transformers)
