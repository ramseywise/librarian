from __future__ import annotations

from pathlib import Path

import frontmatter
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

WIKI_DIR = Path(__file__).parent.parent.parent / "wiki"
MODEL_NAME = "all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def warmup() -> None:
    model = _get_model()
    model.encode(["warmup"], normalize_embeddings=True)


def _page_texts() -> dict[str, str]:
    texts: dict[str, str] = {}
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        post = frontmatter.load(md_file)
        title = post.get("title") or md_file.stem
        summary = post.get("summary") or ""
        texts[md_file.stem] = f"{title}. {summary}\n\n{post.content[:600]}"
    return texts


def compute_embeddings() -> tuple[list[str], np.ndarray]:
    model = _get_model()
    page_texts = _page_texts()
    page_ids = list(page_texts.keys())
    vecs = model.encode([page_texts[p] for p in page_ids], normalize_embeddings=True)
    return page_ids, vecs


def semantic_edges(threshold: float = 0.65) -> list[dict]:
    page_ids, vecs = compute_embeddings()
    sim = cosine_similarity(vecs)
    edges = []
    for i in range(len(page_ids)):
        for j in range(i + 1, len(page_ids)):
            score = float(sim[i, j])
            if score >= threshold:
                a, b = page_ids[i], page_ids[j]
                edges.append({
                    "id": f"sem:{a}->{b}",
                    "source": a,
                    "target": b,
                    "data": {"edgeType": "semantic", "score": round(score, 3)},
                })
    return edges
