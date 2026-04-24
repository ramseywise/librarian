### Step 10: [Phase 6] Streamlit data dashboard — `src/app/dashboard.py`

**Files**: `src/app/dashboard.py` (new), `pyproject.toml` (add `streamlit` dependency)

**What**: Standalone Streamlit app for interactive data exploration of the DuckDB corpus. Separate entry point from Chainlit — not wired into the agent. Useful for browsing clusters, inspecting features, and evaluating model outputs.

**Suggested pages / sections**:
- **Corpus overview** — track count, playlist count, feature distributions (tempo, energy, valence histograms via Polars → Altair/plotly)
- **Cluster browser** — GMM soft-cluster assignments; scatter plot of ENOA coordinates coloured by cluster
- **Playlist inspector** — pick a playlist, see top tracks by LightGBM score, F1/ROC-AUC from last training run
- **Recommendation explorer** — enter a track ID, see top-N similar tracks from `RecommendationEngine` without going through the agent

**Entry point**:
```bash
PYTHONPATH=src uv run streamlit run src/app/dashboard.py
```

**Add to Makefile**:
```makefile
dashboard:
	PYTHONPATH=src uv run streamlit run src/app/dashboard.py
```

**Dependency**:
```bash
uv add streamlit
```

**Done when**: `make dashboard` opens a browser with at least the corpus overview page rendering real data from DuckDB.
