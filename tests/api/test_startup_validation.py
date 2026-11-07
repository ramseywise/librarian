"""F19: each startup problem is named on one line, and the API refuses to start on any of them."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import librarian.api.main as main_module
from librarian.api.startup import find_problems
from librarian.config import Settings, get_settings


def _settings(tmp_path: Path, **overrides: object) -> Settings:
    (tmp_path / "wiki").mkdir(exist_ok=True)
    (tmp_path / "courses").mkdir(exist_ok=True)
    base: dict[str, object] = {
        "override_wiki_dir": tmp_path / "wiki",
        "override_courses_dir": tmp_path / "courses",
        "anthropic_api_key": "sk-test",
        "api_token": "",
        "public_mode": False,
        "chat_enabled": True,
        "anthropic_model": "claude-sonnet-5-5",
    }
    return Settings(**{**base, **overrides})  # type: ignore[arg-type]


def test_a_clean_configuration_has_no_problems(tmp_path: Path) -> None:
    assert find_problems(_settings(tmp_path)) == ([], [])


def test_missing_api_key_is_an_error_when_chat_is_enabled(tmp_path: Path) -> None:
    errors, _ = find_problems(_settings(tmp_path, anthropic_api_key=""))
    assert len(errors) == 1 and "ANTHROPIC_API_KEY" in errors[0]


def test_missing_api_key_is_fine_when_chat_is_disabled(tmp_path: Path) -> None:
    assert find_problems(_settings(tmp_path, anthropic_api_key="", chat_enabled=False)) == ([], [])


def test_missing_wiki_directory(tmp_path: Path) -> None:
    errors, _ = find_problems(_settings(tmp_path, override_wiki_dir=tmp_path / "nope"))
    assert len(errors) == 1 and "wiki directory missing" in errors[0]


def test_missing_courses_directory(tmp_path: Path) -> None:
    errors, _ = find_problems(_settings(tmp_path, override_courses_dir=tmp_path / "nope"))
    assert len(errors) == 1 and "courses directory missing" in errors[0]


def test_chat_model_must_be_in_the_price_table(tmp_path: Path) -> None:
    errors, _ = find_problems(_settings(tmp_path, anthropic_model="claude-nope"))
    assert len(errors) == 1 and "price table" in errors[0]


def test_token_is_required_in_public_mode(tmp_path: Path) -> None:
    errors, _ = find_problems(_settings(tmp_path, public_mode=True))
    assert len(errors) == 1 and "LIBRARIAN_API_TOKEN" in errors[0]
    assert find_problems(_settings(tmp_path, public_mode=True, api_token="t")) == ([], [])


def test_token_is_required_off_loopback(tmp_path: Path) -> None:
    errors, _ = find_problems(_settings(tmp_path), host="0.0.0.0")
    assert len(errors) == 1 and "LIBRARIAN_API_TOKEN" in errors[0] and "0.0.0.0" in errors[0]
    assert find_problems(_settings(tmp_path, api_token="t"), host="0.0.0.0") == ([], [])


def test_loopback_needs_no_token(tmp_path: Path) -> None:
    for host in ("127.0.0.1", "localhost", "::1"):
        assert find_problems(_settings(tmp_path), host=host) == ([], [])


def test_insecure_turns_the_off_loopback_error_into_a_warning(tmp_path: Path) -> None:
    errors, warnings = find_problems(_settings(tmp_path), host="0.0.0.0", insecure=True)
    assert errors == [] and len(warnings) == 1


def test_every_problem_gets_its_own_line(tmp_path: Path) -> None:
    s = _settings(
        tmp_path,
        anthropic_api_key="",
        override_wiki_dir=tmp_path / "nope",
        anthropic_model="claude-nope",
        public_mode=True,
    )
    errors, _ = find_problems(s)
    assert len(errors) == 4 and all("\n" not in e for e in errors)


@pytest.fixture()
def fresh_settings() -> Iterator[pytest.MonkeyPatch]:
    mp = pytest.MonkeyPatch()
    get_settings.cache_clear()
    yield mp
    mp.undo()
    get_settings.cache_clear()


def test_the_api_exits_at_startup_on_a_problem(
    fresh_settings: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Not only under `--check`: entering the lifespan (uvicorn startup) raises."""
    fresh_settings.setenv("WIKI_DIR", str(tmp_path / "missing"))
    with pytest.raises(RuntimeError, match="wiki directory missing"), TestClient(main_module.app):
        pass


def test_the_api_exits_at_startup_without_a_key_while_chat_is_enabled(
    fresh_settings: pytest.MonkeyPatch,
) -> None:
    fresh_settings.setenv("ANTHROPIC_API_KEY", "")
    fresh_settings.setenv("LIBRARIAN_CHAT_ENABLED", "true")
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"), TestClient(main_module.app):
        pass


def test_the_disabled_chat_route_is_404(fresh_settings: pytest.MonkeyPatch) -> None:
    fresh_settings.setenv("ANTHROPIC_API_KEY", "")
    fresh_settings.setenv("LIBRARIAN_CHAT_ENABLED", "false")
    with TestClient(main_module.app) as client:
        assert client.post("/api/chat/stream", json={"query": "hi"}).status_code == 404
