#!/usr/bin/env bash
# Post-write hook: quick lint after any write to wiki/
# Checks only dead wikilinks and missing frontmatter fields — fast checks only.
# Full lint is run manually via /lint.

set -euo pipefail

FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"

# Only run on wiki/ writes
if [[ "$FILE_PATH" != wiki/* ]] || [[ "$FILE_PATH" == *.gitkeep ]]; then
  exit 0
fi

# Skip index and conflicts files
if [[ "$FILE_PATH" == wiki/_index.md ]] || [[ "$FILE_PATH" == wiki/_conflicts.md ]]; then
  exit 0
fi

ISSUES=0

# Check required frontmatter fields
for field in "title:" "tags:" "summary:" "updated:"; do
  if ! grep -q "^${field}" "$FILE_PATH" 2>/dev/null; then
    echo "⚠ wiki-lint: missing frontmatter field '${field}' in ${FILE_PATH}" >&2
    ISSUES=$((ISSUES + 1))
  fi
done

# Check for dead wikilinks (basic — checks if referenced file exists in wiki/)
while IFS= read -r link; do
  # Convert [[Page Name]] to kebab-case filename
  slug=$(echo "$link" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -d '[]')
  if ! find wiki/ -name "${slug}.md" -o -name "*${slug}*.md" 2>/dev/null | grep -q .; then
    echo "⚠ wiki-lint: possible dead wikilink [[${link}]] in ${FILE_PATH}" >&2
  fi
done < <(grep -oP '(?<=\[\[)[^\]]+(?=\]\])' "$FILE_PATH" 2>/dev/null | grep -v '^_' || true)

# Check for orphan prevention: new pages must have at least one incoming backlink
# Only check .md files in wiki subdirectories (not _index, _conflicts, _relink_suggestions, _bridge_suggestions)
PAGE_SLUG=$(basename "$FILE_PATH" .md)
if [[ "$PAGE_SLUG" != _* ]]; then
  # Search for any [[Page Title]] reference to this page from other files
  TITLE=$(grep -oP '(?<=^title: ).+' "$FILE_PATH" 2>/dev/null | head -1)
  HAS_BACKLINK=0

  # Check by slug match
  if grep -rl "\[\[.*${PAGE_SLUG}.*\]\]" wiki/ 2>/dev/null | grep -v "$FILE_PATH" | grep -q .; then
    HAS_BACKLINK=1
  fi

  # Check by title match (if different from slug)
  if [[ $HAS_BACKLINK -eq 0 ]] && [[ -n "$TITLE" ]]; then
    if grep -rl "\[\[${TITLE}\]\]" wiki/ 2>/dev/null | grep -v "$FILE_PATH" | grep -q .; then
      HAS_BACKLINK=1
    fi
  fi

  if [[ $HAS_BACKLINK -eq 0 ]]; then
    echo "⚠ wiki-lint: ORPHAN — no incoming backlinks found for ${FILE_PATH}. Add a [[${TITLE:-$PAGE_SLUG}]] reference from at least one other wiki page." >&2
    ISSUES=$((ISSUES + 1))
  fi
fi

if [[ $ISSUES -gt 0 ]]; then
  echo "wiki-lint: ${ISSUES} issue(s) found in ${FILE_PATH} — run /lint for full report" >&2
fi

exit 0
