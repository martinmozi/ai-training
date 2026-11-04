# AI coding agenti v praxi: od zadania po overený diff

> **Pre koho:** pre vývojárov, ktorí už pracujú s Copilotom, Claude Code, Codexom alebo podobným agentom a chcú rozumieť, prečo sa agent správa tak, ako sa správa.
>
> **Čo je okolo:** cvičenia sú v [`cvicenie/`](cvicenie/README.md), hotová konfigurácia na skopírovanie v [`claude tutorial/`](claude%20tutorial/README.md), prehľad celého balíka v [`README.md`](README.md).
>
> **Ako čítať:** kapitoly 1 až 6 opisujú mechanizmy, ktoré platia vo všetkých nástrojoch. Príklady a príkazy sú z Claude Code, ekvivalenty v GitHub Copilote nájdeš v [prílohe B.5](priloha-b-ceny-a-prikazy.md#b5-claude-code-a-github-copilot). Konkrétne produkty, ceny a príkazy sú v [prílohách](priloha-a-nastroje.md) so stavom k októbru 2026, lebo sa menia najrýchlejšie.

## Obsah

0. [Ciele](#0-ciele)
1. [Jedna úloha od zadania po diff](01-jedna-uloha.md)
2. [Kontext: ako agent pracuje a čo ho stojí](02-kontext.md)
3. [Building blocks](03-building-blocks.md)
4. [Bezpečnosť: čo agent smie a kam idú dáta](04-bezpecnost.md)
5. [Postup práce](05-postup-prace.md)
6. [Záverečné cvičenie](06-zaverecne-cvicenie.md)
7. [Ťahák](07-tahak.md)

Prílohy (stav k 10/2026):
[A. Nástroje](priloha-a-nastroje.md) ·
[B. Ceny a príkazy](priloha-b-ceny-a-prikazy.md) ·
[C. Setup tímu Claude Code](priloha-c-setup-timu-claude-code.md) ·
[Zdroje](#zdroje)

---

<a id="0-ciele"></a>

## 0. Ciele

Predpoklad: vieš programovať, používaš git a terminál. Agenta si už aspoň skúsil. Po školení vieš:

| | Vieš | Kapitola | Vyskúšaš v |
|---|---|---|---|
| 1 | napísať overiteľné zadanie a skontrolovať plán skôr, než agent píše kód | [1](01-jedna-uloha.md), [5.1](05-postup-prace.md#51-explore--plan--code--commit) | ukážka, cvičenie 6 |
| 2 | spoznať typické chyby výstupu: upravený test, test, ktorý nikdy nepadal, zmeny navyše, „hotovo“ bez testov | [1](01-jedna-uloha.md), [5.2](05-postup-prace.md#52-tdd-a-overenie-pred-dokoncenim) | cvičenie 6 |
| 3 | vysvetliť, čo stojí kontext, prečo sa dlhá session zhoršuje a čo urobí kompakcia, a vybrať model a effort podľa úlohy | [2](02-kontext.md) | cvičenie 2 |
| 4 | rozhodnúť, či niečo patrí do pamäte, skillu, hooku, subagenta, MCP alebo pluginu, a postaviť si vlastný skill | [3](03-building-blocks.md) | cvičenie 3 |
| 5 | nastaviť povolenia a sandbox tak, aby sa agent nedostal k tajomstvám ani nevedel posielať dáta von, a vedieť, čo odchádza do API | [4](04-bezpecnost.md) | cvičenie 4 |
| 6 | ladiť chybu s agentom systematicky: reprodukcia, rozsah, hypotézy, dôkaz | [5.3](05-postup-prace.md#53-debugovanie-s-agentom) | cvičenie 5 |
| 7 | pracovať paralelne vo worktrees, spúšťať agenta v skriptoch a CI a vedieť, kedy ho nepoužiť | [5.4](05-postup-prace.md#54-sessiony-commity-a-paralelna-praca) až [5.6](05-postup-prace.md#56-kedy-agenta-nepouzit) | ťahák |
| 8 | zmerať, či agent tímu pomáha: baseline, metriky tempa spolu s kvalitou, porovnanie PR s agentom a bez neho | [5.7](05-postup-prace.md#57-meranie-prinosu) | vlastný tím po školení |

---

<a id="zdroje"></a>

## Zdroje

- Anthropic: *Claude Code: Best practices for agentic coding*; *Effective context engineering for AI agents*; dokumentácia Claude Code, code.claude.com/docs
- Dokumentácia Claude Code, overené 10/2026: [permissions](https://code.claude.com/docs/en/permissions), [sandboxing](https://code.claude.com/docs/en/sandboxing), [data usage](https://code.claude.com/docs/en/data-usage), [model config](https://code.claude.com/docs/en/model-config), [skills](https://code.claude.com/docs/en/skills), [plugins](https://code.claude.com/docs/en/plugins), [MCP](https://code.claude.com/docs/en/mcp), [headless](https://code.claude.com/docs/en/headless), [GitHub Actions](https://code.claude.com/docs/en/github-actions), [worktrees](https://code.claude.com/docs/en/worktrees), [interactive mode](https://code.claude.com/docs/en/interactive-mode)
- GitHub: [Copilot CLI command reference](https://docs.github.com/en/copilot/reference/cli-command-reference)
- Boris Cherny na X: [osobný setup](https://x.com/bcherny/status/2007179832300581177), [tipy tímu](https://x.com/bcherny/status/2017742741636321619), [Steps of AI Adoption](https://x.com/bcherny/status/2077929379661844559)
- OpenAI: dokumentácia Codex, developers.openai.com/codex
- GitHub: dokumentácia Copilot, docs.github.com/copilot
- agents.md, modelcontextprotocol.io, aider.chat
- Chroma Research: *Context Rot* (2025); Liu et al.: *Lost in the Middle* (2023)
- METR: [*Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity*](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) (2025); Google Cloud DORA: [*Accelerate State of DevOps Report*](https://dora.dev/research/2024/dora-report/) (2024)
