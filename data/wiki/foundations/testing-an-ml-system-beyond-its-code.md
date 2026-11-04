---
title: "Testing an ML System Beyond Its Code"
tags: [foundations, pattern]
summary: "Code tests pass on a correct function fed broken data, so also test data validity, model behaviour (minimum functionality, invariance, direction) and model sanity (overfit a tiny batch), with injected seams and a container integration test against fake cloud services."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--05-mlops-maturity-and-best-practices.md
---

# Testing an ML System Beyond Its Code

An ML system changes when code, data or model changes, so it needs tests on all three. A correct function on broken data gives a wrong model and passing tests.

## Seams for code tests

Split a service so side effects are injected: model location read from an environment override, an endpoint URL pointing at a fake cloud service in tests, and output callbacks passed to the handler. Then a handler test uses a mock model and a list's `append` as the callback, with no cloud and no real model. Mocking everything misses packaging, env-var and wiring bugs; tests that hit real cloud are slow, costly and can touch production.

**Integration test:** run the real container with docker-compose against fake cloud services (LocalStack needs no account), post an event, and assert the response and the record in the fake output stream. A tolerance-based diff (`DeepDiff` at one significant digit) lets through more than it seems: against an expected 21.3, 21.34 passed and 21.36 failed, and an added or removed key was never read by the two asserts used.

## Data validity

Run in the feature pipeline: no nulls where none are allowed, categoricals in expected values, floats in range; for text, length, encoding, language. A batch with distance multiplied by 1000 failed the range check. Fixed ranges from training percentiles trip on healthy new data when the training set was small; add margin and refit bounds each run.

## Behaviour (black-box, CheckList style)

- **Minimum functionality:** simple cases it must always get right.
- **Invariance:** a perturbation that should not change output (an extra irrelevant key) does not.
- **Directional:** a perturbation that should change output does, in the right direction (8 miles predicted longer than 2: 30.5 against 11.3 minutes).

## Model sanity

Cheap catches for a run that finishes yet is wrong: check input and output shapes, that loss falls after one batch, that the model can overfit a tiny batch to near-zero loss, that the pipeline runs on every supported device, that early stopping and checkpoint logic fires. Slow, so gate them in CI on changes to model code. Overfitting 32 rows reached loss 0.0002 for a healthy model; an optimiser holding another object's parameters stayed at 4.4106 with no error raised: if it cannot memorise 32 rows, it is a wiring bug, not tuning.

## Pitfalls

- A bad record on a stream retries the batch, blocking the shard until expiry or a retry limit; catch it and send it to a dead-letter destination.

## See Also
- [[ML Test Score: Scoring Production Readiness by the Minimum]] — related
- [[PyTorch Training Loop Silent Bugs]] — related
- [[Rerunnable Cleaning Loader with Assertions]] — related
- [[MLOps Maturity Levels and CT vs CI/CD]] — related
