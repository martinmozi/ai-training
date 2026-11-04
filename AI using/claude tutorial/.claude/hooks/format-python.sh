#!/usr/bin/env bash
# PostToolUse (Edit|Write): naformátuj upravený Python súbor, chyby formátovača agenta nezastavia.
path=$(jq -r '.tool_input.file_path // empty')
case "$path" in
  *.py) command -v ruff >/dev/null && ruff format --quiet "$path" ;;
esac
exit 0
