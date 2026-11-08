"""Upgrade freshness gate, failure alert, S3 command shape, Postgres paths (tools mocked), CLI."""

from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest

from librarian import cli
from librarian.accounts import mailer
from librarian.config import Settings
from librarian.ops import cli as ops_cli
from librarian.ops import dbtools, proc, restore, schedule
from librarian.ops.backup import run_backup
from librarian.ops.proc import OpsError
from librarian.ops.restore import PostgresTarget
from librarian.ops.storage import LocalStorage, S3Storage, open_storage
from librarian.ops.upgrade import StaleBackupError, check_tag, ensure_fresh_backup

NOW = datetime(2026, 11, 8, 12, 0, tzinfo=UTC)


def _count_bases(bucket: Path) -> int:
    return len(list(bucket.glob("*.manifest.json")))


def test_upgrade_gate_uses_a_backup_younger_than_15_minutes(
    settings: Settings, db_url: str, bucket: Path, calls: list[list[str]]
) -> None:
    first = run_backup(settings, now=NOW - timedelta(minutes=14, seconds=59), url=db_url)
    gate = ensure_fresh_backup(settings, now=NOW, url=db_url)
    assert (gate.base, gate.taken) == (first.base, False)
    assert _count_bases(bucket) == 1


def test_upgrade_gate_takes_a_new_backup_when_the_newest_is_older(
    settings: Settings, db_url: str, bucket: Path, calls: list[list[str]]
) -> None:
    old = run_backup(settings, now=NOW - timedelta(minutes=16), url=db_url)
    gate = ensure_fresh_backup(settings, now=NOW, url=db_url)
    assert gate.taken and gate.base != old.base
    assert _count_bases(bucket) == 2


def test_upgrade_gate_with_no_take_refuses_a_stale_backup(
    settings: Settings, db_url: str, bucket: Path, calls: list[list[str]]
) -> None:
    run_backup(settings, now=NOW - timedelta(minutes=16), url=db_url)
    with pytest.raises(StaleBackupError):
        ensure_fresh_backup(settings, take=False, now=NOW, url=db_url)
    assert _count_bases(bucket) == 1


def test_upgrade_gate_with_an_empty_bucket_takes_one(
    settings: Settings, db_url: str, bucket: Path, calls: list[list[str]]
) -> None:
    assert ensure_fresh_backup(settings, now=NOW, url=db_url).taken


def test_a_dump_without_a_manifest_does_not_count_as_a_backup(
    settings: Settings, bucket: Path, calls: list[list[str]]
) -> None:
    bucket.mkdir()
    (bucket / "librarian-20261108T115900Z-x.dump.age").write_bytes(b"half uploaded")
    with pytest.raises(StaleBackupError):
        ensure_fresh_backup(settings, take=False, now=NOW)


def test_image_tag_is_validated() -> None:
    assert check_tag("ghcr.io/me/librarian:sha-abc123")
    for bad in ("", "a b", "x;rm", "-evil", "a\nb"):
        with pytest.raises(OpsError):
            check_tag(bad)


