#!/usr/bin/env bash
# SessionStart (compact): po kompakcii vráť do kontextu stav úlohy z disku, nie zo zhrnutia.
cd "$CLAUDE_PROJECT_DIR" || exit 0
echo "Vetva: $(git branch --show-current)"
echo "Posledné commity:"
git log --oneline -5
echo "Necommitnuté zmeny:"
git status --short
[ -f PLAN.md ] && { echo "Obsah PLAN.md:"; cat PLAN.md; }
exit 0
