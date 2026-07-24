#!/usr/bin/env bash
# PreToolUse hook: enforce the Buyi invariant "raw/ is immutable once written".
#
# Blocks Edit/Write to a raw/ path that ALREADY EXISTS. Creation is explicitly
# permitted — nine etl/ ingest scripts write new files into raw/ by design, so a
# blanket write-block would break every one of them.
#
# Exit 2 = block the tool call (stderr goes back to the model).
# Exit 0 = allow.

set -euo pipefail

FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"

[[ -z "$FILE_PATH" ]] && exit 0

# Normalise to a repo-relative path so absolute paths and ../ can't slip past.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
if [[ "$FILE_PATH" = /* ]]; then
  ABS="$FILE_PATH"
else
  ABS="${REPO_ROOT}/${FILE_PATH}"
fi

# Resolve .. segments without requiring intermediate dirs to exist.
# Python's os.path.normpath works on the string; no filesystem access needed.
ABS="$(python3 -c "import os,sys; print(os.path.normpath(sys.argv[1]))" "$ABS")"

case "$ABS" in
  "${REPO_ROOT}/raw/"*) ;;
  *) exit 0 ;;  # outside raw/ — not our concern
esac

# The invariant is no-mutate, not no-write: only an EXISTING file is protected.
if [[ -e "$ABS" ]]; then
  REL="${ABS#"${REPO_ROOT}/"}"
  cat >&2 <<EOF
BLOCKED: ${REL} already exists under raw/.

raw/ is immutable once written (SANYI.md, 不易 Buyi). Every wiki page's sources:
list resolves to raw files — mutating one silently invalidates every page citing
it. Creating NEW files under raw/ is permitted; editing or overwriting one is not.

If this source genuinely changed, add a new dated file alongside it instead.
EOF
  exit 2
fi

exit 0
