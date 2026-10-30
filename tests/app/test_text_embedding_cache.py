"""shared.embeddings.encode_texts_cached — the on-disk lesson-vector cache behind
course ↔ concept semantic linking. A fake model stands in for MiniLM."""

from __future__ import annotations

from pathlib import Path

import pytest

np = pytest.importorskip("numpy")  # needs the `api` extra; CI without it skips
embeddings = pytest.importorskip("shared.embeddings")


class _FakeModel:
    def __init__(self) -> None:
        self.encoded: list[str] = []

    def encode(self, texts: list[str], normalize_embeddings: bool = True) -> np.ndarray:
        self.encoded.extend(texts)
        vecs = np.array([[len(t), 1.0, 0.0] for t in texts], dtype=np.float32)
        return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


@pytest.fixture()
def model(monkeypatch: pytest.MonkeyPatch) -> _FakeModel:
    fake = _FakeModel()
    monkeypatch.setattr(embeddings, "_get_model", lambda: fake)
    return fake


def test_encodes_only_uncached_texts(model: _FakeModel, tmp_path: Path) -> None:
    cache = tmp_path / "c" / "lessons.npz"
    first = embeddings.encode_texts_cached(["alpha", "beta"], cache)
    assert first.shape == (2, 3) and cache.exists()
    assert model.encoded == ["alpha", "beta"]

    again = embeddings.encode_texts_cached(["beta", "alpha"], cache)
    assert model.encoded == ["alpha", "beta"]  # warm restart: nothing re-encoded
    np.testing.assert_allclose(again, first[::-1])

    embeddings.encode_texts_cached(["alpha", "gamma!"], cache)
    assert model.encoded == ["alpha", "beta", "gamma!"]  # edited/new text only


def test_prunes_to_live_texts_and_survives_corrupt_cache(model: _FakeModel, tmp_path: Path) -> None:
    cache = tmp_path / "lessons.npz"
    embeddings.encode_texts_cached(["a", "b", "c"], cache)
    embeddings.encode_texts_cached(["a"], cache)
    with np.load(cache) as z:
        assert len(z["keys"]) == 1

    cache.write_bytes(b"not an npz")
    out = embeddings.encode_texts_cached(["a"], cache)
    assert out.shape == (1, 3)
    assert embeddings.encode_texts_cached([], cache).shape[0] == 0
