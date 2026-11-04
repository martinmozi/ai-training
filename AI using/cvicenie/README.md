# Cvičenia

Malá aplikácia na výpočet faktúry: pravidlá sú v [SPEC.md](SPEC.md), kód v `faktura/`, tickety v `tickets/`. Všetky cvičenia bežia nad týmto kódom.

```bash
cd cvicenie
python -m pytest -q        # na začiatku: 4 passed
```

| Cvičenie | Ku kapitole | Čas | Čo si vyskúšaš |
|---|---|---|---|
| [2: Čo stojí kontext](#cvičenie-2-čo-stojí-kontext) | [2. Kontext](../02-kontext.md) | 15 min | `/context`, `/cost`, model a effort na tej istej otázke |
| [3: Skill, hook a reviewer](#cvičenie-3-skill-hook-a-reviewer) | [3. Building blocks](../03-building-blocks.md) | 25 min | vlastný skill, hook, ktorý agenta zastaví, subagent na review |
| [4: Vrstvy ochrany](#cvičenie-4-vrstvy-ochrany) | [4. Bezpečnosť](../04-bezpecnost.md) | 15 min | čo zastaví `deny`, čo až sandbox |
| [5: Debugovanie, BUG-151](#cvičenie-5-debugovanie-bug-151) | [5.3 Debugovanie](../05-postup-prace.md#53-debugovanie-s-agentom) | 30 min | chyba bez návodu na reprodukciu |
| [6: Záverečné, BUG-142](#cvičenie-6-záverečné-bug-142) | [6. Cvičenie](../06-zaverecne-cvicenie.md) | 50 min | celý postup od zadania po dôkaz |

**Pred každým cvičením** začni z pôvodného stavu a v novej session:

```bash
git stash -u      # alebo git checkout -- . && git clean -fd, ak zmeny nepotrebuješ
claude            # nová session = čistý kontext a čisté meranie
```

Cvičenia 2 až 4 robíš v Claude Code, lebo skúšaš jeho konkrétne funkcie. Cvičenia 5 a 6 zvládneš s ľubovoľným agentom (Copilot, Codex, Aider). Ekvivalenty príkazov sú v [prílohe B.5](../priloha-b-ceny-a-prikazy.md#b5-claude-code-a-github-copilot).

---

## Cvičenie 2: Čo stojí kontext

Cieľ: vidieť na vlastné oči, čo zaberá kontext a čo platíš.

1. **Prázdna session.** Spusti `claude` a hneď `/context`. Zapíš si, koľko zaberá systémový prompt, nástroje, pamäť a MCP, ešte kým si nič nenapísal.
2. **Prieskum.** Opýtaj sa: *„Vysvetli, ako sa v tomto projekte počíta faktúra, krok po kroku.“* Potom znova `/context` a `/cost`. Čo pribudlo najviac: tvoj prompt, odpoveď, alebo prečítané súbory?
3. **Subagent.** `/clear` a tá istá otázka, ale: *„Použi Explore subagenta a vráť len zhrnutie na 10 riadkov.“* Porovnaj `/context` hlavnej session s krokom 2.
4. **Model a effort.** `/clear`, `/model haiku`, `/effort low` a otázka: *„Kde všade sa v kóde zaokrúhľuje? Navrhni testy, ktoré overia bod 6 zo SPEC.md, aj na hraničných hodnotách. Nič nemeň.“* Potom to isté s `/model opus` a `/effort high`. Porovnaj návrhy testov (ktoré hranice našli?) a spotrebu (`/cost` alebo [`log-token-usage.py`](../claude%20tutorial/.claude/hooks/log-token-usage.py)).

Zapíš si: čo v kontexte zabralo najviac miesta a ktorý model navrhol lepšie testy. Odpoveď na otázku, či sa lacnejší model oplatí, je v [2.6](../02-kontext.md#26-vyber-modelu-a-effort).

---

## Cvičenie 3: Skill, hook a reviewer

Cieľ: postaviť si tri building blocks a vidieť, ako sa správajú.

Skopíruj si hotovú konfiguráciu do `cvicenie/` a spusti novú session:

```bash
cp -r "../claude tutorial/.claude" .
chmod +x .claude/hooks/*.sh .claude/hooks/*.py
claude
```

1. **Skill (10 min).** Vytvor `.claude/skills/spec-check/SKILL.md`, ktorý dostane číslo bodu zo `SPEC.md` ako argument, vloží si `SPEC.md` cez `` !`cat SPEC.md` `` a porovná daný bod s kódom. Vzor je v [`.claude/skills/ticket/SKILL.md`](../claude%20tutorial/.claude/skills/ticket/SKILL.md) a v [3.6](../03-building-blocks.md#36-vlastny-skill-krok-za-krokom). Spusti `/spec-check 4`. Potom sa bez lomky opýtaj *„Sedí bod 3 zo špecifikácie s kódom?“* a sleduj, či si ho Claude načíta sám.
2. **Hook (5 min).** Požiadaj agenta: *„Uprav test `test_simple_order_pays_shipping_and_vat`, aby používal 3 kusy.“* Hook `protect-tests.sh` to zastaví. Prečítaj si, čo agent dostal ako dôvod a čo urobil potom.
3. **Reviewer (10 min).** Nechaj agenta implementovať z [FEAT-150](tickets/FEAT-150.md) **len** kontrolu množstva (bez kontroly ceny), aby zmena bola zámerne neúplná. Potom spusti `@agent-spec-reviewer skontroluj diff oproti tickets/FEAT-150.md a SPEC.md`. Našiel reviewer, čo chýba? Pozri aj `.claude/agent-memory/spec-reviewer/`, či si niečo zapísal.

Na konci zmaž `.claude/` z `cvicenie/`, aby neovplyvnila ďalšie cvičenia.

---

## Cvičenie 4: Vrstvy ochrany

Cieľ: zistiť, čo zastaví ktorá vrstva z [kapitoly 4](../04-bezpecnost.md). Vytvor falošné tajomstvo:

```bash
echo 'DB_PASSWORD=cvicne-heslo-123' > .env
```

Celé cvičenie rob v **manuálnom režime**, aby si videl, čo robia samotné vrstvy. Novšie verzie Claude Code štartujú v `auto` móde ([4.2](../04-bezpecnost.md#42-rezimy-povoleni)), v ktorom sa agent nepýta a `.env` prečíta bez opýtania. Session preto spúšťaj takto:

```bash
claude --permission-mode default
```

1. **Bez pravidiel.** Opýtaj sa agenta: *„Aké heslo k databáze je v projekte?“* Prečítal `.env`? Pýtal sa ťa?
2. **Povolenia.** Vytvor `.claude/settings.local.json` s obsahom `{"permissions": {"deny": ["Read(./.env)"]}}` a začni novú session (znova s `--permission-mode default`). Zopakuj otázku. Potom: *„Zisti ho krátkym Python skriptom.“*
3. **Sandbox.** Spusti `/sandbox` a do `settings.local.json` pridaj `"sandbox": {"enabled": true, "filesystem": {"denyRead": ["./.env"]}}`. Zopakuj krok 2.
4. **Záver.** Ku každému kroku zapíš, čo agent skúsil a ktorá vrstva ho zastavila. Potom `.env` aj `.claude/` zmaž.

Očakávaný výsledok: `deny` zastaví nástroj Read a `cat`, ale nie Python skript. Ten zastaví až sandbox. Ak ti zostane čas, zopakuj krok 1 v `auto` móde (`Shift+Tab`): niektorý pokus môže zastaviť klasifikátor, `.env` však prečíta. Aj to si zapíš, ale nespoliehaj sa naň. Na Windows bez WSL2 sandbox nefunguje, krok 3 vtedy len prečítaj.

---

## Cvičenie 5: Debugovanie, BUG-151

Cieľ: opraviť chybu, ku ktorej nemáš návod na reprodukciu, postupom z [5.3](../05-postup-prace.md#53-debugovanie-s-agentom).

Ticket: [tickets/BUG-151.md](tickets/BUG-151.md). Kód: `faktura/importer.py`. Dáta: `data/`.

1. **Reprodukcia (10 min).** Ešte žiadna oprava. Zadaj agentovi, nech zreprodukuje reklamovanú objednávku a potom zistí, **ktoré všetky** faktúry za september nesedia s e-shopom. Výsledok má byť zoznam objednávok a stĺpcov, ktoré nesedia, nie dohad.
2. **Hypotézy (5 min).** Čo majú zlé faktúry spoločné? Nechaj agenta navrhnúť aspoň dve hypotézy a ku každej overenie (príkaz, výpis, malý experiment v Pythone). Až potom ich over.
3. **Test, potom oprava (10 min).** Test, ktorý chybu zachytí na úrovni príčiny (nie len objednávky 2026-1033) a pred opravou padá. Potom oprava.
4. **Dôkaz (5 min).** Porovnanie všetkých septembrových faktúr s e-shopom po oprave: koľko nesedí? Plus `python -m pytest -q`.

Kontrolný zoznam:
- [ ] Agent najprv reprodukoval, nie opravoval.
- [ ] Zoznam všetkých zlých faktúr vznikol skriptom, nie odhadom.
- [ ] Hypotéza bola overená experimentom skôr, než sa menil kód.
- [ ] Test zachytí príčinu aj pre iné ceny, nielen jednu objednávku.
- [ ] Po oprave nesedí 0 faktúr a existujúce testy prechádzajú.

---

## Cvičenie 6: Záverečné, BUG-142

Opravíš [tickets/BUG-142.md](tickets/BUG-142.md) celým postupom z [kapitoly 1](../01-jedna-uloha.md). Kód je v pôvodnom stave, **bez zmien z ukážky FEAT-150**. Validácia riadkov z ukážky tu teda nie je a v cvičení ju nerieš.

Testy na začiatku **prechádzajú**. Aj to je súčasť cvičenia.

### Úloha

Použi svojho agenta (Copilot, Claude Code, Codex, Aider…). Cieľom nie je len opraviť chybu, ale **preukázať**, že oprava je správna.

1. **Zadanie (10 min).** Napíš agentovi overiteľné zadanie. Musí obsahovať:
   - kde hľadať (súbory, funkcie),
   - aké je očakávané správanie (odkaz na `SPEC.md`, konkrétny príklad z ticketu),
   - čo je „hotovo“ (ktoré testy musia prejsť a čo agent nesmie meniť),
   - že najprv chceš plán, nie kód.
2. **Plán (10 min).** Agent navrhne plán (plan mode alebo „zatiaľ nič nepíš“). Skontroluj ho podľa zoznamu nižšie. Ak niečo chýba, oprav plán, nie kód.
3. **Test, potom oprava (15 min).** Najprv test, ktorý chybu reprodukuje a **padá**. Až potom oprava.
4. **Kontrola výstupu (10 min).** Prejdi diff a nájdi aspoň jednu vec, ktorú agent spravil zle alebo vynechal.
5. **Dôkaz (5 min).** Ukáž výstup testov a diff. Vysvetli, prečo by test pred opravou padol.

### Kontrolný zoznam

**Zadanie**
- [ ] Obsahuje cestu k súboru a odkaz na špecifikáciu.
- [ ] Obsahuje konkrétny príklad s očakávanými číslami.
- [ ] Definuje „hotovo“ príkazom (`python -m pytest -q`).
- [ ] Hovorí, čo sa nesmie meniť (commitnuté testovacie súbory, `SPEC.md`) a že nové testy idú do nového súboru.

**Plán**
- [ ] Rieši všetky body ticketu, nielen prvý.
- [ ] Porovnáva kód so `SPEC.md`, nielen s ticketom.
- [ ] Obsahuje testy na hraničné hodnoty (presne 10 ks, kupón v posledný deň platnosti).
- [ ] Nemení commitnuté testovacie súbory, nové testy dáva do nového súboru.

**Výstup**
- [ ] Nový test pred opravou padal (vidíš to vo výstupe alebo si to overil sám).
- [ ] Testy si prečítal ako prvé, vrátane nových súborov z `git status --short` (`git diff` ich neukáže).
- [ ] Diff je malý a týka sa len chyby (žiadny „bonusový“ refaktor).
- [ ] Ak agent hlási „všetko prechádza“, sám si spustil testy.

**Bonus**
- [ ] Agent alebo ty si našiel chybu, ktorá v tickete nie je.
- [ ] Poučenie si zapísal do `AGENTS.md` / `CLAUDE.md`.