def test_cli_upgrade_exit_codes(
    settings: Settings,
    db_url: str,
    bucket: Path,
    calls: list[list[str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("librarian.ops.backup.database_url", lambda: db_url)
    monkeypatch.setattr(ops_cli, "get_settings", lambda: Settings())
    monkeypatch.setattr("librarian.ops.upgrade.run_backup", run_backup)
    assert ops_cli.main(["upgrade", "sha-1", "--no-take"]) == 3
    assert ops_cli.main(["upgrade", "bad tag"]) == 1


# ── failure alert ───────────────────────────────────────────────────────────


def test_failed_backup_exits_nonzero_and_emails_the_owner(
    db_url: str, bucket: Path, calls: list[list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_BACKUP_URL", f"file://{bucket}")
    monkeypatch.setenv("LIBRARIAN_BACKUP_AGE_RECIPIENT", "age1x")
    monkeypatch.setattr(
        "librarian.ops.backup.database_url", lambda: f"sqlite:///{bucket}/missing.sqlite3"
    )
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("EMAIL_FROM", "ops@example.com")
    monkeypatch.setenv("LIBRARIAN_OWNER_EMAIL", "me@example.com")
    sent: list[dict] = []

    def handler(req: httpx.Request) -> httpx.Response:
        sent.append(json.loads(req.content))
        return httpx.Response(200, json={"id": "1"})

    monkeypatch.setattr(mailer, "transport", httpx.MockTransport(handler))
    monkeypatch.setattr(ops_cli, "get_settings", lambda: Settings())
    assert ops_cli.main(["backup"]) == 1
    assert len(sent) == 1
    assert sent[0]["to"] == ["me@example.com"] and "backup failed" in sent[0]["subject"]
    assert "re_test" not in json.dumps(sent[0])


def test_failed_backup_without_mail_configured_still_exits_nonzero(
    bucket: Path, calls: list[list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_BACKUP_URL", f"file://{bucket}")
    monkeypatch.setenv("LIBRARIAN_BACKUP_AGE_RECIPIENT", "age1x")
    monkeypatch.setattr(
        "librarian.ops.backup.database_url", lambda: f"sqlite:///{bucket}/missing.sqlite3"
    )
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.setattr(ops_cli, "get_settings", lambda: Settings())
    assert ops_cli.main(["backup"]) == 1


# ── schedule ────────────────────────────────────────────────────────────────


def test_next_run_is_the_next_slot_strictly_after_now() -> None:
    assert schedule.next_run(datetime(2026, 11, 8, 3, 0, tzinfo=UTC), "03:30") == datetime(
        2026, 11, 8, 3, 30, tzinfo=UTC
    )
    assert schedule.next_run(datetime(2026, 11, 8, 3, 30, tzinfo=UTC), "03:30") == datetime(
        2026, 11, 9, 3, 30, tzinfo=UTC
    )


def test_schedule_loop_survives_a_failed_backup(
    settings: Settings, bucket: Path, calls: list[list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    slept: list[float] = []
    n = {"runs": 0}

    def boom(_s: Settings) -> None:
        n["runs"] += 1
        raise OpsError("bucket unreachable")

    monkeypatch.setattr(schedule, "run_backup", boom)
    clock = iter([NOW, NOW, NOW + timedelta(days=1), NOW + timedelta(days=1)])
    s = Settings()
    # once=False would loop forever; two iterations by hand through once=True
    schedule.loop(s, once=True, sleep=slept.append, clock=lambda: next(clock))
    assert n["runs"] == 1 and slept and slept[0] > 0


# ── storage ─────────────────────────────────────────────────────────────────


def test_s3_storage_uses_aws_cli_with_the_endpoint(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: list[list[str]] = []

    def fake_run(cmd, *, env=None, timeout=0.0):  # noqa: ANN001, ANN202
        seen.append(list(cmd))
        out = "                           PRE old/\n2026-11-08 03:30:01     12 librarian-20261108T033000Z-a.manifest.json\n"
        return subprocess.CompletedProcess(cmd, 0, out, "")

    monkeypatch.setattr(proc, "run", fake_run)
    s = S3Storage("s3://bkt/pre/", "https://acct.r2.cloudflarestorage.com")
    f = tmp_path / "x"
    f.write_text("x")
    s.put(f, "x.dump.age")
    assert s.names() == ["librarian-20261108T033000Z-a.manifest.json"]
    assert seen[0][:4] == ["aws", "s3", "cp", str(f)]
    assert seen[0][4] == "s3://bkt/pre/x.dump.age"
    assert seen[0][-2:] == ["--endpoint-url", "https://acct.r2.cloudflarestorage.com"]
    assert seen[1][:3] == ["aws", "s3", "ls"]


def test_open_storage_picks_by_scheme(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("LIBRARIAN_BACKUP_URL", f"file://{tmp_path}")
    assert isinstance(open_storage(Settings()), LocalStorage)
    monkeypatch.setenv("LIBRARIAN_BACKUP_URL", "s3://b/p")
    assert isinstance(open_storage(Settings()), S3Storage)
    monkeypatch.setenv("LIBRARIAN_BACKUP_URL", "ftp://x")
    with pytest.raises(OpsError):
        open_storage(Settings())
    monkeypatch.setenv("LIBRARIAN_BACKUP_URL", "")
    with pytest.raises(OpsError, match="not set"):
        open_storage(Settings())


def test_missing_tool_is_a_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: None)
    with pytest.raises(OpsError, match="age"):
        proc.require("age")


# ── postgres (tools mocked) ─────────────────────────────────────────────────


def test_pg_args_keep_the_password_off_the_command_line() -> None:
    args, env = dbtools.pg_args("postgresql://librarian:s3cret@postgres:5432/librarian")
    assert "s3cret" not in " ".join(args)
    assert env == {"PGPASSWORD": "s3cret"} and "postgres" in args


def test_postgres_dump_runs_pg_dump_fc_on_an_exported_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[tuple[list[str], dict[str, str]]] = []

    class Snap:
        id = "00000003-1"

        def read(self) -> tuple[dict[str, int], str | None]:
            return {"users": 2}, "0005"

    @contextmanager
    def fake_snapshot(url: str):  # noqa: ANN202
        yield Snap()

    def fake_run(cmd, *, env=None, timeout=0.0):  # noqa: ANN001, ANN202
        seen.append((list(cmd), dict(env or {})))
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(dbtools, "_pg_snapshot", fake_snapshot)
    monkeypatch.setattr(proc, "run", fake_run)
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    snap = dbtools.dump_database("postgres://librarian:pw@db:5432/librarian", tmp_path / "x.dump")
    cmd, env = seen[0]
    assert cmd[:2] == ["pg_dump", "-Fc"] and "--snapshot" in cmd and "pw" not in cmd
    assert env == {"PGPASSWORD": "pw"}
    assert (snap.dialect, snap.counts, snap.revision) == ("postgresql", {"users": 2}, "0005")


def test_postgres_target_restores_into_a_scratch_database_then_renames(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    statements: list[str] = []
    cmds: list[list[str]] = []
    target = PostgresTarget("postgresql://librarian:pw@db:5432/librarian")
    monkeypatch.setattr(target, "_admin", lambda *stmts: statements.extend(stmts))
    monkeypatch.setattr(
        proc,
        "run",
        lambda cmd, **kw: cmds.append(list(cmd)) or subprocess.CompletedProcess(cmd, 0, "", ""),
    )
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")

    scratch = target.scratch("t1")
    target.load(tmp_path / "x.dump", scratch)
    old = target.swap(scratch, "t1")

    assert statements[0] == 'CREATE DATABASE "librarian_restore_t1"'
    assert cmds[0][0] == "pg_restore" and "librarian_restore_t1" in cmds[0]
    assert "pw" not in " ".join(cmds[0])
    assert 'ALTER DATABASE "librarian" RENAME TO "librarian_pre_restore_t1"' in statements
    assert 'ALTER DATABASE "librarian_restore_t1" RENAME TO "librarian"' in statements
    assert old == "librarian_pre_restore_t1"


def test_postgres_scratch_is_dropped_when_the_check_fails(
    settings: Settings,
    db_url: str,
    bucket: Path,
    calls: list[list[str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    m = run_backup(settings, unencrypted=True, now=NOW, url=db_url)
    log: list[str] = []

    class Fake:
        def is_empty(self) -> bool:
            return True

        def scratch(self, tag: str) -> str:
            return "sqlite:///" + str(bucket / "scratch.sqlite3")

        def load(self, dump: Path, scratch_url: str) -> None:
            raise OpsError("pg_restore exited 1")

        def swap(self, scratch_url: str, tag: str) -> str:
            log.append("swap")
            return ""

        def discard(self, scratch_url: str) -> None:
            log.append("discard")

    with pytest.raises(OpsError):
        restore.run_restore(settings, m.base, target=Fake(), url="sqlite:///unused")
    assert log == ["discard"]


# ── registration ────────────────────────────────────────────────────────────


def test_ops_group_is_registered() -> None:
    assert set(cli.GROUPS["ops"]) == {"backup", "restore", "upgrade", "schedule", "list"}
    assert all(v.target == "librarian.ops.cli:main" for v in cli.GROUPS["ops"].values())
