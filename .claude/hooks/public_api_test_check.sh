#!/usr/bin/env bash

set -euo pipefail

source .claude/hooks/lib.sh

path=$(claude_path)
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '^/?.*/src/agents/.*\.py$|^src/agents/.*\.py$' || exit 0

python3 - "$path" <<'PY'
import ast
import os
import re
import subprocess
import sys

path = sys.argv[1]
repo = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
abs_path = os.path.abspath(path)
rel = os.path.relpath(abs_path, repo)
test_rel = rel.replace("src/agents/", "tests/")
test_rel = os.path.join(os.path.dirname(test_rel), f"test_{os.path.basename(test_rel)}")
test_path = os.path.join(repo, test_rel)

diff = subprocess.run(["git", "diff", "--unified=0", "--", rel], capture_output=True, text=True, check=False).stdout
added = set()
for line in diff.splitlines():
    if not line.startswith("+") or line.startswith("+++"):
        continue
    text = line[1:].lstrip()
    m = re.match(r"(?:async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text)
    if m and not m.group(1).startswith("_"):
        added.add(m.group(1))
    m = re.match(r"class\s+([A-Za-z_][A-Za-z0-9_]*)\b", text)
    if m and not m.group(1).startswith("_"):
        added.add(m.group(1))

status = subprocess.run(["git", "status", "--porcelain", "--", rel], capture_output=True, text=True, check=False).stdout.strip()
if not diff.strip() and status.startswith("??"):
    with open(abs_path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=abs_path)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            added.add(node.name)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            added.add(node.name)

if not added:
    raise SystemExit(0)

if not os.path.exists(test_path):
    print(f"Coverage: {test_rel} does not exist — added public API needs tests: {', '.join(sorted(added))}", file=sys.stderr)
    raise SystemExit(0)

with open(test_path, encoding="utf-8") as fh:
    test_text = fh.read()

missing = [name for name in sorted(added) if f"def test_{name}" not in test_text and f"{name}" not in test_text]
if missing:
    print(f"Coverage: add or update tests for new public API in {path}: {', '.join(missing)}", file=sys.stderr)
PY

exit 0
