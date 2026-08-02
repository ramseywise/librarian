from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from tools.cartographer.parser import (
    _REQUIRED_SECTION_IDS,
    _SECTION_ID_LIST,
    _SYSTEM_PROMPT,
    ReportTruncatedError,
    SectionContractError,
    _context_bucket,
    _missing_section_ids,
    _usage_cost,
    aggregate,
    call_claude,
    generate_report_html,
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


def _assistant_with_tools(ts: str, tool_blocks: list[dict[str, Any]]) -> dict[str, Any]:
    """Assistant message with tool_use blocks in content."""
    base = _assistant(ts)
    base["message"]["content"] = [
        {"type": "text", "text": "ok"},
        *tool_blocks,
    ]
    return base


@pytest.mark.unit
def test_agent_spawns_extraction(tmp_path: Path) -> None:
    tools = [
        {
            "type": "tool_use",
            "name": "Agent",
            "input": {
                "subagent_type": "Explore",
                "description": "Find config files",
                "model": "haiku",
            },
        },
        {
            "type": "tool_use",
            "name": "Agent",
            "input": {
                "description": "Review changes",
            },
        },
        {
            "type": "tool_use",
            "name": "Agent",
            "input": {
                "subagent_type": "code-reviewer",
                "description": "Check quality",
                "model": "sonnet",
            },
        },
    ]
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [_user("2026-07-20T10:00:00Z"), _assistant_with_tools("2026-07-20T10:00:05Z", tools)],
    )
    session = parse_session(tmp_path / "proj" / "sess-1.jsonl")
    assert session is not None
    spawns = session["agent_spawns"]
    assert len(spawns) == 3
    assert spawns[0] == {"type": "Explore", "description": "Find config files", "model": "haiku"}
    assert spawns[1] == {"type": "general-purpose", "description": "Review changes", "model": None}
    assert spawns[2] == {"type": "code-reviewer", "description": "Check quality", "model": "sonnet"}


@pytest.mark.unit
def test_agent_spawns_empty_when_no_agent_calls(tmp_path: Path) -> None:
    tools = [{"type": "tool_use", "name": "Read", "input": {"file_path": "/tmp/x"}}]
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [_user("2026-07-20T10:00:00Z"), _assistant_with_tools("2026-07-20T10:00:05Z", tools)],
    )
    session = parse_session(tmp_path / "proj" / "sess-1.jsonl")
    assert session is not None
    assert session["agent_spawns"] == []


@pytest.mark.unit
def test_subagent_type_defaults_to_general_purpose(tmp_path: Path) -> None:
    tools = [{"type": "tool_use", "name": "Agent", "input": {"description": "Do something"}}]
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [_user("2026-07-20T10:00:00Z"), _assistant_with_tools("2026-07-20T10:00:05Z", tools)],
    )
    session = parse_session(tmp_path / "proj" / "sess-1.jsonl")
    assert session is not None
    assert session["agent_spawns"][0]["type"] == "general-purpose"


@pytest.mark.unit
def test_friction_label_extraction(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [
            _user("2026-07-20T10:00:00Z", text="FRICTION: skill X never triggered\nother text"),
            _assistant("2026-07-20T10:00:05Z"),
            _user("2026-07-20T10:01:00Z", text="FRICTION: hook blocked my edit"),
            _assistant("2026-07-20T10:01:05Z"),
        ],
    )
    session = parse_session(tmp_path / "proj" / "sess-1.jsonl")
    assert session is not None
    assert session["friction_labels"] == ["skill X never triggered", "hook blocked my edit"]
    assert session["friction_label_count"] == 2


@pytest.mark.unit
def test_friction_label_absent(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [_user("2026-07-20T10:00:00Z", text="normal message"), _assistant("2026-07-20T10:00:05Z")],
    )
    session = parse_session(tmp_path / "proj" / "sess-1.jsonl")
    assert session is not None
    assert session["friction_labels"] == []
    assert session["friction_label_count"] == 0


@pytest.mark.unit
def test_friction_label_truncated(tmp_path: Path) -> None:
    long_label = "x" * 300
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [
            _user("2026-07-20T10:00:00Z", text=f"FRICTION: {long_label}"),
            _assistant("2026-07-20T10:00:05Z"),
        ],
    )
    session = parse_session(tmp_path / "proj" / "sess-1.jsonl")
    assert session is not None
    assert len(session["friction_labels"][0]) == 200


