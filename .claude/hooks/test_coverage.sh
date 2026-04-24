#!/usr/bin/env bash
# PostToolUse hook for Write|Edit — warns about public functions without tests
# Advisory only (exit 0) — does not block edits

path=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '/src/agents/.*\.py$' || exit 0

# Skip __init__.py, __main__.py, config files
basename=$(basename "$path")
echo "$basename" | grep -qE '^__' && exit 0
echo "$basename" | grep -qE '^config\.py$' && exit 0

# Derive test file path: src/agents/X/Y.py → tests/X/test_Y.py
rel=${path#*src/agents/}
pkg_dir=$(dirname "$rel")
mod=$(basename "$rel" .py)
test_file="tests/${pkg_dir}/test_${mod}.py"

# Extract public function names from source (def name, no _ prefix)
src_funcs=$(uv run python3 -c "
import ast, sys
with open('$path') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if not node.name.startswith('_'):
            print(node.name)
" 2>/dev/null | sort -u)

[ -z "$src_funcs" ] && exit 0

# If test file doesn't exist, warn about all functions
if [ ! -f "$test_file" ]; then
  count=$(echo "$src_funcs" | wc -l | tr -d ' ')
  echo "Coverage: $test_file does not exist — $count public function(s) untested" >&2
  exit 0
fi

# Check each function for a matching test_* in the test file
missing=""
while IFS= read -r func; do
  [ -z "$func" ] && continue
  if ! grep -qE "def test_.*${func}|def test_${func}" "$test_file" 2>/dev/null; then
    missing="$missing  $func\n"
  fi
done <<< "$src_funcs"

if [ -n "$missing" ]; then
  printf "Coverage: untested public functions in %s:\n%b" "$path" "$missing" >&2
fi

exit 0
