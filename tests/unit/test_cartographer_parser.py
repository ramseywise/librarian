from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.cartographer.parser import (
    _context_bucket,
    _usage_cost,
    aggregate,
    iter_sessions,
    iter_subagent_sessions,
    parse_session,
)


def _user(ts: str, text: str = "hello", **extra: bool) -> dict[str, Any]:
    return {
        "type": "user",
        "timestamp": ts,
        "message": {"content": text},
        **extra,
    }


def _assistant(
    ts: str,
    input_tokens: int = 100,
    output_tokens: int = 50,
    cache_read: int = 0,
    cache_write: int = 0,
    model: str = "claude-sonnet-5",
) -> dict[str, Any]:
    return {
        "type": "assistant",
        "timestamp": ts,
        "message": {
            "model": model,
            "content": [{"type": "text", "text": "ok"}],
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_read_input_tokens": cache_read,
                "cache_creation_input_tokens": cache_write,
            },
        },
    }


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")


@pytest.mark.unit
def test_usage_cost_weights() -> None:
    usage = {
        "input_tokens": 100,
        "cache_creation_input_tokens": 100,
        "cache_read_input_tokens": 1000,
        "output_tokens": 10,
    }
    # 100*1.0 + 100*1.25 + 1000*0.1 + 10*5.0
    assert _usage_cost(usage) == pytest.approx(375.0)


@pytest.mark.unit
def test_context_buckets() -> None:
    assert _context_bucket(10_000) == "<50k"
    assert _context_bucket(50_000) == "50-100k"
    assert _context_bucket(149_999) == "100-150k"
    assert _context_bucket(150_000) == ">150k"


@pytest.mark.unit
def test_parse_session_cost_and_context(tmp_path: Path) -> None:
    records = [
        _user("2026-07-01T10:00:00Z"),
        _assistant("2026-07-01T10:00:05Z", input_tokens=1000, output_tokens=100),
        _assistant(
            "2026-07-01T10:01:00Z",
            input_tokens=1000,
            output_tokens=100,
            cache_read=160_000,
        ),
    ]
    path = tmp_path / "session-a.jsonl"
    _write_jsonl(path, records)
    session = parse_session(path)
    assert session is not None
    # msg1: 1000 + 500 = 1500; msg2: 1000 + 16000 + 500 = 17500
    assert session["cost_units"] == pytest.approx(19_000.0)
    assert session["max_context"] == 161_000
    assert session["context_bucket_cost"]["<50k"] == pytest.approx(1500.0)
    assert session["context_bucket_cost"][">150k"] == pytest.approx(17_500.0)
    assert len(session["cost_events"]) == 2
    assert session["compact_count"] == 0


@pytest.mark.unit
def test_parse_session_compact_count(tmp_path: Path) -> None:
    records = [
        _user("2026-07-01T10:00:00Z"),
        _assistant("2026-07-01T10:00:05Z"),
        {"type": "system", "subtype": "compact_boundary", "timestamp": "2026-07-01T10:05:00Z"},
        _user("2026-07-01T10:05:01Z", text="summary", isCompactSummary=True),
    ]
    path = tmp_path / "session-b.jsonl"
    _write_jsonl(path, records)
    session = parse_session(path)
    assert session is not None
    # boundary + flagged summary describe one compact — not two
    assert session["compact_count"] == 1


@pytest.mark.unit
def test_parse_session_skill_cost_attribution(tmp_path: Path) -> None:
    records = [
        _user("2026-07-01T10:00:00Z", text="<command-name>/execute</command-name> args"),
        _user("2026-07-01T10:00:01Z", text="Base directory for this skill: ...expanded prompt"),
        _assistant("2026-07-01T10:00:05Z", input_tokens=1000, output_tokens=0),
        _assistant("2026-07-01T10:00:10Z", input_tokens=1000, output_tokens=0),
        _user("2026-07-01T10:10:00Z", text="now something unrelated"),
        _assistant("2026-07-01T10:10:05Z", input_tokens=5000, output_tokens=0),
    ]
    path = tmp_path / "session-c.jsonl"
    _write_jsonl(path, records)
    session = parse_session(path)
    assert session is not None
    assert session["skill_costs"] == {"execute": pytest.approx(2000.0)}


