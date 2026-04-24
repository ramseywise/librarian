#!/usr/bin/env bash

set -euo pipefail

source .claude/hooks/lib.sh

path=$(claude_path)
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '(^|/)(CLAUDE\.md|.*\.md)$' || exit 0

python3 - "$path" <<'PY'
import os
import re
import sys

path = sys.argv[1]
issues = []

with open(path, encoding="utf-8") as fh:
    lines = fh.readlines()

for idx, line in enumerate(lines, 1):
    if line.rstrip("\n").endswith((" ", "\t")):
        issues.append(f"  trailing whitespace: {idx}")

headings = [line.strip().lower() for line in lines if line.startswith("#")]
dupes = sorted({h for h in headings if headings.count(h) > 1})
for heading in dupes:
    issues.append(f"  duplicate heading: {heading}")

link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
base = os.path.dirname(os.path.abspath(path))
root = os.getcwd()
for idx, line in enumerate(lines, 1):
    for target in link_re.findall(line):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        target = target.split("#", 1)[0].strip()
        if not target:
            continue
        candidate = os.path.normpath(os.path.join(base, target))
        if os.path.exists(candidate):
            continue
        candidate = os.path.normpath(os.path.join(root, target))
        if os.path.exists(candidate):
            continue
        issues.append(f"  broken link: {idx} -> {target}")

if len(lines) > 500:
    issues.append(f"  file is {len(lines)} lines (>500)")

if issues:
    print(f"Docs hygiene warnings in {path}:", file=sys.stderr)
    for issue in issues[:20]:
        print(issue, file=sys.stderr)
PY

exit 0
