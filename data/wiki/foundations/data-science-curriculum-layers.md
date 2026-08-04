---
title: Data Science Curriculum Layers
tags: [foundations, concept]
summary: "The tree-shaped ML curriculum — statistical foundations, then supervised learning branching to model evaluation and independently to unsupervised/ensembles/Bayesian — plus the six-layer analytics progression that precedes it and the branching decision that ends it."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--CURRICULUM.md
  - data/raw/repos/learn-ai-engineering/data-science--README.md
  - data/raw/repos/learn-ai-engineering/data-analytics--CURRICULUM.md
  - data/raw/repos/learn-ai-engineering/data-analytics--README.md
---

# Data Science Curriculum Layers

Two curricula that chain: analytics is the shared foundation, data science is one of three
branches off it. The interesting structural claim is that **the ML curriculum is a tree,
not a sequence** — most curricula are presented linearly and the linearity is usually a
lie about what actually depends on what.

## Analytics: six layers, then a branch

Python-first, dataset-level work that precedes any specialisation.

| # | Layer | What it covers |
|---|---|---|
| 1 | Python fundamentals | Types, control flow, functions, standard library |
| 2 | Data wrangling | NumPy arrays, pandas DataFrames, indexing, merging, cleaning |
| 3 | EDA + visualisation | Exploratory analysis, plotting, aggregation, time series |
| 4 | Feature engineering | Text representation, NLP preprocessing, TF-IDF, embeddings |
| 5 | Statistical analysis | Hypothesis testing, distributions, A/B testing, correlation vs. causation |
| 6 | Modeling + BI | Semantic analysis, topic modelling, similarity, clustering |

The curriculum **ends with a branching decision** rather than a capstone:

| Goal | Branch |
|---|---|
| Build pipelines and infrastructure | [[Data Engineering Foundations]] |
| Build predictive models, do ML research | Data science (below) |
| Build LLM-powered applications | Generative AI pillars — see [[AI Engineering Curriculum Structure]] |

All three branches require layers 1–3. Layer 4 (feature engineering) is most directly
useful to data science and generative AI, which is a quiet argument that the analytics
foundation is genuinely shared rather than nominally shared.

**Layer 5 is the critical path.** Statistical analysis is named a prerequisite for
interpreting model evaluation metrics correctly, for A/B testing inside pipeline
monitoring, and for the stats interviewing pillar. It is also the layer most often skipped,
because it is the only one that produces no artefact — you cannot demo a correct
understanding of multiple-comparison correction. The identified remaining gaps are causal
inference (DiD, IV, RD), Bayesian A/B testing, non-parametric tests, and time-series
stationarity testing.

## Data science: a tree with two independent branches

```
Layer 1: Statistical Foundations  (readings-only)
    │
    ├── Layer 2: Supervised Learning ──── Layer 3: Model Evaluation
    │                                          (depends on Layer 2)
    │
    └── Layer 4: Unsupervised Learning  (independent of Layer 3)
         │
         └── Layer 5: Ensemble Methods
                  │
                  └── Layer 6: Bayesian Methods
```

| # | Layer | What it covers |
|---|---|---|
| 1 | **Statistical foundations** | Bias-variance, probability, distributions, inference — readings-only, no code |
| 2 | **Supervised learning** | Linear/logistic regression, classification, SVMs, neural net basics |
| 3 | **Model evaluation** | Cross-validation, metric selection, learning curves, train/val/test discipline |
| 4 | **Unsupervised learning** | Clustering, dimensionality reduction, embeddings |
| 5 | **Ensemble methods** | Random forests, gradient boosting, stacking |
| 6 | **Bayesian methods** | Probabilistic programming, MCMC, Bayesian inference |

Three things the tree shape encodes that a list would hide:

**Layer 1 is deliberately code-free.** It grounds vocabulary before any implementation, and
the material tells you to *return to it after each later layer solidifies a technique* —
foundations as something you revisit, not something you complete. Bias-variance means
little before you have watched a model overfit.

**Layer 3 depends on Layer 2 and nothing else.** You cannot meaningfully study evaluation
before you have fit a model to evaluate, but evaluation is not a gate on the rest of the
tree.

**Layer 4 is independent of Layer 3.** You can do clustering and dimensionality reduction
without having studied cross-validation — which is true, and also the reason unsupervised
results are so often reported without any evaluation discipline behind them.

Layer 3 is flagged as the core of the foundations interviewing pillar: **metric
interpretation, train/test discipline, and leakage are the most common interview failure
modes.** That is a claim about what practitioners actually get wrong, not just what is
asked. See [[Eval vs Test Distinction]].

The named coverage gap is at Layer 5: the material uses scikit-learn's
`GradientBoostingClassifier`, while **XGBoost and LightGBM are the actual tabular SOTA**
and have no hands-on treatment. See [[LightGBM vs CatBoost Comparison]].

## Provenance discipline

Both curricula annotate their own material by origin — self-authored notebooks, executed
personal work, companion code for a book, and vendored clones are labelled distinctly, and
material that was never opened or added no unique value was deleted outright rather than
kept for completeness.

This is the same instinct as the wiki's split between `patterns/` (discovered while
building) and subject directories (synthesised from external sources): **provenance
predicts value, so it has to survive filing.** A cloned reference repo and an executed
personal notebook are not interchangeable evidence of anything, and a corpus that files
them identically loses the distinction permanently.

## See Also
- [[AI Engineering Curriculum Structure]] — part-of (the corpus these curricula sit inside)
- [[Data Engineering Foundations]] — alternative-to (the sibling branch off shared analytics layers 1–3)
- [[Notebook Dependency Staleness]] — complements (what happens to this material as its libraries move)
- [[Eval vs Test Distinction]] — extends (Layer 3 discipline, carried into LLM evaluation)
- [[LightGBM vs CatBoost Comparison]] — instance-of (the Layer 5 gradient-boosting gap, filled)
- [[Karpathy LLM Wiki Pattern]] — complements (provenance-preserving filing, same instinct)
