#!/usr/bin/env bash
# End-to-end tests against the built image, used by `make e2e-container` and CI.
#
#   IMAGE          image to run (default librarian:e2e; built from Dockerfile unless SKIP_BUILD=1)
#   E2E_PORT       host port (default 8010, so a dev API on :8000 is left alone)
#   READY_TIMEOUT  seconds to wait for /readyz (default 900: the first start builds the index, ~150 s)
#   KEEP=1         leave the container running afterwards
#
# Mirrors docker-compose.yml: ./data read-only, tmpfs masks over both private dirs, a fresh
# state volume, the token from the environment.
set -euo pipefail

cd "$(dirname "$0")/../.."
IMAGE="${IMAGE:-librarian:e2e}"
PORT="${E2E_PORT:-8010}"
NAME="librarian-e2e"
VOLUME="librarian-e2e-var"
TIMEOUT="${READY_TIMEOUT:-900}"
export E2E_TOKEN="${E2E_TOKEN:-e2e-$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')}"
export E2E_API_URL="http://localhost:${PORT}"
export E2E_UI_URL="${E2E_API_URL}"

cleanup() {
    status=$?
    if [ "${status}" -ne 0 ]; then
        echo "--- container logs (tail)"
        docker logs --tail 80 "${NAME}" 2>&1 || true
    fi
    if [ "${KEEP:-0}" != "1" ]; then
        docker rm -f "${NAME}" >/dev/null 2>&1 || true
        docker volume rm "${VOLUME}" >/dev/null 2>&1 || true
    fi
    exit "${status}"
}
trap cleanup EXIT

if [ "${SKIP_BUILD:-0}" != "1" ]; then
    docker build -f Dockerfile -t "${IMAGE}" .
fi

docker rm -f "${NAME}" >/dev/null 2>&1 || true
docker volume rm "${VOLUME}" >/dev/null 2>&1 || true
# Docker cannot create a tmpfs mountpoint inside a read-only bind mount, so the two private
# directories must exist on the host. On a clean clone they do not (both are gitignored and empty
# here), and `docker compose up` fails the same way: see the PR notes.
mkdir -p data/wiki/private data/courses/private
docker run -d --name "${NAME}" -p "${PORT}:8000" \
    -e LIBRARIAN_API_TOKEN="${E2E_TOKEN}" \
    -v "$PWD/data:/app/data:ro" \
    -v "${VOLUME}:/app/var" \
    --tmpfs /app/data/wiki/private \
    --tmpfs /app/data/courses/private \
    "${IMAGE}" >/dev/null

echo "waiting for /readyz on ${E2E_API_URL} (up to ${TIMEOUT}s)"
deadline=$((SECONDS + TIMEOUT))
until curl -fsS -o /dev/null "${E2E_API_URL}/readyz" 2>/dev/null; do
    if [ "$(docker inspect -f '{{.State.Running}}' "${NAME}")" != "true" ]; then
        echo "container exited before it was ready" >&2
        exit 1
    fi
    if [ "${SECONDS}" -ge "${deadline}" ]; then
        echo "not ready after ${TIMEOUT}s" >&2
        exit 1
    fi
    sleep 5
done
echo "ready after ${SECONDS}s"

# The auth gate, probes and bundled UI; then two of the existing browser smoke tests.
uv run pytest tests/e2e/test_container.py \
    "tests/e2e/test_ui_smoke.py::test_graph_tab" \
    "tests/e2e/test_ui_smoke.py::test_courses_tab_and_concept_jump" \
    -m e2e -v
