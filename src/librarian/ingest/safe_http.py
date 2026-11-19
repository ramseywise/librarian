"""An outbound HTTP client that will not connect to internal addresses.

The scrapers, the presenter's image fetch and the release store follow redirects, and a feed, a
bookmark or a bucket can answer with a redirect to `http://169.254.169.254/` or `http://localhost:…`.
`safe_client()` returns an `httpx.Client` whose transport checks every request, the first one and
each redirect hop (httpx hands every hop to the transport):

1. the host is resolved once, here (a literal IP is not resolved);
2. if any resolved address is loopback, private (RFC 1918, ULA), link-local, multicast,
   unspecified, reserved or otherwise not globally routable, the request fails with
   `UnsafeAddressError` (an `httpx.TransportError`, so existing `except httpx.HTTPError` handlers
   treat it as a failed fetch). IPv4-mapped IPv6 addresses are judged as the IPv4 address;
3. the connection is made to the address that was checked, not to the name: the request URL's
   host is replaced by that IP, `Host` stays the original, and the TLS server name (SNI and
   certificate check) is the original host. A second lookup by the connection layer, which a
   rebinding DNS server could answer differently, never happens.

Where an internal address is legitimate, the operator says so explicitly: the caller passes
`allow_private_addresses=True`; the settings `LIBRARIAN_SCRAPE_ALLOW_PRIVATE_ADDRESSES` (scrapers
and the presenter) and `LIBRARIAN_RELEASE_ALLOW_PRIVATE_ADDRESSES` (the release store) feed it.
Allowing private addresses lifts the check for every address, so it is all or nothing per client.

Environment proxies are not used (`trust_env=False`): through a proxy the proxy resolves the name,
which the check could not see.
"""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable, Sequence
from typing import Any

import httpx

# (host, port) -> addresses. Tests pass a fake; the default asks the system resolver.
Resolver = Callable[[str, int], Sequence[str]]

_DEFAULT_PORTS = {"http": 80, "https": 443}
MAX_REDIRECTS = 5


class UnsafeAddressError(httpx.TransportError):
    """The request would reach an address `safe_client` does not allow."""


def system_resolver(host: str, port: int) -> list[str]:
    """Every address the system resolver gives for `host`, as text, in its order."""
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return [str(info[4][0]) for info in infos]


def _parse(address: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    ip = ipaddress.ip_address(address.split("%", 1)[0])  # drop an IPv6 zone id ("fe80::1%en0")
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return ip.ipv4_mapped
    return ip


def blocked_reason(address: str) -> str | None:
    """Why `address` is refused ("loopback", "private", ...), or None if it may be used."""
    ip = _parse(address)
    for reason, hit in (
        ("unspecified", ip.is_unspecified),
        ("loopback", ip.is_loopback),
        ("link-local", ip.is_link_local),
        ("multicast", ip.is_multicast),
        ("private", ip.is_private),
        ("reserved", ip.is_reserved),
        ("not globally routable", not ip.is_global),
    ):
        if hit:
            return reason
    return None


class SafeTransport(httpx.BaseTransport):
    """Resolve, check, then connect to the checked address (see the module docstring)."""

    def __init__(
        self,
        *,
        allow_private_addresses: bool = False,
        resolver: Resolver | None = None,
        inner: httpx.BaseTransport | None = None,
    ) -> None:
        self._allow = allow_private_addresses
        self._resolve = resolver or system_resolver
        self._inner = inner or httpx.HTTPTransport()

    def _addresses(self, host: str, port: int) -> list[str]:
        try:
            ipaddress.ip_address(host)
            literal = True
        except ValueError:
            literal = False
        if literal:
            addresses = [host]
        else:
            try:
                addresses = list(self._resolve(host, port))
            except OSError as exc:
                raise httpx.ConnectError(f"cannot resolve {host}: {exc}") from exc
        if not addresses:
            raise httpx.ConnectError(f"cannot resolve {host}: no addresses")
        if not self._allow:
            for address in addresses:
                reason = blocked_reason(address)
                if reason:
                    raise UnsafeAddressError(
                        f"refusing {host}: it resolves to {address} ({reason}). "
                        "An operator can allow internal addresses with "
                        "LIBRARIAN_SCRAPE_ALLOW_PRIVATE_ADDRESSES or "
                        "LIBRARIAN_RELEASE_ALLOW_PRIVATE_ADDRESSES."
                    )
        return addresses

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        host = request.url.host
        port = request.url.port or _DEFAULT_PORTS.get(request.url.scheme, 0)
        last: httpx.ConnectError | httpx.ConnectTimeout | None = None
        for address in self._addresses(host, port):
            pinned = httpx.Request(
                request.method,
                request.url.copy_with(host=address.split("%", 1)[0]),
                headers=request.headers,  # Host stays the original name
                stream=request.stream,
                extensions={**request.extensions, "sni_hostname": host},
            )
            try:
                return self._inner.handle_request(pinned)
            except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
                last = exc  # try the next address of the same name
        raise last if last is not None else httpx.ConnectError(f"cannot connect to {host}")

    def close(self) -> None:
        self._inner.close()


def safe_client(
    *,
    allow_private_addresses: bool | None = None,
    resolver: Resolver | None = None,
    transport: httpx.BaseTransport | None = None,
    **client_kwargs: Any,  # noqa: ANN401 - passed to httpx.Client (timeout, headers, ...)
) -> httpx.Client:
    """An `httpx.Client` that checks and pins every address it connects to; follows redirects.

    `allow_private_addresses` None means the `scrape_allow_private_addresses` setting. `resolver`
    and `transport` (the layer that really sends) are for tests. Other keyword arguments go to
    `httpx.Client`.
    """
    if allow_private_addresses is None:
        from librarian.config import get_settings

        allow_private_addresses = get_settings().scrape_allow_private_addresses
    client_kwargs.setdefault("follow_redirects", True)
    client_kwargs.setdefault("max_redirects", MAX_REDIRECTS)
    return httpx.Client(
        transport=SafeTransport(
            allow_private_addresses=allow_private_addresses, resolver=resolver, inner=transport
        ),
        trust_env=False,
        **client_kwargs,
    )
