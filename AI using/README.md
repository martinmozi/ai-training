# AI coding agenti v praxi

Školenie pre vývojárov, ktorí chcú s Claude Code (a podobnými agentmi) pracovať ako power useri: dostať od agenta zmenu, ktorej môžu veriť, vedieť, čo ich to stojí, a mať pod kontrolou, čo agent smie.

**Predpoklad:** základy programovania, git a terminál. Python stačí na úrovni čítania kódu.

## Čo je v balíku

| Dokument | Pre koho | Načo |
|---|---|---|
| [`ai-coding-agenti.md`](ai-coding-agenti.md) | účastník aj lektor | **hlavný text: obsah, ciele a zdroje.** Mechanizmy, postupy a príklady sú v siedmich kapitolách `01-…` až `07-…` a v prílohách `priloha-a/b/c-…`. Podľa nich sa prednáša a k nim sa účastník vracia |
| [`cvicenie/`](cvicenie/README.md) | účastník | **cvičenia.** Malá aplikácia na faktúry, tickety a postup piatich cvičení s kontrolnými zoznamami |
| [`claude tutorial/`](claude%20tutorial/README.md) | účastník | **hotová konfigurácia na skopírovanie:** hooky, subagenti, skill `/ticket`, povolenia, meranie tokenov a [návod na `CLAUDE.md`](claude%20tutorial/claude-md-navod.md) |
| [`tutor.md`](tutor.md) | **len lektor** | časový plán, príprava, riešenia cvičení, typické chyby agentov a na čo sa pozerať pri rozbore |
| [`img/`](img/) | | diagramy k hlavnému textu |

## Ako s tým pracovať

**Na školení** (celý deň alebo dva poldni, plán v `tutor.md`): lektor prechádza kapitoly, po každej veľkej kapitole nasleduje krátke cvičenie a na záver jedno veľké.

| Kapitola | O čom | Cvičenie |
|---|---|---|
| [1. Jedna úloha od zadania po diff](01-jedna-uloha.md) | celý postup na jednom príklade, ukážka naživo | — |
| [2. Kontext](02-kontext.md) | čo agent vidí, čo to stojí, model a effort | 2: čo stojí kontext |
| [3. Building blocks](03-building-blocks.md) | nástroje, MCP, subagenti, hooky, pamäť, skills, pluginy, presety spustenia | 3: skill, hook, reviewer |
| [4. Bezpečnosť](04-bezpecnost.md) | kam idú dáta, povolenia, sandbox, prompt injection | 4: vrstvy ochrany |
| [5. Postup práce](05-postup-prace.md) | overovanie, debugovanie, worktrees, CI, kedy agenta nepoužiť, meranie prínosu | 5: debugovanie BUG-151 |
| [6. Záverečné cvičenie](06-zaverecne-cvicenie.md) | všetko naraz | 6: BUG-142 |
| [7. Ťahák](07-tahak.md) | jedna strana na stôl | — |

**Samoštúdium:** čítaj kapitoly v poradí z [obsahu](ai-coding-agenti.md) a po každej sprav príslušné cvičenie z `cvicenie/README.md`. Ukážku z kapitoly 1 si sprav sám na FEAT-150. Riešenia v `tutor.md` otvor až potom, čo máš vlastné.

**Po školení:** skopíruj si z `claude tutorial/` to, čo rieši tvoj problém (začni jedným hookom, nie všetkými), a [ťahák](07-tahak.md) maj po ruke. Prílohy slúžia na dohľadanie: [nástroje (A)](priloha-a-nastroje.md), [ceny, príkazy a meranie spotreby (B)](priloha-b-ceny-a-prikazy.md), [Copilot ekvivalenty (B.5)](priloha-b-ceny-a-prikazy.md#b5-claude-code-a-github-copilot), [klávesové skratky (B.6)](priloha-b-ceny-a-prikazy.md#b6-ovladanie-claude-code) a [setup tímu Claude Code (C)](priloha-c-setup-timu-claude-code.md).

## Stav

Obsah zodpovedá Claude Code 2.1.30x a dokumentácii k októbru 2026. Príkazy a ceny sa menia najrýchlejšie, preto sú v prílohách.
