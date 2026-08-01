"""Unit tests for LIB #75: wiring the four card renderers into region injection.

INPUT-TOKENS, SKILL-ECONOMICS, TOOL-TRENDS, and FRICTION-REGROUP are rendered
by existing `render_*_card(store)` functions in tools/cartographer/dashboard.py
(authored for the `patch_*_card` in-place path). This issue wires those same
functions into `inject_regions()` via tools/cartographer/__main__.py — no new
renderer code, since each already returns a self-contained HTML fragment.

Covers:
- Each renderer: non-empty output with data, graceful (non-empty) output with
  no data.
- Round-trip: each renderer's output injects cleanly into a marker pair.
- A copy of the real context-dashboard.html: injecting all four regions
  changes only those four regions; the hand-written HOOK-ACTIVITY card and
  all other bytes are preserved exactly.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tools.cartographer.dashboard import (
    inject_regions,
    render_friction_regroup_card,
    render_input_tokens_card,
    render_skill_economics_card,
    render_tool_trends_card,
)
from tools.cartographer.factstore import upsert

JULY_DATE = "2026-07-18"
REGIME = "session-hygiene-v1"


def _row(session_id: str, date: str = JULY_DATE, regime: str = REGIME, **overrides: object) -> dict:
    """A fact row shaped like factstore.FACT_COLUMNS requires (July-era defaults)."""
    row: dict = {
        "session_id": session_id,
        "date": date,
        "project": "/Users/x/repo",
        "era": "jsonl",
        "regime": regime,
        "source_path": f"/tmp/{session_id}",
        "input_tokens": 500,
        "output_tokens": 200,
        "cache_read_tokens": 300,
        "cache_write_tokens": 40,
        "cost_units": 1234.5,
        "compacted": True,
        "is_meta": False,
    }
    row.update(overrides)
    return row


# ---------------------------------------------------------------------------
# render_input_tokens_card
# ---------------------------------------------------------------------------


def test_render_input_tokens_card_with_data(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert([_row("j1", input_tokens=1000), _row("j2", input_tokens=3000)], store)
    result = render_input_tokens_card(store)
    assert result
    assert "Input tokens" in result
    assert "<svg" in result


def test_render_input_tokens_card_no_data(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert([], store)
    result = render_input_tokens_card(store)
    assert result
    assert "No data yet" in result


# ---------------------------------------------------------------------------
# render_skill_economics_card
# ---------------------------------------------------------------------------


def test_render_skill_economics_card_with_data(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert(
        [_row("j1", skill_costs=json.dumps({"wake": 500.0, "grow": 200.0}))],
        store,
    )
    result = render_skill_economics_card(store)
    assert result
    assert "Skill economics" in result
    assert "wake" in result
    assert "grow" in result


def test_render_skill_economics_card_no_data(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert([], store)
    result = render_skill_economics_card(store)
    assert result
    assert "No skill cost data" in result


# ---------------------------------------------------------------------------
# render_tool_trends_card
# ---------------------------------------------------------------------------


def test_render_tool_trends_card_with_data(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert(
        [_row("j1", tool_counts=json.dumps({"Bash": 10, "Read": 5}))],
        store,
    )
    result = render_tool_trends_card(store)
    assert result
    assert "Tool call trends" in result
    assert "Bash" in result


def test_render_tool_trends_card_no_data(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert([], store)
    result = render_tool_trends_card(store)
    assert result
    assert "No tool-count data" in result


# ---------------------------------------------------------------------------
# render_friction_regroup_card
# ---------------------------------------------------------------------------


def test_render_friction_regroup_card_with_data(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert(
        [
            _row(
                "j1",
                human_turns=5,
                user_interruptions=1,
                skill_costs='{"wake":100}',
                session_intent="execution",
                tool_counts='{"Bash":10}',
                tool_error_count=1,
                friction_label_count=0,
            ),
        ],
        store,
    )
    result = render_friction_regroup_card(store)
    assert result
    assert "Prompt-eng" in result
    assert "Loop-eng" in result
    assert "Harness-eng" in result


def test_render_friction_regroup_card_no_data(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert([], store)
    result = render_friction_regroup_card(store)
    assert result
    assert "Prompt-eng" in result
    assert "no data" in result.lower()


# ---------------------------------------------------------------------------
# Round-trip: injects cleanly into a marker pair
# ---------------------------------------------------------------------------

_BEFORE = "SENTINEL_BEFORE\n"
_AFTER = "\nSENTINEL_AFTER"


def _make_html(name: str, inner: str = "<p>old content</p>") -> str:
    return (
        f"{_BEFORE}"
        f"<!-- {name}:START (regenerated by cartographer --facts; do not hand-edit) -->\n"
        f"{inner}\n"
        f"<!-- {name}:END -->"
        f"{_AFTER}"
    )


@pytest.mark.parametrize(
    "region_name,renderer_name",
    [
        ("INPUT-TOKENS", "render_input_tokens_card"),
        ("SKILL-ECONOMICS", "render_skill_economics_card"),
        ("TOOL-TRENDS", "render_tool_trends_card"),
        ("FRICTION-REGROUP", "render_friction_regroup_card"),
    ],
)
def test_roundtrip_inject_card_renderers(
    tmp_path: Path, region_name: str, renderer_name: str
) -> None:
    """Each of the four card renderers' output injects cleanly via inject_regions."""
    import tools.cartographer.dashboard as dashboard_mod

    store = tmp_path / "facts.db"
    upsert(
        [
            _row(
                "j1",
                input_tokens=1000,
                skill_costs=json.dumps({"wake": 500.0}),
                tool_counts=json.dumps({"Bash": 10}),
            )
        ],
        store,
    )
    renderer = getattr(dashboard_mod, renderer_name)
    fragment = renderer(store)

    p = tmp_path / "context-dashboard.html"
    p.write_text(_make_html(region_name), encoding="utf-8")
    inject_regions(p, {region_name: fragment})

    result = p.read_text(encoding="utf-8")
    assert fragment in result
    assert "<p>old content</p>" not in result
    assert _BEFORE in result
    assert _AFTER in result


