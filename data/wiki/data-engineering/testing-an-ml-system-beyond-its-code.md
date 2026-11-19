---
title: "Testing an ML System Beyond Its Code"
tags: [data-engineering, ml-platform, pattern]
summary: "Code tests pass on a correct function fed broken data, so also test data validity, model behaviour (minimum functionality, invariance, direction) and model sanity (overfit a tiny batch), with injected seams and a container integration test against fake cloud services."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--05-mlops-maturity-and-best-practices.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch09-modularity-ml-writing-testable-legible-code.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch10-standards-coding-creating-maintainable-ml-code.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch15-quality-acceptance-testing.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch11-mlops-and-llmops.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch12-mlops-principles.md
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

## Wilson on testable ML code

Wilson (*Machine Learning Engineering in Action*) advises deciding where to split code by how each block can be tested, with a unit test per public and private method on known mock data, run before merging. He concedes pure test-first development is very hard for non-deterministic ML algorithms; his one shown test is a deterministic check of a distribution's percentile points. He also advises post-condition checks such as input length equal to output length, raising a custom exception. Code-craft detail is in [[Python Foundations Reference]]. This is experience-based advice with no measured benefit.

## Wilson on fallbacks, acceptance review and explanations

Wilson (*Machine Learning Engineering in Action*, chapter 15) advises always having a fallback for model output that breaks a business rule or leaves its range, and testing the fallback repeatedly. His anecdote is a regression-driven controller without one that pushed a chuck from about 2,800 to 15,000 RPM. He advises asking experts and owners of prior art for safe ranges, defaults and past failures first. For cold start he advises a default that is fast, simple and relevant (popularity by region or day, expert-curated, high-inventory) and reusing it as the fallback; his dog-grooming example serves a rule-based answer to users with under three earlier appointments (hypothetical).

For release review he ranks release review as: experts judging real users' predictions first, then company-wide dogfooding, then the team testing its own work, with about 50 users per genre in his music example, using unseen-data prediction distributions and random samples rather than handcrafted ones. Dogfooding still carries bias, since employee accounts are unrepresentative. He advises adding explanations before they are needed, using SHAP summary plots for overall feature impact and waterfall plots to explain the most extreme past cases (his wildfire example plots the five largest burn areas). He cautions that SHAP explains the model, not reality, and should be explained to the business first; see [[SHAP Attributions and the Limits of Explanations]].

Limits: no experiments, every number is an illustrative scenario; the shap API details may have dated since 2022; an assert in his `validate_row` listing is written as a tuple and so can never fail.

## The handbook's test list (LLM Engineer's Handbook, appendix)

Iusztin and Labonne list six kinds of test (unit, integration, system, acceptance, regression, stress), with regression applying at every level. Their model tests check tensor shapes, that loss falls after a batch, that a small batch can be overfit toward zero loss, that the model runs on CPU and GPU, and that early stopping and checkpoints work; they run the costly ones only when model code changes. The appendix reports no measurements. In the LLM Twin repository itself the CI holds only a dummy test.

## See Also
- [[ML Test Score: Scoring Production Readiness by the Minimum]] — related
- [[PyTorch Training Loop Silent Bugs]] — related
- [[Rerunnable Cleaning Loader with Assertions]] — related
- [[MLOps Maturity Levels and CT vs CI/CD]] — related
- [[ML Deployment Challenges by Workflow Stage]] — related (verification as one stage among four)
- [[Four Levels of AI Design Complexity]] — related (simulated prototypes miss inference errors)
