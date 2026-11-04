#!/usr/bin/env bash
# Stop: agent neskončí, kým testy padajú. Druhýkrát za sebou ho už nezastaví.
input=$(cat)
[ "$(jq -r '.stop_hook_active' <<<"$input")" = "true" ] && exit 0

cd "$CLAUDE_PROJECT_DIR" || exit 0
# Ak sa nezmenil žiadny súbor okrem testov a dokumentácie, testy smú padať:
# je to TDD fáza „najprv padajúci test“, alebo session bez zmien v kóde (otázka, prieskum).
changed_code=$(git status --porcelain --untracked-files=all -- . | cut -c4- |
  grep -Ev '(^|/)tests?/|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)\.claude/|\.md$')
[ -z "$changed_code" ] && exit 0

if ! output=$(python -m pytest -q 2>&1); then
  reason=$(printf 'Zmenil si kód a testy neprechádzajú, oprav ich pred dokončením:\n%s' "$(tail -n 20 <<<"$output")")
  jq -n --arg reason "$reason" '{decision: "block", reason: $reason}'
fi
exit 0
