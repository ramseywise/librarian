# ML / DS Best Practices

## Reproducibility

- Always seed: `np.random.seed(42)`, `random_state=42` in sklearn, `seed=` in Polars `.sample()`
- Pin hyperparameters in config, never inline in code
- Log model params and metrics at train time (structlog)
- Save artifacts with joblib to `models/` — never commit `.pkl` files

## Pipelines

- Wrap all preprocessing + model in sklearn `Pipeline` — prevents data leakage
- Fit scaler on train split only, transform test with fitted scaler
- `CalibratedClassifierCV` for calibrated probability outputs

## Evaluation

- Always report: accuracy, precision, recall, f1, roc_auc, precision@K
- Silhouette score for clustering quality
- Compare against a naive baseline (e.g. majority class, random)
- Log eval results as structured fields, not print statements

## Data

- Notebooks are for exploration only — move validated logic to `src/`
- Subsample for local dev; log the subsample size and seed
- Validate corpus size before training — log `n_rows`, `n_features`
- `null_values=["", "NA", "NaN"]` on all CSV reads

## Don'ts

- No pandas in ML code — Polars in, numpy arrays to sklearn
- No global mutable state in model modules
- Never load real data files or model weights in unit tests — synthetic fixtures only
- No training inside notebooks — notebooks call `python -m module.train`
