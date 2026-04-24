#!/usr/bin/env bash

set -euo pipefail

source .claude/hooks/lib.sh

command=$(claude_command)
echo "$command" | grep -qE '(^|[[:space:]])git commit([[:space:]]|$)' || exit 0

branch=$(git branch --show-current 2>/dev/null || true)
[ -z "$branch" ] && exit 0
echo "$branch" | grep -qE '^(main|master)$' && exit 0
echo "$branch" | grep -qE 'LIN-[0-9]+' && exit 0

block "Branch naming guard: use LIN-{id} in the branch name for auto-linking. Current branch: $branch"