# --- GUA-43: entrypoint / surface extraction ---------------------------------


@pytest.mark.unit
def test_parse_session_extracts_entrypoint(tmp_path: Path) -> None:
    """entrypoint field is extracted from JSONL records and surfaced as 'entrypoint'."""
    path = tmp_path / "proj" / "sess-1.jsonl"
    _write_jsonl(
        path,
        [
            {**_user("2026-07-18T10:00:00Z"), "entrypoint": "claude-vscode"},
            _assistant("2026-07-18T10:00:05Z"),
        ],
    )
    session = parse_session(path)
    assert session is not None
    assert session["entrypoint"] == "claude-vscode"


@pytest.mark.unit
def test_parse_session_entrypoint_none_when_absent(tmp_path: Path) -> None:
    """Sessions without an entrypoint field return None -- pre-entrypoint transcripts."""
    path = tmp_path / "proj" / "sess-1.jsonl"
    _write_jsonl(path, [_user("2026-07-18T10:00:00Z"), _assistant("2026-07-18T10:00:05Z")])
    session = parse_session(path)
    assert session is not None
    assert session["entrypoint"] is None


# --- Step 1: turns_since_last_compact + compact_trigger ----------------------


@pytest.mark.unit
def test_parse_session_compact_trigger_and_turns_since(tmp_path: Path) -> None:
    """compact_boundary with compactMetadata.trigger populates both new fields."""
    compact_boundary = {
        "type": "system",
        "subtype": "compact_boundary",
        "timestamp": "2026-07-18T10:05:00Z",
        "compactMetadata": {"trigger": "manual", "preTokens": 90000, "postTokens": 5000},
    }
    path = tmp_path / "proj" / "sess-1.jsonl"
    _write_jsonl(
        path,
        [
            _user("2026-07-18T10:00:00Z"),
            _assistant("2026-07-18T10:00:05Z"),
            compact_boundary,
            # tool result (not a human turn) — should NOT count
            {
                "type": "user",
                "timestamp": "2026-07-18T10:05:05Z",
                "message": {
                    "content": [{"type": "tool_result", "tool_use_id": "x", "content": "ok"}]
                },
            },
            _user("2026-07-18T10:06:00Z", text="first post-compact"),
            _assistant("2026-07-18T10:06:05Z"),
            _user("2026-07-18T10:07:00Z", text="second post-compact"),
        ],
    )
    session = parse_session(path)
    assert session is not None
    assert session["compact_trigger"] == "manual"
    assert session["turns_since_last_compact"] == 2


@pytest.mark.unit
def test_parse_session_no_compact_gives_none(tmp_path: Path) -> None:
    """Sessions that never compacted return None for both fields."""
    path = tmp_path / "proj" / "sess-2.jsonl"
    _write_jsonl(
        path,
        [_user("2026-07-18T10:00:00Z"), _assistant("2026-07-18T10:00:05Z")],
    )
    session = parse_session(path)
    assert session is not None
    assert session["compact_trigger"] is None
    assert session["turns_since_last_compact"] is None


# --- Section contract validation (LIB-61) -----------------------------------


def _html_with_ids(*section_ids: str) -> str:
    body = "".join(f'<div id="{sid}"></div>' for sid in section_ids)
    return f"<!DOCTYPE html><html><body>{body}</body></html>"


@pytest.mark.unit
def test_missing_section_ids_all_present() -> None:
    html = _html_with_ids(*_REQUIRED_SECTION_IDS)
    assert _missing_section_ids(html) == []


@pytest.mark.unit
def test_missing_section_ids_reports_absent_ones() -> None:
    present = _REQUIRED_SECTION_IDS[:-2]
    html = _html_with_ids(*present)
    missing = _missing_section_ids(html)
    assert missing == list(_REQUIRED_SECTION_IDS[-2:])


