"""Content releases: the wiki, courses, built slides and search index as one verified package.

CI builds `content-<sha>.tar.zst` from a tag (`package`), uploads it next to its `.sha256` and
then rewrites `latest` (`store`). A running API pulls the release `latest` names (or the pinned
one), checks the checksum, unpacks it beside the previous ones and swaps two symlinks: the
content tree and the index (`install`). Nothing restarts; every worker reads through the
symlinks, so all of them serve the new release within a few seconds.

Layout under the state dir (`var/`):

    content/releases/<name>/     manifest.json, wiki/, courses/, slides/, index/<id>.duckdb
    content/current              -> releases/<name>   (what the API serves)
    content/pin                  a release name: pulls stop following `latest`
    index/<id>.duckdb, current   the index file, as `librarian index build` lays it out
"""

from __future__ import annotations

from librarian.release.install import (
    InstallResult,
    ReleaseError,
    current_manifest,
    current_name,
    list_releases,
    pin,
    pinned,
    pull,
    unpin,
)

__all__ = [
    "InstallResult",
    "ReleaseError",
    "current_manifest",
    "current_name",
    "list_releases",
    "pin",
    "pinned",
    "pull",
    "unpin",
]
