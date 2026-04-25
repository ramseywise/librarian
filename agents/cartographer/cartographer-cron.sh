#!/usr/bin/env bash
# Observer agent cron job — weekly insights analysis.
#
# Setup (one-time):
#   crontab -e
#   0 9 * * 1 /path/to/repo/src/agents/cartographer/cartographer-cron.sh
#
# Requires:
#   - .env in the repo root with ANTHROPIC_API_KEY
#   - uv installed and on PATH

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
LOG_FILE="${REPO_DIR}/logs/cartographer-cron.log"

cd "${REPO_DIR}"

echo "========================================" >> "${LOG_FILE}"
echo "Run started: $(date '+%Y-%m-%d %H:%M:%S')" >> "${LOG_FILE}"

# Source env vars (API key)
if [ -f "${REPO_DIR}/.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "${REPO_DIR}/.env"
    set +a
fi

# Run cron analysis
uv run cartographer --cron >> "${LOG_FILE}" 2>&1
EXIT_CODE=$?

echo "Run finished: $(date '+%Y-%m-%d %H:%M:%S') (exit ${EXIT_CODE})" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"

exit ${EXIT_CODE}