@pytest.mark.unit
def test_iter_sessions_skips_subagents_and_iter_subagents_attributes(tmp_path: Path) -> None:
    main_records = [_user("2026-07-01T10:00:00Z"), _assistant("2026-07-01T10:00:05Z")]
    sub_records = [
        _user("2026-07-01T10:01:00Z", text="subtask", isSidechain=True),
        _assistant("2026-07-01T10:01:05Z", input_tokens=2000, output_tokens=200),
    ]
    _write_jsonl(tmp_path / "proj" / "sess-1.jsonl", main_records)
    _write_jsonl(tmp_path / "proj" / "sess-1" / "subagents" / "agent-x.jsonl", sub_records)

    mains = iter_sessions(tmp_path)
    assert [s["session_id"] for s in mains] == ["sess-1"]
    assert mains[0]["is_subagent"] is False

    subs = iter_subagent_sessions(tmp_path)
    assert len(subs) == 1
    assert subs[0]["is_subagent"] is True
    assert subs[0]["parent_session_id"] == "sess-1"


@pytest.mark.unit
def test_aggregate_economics(tmp_path: Path) -> None:
    # Two overlapping main sessions + one subagent under sess-1
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [
            _user("2026-07-01T10:00:00Z", text="/execute the plan"),
            _assistant("2026-07-01T10:00:05Z", input_tokens=1000, output_tokens=0),
            _user("2026-07-01T11:00:00Z"),
            _assistant("2026-07-01T11:00:05Z", input_tokens=1000, output_tokens=0),
        ],
    )
    _write_jsonl(
        tmp_path / "proj" / "sess-2.jsonl",
        [
            _user("2026-07-01T10:30:00Z"),
            _assistant("2026-07-01T10:30:05Z", input_tokens=1000, output_tokens=0),
            _user("2026-07-01T12:00:00Z"),
        ],
    )
    _write_jsonl(
        tmp_path / "proj" / "sess-1" / "subagents" / "agent-a.jsonl",
        [
            _user("2026-07-01T10:40:00Z", isSidechain=True),
            _assistant("2026-07-01T10:40:05Z", input_tokens=3000, output_tokens=0),
        ],
    )

    sessions = iter_sessions(tmp_path)
    subs = iter_subagent_sessions(tmp_path)
    agg = aggregate(sessions, subs)

    assert agg["usage_cost_units"] == 6000
    # sess-1: 1000 main + 3000 subagent → subagent-heavy; sess-2: 1000
    assert agg["subagents"]["share_of_usage_pct"] == 50
    assert agg["subagents"]["heavy_sessions"] == 1
    # heavy session total (2000 main + 3000 sub = 5000) / 6000
    assert agg["subagents"]["pct_usage_in_heavy_sessions"] == 83
    # 10:00 request: only sess-1 active → "1"; 10:30, 10:40, 11:00 fall inside both
    # session intervals → "2-3"
    assert agg["parallelism_usage_pct"]["1"] == 17
    assert agg["parallelism_usage_pct"]["2-3"] == 83
    assert agg["parallelism_usage_pct"]["4+"] == 0
    # all requests small context
    assert agg["context_usage_pct"]["<50k"] == 100
    assert agg["pct_usage_over_150k_context"] == 0
    # /execute turn = first assistant msg of sess-1 only
    assert agg["skill_usage_pct"]["execute"] == pytest.approx(16.7)
    assert agg["cache"]["hit_rate_pct"] == 0


@pytest.mark.unit
def test_aggregate_cache_savings(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [
            _user("2026-07-01T10:00:00Z"),
            _assistant(
                "2026-07-01T10:00:05Z",
                input_tokens=0,
                output_tokens=0,
                cache_read=90_000,
                cache_write=10_000,
            ),
        ],
    )
    agg = aggregate(iter_sessions(tmp_path), [])
    assert agg["cache"]["hit_rate_pct"] == 90
    # actual: 90k*0.1 + 10k*1.25 = 21.5k vs uncached 100k → 78.5% ≈ 78%
    assert agg["cache"]["savings_vs_uncached_pct"] == 78


