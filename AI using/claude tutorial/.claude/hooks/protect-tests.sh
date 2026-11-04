#!/usr/bin/env bash
# PreToolUse (Edit|Write): commitnuté testy sa nesmú meniť, nové áno.
path=$(jq -r '.tool_input.file_path // empty')
case "$path" in
  */tests/*|*/test/*|*_test.py|*/test_*.py)
    if git -C "$CLAUDE_PROJECT_DIR" ls-files --error-unmatch "$path" >/dev/null 2>&1; then
      echo "Súbor $path je commitnutý test a nesmieš ho meniť. Napíš nový test do nového súboru, alebo sa najprv opýtaj." >&2
      exit 2
    fi
    ;;
esac
exit 0
