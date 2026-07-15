---
title: Track2Vec Playlist Co-Occurrence Embeddings
tags: [llm, pattern]
summary: Item2vec-style technique — treat playlists as "sentences" and item IDs as "words", train Word2Vec over co-occurrence to get dense embeddings that capture human curation intent rather than content similarity.
updated: 2026-07-14
sources:
  - raw/claude-docs/listen-wiseer/docs/plans/phase3a_preprocessing.md
---

# Track2Vec Playlist Co-Occurrence Embeddings

A named instance of the **item2vec / prod2vec** pattern: reuse Word2Vec's skip-gram
machinery on a non-language sequence by reframing the domain data as "sentences" of
co-occurring items.

## Mechanism

1. Treat each playlist as a sentence; each track ID as a word.
2. Train a skip-gram `Word2Vec` model over these sequences: `gensim.Word2Vec(sentences, vector_size=64, window=5, min_count=1, sg=1, seed=42)`.
3. The resulting per-track embedding encodes **which tracks tend to appear together in
   the same playlists** — i.e. human curation intent — not acoustic/audio-feature
   similarity.
4. Store embeddings once (expensive to compute, reused across training runs) in a
   dedicated table (`track_embeddings`, one row per track, `DOUBLE[64]` column,
   versioned via a `model_version` string) rather than recomputing per request.
5. Expose the embedding to downstream models as a **scalar**, not a raw vector — e.g.
   `embedding_similarity = cosine(seed_embedding, candidate_embedding)` — so it slots
   into a flat feature vector alongside audio features without needing a separate
   embedding-aware model architecture.

## Why it's distinct from audio-feature similarity

Audio features (danceability, energy, tempo, ...) measure acoustic properties of a
track in isolation. Track2Vec measures **which tracks a human curator (or a corpus of
curators) chose to put next to each other** — two tracks can be acoustically
dissimilar but still co-occur constantly in playlists (e.g. a DJ transition track), and
Track2Vec captures that signal while audio-feature cosine similarity cannot.

## Coverage gap

Tracks that don't appear in any playlist get no embedding (all-zero vector) — the
imputation cascade (artist-median → genre-median → global-median for audio features)
does not extend to embeddings; a zero embedding_similarity is treated as "no curation
signal available" rather than imputed.

## Applied in

[[Listen-Wiseer Project]] — used as one of three new signal groups (alongside
imputation cascade and collaborative/temporal features) added during the Phase 3a
feature-engineering pass, feeding the per-playlist LightGBM/CatBoost reranker (see
[[LightGBM vs CatBoost Comparison]]).

## See Also
- [[Listen-Wiseer Project]]
- [[LightGBM vs CatBoost Comparison]]
- [[Agentic Workflow Patterns]]
