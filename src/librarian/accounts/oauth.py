"""Sign-in with Google or GitHub: the OAuth authorization-code flow with PKCE.

The API builds the redirect (`authorize_url`) and, on the callback, trades the code for a token
and asks the provider who signed in (`identity`). Only an email the provider says is verified is
returned; the caller decides whether that email may sign in. A provider is enabled when its
client id and secret are both set (`Settings.login_methods`).

Authlib supplies the PKCE challenge and the random verifier. The two HTTP calls are plain httpx:
Authlib's own client runs on the `httpx2` fork, which would put a second HTTP stack in the API.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx
from authlib.common.security import generate_token
from authlib.common.urls import add_params_to_uri
from authlib.oauth2.rfc7636 import create_s256_code_challenge

from librarian.config import Settings

TIMEOUT_S = 10.0
# Tests replace this with an httpx.MockTransport; None is the real network.
transport: httpx.BaseTransport | None = None


class OAuthError(RuntimeError):
    """The provider refused the code or did not return a verified email."""


@dataclass(frozen=True)
class Identity:
    email: str
    name: str | None


@dataclass(frozen=True)
class Provider:
    name: str
    authorize_endpoint: str
    token_endpoint: str
    scope: str
    who: Callable[[httpx.Client], Identity]
    client_id: Callable[[Settings], str]
    client_secret: Callable[[Settings], str]


def _get(client: httpx.Client, url: str) -> Any:  # noqa: ANN401 (provider JSON)
    resp = client.get(url)
    if resp.status_code != 200:
        raise OAuthError(f"{url} answered {resp.status_code}")
    return resp.json()


def _google(client: httpx.Client) -> Identity:
    info = _get(client, "https://openidconnect.googleapis.com/v1/userinfo")
    if not info.get("email") or info.get("email_verified") is not True:
        raise OAuthError("Google returned no verified email")
    return Identity(info["email"], info.get("name"))


def _github(client: httpx.Client) -> Identity:
    user = _get(client, "https://api.github.com/user")
    emails = _get(client, "https://api.github.com/user/emails")
    verified = [e for e in emails if e.get("verified") and e.get("email")]
    chosen = next((e for e in verified if e.get("primary")), None)
    if chosen is None:
        raise OAuthError("GitHub returned no verified primary email")
    return Identity(chosen["email"], user.get("name") or user.get("login"))


PROVIDERS: dict[str, Provider] = {
    "google": Provider(
        "google",
        "https://accounts.google.com/o/oauth2/v2/auth",
        "https://oauth2.googleapis.com/token",
        "openid email profile",
        _google,
        lambda s: s.google_client_id,
        lambda s: s.google_client_secret,
    ),
    "github": Provider(
        "github",
        "https://github.com/login/oauth/authorize",
        "https://github.com/login/oauth/access_token",
        "read:user user:email",
        _github,
        lambda s: s.github_client_id,
        lambda s: s.github_client_secret,
    ),
}


def new_verifier() -> str:
    return generate_token(48)


def authorize_url(
    provider: Provider, settings: Settings, redirect_uri: str, state: str, verifier: str
) -> str:
    return add_params_to_uri(
        provider.authorize_endpoint,
        [
            ("response_type", "code"),
            ("client_id", provider.client_id(settings)),
            ("redirect_uri", redirect_uri),
            ("scope", provider.scope),
            ("state", state),
            ("code_challenge", create_s256_code_challenge(verifier)),
            ("code_challenge_method", "S256"),
        ],
    )


def _token(client: httpx.Client, provider: Provider, settings: Settings, **form: str) -> str:
    resp = client.post(
        provider.token_endpoint,
        data={
            "grant_type": "authorization_code",
            "client_id": provider.client_id(settings),
            "client_secret": provider.client_secret(settings),
            **form,
        },
    )
    # GitHub answers a refused code with 200 and an "error" field.
    body = (
        resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
    )
    token = body.get("access_token")
    if resp.status_code != 200 or not token:
        raise OAuthError(
            f"{provider.name} refused the code ({resp.status_code}, {body.get('error')})"
        )
    return token


def identity(
    provider: Provider, settings: Settings, redirect_uri: str, code: str, verifier: str
) -> Identity:
    """Trade `code` for a token and return the verified email behind it; OAuthError otherwise."""
    headers = {"Accept": "application/json"}
    try:
        with httpx.Client(timeout=TIMEOUT_S, transport=transport, headers=headers) as client:
            token = _token(
                client,
                provider,
                settings,
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=verifier,
            )
            client.headers["Authorization"] = f"Bearer {token}"
            return provider.who(client)
    except (httpx.HTTPError, ValueError) as e:  # ValueError: a body that is not JSON
        raise OAuthError(f"{provider.name} unreachable or garbled: {e}") from e


__all__ = [
    "PROVIDERS",
    "Identity",
    "OAuthError",
    "Provider",
    "authorize_url",
    "identity",
    "new_verifier",
]
