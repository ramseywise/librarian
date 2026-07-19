#!/usr/bin/env bash
# Cartographer scheduled run.
#
# Two cadences, because the two halves have very different costs:
#   --facts  daily   — capture into the fact table. No API key, cheap. This is the
#                      one that matters: local JSONL rotates out in ~5 days, so a
#                      missed window is history lost for good.
#   --cron   weekly  — LLM friction analysis. Needs ANTHROPIC_API_KEY, costs money.
#
# Scheduling is launchd, not crontab — cron does not fire while the Mac is asleep
# and silently skips the window; launchd re-fires on wake. See
# ~/Library/LaunchAgents/com.wiseer.cartographer.{facts,cron}.plist
#
# Usage: cartographer-cron.sh [facts|cron|both]   (default: facts)

set -euo pipefail

MODE="${1:-facts}"

# Repo root is two levels up from tools/cartographer/ — this was ../../.. back when
# the script lived at src/agents/cartographer/, which resolved above the repo.
REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_FILE="${REPO_DIR}/logs/cartographer-cron.log"

mkdir -p "$(dirname "${LOG_FILE}")"
cd "${REPO_DIR}"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "${LOG_FILE}"; }

log "--- run started (mode=${MODE}, repo=${REPO_DIR})"

# Source env vars (API key) — only --cron needs it, but harmless for both.
if [ -f "${REPO_DIR}/.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "${REPO_DIR}/.env"
    set +a
fi

# Fail loudly to the log rather than dying silently: `set -e` would abort before
# the failure was ever recorded, which is how a broken cron job stays invisible.
run_step() {
    local label="$1"
    shift
    log "running: $*"
    if "$@" >> "${LOG_FILE}" 2>&1; then
        log "${label}: ok"
    else
        local code=$?
        log "${label}: FAILED (exit ${code})"
        return "${code}"
    fi
}

EXIT_CODE=0

case "${MODE}" in
    facts) run_step facts uv run cartographer --facts || EXIT_CODE=$? ;;
    cron)  run_step cron  uv run cartographer --cron  || EXIT_CODE=$? ;;
    both)
        run_step facts uv run cartographer --facts || EXIT_CODE=$?
        run_step cron  uv run cartographer --cron  || EXIT_CODE=$?
        ;;
    *)
        log "unknown mode: ${MODE} (expected facts|cron|both)"
        exit 64
        ;;
esac

log "--- run finished (exit ${EXIT_CODE})"
exit "${EXIT_CODE}"
