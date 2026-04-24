#!/usr/bin/env bash

set -euo pipefail

source .claude/hooks/lib.sh

path=$(claude_path)
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '^/?.*/src/.*\.py$|^src/.*\.py$' || exit 0

python3 - "$path" <<'PY'
import ast
import os
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as fh:
    tree = ast.parse(fh.read(), filename=path)

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        if not hasattr(node, "end_lineno") or not hasattr(node, "lineno"):
            continue
        length = node.end_lineno - node.lineno + 1
        if length > 40:
            name = getattr(node, "name", "<anonymous>")
            print(f"Function complexity warning in {path}: {name} spans {length} lines", file=sys.stderr)
            break
PY

exit 0
