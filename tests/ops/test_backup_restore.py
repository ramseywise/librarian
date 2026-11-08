"""SQLite backup -> restore for real against a tmp database; age/aws/pg tools are faked."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from librarian.config import Settings
from librarian.ops import dbtools, restore
from librarian.ops.backup import run_backup
from librarian.ops.manifest import Manifest, make_base, stamp_of
from librarian.ops.proc import OpsError
from librarian.ops.restore import run_restore

NOW = datetime(2026, 11, 8, 3, 30, tzinfo=UTC)


def _rows(url: str, table: str) -> int:
    engine = create_engine(url)
    with engine.connect() as conn:
        n = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
    engine.dispose()
    return int(n or 0)


def _empty_target(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'fresh' / 'target.sqlite3'}"


def test_backup_writes_encrypted_dump_and_manifest(
    settings: Settings, db_url: str, bucket: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    assert m.encrypted and m.dump_object.endswith(".dump.age")
    assert m.alembic_head == dbtools.code_head()
    assert m.tables["users"] == 1 and m.tables["meta"] == 1
    assert "alembic_version" not in m.tables
    assert sorted(p.name for p in bucket.iterdir()) == [
        f"{m.base}.dump.age",
        f"{m.base}.manifest.json",
    ]
    age = next(c for c in calls if c[0] == "age")
    assert age[1:3] == ["--recipient", "age1testrecipient"]
    on_disk = Manifest.model_validate(json.loads((bucket / f"{m.base}.manifest.json").read_text()))
    assert on_disk.dump_sha256 == m.dump_sha256 and on_disk.encrypted_sha256


def test_backup_refuses_without_recipient(
    settings: Settings, db_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_BACKUP_AGE_RECIPIENT", "")
    with pytest.raises(OpsError, match="RECIPIENT"):
        run_backup(Settings(), now=NOW, url=db_url)


def test_round_trip_into_empty_target(
    settings: Settings, db_url: str, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    target = _empty_target(tmp_path)
    key = tmp_path / "key.txt"
    key.write_text("AGE-SECRET-KEY-test")
    result = run_restore(settings, m.base, identity=key, url=target, now=NOW)
    assert result.swapped
    assert _rows(target, "users") == 1 and _rows(target, "meta") == 1
    assert dbtools.read_state(target).revision == m.alembic_head
    assert [c for c in calls if c[0] == "age"][-1][:2] == ["age", "--decrypt"]


def test_restore_latest_resolves_newest(
    settings: Settings, db_url: str, tmp_path: Path, calls: list[list[str]]
) -> None:
    run_backup(settings, now=NOW - timedelta(days=1), url=db_url)
    newest = run_backup(settings, now=NOW, url=db_url)
    key = tmp_path / "key.txt"
    key.write_text("k")
    result = run_restore(settings, "latest", identity=key, url=_empty_target(tmp_path))
    assert result.base == newest.base


def test_restore_refuses_non_empty_target_without_replace(
    settings: Settings, db_url: str, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    key = tmp_path / "key.txt"
    key.write_text("k")
    with pytest.raises(OpsError, match="--replace"):
        run_restore(settings, m.base, identity=key, url=db_url)
    # nothing touched: no scratch files, live rows intact
    assert _rows(db_url, "users") == 1
    assert not list(Path(db_url.removeprefix("sqlite:///")).parent.glob("*.restore-*"))


def test_restore_replace_swaps_and_keeps_the_old_database(
    settings: Settings, db_url: str, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO meta (key, value) VALUES ('later', 'x')"))
    engine.dispose()
    key = tmp_path / "key.txt"
    key.write_text("k")
    result = run_restore(settings, m.base, identity=key, url=db_url, replace=True, now=NOW)
    assert _rows(db_url, "meta") == 1  # the post-backup row is gone from the live database
    old = Path(result.kept_old)
    assert old.is_file() and _rows(f"sqlite:///{old}", "meta") == 2


def test_restore_rejects_row_count_mismatch_and_leaves_target_alone(
    settings: Settings, db_url: str, bucket: Path, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    mf = bucket / f"{m.base}.manifest.json"
    data = json.loads(mf.read_text())
    data["tables"]["users"] = 5  # the manifest claims more rows than the dump holds
    mf.write_text(json.dumps(data))
    target = _empty_target(tmp_path)
    key = tmp_path / "key.txt"
    key.write_text("k")
    with pytest.raises(OpsError, match="users"):
        run_restore(settings, m.base, identity=key, url=target)
    live = Path(target.removeprefix("sqlite:///"))
    assert not live.exists()
    assert not list(live.parent.glob("*.restore-*"))  # scratch discarded


def test_restore_rejects_alembic_head_mismatch(
    settings: Settings, db_url: str, bucket: Path, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    mf = bucket / f"{m.base}.manifest.json"
    data = json.loads(mf.read_text())
    data["alembic_head"] = "0001"
    mf.write_text(json.dumps(data))
    key = tmp_path / "key.txt"
    key.write_text("k")
    with pytest.raises(OpsError, match="revision"):
        run_restore(settings, m.base, identity=key, url=_empty_target(tmp_path))


def test_restore_rejects_a_dump_that_fails_its_checksum(
    settings: Settings, db_url: str, bucket: Path, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    (bucket / m.dump_object).write_bytes(b"AGE:corrupted")
    key = tmp_path / "key.txt"
    key.write_text("k")
    with pytest.raises(OpsError, match="checksum"):
        run_restore(settings, m.base, identity=key, url=_empty_target(tmp_path))


def test_restore_refuses_a_backup_newer_than_the_code(
    settings: Settings, db_url: str, bucket: Path, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    mf = bucket / f"{m.base}.manifest.json"
    data = json.loads(mf.read_text())
    data["alembic_head"] = "9999"
    mf.write_text(json.dumps(data))
    key = tmp_path / "key.txt"
    key.write_text("k")
    with pytest.raises(OpsError, match="newer than this code"):
        run_restore(settings, m.base, identity=key, url=_empty_target(tmp_path))


def test_encrypted_restore_needs_an_identity(
    settings: Settings, db_url: str, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, now=NOW, url=db_url)
    with pytest.raises(OpsError, match="--identity"):
        run_restore(settings, m.base, url=_empty_target(tmp_path))


def test_unencrypted_drill_round_trip_without_age(
    settings: Settings, db_url: str, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, unencrypted=True, now=NOW, url=db_url)
    assert not m.encrypted and not any(c[0] == "age" for c in calls)
    run_restore(settings, m.base, url=_empty_target(tmp_path))
    assert not any(c[0] == "age" for c in calls)


def test_no_swap_verifies_and_leaves_live_alone(
    settings: Settings, db_url: str, tmp_path: Path, calls: list[list[str]]
) -> None:
    m = run_backup(settings, unencrypted=True, now=NOW, url=db_url)
    target = _empty_target(tmp_path)
    result = run_restore(settings, m.base, url=target, swap=False)
    assert not result.swapped
    assert not Path(target.removeprefix("sqlite:///")).exists()
    assert Path(result.scratch_url.removeprefix("sqlite:///")).is_file()


def test_base_names_carry_the_timestamp() -> None:
    base = make_base(NOW, "sha/odd release")
    assert base == "librarian-20261108T033000Z-sha-odd-release"
    assert stamp_of(base) == NOW
    assert restore.base_of(f"{base}.dump.age") == base
