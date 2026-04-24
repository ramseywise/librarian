#!/usr/bin/env bash

set -euo pipefail

claude_path() {
  jq -r '.file_path // empty' <<<"${CLAUDE_TOOL_INPUT:-}"
}

claude_command() {
  jq -r '.command // empty' <<<"${CLAUDE_TOOL_INPUT:-}"
}

claude_content() {
  jq -r '.new_string // .content // empty' <<<"${CLAUDE_TOOL_INPUT:-}"
}

warn() {
  printf '%s\n' "$*" >&2
}

block() {
  printf '%s\n' "$*" >&2
  exit 2
}
