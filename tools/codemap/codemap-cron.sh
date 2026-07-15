#!/usr/bin/env bash
# Codemap indexing cron job — reindexes all configured repos unattended.
#
# Setup (one-time, NOT done automatically by this repo):
#   crontab -e
#   */30 * * * * /path/to/repo/tools/codemap/codemap-cron.sh
#
# Requires:
#   - .env in the repo root (if any codemap config needs it later)
#   - uv installed and on PATH
#   - tools/codemap/repos.txt configured with at least one repo

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_FILE="${REPO_DIR}/logs/codemap-cron.log"

cd "${REPO_DIR}"
mkdir -p "${REPO_DIR}/logs"

echo "========================================" >> "${LOG_FILE}"
echo "Run started: $(date '+%Y-%m-%d %H:%M:%S')" >> "${LOG_FILE}"

if [ -f "${REPO_DIR}/.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "${REPO_DIR}/.env"
    set +a
fi

uv run codemap >> "${LOG_FILE}" 2>&1
EXIT_CODE=$?

echo "Run finished: $(date '+%Y-%m-%d %H:%M:%S') (exit ${EXIT_CODE})" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"

exit ${EXIT_CODE}
