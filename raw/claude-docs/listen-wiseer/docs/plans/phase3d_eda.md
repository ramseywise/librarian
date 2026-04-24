Plan: 3d_eda — EDA Notebook Suite
Directory: notebooks/eda/
00_test_functions.ipynb — Smoke Tests
Validate that the stack works end-to-end from a notebook context.

Section	What	Functions/imports used
DB connection	Open DuckDB, query track_profile LIMIT 5, print schema	etl.db.get_connection, init_schema
Corpus load	build_feature_matrix(conn), check shape + dtypes	recommend.preprocessing.build_feature_matrix
Cache round-trip	Write parquet, read back, assert equality	paths.CACHE_DIR
Model artifacts	Load GMM + scaler, predict on 1 row	joblib.load, paths.MODELS_DIR
Genre lookup	genre_to_enoa("indie rock", ...)	recommend.modules.genre
Similarity	find_similar(corpus, query_row, k=5)	recommend.modules.similarity
Cluster assignment	build_cluster_features + predict_cluster_probs on 1 row	recommend.modules.clustering
Engine	RecommendationEngine init, single recommend() call per pipeline type	recommend.engine
Metrics JSONL	Load a models/metrics/*.jsonl, parse lines	stdlib json
01_corpus_health.ipynb — Data Quality
Section	What
Shape & memory	Row/col counts, estimated memory, dtypes summary
Null audit	Per-column null counts + heatmap. Flag cols >5% missing
features_source breakdown	Count by provenance: spotify, lastfm, imputed_artist, imputed_genre, imputed_global
Duplicates	Check id uniqueness. Check near-duplicate tracks (same name+artist, different IDs)
Feature distributions	Histograms for all 9 audio features + popularity, fave_score, n_playlists
ENOA coordinate coverage	Scatter of (left, top) — how many tracks have real coords vs imputed/zero
Outlier detection	Z-score or IQR flagging on tempo, loudness, duration_ms
Decade/year coverage	Bar chart of decade, histogram of year
Embedding coverage	% of tracks with non-zero t2v_0..t2v_63
02_explore_library.ipynb — Library Exploration
Section	What
Playlist overview	Count tracks per playlist, bar chart. Pull from playlist_tracks join
Playlist genre profiles	For each playlist: top gen_4/gen_6 distributions. Use playlist_genre table or derive from track_genre
Artist stats	Top artists by track count, by avg popularity. Genre diversity per artist
Track deep-dive	Most popular, least popular, most-playlisted tracks. Fave score distribution
Temporal patterns	Tracks per decade, release year histogram, how playlists differ in era
Audio feature profiles	Radar/spider plots per playlist (mean audio features). Compare 2-3 playlists side-by-side
Genre distribution	Bar chart of genre_cat / my_genre across full library. Treemap of gen_4 → gen_6 → gen_8
03_feature_engineering.ipynb — Features & Importance
Section	What
Feature correlation matrix	Heatmap of all SIMILARITY_FEATURES (15) + retrieval features
Collinearity check	VIF or pairwise >0.9 correlation flagging
Feature vs target	For 1-2 playlists: violin plots of each feature split by positive/negative label
Engineered features	Inspect year_normalized, duration_ms_normalized, playlist_diversity, fave_score, artist_enoa_top/left, pp_* propagated features
Track2Vec embeddings	t-SNE/UMAP of t2v_0..t2v_63, colored by gen_4
LightGBM feature importance	Load a trained classifier, extract feature_importances_. Bar chart. Compare across playlists
CatBoost feature importance	Same, with SHAP values if available (CatBoost has built-in)
Permutation importance	sklearn.inspection.permutation_importance on test set for 1-2 playlists
04_genre_clustering.ipynb — Genre Space & ENOA
This is the genre-focused deep dive.

Section	What
ENOA full map	Scatter of all 6k+ genres from genre_xy — (left, top), colored by color column
Library overlay	Overlay library tracks' (left, top) onto the genre map
Genre taxonomy tree	Sankey or sunburst: gen_4 → gen_6 → gen_8 → my_genre → first_genre
Spatial clustering	KMeans/DBSCAN on (top, left) for the 6k genre points. Compare to gen_4/gen_6 labels
Genre zone exploration	Pick 3-4 genres, visualize expand_genre_zone() circles (radius=1500) on the scatter. Show which tracks fall in each zone
Genre coverage gaps	Which gen_4/gen_6 regions are under-represented in the library?
ENOA as feature	How well do (top, left) predict gen_4? Quick decision boundary visualization
Cross-playlist genre overlap	Jaccard similarity of genre sets between playlists
05_retrieval_diagnostics.ipynb — Similarity & Clustering Quality
Section	What
GMM cluster profiles	8 clusters: size distribution, mean audio features per cluster, radar plots
Silhouette analysis	Per-cluster silhouette scores. Identify weak clusters
Cluster-genre alignment	Contingency table: cluster_id × gen_4. Heatmap. Are clusters genre-coherent?
Soft membership	Distribution of max cluster_prob across corpus. How "confident" are assignments?
Similarity score distributions	For 2-3 playlists: histogram of similarity_score for positives vs negatives
Cosine similarity heatmap	Track-to-track similarity matrix for a single playlist (~50 tracks)
Retrieval recall	For a playlist, run find_similar(centroid, k=100). What % of actual playlist tracks appear?
Camelot wheel	Visualize camelot_distance distribution for playlist tracks. How key-coherent are playlists?
Candidate filtering	For a query, show: full corpus → cluster filter → cosine top-100. How much does each stage cut?
06_model_comparison.ipynb — LightGBM vs CatBoost
Section	What
Load metrics	Parse all models/metrics/*.jsonl files into a Polars DataFrame
Per-playlist comparison	Paired bar charts: LightGBM vs CatBoost for each metric (Brier, log-loss, ROC-AUC, precision@10)
Win/loss summary	Which model wins on Brier? On log-loss? On precision@10? Counts + percentages
Score distribution	Box plots of each metric across playlists, grouped by model type
Metric correlations	Does good Brier → good precision@10? Scatter matrix across metrics
Per-playlist deep dive	For the playlists where models disagree most: what's different about those playlists? (size, genre diversity, decade spread)
Temporal stability	If multiple runs exist: metrics over time. Are results stable across retrains?
Recommendation: keep or switch	Summary table with the decision criteria
07_rerank_audit.ipynb — End-to-End Pipeline Inspection
Section	What
Pick a playlist	Load a playlist profile (centroid, modal_key, mean_tempo)
Stage 1: Cluster filter	Show corpus → filtered candidates. Count, cluster_prob distribution
Stage 2: Cosine retrieval	Top-100 by similarity. Show score distribution, genre breakdown
Stage 3: Rerank (LightGBM)	Apply classifier. Show rerank_score distribution. How much does ordering change?
Stage 3b: Rerank (CatBoost)	Same playlist, CatBoost. Side-by-side top-20 comparison
Stage 4: MMR diversification	Show pre-MMR vs post-MMR selection. What got swapped?
Rank correlation	Spearman/Kendall between cosine rank, LightGBM rank, CatBoost rank
Known-good audit	For tracks actually in the playlist: where do they rank at each stage?
Failure cases	Tracks ranked high that are clearly wrong genre/era. Why did the model like them?
