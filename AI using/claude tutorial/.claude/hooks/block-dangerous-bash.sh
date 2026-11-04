#!/usr/bin/env bash
# PreToolUse (Bash): príkazy, ktoré sa nedajú vrátiť alebo idú von, spúšťa len človek.
cmd=$(jq -r '.tool_input.command // empty')
deny() {
  echo "Príkaz zablokovaný: $1. Ak je naozaj potrebný, napíš ho používateľovi a nech ho spustí sám." >&2
  exit 2
}
grep -Eq 'git +push +.*(--force|-f( |$))' <<<"$cmd" && deny "force push"
grep -Eq 'git +reset +--hard' <<<"$cmd" && deny "git reset --hard zahodí necommitnuté zmeny"
grep -Eq 'git +clean +-[a-z]*f' <<<"$cmd" && deny "git clean maže nesledované súbory"
grep -Eq 'rm +-[a-z]*r[a-z]*f?[a-z]* +(/|~|\.\.?)( |$)' <<<"$cmd" && deny "rekurzívne mazanie celého adresára"
grep -Eqi '(drop|truncate) +table' <<<"$cmd" && deny "zmena dát v databáze"
exit 0