@pytest.mark.unit
def test_parse_session_extracts_attribution_agent(tmp_path: Path) -> None:
    """CLI 2.1.201+ tags subagent records with the agent type name."""
    path = tmp_path / "proj" / "sess-1" / "subagents" / "agent-a.jsonl"
    _write_jsonl(
        path,
        [
            {**_user("2026-07-18T10:00:00Z"), "attributionAgent": "Explore"},
            _assistant("2026-07-18T10:00:05Z"),
        ],
    )
    session = parse_session(path)
    assert session is not None
    assert session["attribution_agent"] == "Explore"


@pytest.mark.unit
def test_parse_session_attribution_absent_pre_2_1_201(tmp_path: Path) -> None:
    """Older transcripts carry no name; the field stays None rather than guessing."""
    path = tmp_path / "proj" / "sess-1" / "subagents" / "agent-a.jsonl"
    _write_jsonl(path, [_user("2026-07-10T10:00:00Z"), _assistant("2026-07-10T10:00:05Z")])
    session = parse_session(path)
    assert session is not None
    assert session["attribution_agent"] is None


@pytest.mark.unit
def test_parse_session_splits_cost_by_model(tmp_path: Path) -> None:
    path = tmp_path / "proj" / "sess-1.jsonl"
    _write_jsonl(
        path,
        [
            _user("2026-07-18T10:00:00Z"),
            _assistant("2026-07-18T10:00:05Z", output_tokens=50, model="claude-opus-4-8"),
            _assistant("2026-07-18T10:00:09Z", output_tokens=30, model="claude-haiku-4-5"),
        ],
    )
    session = parse_session(path)
    assert session is not None
    assert set(session["model_costs"]) == {"claude-opus-4-8", "claude-haiku-4-5"}
    assert session["model_output_tokens"]["claude-opus-4-8"] == 50
    assert session["model_output_tokens"]["claude-haiku-4-5"] == 30
    # Per-model costs partition the session total, never duplicate it.
    assert sum(session["model_costs"].values()) == pytest.approx(session["cost_units"], rel=0.02)


@pytest.mark.unit
def test_subagent_costs_roll_up_to_parent(tmp_path: Path) -> None:
    """Subagent spend is charged to the parent, split by agent name and model."""
    from tools.cartographer.factstore import UNATTRIBUTED_AGENT, _subagent_costs_by_parent

    _write_jsonl(
        tmp_path / "proj" / "sess-1" / "subagents" / "agent-a.jsonl",
        [
            {**_user("2026-07-18T10:00:00Z"), "attributionAgent": "Explore"},
            _assistant("2026-07-18T10:00:05Z", model="claude-haiku-4-5"),
        ],
    )
    # Same parent, no attribution -> lands in the unattributed bucket, not dropped.
    _write_jsonl(
        tmp_path / "proj" / "sess-1" / "subagents" / "agent-b.jsonl",
        [
            _user("2026-07-18T10:01:00Z"),
            _assistant("2026-07-18T10:01:05Z", model="claude-sonnet-5"),
        ],
    )
    rolled = _subagent_costs_by_parent(tmp_path)

    assert set(rolled) == {"sess-1"}
    by_agent = rolled["sess-1"]["by_agent"]
    assert set(by_agent) == {"Explore", UNATTRIBUTED_AGENT}
    assert by_agent["Explore"]["n"] == 1
    assert by_agent[UNATTRIBUTED_AGENT]["n"] == 1
    # Per-model coverage is complete even where the agent name is missing.
    assert set(rolled["sess-1"]["by_model"]) == {"claude-haiku-4-5", "claude-sonnet-5"}


@pytest.mark.unit
def test_from_jsonl_leaves_subagent_costs_null_without_subagents(tmp_path: Path) -> None:
    """A parent that spawned nothing stores NULL, not an empty object -- absence of
    subagent use must stay distinguishable from a zero-cost subagent."""
    from tools.cartographer.factstore import from_jsonl

    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [_user("2026-07-18T10:00:00Z"), _assistant("2026-07-18T10:00:05Z")],
    )
    rows = from_jsonl(tmp_path)
    assert len(rows) == 1
    assert rows[0]["subagent_costs"] is None
