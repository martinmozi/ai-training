[Obsah](ai-coding-agenti.md)

<a id="priloha-c-setup-borisa-chernyho-a-timu-claude-code"></a>

# Príloha C: Setup Borisa Chernyho a tímu Claude Code

Zhrnutie vlákien z X, text overený cez threadreaderapp.com. Modely a príkazy sú zo stavu v čase vlákna.

**Osobný setup** ([2. 1. 2026](https://x.com/bcherny/status/2007179832300581177)), podľa vlastných slov *„surprisingly vanilla“*:

1. 5 sessionov paralelne v termináli a ďalších 5–10 na claude.ai/code, notifikácie, keď niektorá čaká na vstup.
2. Opus 4.5 s thinkingom na všetko: pomalší než Sonnet, ale treba ho menej usmerňovať, takže je *„takmer vždy v konečnom dôsledku rýchlejší“*.
3. Jeden zdieľaný `CLAUDE.md` v gite, celý tím doň pridáva pravidlá niekoľkokrát týždenne. V PR kolegov sa označí `@claude`, aby poučenie doplnil do `CLAUDE.md`.
4. Väčšina sessionov začína v plan mode, potom auto-accept edits. *„A good plan is really important!“*
5. Slash commands na každý opakovaný postup (`/commit-push-pr`), v gite. Command si vopred inline bashom zistí `git status`, aby ušetril výmeny s modelom.
6. Subagenti `code-simplifier` a `verify-app`. PostToolUse hook na formátovanie.
7. Bez `--dangerously-skip-permissions`, bezpečné príkazy povolené v zdieľanom `.claude/settings.json`. Bez povolení len v sandboxe.
8. Pri dlhých úlohách overenie background agentom alebo `Stop` hookom.
9. **Najdôležitejšie: daj Claudovi spôsob, ako si overiť prácu.** Výsledok je potom *„2–3× kvalitnejší“*. *„Invest in making this rock-solid.“*

**Tipy tímu** ([31. 1. 2026](https://x.com/bcherny/status/2017742741636321619)):
- 3–5 git worktrees, každý s vlastnou session, je podľa tímu najväčšie zvýšenie produktivity.
- Jeden Claude píše plán, druhý ho reviewuje *„ako staff engineer“*. Keď sa niečo pokazí, naplánuj znova.
- Po každej korekcii: *„Update your CLAUDE.md so you don't make that mistake again.“*
- Prompty: *„Prove to me this works“*, *„Knowing everything you know now, scrap this and implement the elegant solution.“*

**Polovica 2026** ([17. 7. 2026](https://x.com/bcherny/status/2077929379661844559), *Steps of AI Adoption*): ďalší posun neprinesú tokeny, ale end-to-end overovanie, auto mode na povolenia, automatický code a security review a rozhrania na riadenie viacerých agentov. Návratnosť meria otázka *„Robili by ste túto prácu aj tak? Koľko inžinierskych hodín by stála?“*

---

[← Príloha B: Ceny a príkazy](priloha-b-ceny-a-prikazy.md) · [Obsah](ai-coding-agenti.md)
