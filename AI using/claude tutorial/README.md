# Príklady z praxe: konfigurácia Claude Code na skopírovanie

Hotové súbory k [hlavnému textu](../ai-coding-agenti.md): povolenia ([kapitola 4](../04-bezpecnost.md)), hooky a subagenti ([3.2](../03-building-blocks.md#32-subagenti), [3.3](../03-building-blocks.md#33-hooks-pravidla-ktore-platia-vzdy)), skill ([3.6](../03-building-blocks.md#36-vlastny-skill-krok-za-krokom)) a meranie spotreby ([B.4](../priloha-b-ceny-a-prikazy.md#b4-spotreba-na-jednu-ulohu)). Návod, ako napísať `CLAUDE.md`, je v [`claude-md-navod.md`](claude-md-navod.md).

| Čo | Súbor | Kapitola |
|---|---|---|
| povolenia allow/ask/deny | `.claude/settings.json` (`permissions`) | 4.3 |
| hooky | `.claude/settings.json` (`hooks`) + `.claude/hooks/` | 3.3, 4.6 |
| subagenti | `.claude/agents/` | 3.2 |
| skill `/ticket` | `.claude/skills/ticket/SKILL.md` | 3.6 |
| meranie tokenov | `.claude/hooks/log-token-usage.py` (osobné nastavenia) | B.4 |

Priečinok `.claude/` skopíruj celý, alebo si vyber len časti.

```bash
cp -r "claude tutorial/.claude" /cesta/k/projektu/
chmod +x /cesta/k/projektu/.claude/hooks/*.sh /cesta/k/projektu/.claude/hooks/*.py
```

Potrebuješ `bash`, `jq` a `git`. Pre Python hooky aj `pytest` a `ruff`. Na Windows to beží v Git Bash.

## Kedy stačí default Claude Code v auto mode

Od verzie 2.1.283 sa interaktívna session v termináli a vo VS Code štandardne spúšťa v **auto mode** (stav 10/2026). Agent sa nepýta na každý príkaz. Každú akciu pred spustením posúdi druhý model (klasifikátor). Ten podľa dokumentácie štandardne blokuje napríklad:

- force push, `git reset --hard`, `git clean -fd`, `git checkout -- .`,
- deploy a migrácie do produkcie,
- `curl | bash`,
- posielanie citlivých dát von a vypísanie živého tokenu,
- nevratné zmazanie súborov, ktoré existovali pred session,
- vypnutie CI kontrol a zakomentovanie testu, ktorý chráni bezpečnosť (auth, validácia).

Bez opýtania naopak povolí lokálne zmeny v pracovnom adresári, inštaláciu závislostí z lock súboru, **čítanie `.env`** a push do ľubovoľnej vetvy aktuálneho repa.

**Default bez hookov a vlastných agentov stačí, keď:**

- robíš krátku, ohraničenú úlohu, ktorej diff si potom celý prečítaš,
- pracuješ na vlastnej vetve a nič nejde do produkcie,
- v repe nie sú tajomstvá, ktoré by agent nemal mať v kontexte,
- testy spúšťaš a kontroluješ sám, alebo ich agent spúšťa, lebo to máš v `CLAUDE.md`,
- skúšaš, prototypuješ alebo sa učíš nový kód.

V takom prípade by ti hooky a vlastní agenti pridali len údržbu a čas pri každom kroku. Stačí dobré zadanie, `CLAUDE.md` s príkazom na testy a kontrola diffu.

**Čo auto mode nerieši**, a preto majú hooky a agenti zmysel:

- **Nie je to záruka.** Dokumentácia výslovne píše, že auto mode znižuje počet otázok, ale bezpečnosť nezaručuje. Klasifikátor je model, nie pravidlo.
- **Nekontroluje kvalitu.** Neoverí, či testy prešli, či agent nezmenil bežný test, aby prešiel, ani či zmena zodpovedá špecifikácii. Úpravu testu zablokuje len vtedy, keď ide o test bezpečnosti.
- **Hranice z chatu sa môžu stratiť.** Pokyn „nepushuj“ si klasifikátor číta z konverzácie. Ak ho kompakcia zo zhrnutia vynechá, prestane platiť. Na tvrdú hranicu treba `permissions.deny` alebo hook.
- **`.env` číta bez opýtania**, lebo predpokladá, že tajomstvá posiela len do správneho API. Ak nechceš, aby boli v kontexte vôbec, potrebuješ hook alebo `deny` pravidlo.
- **Agent menej často kladie doplňujúce otázky.** Auto mode ho vedie k tomu, aby pokračoval sám. Pri nejasnom zadaní si odpoveď domyslí.

### Rozhodovacia tabuľka

| Situácia | Default auto mode | Pridaj |
|---|---|---|
| malá oprava, diff si prečítaš celý | ✅ stačí | nič |
| prieskum cudzieho kódu, otázka „kde a ako“ | ✅ stačí, Claude Code má vstavaného Explore subagenta | `explorer.md` cez `@agent-explorer`, ak chceš pevný formát výstupu alebo lacnejší model (pozri [vstavaní a vlastní agenti](#vstavani-a-vlastni-agenti)) |
| TDD alebo oprava chyby, kde testy nesmú meniť | ⚠️ úpravu bežného testu nezastaví | `protect-tests.sh` |
| agent často hlási „hotovo“ bez spustenia testov | ⚠️ kvalitu nerieši | `tests-must-pass.sh` |
| tím a CI s formátovačom | ⚠️ netýka sa ho | `format-python.sh` |
| repo s `.env`, kľúčmi alebo certifikátmi | ⚠️ `.env` číta | `protect-secrets.sh` alebo `permissions.deny` |
| dlhá úloha cez viac kompakcií | ⚠️ zhrnutie je výber modelu | `after-compact.sh` + `PLAN.md` |
| zmena podľa špecifikácie, pred commitom | ⚠️ nevie, čo je správne | `spec-reviewer.md` |
| oprava chyby, chceš dôkaz | ⚠️ nevie, či test dokazuje opravu | `test-verifier.md` |
| nebezpečné git príkazy | ✅ force push a `reset --hard` blokuje sám | `block-dangerous-bash.sh` len v manual mode alebo ako poistka, ktorá nezávisí od klasifikátora |
| agent beží bez dozoru alebo v CI | ❌ auto mode nestačí | sandbox alebo kontajner, `dontAsk` s presným zoznamom povolených nástrojov, hooky |

Jednoduché pravidlo: **auto mode chráni pred tým, čo sa nedá vrátiť. Hooky a agenti pomáhajú s tým, či je výsledok správny.** Ak výsledok aj tak celý skontroluješ sám, druhú časť nepotrebuješ. Ak ho celý nečítaš, potrebuješ ju.

Hooky sa dajú pridávať postupne. Začni tým, ktorý rieši chybu, ktorú agent u teba naozaj robí, nie všetkými naraz.

## Vstavané a vlastné: čo je pevné, čo si určuješ ty a čo sa čím nahrádza

Stav Claude Code 10/2026, overené v dokumentácii (code.claude.com/docs, stránky *hooks* a *sub-agents*). Iné nástroje to majú inak.

**Najprv v skratke:**

| | Hooky | Subagenti |
|---|---|---|
| Čo je pevné | **zoznam udalostí** (33), vlastnú udalosť pridať nemôžeš | **traja vstavaní agenti** (`Explore`, `Plan`, `general-purpose`) |
| Čo si určuješ ty | čo sa pri udalosti spustí (skript, HTTP, prompt, agent) a pre ktoré nástroje (matcher) | meno, popis, prompt, nástroje, model, pamäť |
| Viac definícií z rôznych miest | **sčítajú sa**, spustia sa všetky | **nahradia sa**, pri rovnakom mene platí jedna |
| Vstavané vs. vlastné | vstavané hooky neexistujú, všetky sú tvoje | vlastný agent s menom vstavaného ho **nahradí** |

### Hooky: pevné udalosti, vlastné skripty

Claude Code spúšťa hooky len v presne daných chvíľach (udalostiach). Ty určíš, čo sa v tej chvíli spustí. Všetky udalosti:

| Oblasť | Udalosti |
|---|---|
| session | `SessionStart`, `SessionEnd`, `Setup` |
| prompt | `UserPromptSubmit`, `UserPromptExpansion` |
| nástroje | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch` |
| povolenia | `PermissionRequest`, `PermissionDenied` (len v auto mode) |
| koniec odpovede | `Stop`, `StopFailure` |
| subagenti a tímy | `SubagentStart`, `SubagentStop`, `TeammateIdle` |
| úlohy | `TaskCreated`, `TaskCompleted` |
| kontext | `PreCompact`, `PostCompact`, `InstructionsLoaded` |
| konfigurácia a prostredie | `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove` |
| model | `PreModelSwitch`, `PostModelSwitch` |
| MCP | `Elicitation`, `ElicitationResult` |
| UI | `Notification`, `MessageDisplay` |

V praxi stačí päť: `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `UserPromptSubmit`. Ostatné sú na automatizáciu a integrácie.

**Matcher** je voľný filter v rámci pevnej udalosti. Pri `PreToolUse` a `PostToolUse` je to meno nástroja (`Edit|Write`, `Bash`, `mcp__github__.*`). Pri `SessionStart` je to dôvod štartu (`startup`, `resume`, `clear`, `compact`). Pri `SubagentStart` a `SubagentStop` je to meno agenta, aj vlastného (`spec-reviewer`).

**Zablokovať** akciu vie len časť udalostí: napríklad `PreToolUse` (nástroj sa nespustí), `UserPromptSubmit` (prompt sa nepošle), `Stop` a `SubagentStop` (agent pokračuje). `PostToolUse` už nič nezablokuje, nástroj prebehol. Vie len poslať modelu správu.

**Kde môžu byť definované a ako sa skladajú:**

| Miesto | Platí |
|---|---|
| managed settings | celá organizácia |
| `~/.claude/settings.json` | všetky tvoje projekty |
| `.claude/settings.json` | projekt, v gite (tak sú nastavené tieto príklady) |
| `.claude/settings.local.json` | projekt, len u teba |
| plugin `hooks/hooks.json` | keď je plugin zapnutý |
| hlavička skillu | od spustenia skillu do konca session |
| hlavička subagenta | kým beží daný subagent |

Hooky sa **nenahrádzajú, ale sčítajú**. Ak máš `PreToolUse` hook v osobných aj projektových nastaveniach, spustia sa oba, a to paralelne. Ten istý príkaz definovaný na dvoch miestach sa spustí raz. Jednotlivý hook sa nedá vypnúť inak než zmazaním. Vypnúť sa dajú len všetky naraz (`"disableAllHooks": true`) a hooky organizácie ani tak nie.

<a id="vstavani-a-vlastni-agenti"></a>

### Subagenti: vstavaní a vlastní

**Vstavaní** sú v každej session:

| Meno | Na čo ho Claude použije |
|---|---|
| `Explore` | prieskum a hľadanie v kóde bez zmien. Štartuje bez `CLAUDE.md`, aby bol rýchly a lacný |
| `Plan` | prieskum v režime plánovania, keď hlavná session nesmie nič meniť |
| `general-purpose` | úloha, ktorá potrebuje prieskum aj úpravy alebo viac nadväzujúcich krokov |

**Vlastných** si vytvoríš ako markdown súbor v `.claude/agents/` (projekt) alebo `~/.claude/agents/` (všetky tvoje projekty). Meno nie je pevné:
- určuje ho pole `name` v hlavičke, nie názov súboru ani podpriečinok,
- má najviac 256 znakov a nesmie obsahovať `:`, lebo dvojbodka je vyhradená pre pluginy (`my-plugin:reviewer`).

**Ako sa nahrádzajú.** Pri rovnakom mene platí jediná definícia, podľa tejto priority:

| Priorita | Odkiaľ |
|---|---|
| 1 (najvyššia) | managed settings (organizácia) |
| 2 | prepínač `--agents` pri štarte (len pre jednu session) |
| 3 | `.claude/agents/` v projekte; pri vnorených priečinkoch vyhráva ten najbližšie k pracovnému adresáru |
| 4 | `~/.claude/agents/` |
| 5 (najnižšia) | plugin |

Vlastný agent s menom `Explore` **nahradí vstavaného**. Dá sa to využiť napríklad na lacnejší prieskum (`model: haiku`). Ak majú dva súbory v tom istom priečinku rovnaké `name`, načíta sa len jeden a nie je isté ktorý. `/doctor` také duplicity nájde.

**Prečo je tu `explorer`, a nie `Explore`.** Príklad má zámerne iné meno, takže vstavaný `Explore` zostane a `explorer` je ďalší agent vedľa neho. Majú však podobný popis, a preto si Claude pri automatickom výbere môže vybrať ktoréhokoľvek z nich. Máš dve možnosti:
- **chceš pevný formát výstupu len niekedy:** nechaj `explorer` a volaj ho cez `@agent-explorer`,
- **chceš, aby každý prieskum bežal tvojím spôsobom:** premenuj `name: explorer` na `name: Explore`. Vstavaného tým nahradíš.

### Ako Claude vyberá subagenta

Hlavný agent má v kontexte `name` a `description` každého subagenta, vstavaného aj vlastného. Telo súboru sa načíta až pri spustení. Spustiť subagenta sa dá štyrmi spôsobmi, zoradenými od „rozhodne model“ po „rozhodneš ty“:

| Spôsob | Príklad | Kto rozhodne |
|---|---|---|
| automaticky | „skontroluj, či zmena sedí so SPEC.md“ | model, podľa tvojej požiadavky a polí `description` |
| menom v texte | „Použi spec-reviewer na BUG-142.“ | model, ale takmer vždy poslúchne |
| @-zmienkou | `@agent-spec-reviewer skontroluj diff` (pozri nižšie) | ty, tento agent sa spustí určite |
| celá session | `claude --agent spec-reviewer` | ty, hlavná session sa sama stane týmto agentom |

**Ako napísať @-zmienku.** Rovnako ako keď v prompte odkazuješ na súbor cez `@`. Dá sa to dvoma spôsobmi a výsledok je rovnaký:

1. **Z ponuky:** do promptu napíš `@`. Zobrazí sa ponuka súborov a agentov. Začni písať meno, napríklad `@spec`, a vyber riadok `spec-reviewer (agent)`. Claude Code ho vloží do promptu ako `@"spec-reviewer (agent)"`. Za neho dopíš úlohu:
   ```text
   @"spec-reviewer (agent)" skontroluj diff oproti BUG-142
   ```
2. **Ručne:** napíš `@agent-` a hneď za tým meno agenta z poľa `name`, bez medzery:
   ```text
   @agent-spec-reviewer skontroluj diff oproti BUG-142
   ```
   Kým píšeš, ponuka ukazuje len súbory, nie agentov. To nevadí, zmienka sa po odoslaní aj tak správne priradí agentovi.

V oboch prípadoch sa spustí presne `spec-reviewer`, nie iný agent. Zvyšok správy („skontroluj diff oproti BUG-142“) dostane hlavný agent a podľa neho napíše zadanie pre `spec-reviewer`.

Čo z toho vyplýva:
- **Pri automatickom výbere rozhoduje popis, nie meno.** Píš ho ako „Use when…“ so slovami, ktoré sa v úlohe objavia. Ak chceš, aby ho Claude používal sám od seba, pridaj „use proactively“.
- **Popisy všetkých agentov sú v každom requeste.** Drž ich krátke. Ak vlastné popisy spolu presiahnu 15 000 tokenov, Claude Code pri štarte zobrazí varovanie.
- **Ani pri @-zmienke nepíšeš zadanie ty.** Zadanie pre subagenta sformuluje hlavný agent z tvojej správy. Ty určíš len to, ktorý agent sa spustí.
- **Pri `--agent` sa správanie session zmení celé.** Prompt agenta nahradí štandardný systémový prompt Claude Code a platia jeho nástroje a model. `CLAUDE.md` sa načíta aj tak.
- **`spec-reviewer` a `test-verifier` volaj sám** (menom alebo cez `@`) v konkrétnom kroku pred commitom. Na automatický výber sa pri kontrolách nespoliehaj.

## Povolenia (`permissions` v `.claude/settings.json`)

| Pravidlo | Prečo |
|---|---|
| `allow`: pytest, ruff, `git diff`, `git log`, `git status` (vzor `Bash(git status *)` pokryje aj samotné `git status`) | príkazy, ktoré agent spúšťa stále, bez otázky pri každom kroku |
| `ask`: `git push` | aj v `auto` mode sa spýta, push je viditeľný pre ostatných |
| `deny`: `.env`, `*.pem`, `*.key`, `secrets/` | tajomstvá nemajú byť v kontexte; `.env.example` ostáva čitateľný |

`deny` na tajomstvá a `protect-secrets.sh` sa prekrývajú zámerne. Pravidlo vynucuje Claude Code a je jednoduchšie, hook vie modelu vysvetliť, čo má spraviť inak, a pokryje aj vzory, ktoré sa pravidlom zapisujú ťažko. Ani jedno nezastaví skript, ktorý si súbor otvorí sám. Na to je sandbox ([kapitola 4.4](../04-bezpecnost.md#44-sandbox-a-kontajner)).

`allow` z projektového `settings.json` začne platiť až potom, čo pri prvom otvorení repa potvrdíš dôveru. `deny` a `ask` platia hneď.

## Hooks (`.claude/settings.json` + `.claude/hooks/`)

| Súbor | Udalosť | Čo robí | Prečo hook a nie pokyn v CLAUDE.md |
|---|---|---|---|
| `protect-tests.sh` | `PreToolUse` Edit/Write | zablokuje úpravu testu, ktorý je už v gite; nové testy povolí | agent pod tlakom „sprav, nech testy prejdú“ rád upraví test |
| `protect-secrets.sh` | `PreToolUse` Read/Edit/Write | zablokuje `.env`, `*.pem`, `*.key`, `credentials*`; `.env.example` povolí | čo agent prečíta, je v kontexte a môže to odísť ďalej |
| `block-dangerous-bash.sh` | `PreToolUse` Bash | zablokuje force push, `git reset --hard`, `git clean -f`, `rm -rf .`, `DROP TABLE` | jedna chyba sa nedá vrátiť, „väčšinou to dodrží“ nestačí |
| `format-python.sh` | `PostToolUse` Edit/Write | `ruff format` na upravený `.py` súbor | formátovanie nemá stáť tokeny ani padať v CI |
| `tests-must-pass.sh` | `Stop` | ak sa zmenil kód mimo testov a `pytest` padá, agent neskončí a dostane posledných 20 riadkov. Keď sa zmenili len testy (TDD, fáza padajúceho testu) alebo nič, nezasahuje | „hotovo“ bez spustenia testov je najčastejšia chyba |
| `after-compact.sh` | `SessionStart` compact | po kompakcii vypíše vetvu, posledné commity, `git status` a `PLAN.md` | zhrnutie kompakcie je výber modelu, toto je stav z disku |
| `mask-card-numbers.py` | `UserPromptSubmit`, `PreToolUse` Read/Edit/Write, `PostToolUse` Bash/Grep/MCP | prompt s číslom karty neodošle, súbor s kartami nepustí cez Read, zakáže zapísať skutočnú kartu do kódu a výstup z Bash, Grep a MCP nástrojov zamaskuje na `453201******0366` | čísla kariet nesmú do kontextu (PCI DSS); model „dá pozor“ až potom, čo ich už videl |
| `log-token-usage.py` | `SessionEnd` (osobné nastavenia) | po session zapíše tokeny podľa modelu, vrátane subagentov, do `~/.claude/token-log.csv`; ručne spustený vypíše súhrn poslednej session | `/cost` po zatvorení session zmizne, takto máš históriu úloh na porovnanie |

Ako sa správajú:
- Exit kód 2 v `PreToolUse` akciu zablokuje, text zo stderr dostane model ako vysvetlenie. Preto správy hovoria, čo má agent spraviť inak.
- `Stop` hook vracia JSON `{"decision": "block", "reason": "..."}`. Kontrola `stop_hook_active` zabráni nekonečnej slučke.
- Ochranné hooky (`protect-tests`, `protect-secrets`, `block-dangerous-bash`, `mask-card-numbers`) majú `"onFailure": "block"`: keď skript spadne alebo vyprší, akcia sa nevykoná. Bez toho by sa vykonala (vyžaduje Claude Code 2.1.295+).
- Výstup `SessionStart` hooku sa pridá do kontextu.

**Hranice:** `block-dangerous-bash.sh` je zoznam vzorov, nie sandbox. Príkaz zabalený do skriptu alebo zapísaný inak prejde. Je to poistka proti omylu, nie bezpečnostná hranica. Tou sú povolenia (`permissions.deny`), sandbox a kontajner.

**Hranice `mask-card-numbers.py`:** číslo karty spozná len podľa tvaru a Luhnovej kontroly, takže zachytí aj náhodné čísla, ktoré ňou prejdú, a nezachytí kartu rozdelenú inak ako medzerami či pomlčkami. Maskuje výstup nástrojov v matcheri `Bash|Grep|mcp__.*`. Nástroj, ktorý tam nie je, prejde bez maskovania, preto pri pridaní nového nástroja (napr. ďalšieho MCP servera s iným menom) skontroluj matcher. Pôvodný výstup nástroja zostáva v telemetrii a zablokovaný prompt v lokálnej histórii. Je to ochrana kontextu modelu, nie náhrada tokenizácie a maskovania v produkčných dátach.

**`log-token-usage.py` nie je v `settings.json`.** Je to meranie pre teba, nie pravidlo pre tím. Zapni si ho v `~/.claude/settings.json` alebo `.claude/settings.local.json` (pozri [B.4](../priloha-b-ceny-a-prikazy.md#b4-spotreba-na-jednu-ulohu)). Ukladá len čísla, názov session a vetvu, žiadny obsah konverzácie.

**Prispôsobenie:** `tests-must-pass.sh` spúšťa `python -m pytest -q`. Pri inom projekte zmeň príkaz (`npm test --silent`, `./gradlew test -q`). Pri pomalých testoch spúšťaj len rýchlu sadu, hook beží pri každom pokuse skončiť. Ak máš testy inde než v `tests/`, `test_*.py` alebo `*_test.py`, uprav aj vzor v `grep -Ev`, podľa ktorého hook rozozná zmenu kódu od zmeny testov.

## Skill `/ticket` (`.claude/skills/ticket/`)

Postup z kapitoly 1 hlavného textu ako príkaz: `/ticket BUG-142`. Skill vloží aktuálny `git status` a posledné commity, prečíta ticket a príslušné body `SPEC.md`, navrhne plán a **počká na schválenie**. Potom ide test, ktorý padá, najmenšia oprava a dôkaz.

- `disable-model-invocation: true`: spustíš ho len ty, model ho sám nezavolá, lebo mení kód.
- `allowed-tools`: testy a čítacie git príkazy beží bez pýtania, úpravy súborov sa riadia režimom povolení.
- Predpokladá štruktúru ako v `cvicenie/` (`tickets/`, `SPEC.md`, pytest). Pre iný projekt zmeň cesty a príkaz na testy.

Ako skill napísať a otestovať, je v [3.6](../03-building-blocks.md#36-vlastny-skill-krok-za-krokom).

## Subagenti (`.claude/agents/`)

| Súbor | Na čo | Prečo práve subagent |
|---|---|---|
| `explorer.md` | „kde a ako je implementované X“ | veľa čítania, krátky výsledok; len na čítanie, lacný model |
| `spec-reviewer.md` | porovnať diff so špecifikáciou pred commitom | nevidel priebeh práce, neovplyvnia ho zdôvodnenia autora; s `memory: project` si pamätá opakované chyby |
| `test-verifier.md` | overiť, že nové testy bez opravy padajú a s ňou prechádzajú | presne to, čo hlavný agent rád preskočí; robí to v oddelenom kontexte |

Použitie v session:

```text
@agent-explorer zisti, kde všade sa počíta DPH a či sa zaokrúhľuje skôr než na konci.
@agent-spec-reviewer skontroluj diff oproti BUG-142 a SPEC.md.
@agent-test-verifier over nové testy v tests/test_bug142.py.
```

Cez `@` preto, že tak sa spustí určite tento agent. Pri `explorer` by si inak Claude mohol vybrať vstavaný `Explore` (pozri [vyššie](#vstavani-a-vlastni-agenti)).

`test-verifier` dočasne odkladá zmeny cez `git stash`. Pri necommitnutých zmenách to rob na vetve, kde ťa to neprekvapí, a po skončení skontroluj `git status`.

## Overené

Skripty hookov som skúsil s ukážkovým JSON vstupom (blokovanie aj povolenie). V živej session Claude Code ani v CI neboli spustené.

`log-token-usage.py` som spustil na skutočných transcriptoch Claude Code 2.1.301 (ručne aj so vstupom ako zo `SessionEnd` hooku), vrátane session so subagentmi.
