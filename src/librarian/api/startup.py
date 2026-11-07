"""Startup checks for the API: configuration that would fail later, said once at the start."""

from __future__ import annotations

from librarian.config import Settings


def find_problems(settings: Settings) -> tuple[list[str], list[str]]:
    """(errors, warnings), one line each.

    A missing ANTHROPIC_API_KEY is a warning, not an error: only the chat route needs it and it
    already answers with a clear failure, while the rest of the API (and every test run
    without a key) works.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not settings.wiki_dir.is_dir():
        errors.append(f"wiki directory missing: {settings.wiki_dir}")
    if not settings.courses_dir.is_dir():
        errors.append(f"courses directory missing: {settings.courses_dir}")
    for name, value in (
        ("LIBRARIAN_CHAT_INPUT_USD_PER_MTOK", settings.chat_input_usd_per_mtok),
        ("LIBRARIAN_CHAT_OUTPUT_USD_PER_MTOK", settings.chat_output_usd_per_mtok),
    ):
        if value <= 0:
            errors.append(f"{name} must be above 0, got {value}")
    if not settings.anthropic_api_key:
        warnings.append("ANTHROPIC_API_KEY is not set: /api/chat/stream will fail")
    return errors, warnings
