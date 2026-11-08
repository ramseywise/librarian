"""Startup checks for the API: configuration that would fail later, said once at the start."""

from __future__ import annotations

from librarian.config import Settings
from librarian.pricing import PRICES, price_for


def is_loopback(host: str) -> bool:
    return host in {"localhost", "::1"} or host.startswith("127.")


def find_problems(
    settings: Settings, *, host: str | None = None, insecure: bool = False
) -> tuple[list[str], list[str]]:
    """(errors, warnings), one line each. The API refuses to start on any error.

    Errors: the wiki or courses directory is missing, the chat model is not in the price table,
    the chat is enabled with no ANTHROPIC_API_KEY, open mode (no login and no LIBRARIAN_API_TOKEN)
    where the API is reachable from outside (public mode, or a non-loopback `host` without
    `insecure`), and a login method without LIBRARIAN_PUBLIC_URL or the session secret. Warnings:
    a non-loopback `host` served open under `insecure`.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not settings.wiki_dir.is_dir():
        errors.append(f"wiki directory missing: {settings.wiki_dir}")
    if not settings.courses_dir.is_dir():
        errors.append(f"courses directory missing: {settings.courses_dir}")
    errors.extend(find_model_problems(settings))
    if settings.chat_enabled and not settings.anthropic_api_key:
        errors.append("ANTHROPIC_API_KEY is not set (or set LIBRARIAN_CHAT_ENABLED=false)")
    if settings.open_mode:
        if settings.public_mode:
            errors.append(
                "neither a login method nor LIBRARIAN_API_TOKEN is set in public mode (LIBRARIAN_PUBLIC)"
            )
        elif host is not None and not is_loopback(host):
            line = f"no login method or LIBRARIAN_API_TOKEN is set and the API binds {host}"
            if insecure:
                warnings.append(f"{line}: serving it open (--insecure)")
            else:
                errors.append(f"{line} (set one, or pass --insecure to serve unauthenticated)")
    errors.extend(find_login_problems(settings))
    return errors, warnings


def find_login_problems(settings: Settings) -> list[str]:
    """A login method needs the URL its links point at, and OAuth a secret to sign its state."""
    methods = settings.login_methods
    if not methods:
        return []
    problems = []
    if not settings.public_url.startswith(("https://", "http://localhost", "http://127.")):
        problems.append(
            "LIBRARIAN_PUBLIC_URL must be the https URL users open (or http://localhost) "
            f"when login is configured ({', '.join(methods)})"
        )
    if set(methods) & {"google", "github"} and len(settings.session_secret) < 32:
        problems.append("LIBRARIAN_SESSION_SECRET must be at least 32 characters for OAuth login")
    return problems


def find_model_problems(settings: Settings) -> list[str]:
    """The configured chat model must be in the price table, or the spend cap cannot count it."""
    if price_for(settings.anthropic_model) is None:
        return [
            f"ANTHROPIC_MODEL {settings.anthropic_model!r} has no entry in the price table "
            f"(librarian.pricing); known: {', '.join(sorted(PRICES))}"
        ]
    return []
