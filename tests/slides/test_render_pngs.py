"""render_pngs renders beside the target and swaps in on success: a failed render keeps the old PNGs."""

from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

pytest.importorskip("pptx")
from librarian.tools.slides import build_deck as bd


class _FakeSlide:
    part = SimpleNamespace(rels={}, drop_rel=lambda r: None)


class _FakePrs:
    def __init__(self, n: int) -> None:
        self.slides = _Slides(n)
        self.part = SimpleNamespace(drop_rel=lambda r: None)

    def save(self, path: str) -> None:
        Path(path).write_bytes(b"pptx")


class _Slides(list):  # type: ignore[type-arg]
    def __init__(self, n: int) -> None:
        super().__init__([_FakeSlide() for _ in range(n)])
        self._sldIdLst: list[Any] = []


@pytest.fixture()
def stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bd, "Presentation", lambda path: _FakePrs(2))
    monkeypatch.setattr(bd.shutil, "which", lambda name: f"/bin/{name}")


def _ql(render: int | None):
    """A qlmanage stand-in: writes `render` PNGs (None = fail)."""

    def run(cmd: list[str], **kw: Any) -> None:
        if render is None:
            raise subprocess.CalledProcessError(1, cmd)
        out = Path(cmd[cmd.index("-o") + 1])
        for single in cmd[cmd.index("-o") + 2 :][:render]:
            (out / f"{Path(single).name}.png").write_bytes(b"new")

    return run


def _old(out: Path) -> None:
    out.mkdir(parents=True)
    (out / "slide-01.png").write_bytes(b"old1")
    (out / "slide-02.png").write_bytes(b"old2")


def test_a_failed_render_keeps_the_old_pngs(
    stub: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "deck" / "preview"
    _old(out)
    monkeypatch.setattr(bd.subprocess, "run", _ql(None))
    with pytest.raises(subprocess.CalledProcessError):
        bd.render_pngs(tmp_path / "d.pptx", out)
    assert [(p.name, p.read_bytes()) for p in sorted(out.glob("*.png"))] == [
        ("slide-01.png", b"old1"),
        ("slide-02.png", b"old2"),
    ]
    assert not [p for p in out.parent.iterdir() if p.name.startswith(".render-")]


def test_a_partial_render_does_not_displace_a_full_old_set(
    stub: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "deck" / "preview"
    _old(out)
    monkeypatch.setattr(bd.subprocess, "run", _ql(1))
    pngs = bd.render_pngs(tmp_path / "d.pptx", out)
    assert [p.read_bytes() for p in pngs] == [b"old1", b"old2"]


def test_a_good_render_replaces_the_old_pngs(
    stub: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "deck" / "preview"
    _old(out)
    monkeypatch.setattr(bd.subprocess, "run", _ql(2))
    pngs = bd.render_pngs(tmp_path / "d.pptx", out)
    assert [p.read_bytes() for p in pngs] == [b"new", b"new"]
    assert sorted(p.name for p in out.glob("*.png")) == ["slide-01.png", "slide-02.png"]
    assert not [p for p in out.parent.iterdir() if p.name.startswith(".render-")]
