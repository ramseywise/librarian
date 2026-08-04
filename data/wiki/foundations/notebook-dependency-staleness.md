---
title: Notebook Dependency Staleness
tags: [foundations, reference]
summary: "Migration maps for the three library breaks that strand old ML notebooks — sklearn 0.20→1.4, TensorFlow 1.x→2.x, PyMC3→PyMC 5 — plus the two-phase triage that distinguishes a mechanical import swap from a genuine rewrite."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--CURRICULUM.md
---

# Notebook Dependency Staleness

Old ML notebooks stop running for three distinct reasons, and the distinction determines
the cost of fixing them. This page is the reference map from a full audit of a five-year
notebook corpus.

## The two-phase triage

The audit's organising move: separate breaks that a **compatibility shim** can absorb from
breaks that need a **rewrite**.

| Phase | Break type | Cost |
|---|---|---|
| **Phase 1** | Renamed parameters, moved namespaces, removed kwargs | Mechanical — find and replace |
| **Phase 2** | Removed APIs with no successor at the same abstraction level | Genuine rewrite against the new idiom |

The value of triaging is that Phase 1 is *bulk-fixable and low-risk* while Phase 2 requires
understanding what the code was doing. Running them together makes the whole corpus look
equally expensive, which is how notebook collections end up abandoned. The audit found most
notebooks needed only Phase 1 — the stranding was mostly illusory.

**The reliable Phase 2 signal is a removed *abstraction*, not a removed function.**
`tf.contrib.layers.fully_connected` has no drop-in replacement because TF2 moved from graph
construction to Keras layers; the concept was relocated, not renamed. Compare
`OneHotEncoder(sparse=)` → `sparse_output=`, where only the spelling changed.

A corollary worth stating: **a filename is not a version claim.** The audit found notebooks
named `_PyMC3` that already used the modern import, and notebooks named `_PyMC_current`
that were still on the old one. Verify the import line, not the label.

## scikit-learn 0.20 → 1.4+

Fully Phase 1 — no rewrites needed across the corpus.

| Old | New | Break |
|---|---|---|
| `sklearn.cross_validation` | `sklearn.model_selection` | Namespace removed in 0.20 |
| `sklearn.grid_search` | `sklearn.model_selection` | Namespace removed in 0.20 |
| `DummyClassifier(strategy="warn")` | `strategy="stratified"` | Default changed in 1.1 |
| `OneHotEncoder(sparse=True)` | `sparse_output=` | Renamed 1.2, removed 1.4 |
| `GridSearchCV(iid=True)` | Remove the param | Removed in 1.0 |
| `LogisticRegression()` | `LogisticRegression(max_iter=1000)` | Default iterations no longer converge on some datasets |

The `max_iter` row is the one that doesn't announce itself: the code runs, emits a
convergence warning, and returns a worse model. **Silent degradation is more dangerous than
an ImportError** — a break that raises gets fixed, a break that warns gets scrolled past.

## TensorFlow 1.x → 2.x

Split decision: `tf.compat.v1` bridge for most notebooks, full Keras rewrite where
`tf.contrib` appears. `tf.contrib` was deleted wholesale in TF2, so any notebook touching
it is Phase 2 by definition.

| Old | New |
|---|---|
| `tf.contrib.layers.xavier_initializer(seed=N)` | `tf.keras.initializers.glorot_uniform(seed=N)` |
| `tf.contrib.layers.flatten(P)` | `tf.keras.layers.Flatten()(P)` |
| `tf.contrib.layers.fully_connected(F, n, activation_fn=None)` | `tf.keras.layers.Dense(n, activation=None)(F)` |
| `tf.get_variable(name, shape, initializer=...)` | `tf.Variable(initializer(shape=shape))` |
| `tf.placeholder(dtype, shape)` | Function argument or `tf.keras.Input` |
| `with tf.Session() as sess: sess.run(op)` | `op.numpy()` — eager execution |
| `tf.confusion_matrix` | `tf.math.confusion_matrix(...).numpy()` |

The `tf.Session` → eager row is the conceptual break rather than a syntactic one: TF1
separated graph definition from execution, TF2 collapsed them. `tf.compat.v1` with
`disable_v2_behavior()` restores the old model wholesale, which is why it works as a Phase 1
bridge — and also why it is a holding action rather than a migration.

## PyMC3 → PyMC 5

PyMC3 broke at v4. Some removals have no successor in the library at all.

| Old | New |
|---|---|
| `import pymc3 as pm` | `import pymc as pm` |
| `pm.Normal('x', sd=N)` | `pm.Normal('x', sigma=N)` |
| `pm.traceplot(trace)` | `az.plot_trace(trace)` (arviz) |
| `pm.summary(trace)` | `az.summary(trace)` — same DataFrame interface |
| `pm.plot_posterior(trace)` | `az.plot_posterior(trace)` |
| `pm.sample(draws, init='MAP')` | `pm.sample(draws)`, or `initvals=pm.find_MAP()` |
| `pm.glm.GLM.from_formula(...)` | Removed — use the `bambi` library |
| `pm.iter_sample(...)` | Removed — `pm.sample` with progressive callbacks |
| `traces.varnames` | `list(idata.posterior.data_vars)` — InferenceData format |
| Theano custom ops | PyTensor equivalents |

Two rows are structural rather than cosmetic. **The plotting and summary functions moved
out of the library into arviz** — PyMC narrowed to modelling and inference and handed
diagnostics to a separate package. And `traces.varnames` → `idata.posterior.data_vars`
reflects a change in the *return type*: traces became xarray-backed InferenceData, so
downstream code that indexed traces needs rethinking rather than renaming.

`pm.glm` and `pm.iter_sample` were removed with no in-library successor, which is the case
where **pinning beats porting**. The audit's resolution for one such notebook — a completed
course assignment with no ongoing role — was to pin `pymc3==3.11.4` + `theano-pymc==1.1.2`
and add inline migration comments.

## When to pin instead of port

Pinning is the right answer when a notebook is a **record rather than a tool**: a finished
course assignment, an executed analysis whose output is the artefact. Porting is right when
the notebook is on a learning path someone will actually re-run, or when it is a template
for new work. The audit applied exactly this split — curriculum-path notebooks migrated,
one legacy assignment pinned.

The general principle: migration cost is justified by **expected future executions**, not by
tidiness. A corpus where everything must run on current libraries is one where old work gets
deleted rather than pinned.

## See Also
- [[Data Science Curriculum Layers]] — part-of (the notebooks this audit covers)
- [[AI Engineering Curriculum Structure]] — complements (the corpus containing this material)
- [[Data Engineering Foundations]] — complements (the same version-drift problem in pipeline code rather than notebooks)
