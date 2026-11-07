#!/bin/sh
# Container entrypoint: validate the configuration, then hand over to the command.
#
# `librarian api --check` exits 1 on a config error (missing token, unreadable data dir, ...), so
# a misconfigured container stops here with the reason on stderr instead of starting half-working.
# The API also gets `librarian db upgrade` (idempotent; replicas serialise on a Postgres advisory lock).
# Only the API gets the check; any other command (`docker run librarian sh`) runs as given.
#
# The private mountpoints (data/wiki/private, data/courses/private) cannot be made here: the data
# mount is read-only and Docker creates tmpfs mountpoints before this script runs.
# docker-compose.yml creates them with its `prepare` service instead.
set -eu

if [ "${1:-}" = "librarian" ] && [ "${2:-}" = "api" ]; then
    librarian api --check
    librarian db upgrade
fi
exec "$@"