# ---------------------------------------------------------------------------
# Real-dashboard fixture: injecting the four regions is a near-no-op and does
# not disturb HOOK-ACTIVITY or any other content.
# ---------------------------------------------------------------------------

_REAL_DASHBOARD = Path("~/workspace/guacamayo/.sounding/context-dashboard.html").expanduser()


@pytest.mark.skipif(
    not _REAL_DASHBOARD.exists(), reason="guacamayo context-dashboard.html not present"
)
def test_inject_four_regions_preserves_hook_activity_and_other_bytes(tmp_path: Path) -> None:
    """Injecting the four wired regions into a COPY of the real dashboard changes only
    those four regions; HOOK-ACTIVITY and everything else is preserved byte-for-byte.

    Never writes to the live guacamayo file — operates on a copy in tmp_path.
    """
    copy_path = tmp_path / "context-dashboard.html"
    shutil.copy(_REAL_DASHBOARD, copy_path)
    original = copy_path.read_text(encoding="utf-8")

    def _region_slice(text: str, name: str) -> tuple[int, int, str]:
        start_tag = f"<!-- {name}:START"
        end_tag = f"<!-- {name}:END -->"
        start_idx = text.index(start_tag)
        comment_end = text.index("-->", start_idx) + 3
        end_idx = text.index(end_tag, comment_end)
        return comment_end, end_idx, text[comment_end:end_idx]

    # Capture HOOK-ACTIVITY (untouched region) and full-file byte count before.
    _, _, hook_before = _region_slice(original, "HOOK-ACTIVITY")

    store = tmp_path / "facts.db"
    upsert(
        [
            _row(
                "j1",
                input_tokens=1000,
                skill_costs=json.dumps({"wake": 500.0}),
                tool_counts=json.dumps({"Bash": 10}),
                human_turns=5,
                user_interruptions=0,
                session_intent="execution",
                tool_error_count=0,
                friction_label_count=0,
            )
        ],
        store,
    )

    regions = {
        "INPUT-TOKENS": render_input_tokens_card(store),
        "SKILL-ECONOMICS": render_skill_economics_card(store),
        "TOOL-TRENDS": render_tool_trends_card(store),
        "FRICTION-REGROUP": render_friction_regroup_card(store),
    }
    inject_regions(copy_path, regions)
    result = copy_path.read_text(encoding="utf-8")

    # HOOK-ACTIVITY region body is byte-for-byte identical.
    _, _, hook_after = _region_slice(result, "HOOK-ACTIVITY")
    assert hook_after == hook_before

    # Everything before the first wired region's start and after the last
    # wired region's end that isn't itself a wired region should be
    # unaffected. Cheaper check: bytes outside all four wired regions are
    # unchanged by comparing the file with each wired region's content
    # blanked out on both sides.
    def _strip_regions(text: str, names: list[str]) -> str:
        for name in names:
            start_tag = f"<!-- {name}:START"
            end_tag = f"<!-- {name}:END -->"
            start_idx = text.index(start_tag)
            comment_end = text.index("-->", start_idx) + 3
            end_idx = text.index(end_tag, comment_end)
            text = text[:comment_end] + "\n<STRIPPED>\n" + text[end_idx:]
        return text

    wired = ["INPUT-TOKENS", "SKILL-ECONOMICS", "TOOL-TRENDS", "FRICTION-REGROUP"]
    assert _strip_regions(original, wired) == _strip_regions(result, wired)

    # Each wired region actually changed content (not a coincidental match)
    # or at minimum contains the freshly rendered fragment.
    for name, fragment in regions.items():
        _, _, injected = _region_slice(result, name)
        assert fragment.strip() == injected.strip()
