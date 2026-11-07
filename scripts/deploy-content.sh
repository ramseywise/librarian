#!/usr/bin/env bash
# Push data/wiki and data/courses to a deployed host, never anything under private/, then restart.
#
#   DEPLOY_HOST=user@host DEPLOY_PATH=/srv/librarian make deploy-content
#
# DEPLOY_PATH is the compose project directory on the host; the content lands in its data/.
# Safety, in order:
#   1. rsync runs with --exclude 'private/' (override only in tests via DEPLOY_EXCLUDE).
#   2. A dry run (--itemize-changes) lists everything the transfer would touch; any path with a
#      private/ component aborts before a byte moves. This is the guard against a broken exclude.
#   3. After the transfer, the destination is searched for files under any private/ directory;
#      one hit fails the deploy (docker's empty private mountpoints there are ignored).
#   4. Only then `docker compose restart librarian` on the host.
#
# Built slides: the locally built var/slides/ (DEPLOY_SLIDES_SRC) goes to $DEPLOY_PATH/content/slides/
# (DEPLOY_SLIDES_DEST), mounted in the container as var/content/current/slides, which the API serves.
# The API never builds decks in production. Same exclude, dry-run guard and post-check as above.
#
# Test hooks: DEPLOY_LOCAL=1 treats DEPLOY_PATH as a local directory (no ssh) and skips the
# restart; DEPLOY_SRC points at a fake repo root.
set -euo pipefail

: "${DEPLOY_HOST:?DEPLOY_HOST is not set (e.g. user@host); refusing to deploy}"
: "${DEPLOY_PATH:?DEPLOY_PATH is not set (the compose directory on the host); refusing to deploy}"

SRC_ROOT="${DEPLOY_SRC:-$(cd "$(dirname "$0")/.." && pwd)}"
SERVICE="${DEPLOY_SERVICE:-librarian}"
LOCAL_MODE="${DEPLOY_LOCAL:-0}"      # 1 = DEPLOY_PATH is a local directory (tests)
RESTART="${DEPLOY_RESTART:-1}"
TRANSFER_LIST="$(mktemp)"
trap 'rm -f "$TRANSFER_LIST"' EXIT

if [ "$LOCAL_MODE" = "1" ]; then
    DEST_ROOT="$DEPLOY_PATH"
else
    DEST_ROOT="$DEPLOY_HOST:$DEPLOY_PATH"
fi

RSYNC=(rsync -a --delete --exclude "${DEPLOY_EXCLUDE:-private/}")
SOURCES=("$SRC_ROOT/data/wiki" "$SRC_ROOT/data/courses")

dest_for() { echo "$DEST_ROOT/data/"; }

SLIDES_SRC="${DEPLOY_SLIDES_SRC:-$SRC_ROOT/var/slides}"
SLIDES_DEST_REL="${DEPLOY_SLIDES_DEST:-content/slides}"
HAVE_SLIDES=0
if [ -d "$SLIDES_SRC" ]; then HAVE_SLIDES=1; fi

if [ "$LOCAL_MODE" = "1" ]; then
    mkdir -p "$DEPLOY_PATH/data"
    if [ "$HAVE_SLIDES" = "1" ]; then mkdir -p "$DEPLOY_PATH/$SLIDES_DEST_REL"; fi
fi
if [ "$HAVE_SLIDES" = "0" ]; then
    echo "note: no built slides at $SLIDES_SRC (run make slides-all PREVIEW=1 first); skipping slides" >&2
elif [ "$LOCAL_MODE" != "1" ]; then
    ssh "$DEPLOY_HOST" "mkdir -p '$DEPLOY_PATH/$SLIDES_DEST_REL'"
fi

# Pass 1: dry run, list every path rsync would touch.
: >"$TRANSFER_LIST"
for src in "${SOURCES[@]}"; do
    "${RSYNC[@]}" --dry-run --itemize-changes "$src" "$(dest_for "$src")" >>"$TRANSFER_LIST"
done
if [ "$HAVE_SLIDES" = "1" ]; then
    "${RSYNC[@]}" --dry-run --itemize-changes "$SLIDES_SRC/" "$DEST_ROOT/$SLIDES_DEST_REL/" >>"$TRANSFER_LIST"
fi

if grep -E '(^|[[:space:]/])private(/|$)' "$TRANSFER_LIST" >/dev/null; then
    echo "ABORT: the transfer list contains a private/ path:" >&2
    grep -E '(^|[[:space:]/])private(/|$)' "$TRANSFER_LIST" >&2
    exit 1
fi
echo "dry run clean: $(wc -l <"$TRANSFER_LIST" | tr -d ' ') entries, none under private/"

# Pass 2: the transfer.
for src in "${SOURCES[@]}"; do
    "${RSYNC[@]}" "$src" "$(dest_for "$src")"
done
if [ "$HAVE_SLIDES" = "1" ]; then
    "${RSYNC[@]}" "$SLIDES_SRC/" "$DEST_ROOT/$SLIDES_DEST_REL/"
fi

# Post-check: no file under any private/ directory at the destination.
find_private='find data content -path "*/private/*" -type f 2>/dev/null | head -5 || true'
if [ "$LOCAL_MODE" = "1" ]; then
    leaked="$(cd "$DEPLOY_PATH" && eval "$find_private")"
else
    leaked="$(ssh "$DEPLOY_HOST" "cd '$DEPLOY_PATH' && $find_private")"
fi
if [ -n "$leaked" ]; then
    echo "ABORT: private files exist at the destination:" >&2
    echo "$leaked" >&2
    exit 1
fi
echo "post-check clean: no files under private/ at the destination"

if [ "$RESTART" = "1" ] && [ "$LOCAL_MODE" != "1" ]; then
    ssh "$DEPLOY_HOST" "cd '$DEPLOY_PATH' && docker compose restart $SERVICE"
fi
echo "deployed"
