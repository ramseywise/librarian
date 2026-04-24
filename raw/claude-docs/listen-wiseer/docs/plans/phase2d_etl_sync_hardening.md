# Plan: Phase 2d — ETL Bootstrap + Sync Hardening
Date: 2026-04-03
Status: COMPLETE (Steps 0a–0i done; see Step 0 Summary below)
Predecessor: Phase 2c (Last.fm integration)
Next: Phase 3a (feature engineering / preprocessing)

---

## Goal

Bootstrap the DuckDB from CSV archives, harden incremental sync with rate-limit throttle and 23h cooldown guard, set up macOS launchd cron.

---

## Pre-requisites

- Phase 2c complete: Last.fm integration merged, 222 tests passing

---

### Step 0: Bootstrap DB + incremental sync hardening

**Context**: DB is currently empty (`data/listen_wiseer.db` has no tables). All historical data lives in `data/archived/`. The incremental sync logic in `sync.py` is architecturally correct but hits rate limits on large libraries because there is no inter-batch throttle and no time-based guard preventing re-runs within a short window.

**Files**:
- `src/etl/db.py` — add `last_synced TIMESTAMP` column to `playlists` DDL
- `src/spotify/fetch.py` — add 100ms sleep between batches in `fetch_audio_features` and `fetch_artist_features`
- `src/etl/sync.py` — `plan_sync` skips playlists synced within 23h; `upsert_playlists` writes `last_synced`

**Sub-steps** (each independently runnable):

**0a — Bootstrap from archives (zero API calls)**:
```bash
cd projects/listen-wiseer
PYTHONPATH=src uv run python -m etl.bootstrap
```
Expected output: `~2870 tracks, 20 playlists, genre mappings, enriched profiles`.
Validate:
```bash
PYTHONPATH=src uv run python -c "
import duckdb
conn = duckdb.connect('data/listen_wiseer.db')
for t in ['tracks','audio_features','playlists','genre_map','track_profile']:
    n = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(f'{t}: {n}')
"
```

**0b — Add `last_synced` to schema**:
```python
# src/etl/db.py — add to playlists DDL:
last_synced  TIMESTAMP
# and migration line:
ALTER TABLE playlists ADD COLUMN IF NOT EXISTS last_synced TIMESTAMP;
```

**0c — Inter-batch delay** (100ms between batches):
```python
# src/spotify/fetch.py — in fetch_audio_features and fetch_artist_features loops:
import time
# after each batch response:
time.sleep(0.1)
```

**0d — `plan_sync` respects `last_synced`** (skip if synced within 23h):
```python
# src/etl/sync.py — add to PlaylistSyncItem:
last_synced: datetime | None

@property
def needs_sync(self) -> bool:
    if not self.include_in_refresh:
        return False
    if self.last_synced is not None:
        age_hours = (datetime.now() - self.last_synced).total_seconds() / 3600
        if age_hours < 23:
            return False
    return self.is_new or self.spotify_track_count != self.db_track_count
```

**0e — `upsert_playlists` writes `last_synced`**:
```python
# after track sync completes for a playlist, update last_synced:
conn.execute(
    "UPDATE playlists SET last_synced = NOW() WHERE playlist_id = ?",
    [item.playlist_id]
)
```

**0f — Fix re-auth scope** (audio-features was 403 — likely missing scope, not deprecated for this app):
```python
# src/spotify/auth.py — add to SCOPES:
"user-read-private",   # required for audio-features endpoint
```
Then delete `.spotify_cache` and run `make mcp-server` once to re-authenticate (browser opens, one-time).
After re-auth, re-test audio-features: `client.get("audio-features", ids="<any_track_id>")` should return 200.

**0g — Per-step sync with limits** ✓ DONE 2026-04-03 (safe for testing, prevents blast radius):
```python
# src/etl/sync.py — add limit params to each step:
def sync_tracks(conn, client, items, max_playlists=None, max_tracks=None): ...
def sync_audio_features(conn, client, limit=None): ...
def sync_artist_features(conn, client, limit=None): ...
def sync(conn, client, max_playlists=None, max_tracks=None, limit=None): ...

# main() — add CLI args:
# PYTHONPATH=src uv run python -m etl.sync --playlists 1 --tracks 5
```
Also: `upsert_playlists` should default new-from-Spotify playlists (not in `my_playlists.csv`) to
`include_in_refresh = FALSE` so they don't get swept up automatically.

**0h — Validate each step independently with limits** ✓ DONE 2026-04-03:
```bash
# Test 1: just playlist upsert (no tracks)
PYTHONPATH=src uv run python -m etl.sync --playlists 0
# Test 2: 1 playlist, 5 tracks
PYTHONPATH=src uv run python -m etl.sync --playlists 1 --tracks 5
# Test 3: audio features for 5 tracks
PYTHONPATH=src uv run python -m etl.sync --audio 5
# Test 4: artist features for 5 artists
PYTHONPATH=src uv run python -m etl.sync --artists 5
```

**0i — Cron setup** ✓ DONE 2026-04-04 (macOS launchd):
```bash
# Daily at 02:00. Run after 0h validates.
# Create ~/Library/LaunchAgents/com.wiseer.listen-wiseer-sync.plist
```

**Tests**:
```python
# tests/unit/test_sync_plan.py — add:
from datetime import datetime, timedelta

def test_plan_sync_skips_recently_synced(mock_conn):
    """Playlist synced 1h ago should not need_sync even if counts differ."""
    item = PlaylistSyncItem(
        playlist_id="x", playlist_name="test",
        spotify_track_count=10, db_track_count=8,
        is_new=False, include_in_refresh=True,
        last_synced=datetime.now() - timedelta(hours=1),
    )
    assert not item.needs_sync

def test_plan_sync_syncs_stale_after_24h(mock_conn):
    """Playlist synced 25h ago with count mismatch should need_sync."""
    item = PlaylistSyncItem(
        playlist_id="x", playlist_name="test",
        spotify_track_count=10, db_track_count=8,
        is_new=False, include_in_refresh=True,
        last_synced=datetime.now() - timedelta(hours=25),
    )
    assert item.needs_sync
```

**Done when**: `make init-db` populates DB with ~2870 tracks; `make data-sync` runs without rate limit errors and skips recently-synced playlists; new tests pass.

---