@pytest.mark.unit
def test_generate_report_html_all_nine_present_no_retry() -> None:
    """When the first response has all nine ids, call_claude is invoked exactly once."""
    full_html = _html_with_ids(*_REQUIRED_SECTION_IDS)
    with patch("tools.cartographer.parser.call_claude", return_value=full_html) as mock_call:
        result = generate_report_html("fake-key", "prompt", "fake-model")
    assert result == full_html
    mock_call.assert_called_once()


@pytest.mark.unit
def test_generate_report_html_missing_id_triggers_one_retry() -> None:
    """A response missing one id triggers exactly one retry with a corrective prompt."""
    incomplete_html = _html_with_ids(*_REQUIRED_SECTION_IDS[:-1])
    full_html = _html_with_ids(*_REQUIRED_SECTION_IDS)
    with patch(
        "tools.cartographer.parser.call_claude",
        side_effect=[incomplete_html, full_html],
    ) as mock_call:
        result = generate_report_html("fake-key", "prompt", "fake-model")
    assert result == full_html
    assert mock_call.call_count == 2
    # The retry prompt must name the specific missing id.
    retry_prompt = mock_call.call_args_list[1].args[1]
    assert _REQUIRED_SECTION_IDS[-1] in retry_prompt


@pytest.mark.unit
def test_generate_report_html_still_missing_after_retry_raises() -> None:
    """If the retry also comes back incomplete, raise naming the missing ids -- never save silently."""
    incomplete_html = _html_with_ids(*_REQUIRED_SECTION_IDS[:-2])
    still_incomplete_html = _html_with_ids(*_REQUIRED_SECTION_IDS[:-1])
    with (
        patch(
            "tools.cartographer.parser.call_claude",
            side_effect=[incomplete_html, still_incomplete_html],
        ) as mock_call,
        pytest.raises(SectionContractError) as exc_info,
    ):
        generate_report_html("fake-key", "prompt", "fake-model")
    assert mock_call.call_count == 2
    assert _REQUIRED_SECTION_IDS[-1] in str(exc_info.value)


# --- GUA-41: error taxonomy regression (confusion-matrix rows must not reappear) --------


def _tool_error_session(tmp_path: Path, error_text: str) -> dict[str, Any]:
    """Write a single-error session and return the parsed result."""
    path = tmp_path / "sess.jsonl"
    record = {
        "type": "user",
        "timestamp": "2026-08-01T10:00:00Z",
        "message": {
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "t1",
                    "is_error": True,
                    "content": error_text,
                }
            ]
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record) + "\n")
    result = parse_session(path)
    assert result is not None
    return result["tool_errors"]


@pytest.mark.unit
def test_taxonomy_inputvalidationerror_is_invalid_tool_input(tmp_path: Path) -> None:
    """InputValidationError must NOT land in command_failed (was 340 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "<tool_use_error>InputValidationError: Read failed due to the following issue:\n"
        "An unexpected parameter `description` was provided.</tool_use_error>",
    )
    assert errors.get("invalid_tool_input", 0) == 1
    assert errors.get("command_failed", 0) == 0


@pytest.mark.unit
def test_taxonomy_has_not_been_read_yet_is_read_before_write(tmp_path: Path) -> None:
    """'has not been read yet' must NOT land in other (was 228 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "<tool_use_error>File has not been read yet. Read it first before writing to it.</tool_use_error>",
    )
    assert errors.get("read_before_write", 0) == 1
    assert errors.get("other", 0) == 0


@pytest.mark.unit
def test_taxonomy_file_does_not_exist_is_file_not_found(tmp_path: Path) -> None:
    """'does not exist' must NOT land in other (was 130 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "File does not exist. Note: your current working directory is /workspace.",
    )
    assert errors.get("file_not_found", 0) == 1
    assert errors.get("other", 0) == 0


@pytest.mark.unit
def test_taxonomy_cancelled_parallel_is_cancelled(tmp_path: Path) -> None:
    """'Cancelled:' must NOT land in other (was 121 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "<tool_use_error>Cancelled: parallel tool call Bash(...) errored</tool_use_error>",
    )
    assert errors.get("cancelled", 0) == 1
    assert errors.get("other", 0) == 0


