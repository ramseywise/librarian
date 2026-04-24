Phase 3c Plan: Train/Inference Gap Fix + CatBoost Comparison
Context
Current state: The LightGBM reranker trains on 21 continuous features. Two of them (similarity_score, cluster_prob) are zeroed out during training but carry real values at inference — the model can't learn from them. Additionally, categorical signals (decade, gen_4/gen_8) are available on the corpus but unused by the classifier.

This phase does two things:

Fix the train/inference feature distribution mismatch
Add CatBoost as an alternative estimator and run a head-to-head comparison, leveraging CatBoost's native categorical handling by adding decade + gen_4 as new features
Files touched
File	Change
Fix feature gap; add categorical features; make estimator configurable; add brier/log-loss metrics
Pass GMM to classifier training; thread --compare flag; log new metrics
uv add catboost
Updated + parametrized tests
Updated tests for new signatures
Steps
Step 1 — Fix cluster_prob at training time (train.py, classifiers.py)

Pass gmm + scaler through to train_playlist_classifier. Before building features, compute cluster_prob for every corpus row (same as filter_corpus_by_cluster does at inference: max(gmm.predict_proba(row))). Add it as a real column instead of lit(0.0).

Step 2 — Fix similarity_score at training time (classifiers.py)

After building the playlist centroid from positive tracks, compute standard cosine similarity for all corpus rows using compute_weighted_cosine(corpus_features, centroid, weights). Set this as the similarity_score column. No LOO — standard cosine for everyone. Rationale: at inference, candidates are scored against the full centroid; positives contributing to their own centroid is negligible with 20+ tracks, and the model needs to learn that high similarity is correlated with membership.

Step 3 — Add categorical features for CatBoost (classifiers.py)

Extend the feature set with 2 categorical columns available on the corpus:

decade (8 categories) — era-specific taste signal missing from year_normalized
gen_4 (4 genre buckets) — discrete genre boundaries beyond continuous top/left
For LightGBM: one-hot encode these (simple, no changes to the numeric pipeline). For CatBoost: pass as native categoricals via cat_features parameter.

Update CLASSIFIER_FEATURES to include these, with a separate CATEGORICAL_FEATURES constant.

Step 4 — Make estimator configurable (classifiers.py)

Add model_type: Literal["lightgbm", "catboost"] parameter to train_playlist_classifier (default "lightgbm"). Factory function selects the base estimator:

"lightgbm" → LGBMClassifier (current config) + one-hot categoricals
"catboost" → CatBoostClassifier(verbose=0, random_state=42, auto_class_weights="Balanced") + native categoricals
Both wrapped in CalibratedClassifierCV → Pipeline as today.

Step 5 — Add Brier score + log-loss to evaluation (classifiers.py, train.py)

Add sklearn.metrics.brier_score_loss and sklearn.metrics.log_loss to the metrics dict. These are the metrics that matter most for calibrated probabilities used as rerank scores. Log them alongside existing metrics.

Step 6 — Add --compare CLI flag (train.py)

Add argparse to main(). When --compare is passed:

For each playlist, train both LightGBM and CatBoost on the same train/test split
Log metrics side-by-side per playlist
At the end, log aggregate comparison (mean brier, mean log-loss, win counts per model)
Default behavior (no flag) trains LightGBM only — no change to existing workflow.

Step 7 — Add catboost dependency (
)

uv add catboost

Step 8 — Update tests (test_classifiers.py, test_train.py)

Update train_playlist_classifier call signatures (new gmm param, model_type param)
Verify similarity_score and cluster_prob are non-zero in training features
Parametrize estimator tests over ["lightgbm", "catboost"]
Test --compare flag plumbing
Test categorical feature encoding for both paths
Execution order
#	Step	Risk
1	Fix cluster_prob	Low
2	Fix similarity_score	Low (no LOO complexity)
3	Add categorical features	Low-medium (new feature columns)
4	Make estimator configurable	Low
5	Add Brier + log-loss	Low
6	--compare flag	Low
7	uv add catboost	Low
8	Update tests	Low
Not touched
engine.py, pipelines.py, similarity.py, clustering.py — no changes
MCP server, agent, Chainlit — unaffected
GMM training — unaffected
Existing models/*.pkl — will need retraining (expected)
