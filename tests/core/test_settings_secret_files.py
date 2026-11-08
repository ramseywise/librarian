"""`<NAME>_FILE` for every secret setting: read from the file, newline stripped, loud on error."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import AliasChoices

from librarian.config import SECRET_FIELDS, SecretFileError, Settings


def _alias(field: str) -> str:
    alias = Settings.model_fields[field].validation_alias
    assert isinstance(alias, AliasChoices)
    return str(alias.choices[0])


@pytest.fixture(autouse=True)
def _clean(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for f in SECRET_FIELDS:
        monkeypatch.delenv(_alias(f), raising=False)
        monkeypatch.delenv(f"{_alias(f)}_FILE", raising=False)
    monkeypatch.setitem(Settings.model_config, "env_file", str(tmp_path / "no.env"))


@pytest.mark.parametrize("field", SECRET_FIELDS)
def test_every_secret_setting_reads_its_file(
    field: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = tmp_path / "secret"
    f.write_text("s3cret-value\n")
    monkeypatch.setenv(f"{_alias(field)}_FILE", str(f))
    assert getattr(Settings(), field) == "s3cret-value"


def test_only_trailing_newlines_are_stripped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = tmp_path / "secret"
    f.write_text("  has spaces  \r\n\n")
    monkeypatch.setenv("LIBRARIAN_SESSION_SECRET_FILE", str(f))
    assert Settings().session_secret == "  has spaces  "


def test_plain_env_still_works(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", "plain")
    assert Settings().api_token == "plain"


def test_both_forms_is_an_error_that_names_the_variable_not_the_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = tmp_path / "secret"
    f.write_text("from-file")
    monkeypatch.setenv("RESEND_API_KEY_FILE", str(f))
    monkeypatch.setenv("RESEND_API_KEY", "from-env-xyz")
    with pytest.raises(SecretFileError, match="RESEND_API_KEY or RESEND_API_KEY_FILE") as e:
        Settings()
    assert "from-env-xyz" not in str(e.value) and "from-file" not in str(e.value)


def test_an_unreadable_file_is_an_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY_FILE", str(tmp_path / "missing"))
    with pytest.raises(SecretFileError, match="ANTHROPIC_API_KEY_FILE"):
        Settings()


def test_the_file_form_is_read_from_the_dotenv_file_too(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    secret = tmp_path / "secret"
    secret.write_text("dotenv-file-value\n")
    env = tmp_path / "x.env"
    env.write_text(f"LIBRARIAN_METRICS_TOKEN_FILE={secret}\n")
    monkeypatch.setitem(Settings.model_config, "env_file", str(env))
    assert Settings().metrics_token == "dotenv-file-value"


def test_an_empty_file_form_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN_FILE", "")
    assert Settings().api_token == ""