@pytest.mark.unit
def test_taxonomy_pretooluse_hook_is_blocked_by_hook(tmp_path: Path) -> None:
    """PreToolUse hook errors must NOT land in other (was 87 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "PreToolUse:Bash hook error: [bash ~/.claude/hooks/risky_git_guard.sh]: "
        "Blocked: Claude does not commit (only worktree agents).",
    )
    assert errors.get("blocked_by_hook", 0) == 1
    assert errors.get("other", 0) == 0


@pytest.mark.unit
def test_taxonomy_blocked_message_is_blocked_by_hook(tmp_path: Path) -> None:
    """Explicit 'Blocked:' messages must NOT land in other (part of 87 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "<tool_use_error>Blocked: sleep 45 followed by: echo waited.</tool_use_error>",
    )
    assert errors.get("blocked_by_hook", 0) == 1
    assert errors.get("other", 0) == 0


@pytest.mark.unit
def test_taxonomy_disable_model_invocation_is_skill_not_invocable(tmp_path: Path) -> None:
    """disable-model-invocation must NOT land in other (was 79 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "<tool_use_error>Skill workflow-plan cannot be used with Skill tool "
        "due to disable-model-invocation</tool_use_error>",
    )
    assert errors.get("skill_not_invocable", 0) == 1
    assert errors.get("other", 0) == 0


@pytest.mark.unit
def test_taxonomy_eisdir_is_is_a_directory(tmp_path: Path) -> None:
    """EISDIR must NOT land in other (was 78 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "EISDIR: illegal operation on a directory, read '/Users/wiseer/.claude/skills/workflow-retro'",
    )
    assert errors.get("is_a_directory", 0) == 1
    assert errors.get("other", 0) == 0


@pytest.mark.unit
def test_taxonomy_modified_since_read_is_stale_read(tmp_path: Path) -> None:
    """'modified since read' must NOT land in other (was 40 misclassified)."""
    errors = _tool_error_session(
        tmp_path,
        "<tool_use_error>File has been modified since read, either by the user or by a linter. "
        "Read it again before attempting to write.</tool_use_error>",
    )
    assert errors.get("stale_read", 0) == 1
    assert errors.get("other", 0) == 0


@pytest.mark.unit
def test_taxonomy_exit_code_no_such_file_is_command_failed_not_file_not_found(
    tmp_path: Path,
) -> None:
    """'Exit code 1 ... no such file' from shell output = command_failed (was 38 swapped).
    The exit-code signal is more precise — the shell decided the outcome, not the tool layer."""
    errors = _tool_error_session(
        tmp_path,
        "Exit code 1\nls: agents: No such file or directory\ncore\nevals",
    )
    # With the new table, "no such file" fires before "exit code" — this is a deliberate
    # design choice: the file-not-found signal is more actionable than the exit code.
    # The test pins current behaviour so any future reorder shows up explicitly.
    assert errors.get("file_not_found", 0) == 1


@pytest.mark.unit
def test_taxonomy_string_to_replace_not_found_is_edit_failed(tmp_path: Path) -> None:
    """'String to replace not found' must land in edit_failed, not file_not_found."""
    errors = _tool_error_session(
        tmp_path,
        "<tool_use_error>String to replace not found in file.\nString: some text here</tool_use_error>",
    )
    assert errors.get("edit_failed", 0) == 1
    assert errors.get("file_not_found", 0) == 0


@pytest.mark.unit
def test_taxonomy_invalid_tool_input_separate_from_command_failed(tmp_path: Path) -> None:
    """invalid_tool_input (agent-side) and command_failed (env-side) must be distinct buckets."""
    import json

    path = tmp_path / "multi.jsonl"
    records = [
        {
            "type": "user",
            "timestamp": "2026-08-01T10:00:00Z",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "t1",
                        "is_error": True,
                        "content": "<tool_use_error>InputValidationError: Read failed.</tool_use_error>",
                    }
                ]
            },
        },
        {
            "type": "user",
            "timestamp": "2026-08-01T10:01:00Z",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "t2",
                        "is_error": True,
                        "content": "Exit code 1\nsome command output",
                    }
                ]
            },
        },
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    result = parse_session(path)
    assert result is not None
    errors = result["tool_errors"]
    assert errors.get("invalid_tool_input", 0) == 1
    assert errors.get("command_failed", 0) == 1
