"""safe_client: refuses internal addresses on every hop, connects to the address it checked.

A fake resolver and a mocked transport stand in for DNS and the network.
"""

# ruff: noqa: SIM117 - nested `with` keeps the client and the expected error separate
from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest

from librarian.config import get_settings
from librarian.ingest import safe_http
from librarian.ingest.base import safe_client as base_safe_client
from librarian.ingest.safe_http import UnsafeAddressError, blocked_reason, safe_client

PUBLIC = "93.184.216.34"


def _resolver(table: dict[str, list[str]], calls: list[str] | None = None) -> safe_http.Resolver:
    def resolve(host: str, port: int) -> list[str]:
        if calls is not None:
            calls.append(host)
        return table[host]

    return resolve


def _client(
    table: dict[str, list[str]],
    handler: Callable[[httpx.Request], httpx.Response],
    calls: list[str] | None = None,
    **kw: bool,
) -> httpx.Client:
    return safe_client(
        resolver=_resolver(table, calls), transport=httpx.MockTransport(handler), **kw
    )


def test_base_reexports_the_client() -> None:
    assert base_safe_client is safe_client


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "127.8.8.8",
        "10.0.0.5",
        "172.16.0.1",
        "192.168.1.1",
        "169.254.169.254",
        "224.0.0.1",
        "0.0.0.0",
        "100.64.0.1",
        "::1",
        "::",
        "fe80::1",
        "fe80::1%en0",
        "fc00::1",
        "fd12:3456::1",
        "ff02::1",
        "::ffff:127.0.0.1",
        "::ffff:10.1.2.3",
        "::ffff:169.254.169.254",
    ],
)
def test_internal_addresses_are_blocked(address: str) -> None:
    assert blocked_reason(address)


@pytest.mark.parametrize("address", [PUBLIC, "8.8.8.8", "2606:4700:4700::1111", "::ffff:8.8.8.8"])
def test_public_addresses_pass(address: str) -> None:
    assert blocked_reason(address) is None


def test_public_host_is_fetched_at_the_checked_address() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, text="ok")

    calls: list[str] = []
    with _client({"feed.example": [PUBLIC]}, handler, calls) as client:
        assert client.get("https://feed.example/rss").text == "ok"
    [req] = seen
    assert req.url.host == PUBLIC  # connects to the address that was checked
    assert req.headers["host"] == "feed.example"  # the name is kept for the server
    assert req.extensions["sni_hostname"] == "feed.example"  # and for the TLS check
    assert calls == ["feed.example"]  # resolved once


@pytest.mark.parametrize(
    "address", ["127.0.0.1", "10.1.1.1", "169.254.169.254", "0.0.0.0", "::1", "fe80::1", "ff02::1"]
)
def test_first_request_to_an_internal_name_is_refused(address: str) -> None:
    sent: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(200)

    with _client({"evil.example": [address]}, handler) as client:
        with pytest.raises(UnsafeAddressError, match=r"evil\.example"):
            client.get("https://evil.example/")
    assert sent == []


def test_literal_ip_urls_are_checked_without_a_lookup() -> None:
    calls: list[str] = []
    with _client({}, lambda r: httpx.Response(200), calls) as client:
        for url in ("http://127.0.0.1:8000/", "http://[::1]/", "http://[::ffff:10.0.0.1]/"):
            with pytest.raises(UnsafeAddressError):
                client.get(url)
        assert client.get(f"http://{PUBLIC}/").status_code == 200
    assert calls == []


def test_one_bad_address_among_good_ones_refuses_the_name() -> None:
    with _client({"mixed.example": [PUBLIC, "10.0.0.9"]}, lambda r: httpx.Response(200)) as c:
        with pytest.raises(UnsafeAddressError):
            c.get("https://mixed.example/")


def test_every_redirect_hop_is_checked() -> None:
    sent: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request.headers["host"])
        if request.headers["host"] == "a.example":
            return httpx.Response(302, headers={"location": "https://b.example/next"})
        if request.headers["host"] == "b.example":
            return httpx.Response(302, headers={"location": "http://metadata.example/latest"})
        return httpx.Response(200, text="secret")

    table = {
        "a.example": [PUBLIC],
        "b.example": ["8.8.8.8"],
        "metadata.example": ["169.254.169.254"],
    }
    with _client(table, handler) as client:
        with pytest.raises(UnsafeAddressError, match=r"metadata\.example"):
            client.get("https://a.example/")
    assert sent == ["a.example", "b.example"]  # the internal hop was never sent


