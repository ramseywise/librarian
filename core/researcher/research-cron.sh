#!/usr/bin/env bash
# Research agent batch processor — intended for crontab at 4am daily.
#
# Setup (one-time):
#   crontab -e
#   0 4 * * * /path/to/repo/scripts/research-cron.sh
#
# Requires:
#   - .env in the repo root with ANTHROPIC_API_KEY
#   - uv installed and on PATH
#   - pdftotext/pdfinfo installed (poppler)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="${REPO_DIR}/logs/research-cron.log"

# --- Token / cost limits ---
# Max PDFs to process per cron run (each PDF = ~3 API calls)
MAX_PDFS="${RESEARCH_CRON_MAX_PDFS:-5}"
# Max tokens per API call (controls output length)
MAX_TOKENS="${RESEARCH_CRON_MAX_TOKENS:-4096}"

cd "${REPO_DIR}"

# Timestamp the run
echo "========================================" >> "${LOG_FILE}"
echo "Run started: $(date '+%Y-%m-%d %H:%M:%S')" >> "${LOG_FILE}"
echo "Limits: max_pdfs=${MAX_PDFS}, max_tokens=${MAX_TOKENS}" >> "${LOG_FILE}"

# Source env vars (API key, path overrides)
if [ -f "${REPO_DIR}/.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "${REPO_DIR}/.env"
    set +a
fi

# Export limits for the batch runner
export RESEARCH_CRON_MAX_PDFS="${MAX_PDFS}"
export RESEARCH_CRON_MAX_TOKENS="${MAX_TOKENS}"

# Run batch processing with PDF limit
uv run research-agent --batch --max-pdfs "${MAX_PDFS}" >> "${LOG_FILE}" 2>&1
EXIT_CODE=$?

echo "Run finished: $(date '+%Y-%m-%d %H:%M:%S') (exit ${EXIT_CODE})" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"

exit ${EXIT_CODE}
