#!/usr/bin/env bash

set -euo pipefail

source .claude/hooks/lib.sh

command=$(claude_command)
echo "$command" | grep -qE '(^|[[:space:]])git([[:space:]]|$)' || exit 0

if echo "$command" | grep -qE 'push[[:space:]]+--force(-with-lease)?|push[[:space:]]+-f|reset[[:space:]]+--hard|clean[[:space:]]+-fd|rebase[[:space:]]+-i|rebase[[:space:]]+--interactive|branch[[:space:]]+-D|checkout[[:space:]]+-f|switch[[:space:]]+-f'; then
  block "Blocked: destructive git command."
fi

exit 0