def test_redirect_to_a_literal_internal_ip_is_refused() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(301, headers={"location": "http://127.0.0.1:9200/_cat"})

    with _client({"a.example": [PUBLIC]}, handler) as client, pytest.raises(UnsafeAddressError):
        client.get("https://a.example/")


def test_a_public_redirect_chain_is_followed_and_pinned_per_hop() -> None:
    hosts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        if request.url.path == "/":
            return httpx.Response(302, headers={"location": "https://b.example/final"})
        return httpx.Response(200, text="done")

    table = {"a.example": [PUBLIC], "b.example": ["8.8.4.4"]}
    with _client(table, handler) as client:
        assert client.get("https://a.example/").text == "done"
    assert hosts == [PUBLIC, "8.8.4.4"]


def test_a_rebinding_answer_cannot_change_the_connected_address() -> None:
    """The resolver answers differently each time: the first (checked) answer is the one used."""
    answers = iter([[PUBLIC], ["127.0.0.1"]])
    seen: list[str] = []

    def resolve(host: str, port: int) -> list[str]:
        return next(answers)

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.host)
        return httpx.Response(200)

    with safe_client(resolver=resolve, transport=httpx.MockTransport(handler)) as client:
        client.get("https://rebind.example/")
    assert seen == [PUBLIC]


def test_unresolvable_name_is_a_connect_error() -> None:
    def resolve(host: str, port: int) -> list[str]:
        raise OSError("no such host")

    with safe_client(
        resolver=resolve, transport=httpx.MockTransport(lambda r: httpx.Response(200))
    ) as c:
        with pytest.raises(httpx.ConnectError):
            c.get("https://nowhere.example/")


def test_refusal_is_an_httpx_error_so_scrapers_treat_it_as_a_failed_fetch() -> None:
    assert issubclass(UnsafeAddressError, httpx.HTTPError)


def test_operator_override_allows_internal_addresses() -> None:
    with _client(
        {"minio.internal": ["10.0.0.7"]},
        lambda r: httpx.Response(200, text="bucket"),
        allow_private_addresses=True,
    ) as client:
        assert client.get("http://minio.internal/latest").text == "bucket"


def test_setting_feeds_the_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_SCRAPE_ALLOW_PRIVATE_ADDRESSES", "1")
    get_settings.cache_clear()
    try:
        with _client({"wiki.internal": ["192.168.0.4"]}, lambda r: httpx.Response(200)) as c:
            assert c.get("https://wiki.internal/").status_code == 200
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()
    with _client({"wiki.internal": ["192.168.0.4"]}, lambda r: httpx.Response(200)) as c:
        with pytest.raises(UnsafeAddressError):
            c.get("https://wiki.internal/")


def test_environment_proxies_are_not_used(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.invalid:3128")
    with _client({"a.example": [PUBLIC]}, lambda r: httpx.Response(200)) as client:
        assert client.get("https://a.example/").status_code == 200


def test_connect_failure_falls_through_to_the_next_address() -> None:
    attempts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request.url.host)
        if request.url.host == PUBLIC:
            raise httpx.ConnectError("down", request=request)
        return httpx.Response(200)

    with _client({"two.example": [PUBLIC, "8.8.8.8"]}, handler) as client:
        assert client.get("https://two.example/").status_code == 200
    assert attempts == [PUBLIC, "8.8.8.8"]


def test_call_sites_use_the_safe_client() -> None:
    """The five fetchers no longer build a bare redirect-following client."""
    from pathlib import Path

    root = Path(safe_http.__file__).resolve().parents[1]
    for rel in (
        "ingest/scrape_feeds.py",
        "ingest/scrape_arxiv.py",
        "ingest/scrape_bookmarks.py",
        "tools/presenter/providers.py",
        "release/store.py",
    ):
        text = (root / rel).read_text()
        assert "follow_redirects=True" not in text, rel
        assert "httpx.Client(" not in text, rel
        assert "safe_client(" in text, rel
