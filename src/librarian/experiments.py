"""Experiments: named variants, one assigned to each user, stably.

`LIBRARIAN_EXPERIMENTS=ranking=control,hybrid-union;prompt=v1,v2` names two experiments. A user's
variant for each is picked by `sha256(user_id + name) mod n`, so it never changes while the list
does not, and users spread evenly without a table. The resolved variants are one string,
`ranking=hybrid-union;prompt=v2`, which goes on every agent log row, feedback row and span; the
`ranking` experiment's `hybrid-union` variant also switches the hybrid candidate path in
`librarian.retrieval.ranking`, which finds it through `librarian.observability.experiment()`.

An admin can pin variants for a request with `X-Librarian-Variant: ranking=hybrid-union`. With no
experiments configured, nothing is assigned and the string is the old process-wide
`LIBRARIAN_EXPERIMENT`. A leaf module, like observability: any layer may use it.
"""

from __future__ import annotations

import hashlib

from librarian.config import Settings
from librarian.observability import experiment as fallback

VARIANT_HEADER = "x-librarian-variant"


def parse(spec: str) -> dict[str, tuple[str, ...]]:
    """`name=a,b;name2=c,d` as {name: (variants,)}. Malformed or empty parts are skipped."""
    found: dict[str, tuple[str, ...]] = {}
    for part in spec.split(";"):
        name, _, variants = part.partition("=")
        choices = tuple(dict.fromkeys(v.strip() for v in variants.split(",") if v.strip()))
        if name.strip() and choices:
            found[name.strip()] = choices
    return found


def pick(user_id: str, name: str, variants: tuple[str, ...]) -> str:
    """The sticky variant of `name` for `user_id`."""
    digest = hashlib.sha256((user_id + name).encode()).digest()
    return variants[int.from_bytes(digest, "big") % len(variants)]


def parse_override(header: str | None, known: dict[str, tuple[str, ...]]) -> dict[str, str]:
    """Pinned variants from the header; names or variants that are not configured are ignored."""
    pinned: dict[str, str] = {}
    for name, variant in ((n.strip(), v.strip()) for n, _, v in _pairs(header or "")):
        if variant in known.get(name, ()):
            pinned[name] = variant
    return pinned


def _pairs(text: str) -> list[tuple[str, str, str]]:
    return [(p.partition("=")) for p in text.split(";") if p.strip()]


def resolve(
    settings: Settings, user_id: str, *, is_admin: bool = False, override: str | None = None
) -> str:
    """The caller's variant string; the process-wide `LIBRARIAN_EXPERIMENT` when none are configured.

    `override` (the header value) applies only to admins, so a member cannot choose a variant.
    """
    known = parse(settings.experiments)
    if not known:
        return fallback()
    pinned = parse_override(override, known) if is_admin else {}
    return ";".join(f"{n}={pinned.get(n) or pick(user_id, n, v)}" for n, v in known.items())
