#!/usr/bin/env bash
# PreToolUse hook for Write|Edit — blocks writes containing secrets.
# Scans new content for API keys, tokens, and credentials.

source "$(dirname "$0")/lib.sh"

content=$(claude_content)
[ -z "$content" ] && exit 0

issues=""

# AWS keys
echo "$content" | grep -qE 'AKIA[0-9A-Z]{16}' && issues="$issues  AWS access key detected\n"

# Generic API keys / tokens (long hex or base64 strings assigned to key-like vars)
echo "$content" | grep -qiE '(api_key|api_secret|secret_key|auth_token|access_token)\s*=\s*["'"'"'][A-Za-z0-9+/=_-]{20,}["'"'"']' && issues="$issues  Possible API key/token in assignment\n"

# Anthropic keys
echo "$content" | grep -qE 'sk-ant-[A-Za-z0-9_-]{20,}' && issues="$issues  Anthropic API key detected\n"

# OpenAI keys
echo "$content" | grep -qE 'sk-[A-Za-z0-9]{20,}' && issues="$issues  OpenAI-style API key detected\n"

# GitHub tokens
echo "$content" | grep -qE '(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}' && issues="$issues  GitHub token detected\n"

# Private keys
echo "$content" | grep -qE 'BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY' && issues="$issues  Private key detected\n"

# Generic password assignments
echo "$content" | grep -qiE '(password|passwd|pwd)\s*=\s*["'"'"'][^"'"'"']{8,}["'"'"']' && issues="$issues  Hardcoded password detected\n"

if [ -n "$issues" ]; then
  printf "Secrets scan blocked this write:\n%b\nMove secrets to .env and reference via settings.\n" "$issues" >&2
  exit 2
fi

exit 0
