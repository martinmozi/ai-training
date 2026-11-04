# Ako napísať dobrý CLAUDE.md

`CLAUDE.md` sa načíta do kontextu na začiatku **každej** session. Každý riadok stojí tokeny a súperí o pozornosť s tvojím zadaním. Preto platí jedno pravidlo:

> **Napíš len to, čo agent nezistí z kódu a čo by bez toho urobil zle.**

## Kde môže byť

| Súbor | Platí |
|---|---|
| `~/.claude/CLAUDE.md` | všetky tvoje projekty (shell, osobné zvyky) |
| `CLAUDE.md` v koreni repa | projekt, v gite, pre celý tím |
| `CLAUDE.local.md` | projekt, len u teba (nedávaj do gitu) |
| `CLAUDE.md` v podpriečinku | načíta sa, až keď agent pracuje v tom priečinku |

Dlhší text daj do samostatného súboru a odkáž naň cez `@docs/architektura.md`, prípadne len napíš, kedy ho má agent otvoriť. Kostru vygeneruje `/init`, potom ju **skráť**.

## Kedy niečo spomenúť

- **Príkazy**, ktoré agent nevie uhádnuť: ako spustiť testy, jeden test, lint, build. Presne, na skopírovanie.
  `python -m pytest tests/unit -q`, nie „spusti testy“.
- **Nečakané veci (gotchas)**: „migrácie generuj cez `make migration`, nie ručne“, „`legacy/` neupravuj, je generovaný“.
- **Prostredie**: OS, shell, verzie, čo nie je nainštalované. „Windows + Git Bash, používaj POSIX príkazy.“
- **Rozhodnutia, ktoré z kódu nevidno**: „nové endpointy píš v `api/v2`, `v1` je zmrazené“, „namiesto async používame thready“.
- **Kedy sa má pýtať**: inštalácia balíkov, zápis do DB, veľký refaktor.
- **Definícia hotovej práce**: „pred odpoveďou spusti `ruff check` a testy dotknutého modulu“.
- **Opakovaná chyba**: ak agent niečo robí zle druhýkrát, pridaj jeden riadok. Toto je najlepší zdroj obsahu.

## Kedy byť stručný alebo nepísať nič

- **Čo vidno z kódu**: štruktúra priečinkov, zoznam tried, použitý framework. Agent si to prečíta sám, keď to potrebuje.
- **Čo vynúti nástroj**: formátovanie, poradie importov, dĺžka riadku. Na to je formátovač (alebo `PostToolUse` hook), nie text.
- **Všeobecné rady**: „píš čistý kód“, „dodržuj best practices“, „buď opatrný“. Nič nemenia, len zaberajú miesto.
- **Dlhé vysvetlenia „prečo“**: stačí jedna veta. Celé zdôvodnenie patrí do dokumentácie.
- **Čo sa často mení**: stav úloh, aktuálna vetva, TODO zoznam. To patrí do `PLAN.md` alebo do zadania.
- **Tajomstvá**: heslá, tokeny, connection stringy. Nikdy.

## Ako písať

- **Konkrétne a overiteľné.** „Testy v `tests/`, názvy `test_<modul>.py`“ namiesto „píš dobré testy“.
- **Krátke odrážky**, nie odstavce. Zoskup ich pod nadpisy (Príkazy, Štýl, Bezpečnosť).
- **Dôraz šetri.** `IMPORTANT` alebo `NIKDY` použi pri jednej-dvoch veciach. Keď je zdôraznené všetko, nie je nič.
- **Pozitívne s náhradou.** „Nepoužívaj `print`, používaj `logger`“ je lepšie než len „nepoužívaj `print`“.
- **Udržuj ho.** Keď riadok neplatí, zmaž ho. Zastaraný pokyn je horší než žiadny.

## Pokyn nie je hranica

`CLAUDE.md` je rada, ktorú model **väčšinou** dodrží. Čo sa nesmie stať nikdy, rieš inak (pozri [README](README.md)):

| Potrebuješ | Použi |
|---|---|
| zakázať príkaz alebo súbor | `permissions.deny` |
| zastaviť úpravu testov, `.env`, force push | `PreToolUse` hook |
| aby agent neskončil s padajúcimi testami | `Stop` hook |
| formátovanie po každej úprave | `PostToolUse` hook |

## Príklad

Zle (dlhé a nič nové):

```markdown
# Projekt
Toto je Python projekt pre spracovanie transakcií. Používa pandas a xgboost.
Píš čistý, čitateľný kód a dodržuj PEP 8. Buď opatrný pri zmenách.
Priečinok src/ obsahuje zdrojový kód, tests/ obsahuje testy...
```

Dobre (krátke, len to, čo agent nevie):

```markdown
## Príkazy
- testy: `python -m pytest tests -q`, jeden test: `python -m pytest tests/test_x.py::test_y`
- lint: `ruff check .` (formátovanie rieši hook, neriešiť ručne)

## Pravidlá
- Windows + Git Bash, POSIX príkazy, nie PowerShell.
- Pred `pip install` sa opýtaj.
- `data/raw/` len na čítanie, výstupy do `data/processed/`.
- Dátumy v DB sú UTC, v reportoch Europe/Bratislava.
```
