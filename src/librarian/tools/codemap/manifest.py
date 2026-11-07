"""Codemap content hashing.

Change tracking lives in the DB (``files.content_hash``), not in a separate manifest
file: a second store could drift from the DB (deleting one left the index empty forever)
and rewriting it per file was O(n^2). This module only provides the hash.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def file_hash(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{h[:16]}"
