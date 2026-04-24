#!/usr/bin/env bash

set -euo pipefail

source .claude/hooks/lib.sh

path=$(claude_path)
[ -z "$path" ] && exit 0

if ! echo "$path" | grep -qE '(^|/)(CLAUDE\.md|\.claude/memory/.*\.md)$'; then
  exit 0
fi

python3 - "$path" <<'PY'
import os
import sys

path = os.path.abspath(sys.argv[1])
repo = os.getcwd()
claude = os.path.join(repo, "CLAUDE.md")
memory_dir = os.path.join(repo, ".claude", "memory")

def normalized_bullets(file_path: str) -> set[str]:
    items: set[str] = set()
    if not os.path.exists(file_path):
        return items
    with open(file_path, encoding="utf-8") as fh:
        for line in fh:
            text = line.strip().lower()
            if text.startswith(("- ", "* ")):
                items.add(text[2:].strip())
    return items

claude_items = normalized_bullets(claude)
memory_items: set[str] = set()
if os.path.isdir(memory_dir):
    for name in os.listdir(memory_dir):
        if name.endswith(".md"):
            memory_items |= normalized_bullets(os.path.join(memory_dir, name))

overlap = sorted(claude_items & memory_items)
if overlap:
    print(f"Memory duplication warning in {path}: keep memory lean and avoid repeating CLAUDE.md", file=sys.stderr)
    for item in overlap[:10]:
        print(f"  overlap: {item}", file=sys.stderr)
PY

exit 0
