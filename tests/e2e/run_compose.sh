#!/usr/bin/env bash
# End-to-end over the whole compose stack: Caddy (TLS) in front of N API replicas on Postgres.
# Used by `make e2e-compose`. This is the phase 2 check: every replica serves, and the e2e set
# passes through the proxy.
#
#   REPLICAS        API containers (default 2), each running LIBRARIAN_API_WORKERS workers (default 2)
#   E2E_HTTPS_PORT  host port for Caddy's 443 (default 8443, so a running stack on 443 is left alone)
#   READY_TIMEOUT   seconds to wait for /readyz (default 900: the indexer builds first)
#   SKIP_BUILD=1    use the librarian:local image as it is
#   KEEP=1          leave the stack running afterwards
#
# Runs as its own compose project (librarian-e2e), so its Postgres and state volumes are fresh
# and are removed afterwards; the default project's are never touched.
set -euo pipefail

cd "$(dirname "$0")/../.."
REPLICAS="${REPLICAS:-2}"
TIMEOUT="${READY_TIMEOUT:-900}"
export LIBRARIAN_HTTPS_PORT="${E2E_HTTPS_PORT:-8443}"
export LIBRARIAN_HTTP_PORT="${E2E_HTTP_PORT:-8080}"
export LIBRARIAN_DOMAIN=localhost
export E2E_TOKEN="${E2E_TOKEN:-e2e-$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')}"
export LIBRARIAN_API_TOKEN="${E2E_TOKEN}"
export E2E_API_URL="https://localhost:${LIBRARIAN_HTTPS_PORT}"
COMPOSE=(docker compose -p librarian-e2e)
CA="$(mktemp -d)/caddy-root.crt"

cleanup() {
    status=$?
    if [ "${status}" -ne 0 ]; then
        echo "--- logs (tail)"
        "${COMPOSE[@]}" logs --tail 40 indexer librarian caddy 2>&1 || true
    fi
    if [ "${KEEP:-0}" != "1" ]; then
        "${COMPOSE[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
    fi
    exit "${status}"
}
trap cleanup EXIT

if [ "${SKIP_BUILD:-0}" != "1" ]; then
    "${COMPOSE[@]}" build librarian
fi
mkdir -p data/wiki/private data/courses/private
"${COMPOSE[@]}" up -d --scale "librarian=${REPLICAS}"

echo "waiting for /readyz on ${E2E_API_URL} (up to ${TIMEOUT}s)"
deadline=$((SECONDS + TIMEOUT))
until curl -fsSk -o /dev/null "${E2E_API_URL}/readyz" 2>/dev/null; do
    if [ "${SECONDS}" -ge "${deadline}" ]; then
        echo "not ready after ${TIMEOUT}s" >&2
        exit 1
    fi
    sleep 5
done
echo "ready after ${SECONDS}s"

# Trust Caddy's internal CA, so the tests check the certificate instead of skipping verification.
"${COMPOSE[@]}" cp caddy:/data/caddy/pki/authorities/local/root.crt "${CA}" >/dev/null
export SSL_CERT_FILE="${CA}"

uv run pytest tests/e2e/test_container.py -m e2e -v

# Enough requests through the proxy that round robin reaches every replica, then check each
# one logged some (the request log line is the API's own, one per request).
for _ in $(seq 40); do
    curl -fsS --cacert "${CA}" -o /dev/null -H "Authorization: Bearer ${E2E_TOKEN}" \
        "${E2E_API_URL}/api/wiki/health"
done
served=0
for id in $("${COMPOSE[@]}" ps -q librarian); do
    n=$(docker logs "${id}" 2>&1 | grep -c '"http.request"' || true)
    echo "replica ${id:0:12}: ${n} requests"
    [ "${n}" -gt 0 ] && served=$((served + 1))
done
if [ "${served}" -ne "${REPLICAS}" ]; then
    echo "only ${served} of ${REPLICAS} replicas served requests" >&2
    exit 1
fi
echo "all ${REPLICAS} replicas served requests"
