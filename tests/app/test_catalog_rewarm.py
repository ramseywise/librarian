"""Wiki-change bursts coalesce into one course-catalog rebuild (app/backend/main.py)."""

from __future__ import annotations

import asyncio

import pytest

from app.backend import main


def test_rewarm_is_debounced(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []
    monkeypatch.setattr(main, "CATALOG_REWARM_DELAY_S", 0.02)
    monkeypatch.setattr(main, "warm_catalog", lambda: calls.append(1))
    monkeypatch.setattr(main, "_rewarm_handle", None)

    async def burst() -> None:
        for _ in range(5):  # five watcher batches inside the quiet window
            main._schedule_catalog_rewarm()
            await asyncio.sleep(0.005)
        await asyncio.sleep(0.1)  # let the timer fire and the executor job finish

    asyncio.run(burst())
    assert calls == [1]


def test_compute_embeddings_is_serialised(monkeypatch: pytest.MonkeyPatch) -> None:
    """Concurrent callers (event-loop routes + catalog thread) must not overlap on DuckDB."""
    pytest.importorskip("duckdb")
    pytest.importorskip("sentence_transformers")
    import threading
    import time

    import shared.embeddings as emb

    active, peak = 0, 0
    guard = threading.Lock()

    def fake() -> tuple[list[str], object]:
        nonlocal active, peak
        with guard:
            active += 1
            peak = max(peak, active)
        time.sleep(0.02)
        with guard:
            active -= 1
        return [], None

    monkeypatch.setattr(emb, "_compute_embeddings", fake)
    threads = [threading.Thread(target=emb.compute_embeddings) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert peak == 1
