# Od modelu k agentovi – ako sa z LLM stane Claude Code

Predchádzajúce kapitoly popisujú model ako funkciu: dostane tokeny a vráti pravdepodobnosti ďalšieho tokenu. Nemá pamäť, nevie čítať súbory, nespúšťa príkazy. Claude Code a GitHub Copilot napriek tomu súbory čítajú, menia kód a spúšťajú testy. Táto kapitola ukazuje, ako sa to dá postaviť z toho, čo už poznáme. Na konci si to postavíme sami v cvičení [mini-agent](cvicenie/mini-agent.md). Pojmy sú v [slovníku](slovnik.md).

Krátka odpoveď: **agent = model + slučka + nástroje.** Všetko ostatné je inžinierstvo okolo toho.

## Čo model naozaj dostane: anatómia API requestu

Aplikácia komunikuje s modelom cez API. Jeden request na Claude API vyzerá takto:

```json
{
  "model": "claude-opus-5-5",
  "max_tokens": 16000,
  "system": "Si programátorský agent a pracuješ v malom Python projekte.",
  "tools": [
    { "name": "read_file",
      "description": "Vráti obsah textového súboru z projektu.",
      "input_schema": { "type": "object",
                        "properties": { "path": { "type": "string" } },
                        "required": ["path"] } }
  ],
  "messages": [
    { "role": "user", "content": "Prečo padajú testy?" }
  ]
}
```

| Časť | Čo to je |
|---|---|
| `system` | systémový prompt: rola, pravidlá, kontext projektu. Pamäťové súbory (`CLAUDE.md`, `copilot-instructions.md`) pridáva nástroj na začiatok kontextu: Claude Code ich posiela ako správu používateľa hneď za systémovým promptom, iné nástroje ich môžu vložiť priamo do `system`. |
| `tools` | zoznam nástrojov, ktoré model smie „zavolať“: meno, popis a JSON schéma parametrov |
| `messages` | celá doterajšia konverzácia: správy používateľa, odpovede modelu, volania nástrojov a ich výsledky |
| `max_tokens` | limit dĺžky odpovede |

Server z týchto častí poskladá **jeden text** v chat šablóne (pozri [instruct tréning](3_trening-a-inferencia.md#instruct-tréning-ako-sa-z-dopĺňača-textu-stane-asistent)), tokenizuje ho a pošle modelu. Odpoveď obsahuje vygenerované bloky, dôvod zastavenia `stop_reason` a spotrebu tokenov `usage`.

Model je **bezstavový**. Server si medzi requestami nič nepamätá (okrem prompt cache, ktorá iba šetrí výpočet). Ak má model vedieť, čo bolo predtým, aplikácia mu to musí poslať znova. Preto každý ďalší krok agenta posiela celú históriu a kontext rastie.

## Volanie nástroja je tiež len text

Model vie iba generovať tokeny. „Zavolať funkciu“ preto znamená, že model **vygeneruje text v dohodnutom formáte** a program okolo neho ho vykoná.

Ako to vyzerá na úrovni tokenov, ukazuje otvorený model Qwen (formát Claude nie je zverejnený, princíp je rovnaký):

```
<|im_start|>system
Máš k dispozícii tieto nástroje:
<tools>
{"name": "read_file", "description": "Vráti obsah súboru.", "parameters": {...}}
</tools><|im_end|>
<|im_start|>user
Prečo padajú testy?<|im_end|>
<|im_start|>assistant
Pozriem sa na kód.
<tool_call>
{"name": "read_file", "arguments": {"path": "faktura.py"}}
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
def zlava(suma, percento): ...
</tool_response><|im_end|>
<|im_start|>assistant
```

Postup:

1. Definície nástrojov sa vložia do promptu ako text. Model ich „vidí“ cez attention rovnako ako zadanie.
2. Model generuje token po tokene. Keď usúdi, že potrebuje súbor, vygeneruje značku `<tool_call>` a JSON s menom a argumentmi.
3. Generovanie sa zastaví a API vráti blok `tool_use` so `stop_reason: "tool_use"`.
4. **Program** (nie model) súbor prečíta a výsledok pošle späť ako blok `tool_result`.
5. Model pokračuje, teraz už s obsahom súboru v kontexte.

**Ako sa to model naučil:** rovnako ako všetko ostatné. V SFT videl tisíce rozhovorov s volaniami nástrojov (s maskovaným lossom iba na svojich tokenoch) a v RL riešil úlohy s nástrojmi a dostal odmenu, keď napríklad prešli testy. Preto sú dnešné modely v práci s nástrojmi dobré a modely spred pár rokov neboli.

**Dôsledky, ktoré priamo platia pre Claude Code a Copilot:**

- **Popis nástroja je prompt.** Model sa rozhoduje iba podľa mena, popisu a schémy. Zlý popis vedie k zlému použitiu.
- **Definície nástrojov zaberajú kontext** v každom requeste, aj keď sa nástroj nepoužije. Preto veľa MCP serverov spomaľuje a predražuje agenta.
- **Volanie môže byť halucinácia.** Model môže vymyslieť neexistujúcu cestu alebo nezmyselný argument. Program musí vstupy overiť (pozri `cesta_v_projekte()` v cvičení).
- **Výsledok nástroja je nedôveryhodný vstup.** Obsah súboru alebo webovej stránky ide do toho istého prúdu tokenov ako pokyny (pozri [prompt injection](4_ai_constraints.md#5-prompt-injection--model-nerozlišuje-pokyn-od-dát)).

## Agentová slučka

Keď model vie požiadať o nástroj, agent je iba slučka okolo neho:

```python
messages = [{"role": "user", "content": uloha}]
while True:
    odpoved = model(system, tools, messages)        # celý kontext odznova
    messages.append(odpoved)
    if odpoved.stop_reason != "tool_use":
        break                                       # model skončil
    vysledky = [vykonaj(volanie) for volanie in odpoved.tool_calls]
    messages.append({"role": "user", "content": vysledky})
```

Kód, ktorý naozaj beží, je funkcia `spusti()` v [cvicenie/mini-agent/agent.py](cvicenie/mini-agent/agent.py) (postup v cvičení [mini-agent](cvicenie/mini-agent.md)). Celý agent má aj s komentármi a logovaním okolo 240 riadkov. Claude Code aj Copilot v agent mode robia v jadre to isté. Líšia sa v inžinierstve okolo slučky:

| V mini-agentovi | V Claude Code / Copilote |
|---|---|
| 4 nástroje (`list_files`, `read_file`, `write_file`, `run_tests`) | desiatky nástrojov: Read, Edit, Bash, Grep, Glob, WebFetch, MCP servery |
| kontrola, že cesta neide mimo projektu | povolenia (allow/ask/deny), sandbox, kontajner |
| otázka „Povoliť zápis?“ | režimy povolení, schvaľovanie príkazov |
| `SYSTEM` reťazec v kóde | systémový prompt nástroja + `CLAUDE.md` / `AGENTS.md` / `copilot-instructions.md` |
| `MAX_KROKOV`, orezanie výstupu na 10 000 znakov | kompakcia kontextu, subagenti, tool search |
| nič | hooky: vlastný kód, ktorý sa spustí pred alebo po každom nástroji |

Keď tomuto mapovaniu rozumiete, druhá časť školenia bude o tom, **ako tieto časti nastaviť**, nie o mágii.

## Kontext ako pracovná pamäť agenta

Agent nemá inú pamäť než kontext. Všetko, čo zistil (prečítané súbory, výstupy testov, vlastné úvahy), je v `messages` a v každom kroku sa posiela znova. Z toho plynú tri problémy:

1. **Cena rastie rýchlejšie ako počet krokov.** Krok 30 posiela celú históriu krokov 1 až 29. Prompt caching zlacní opakujúci sa začiatok, ale nový obsah sa platí vždy.
2. **Kvalita klesá s dĺžkou** (context rot, pozri [prečo sa dlhý kontext zhoršuje](2_transformer-topology.md#prečo-sa-dlhý-kontext-zhoršuje-aj-keď-sa-doň-zmestí)).
3. **Okno je konečné.** Pri dlhej úlohe sa história nezmestí.

Techniky, ktoré to riešia, sa volajú **context engineering** a všetky uvidíte v Claude Code aj Copilote:

| Technika | Čo robí |
|---|---|
| **Cielené čítanie** | čítať časti súborov a výsledky `grep`, nie celé súbory a celé logy |
| **Orezanie výstupu nástroja** | dlhý výstup príkazu skrátiť skôr, než ide do kontextu |
| **Kompakcia** | keď sa kontext blíži k limitu, staršia história sa nahradí zhrnutím |
| **Subagent** | podúloha (napr. prieskum kódu) beží v **novom, prázdnom** kontexte. Hlavnému agentovi sa vráti iba krátky výsledok, nie všetko, čo subagent čítal |
| **Pamäťové súbory** | `CLAUDE.md` a podobné súbory sú iba text, ktorý nástroj na začiatku session vloží do kontextu (Claude Code ako prvú správu hneď za systémovým promptom). Model si nič „nezapamätá“, len si to v každej session znova prečíta |

## Štruktúrovaný výstup

Pri vlastných nadstavbách často netreba voľný text, ale dáta: JSON s poliami, klasifikáciu do kategórií, zoznam nájdených chýb. Prosba v prompte („odpovedz iba JSON-om“) väčšinou funguje, ale nie vždy.

**Štruktúrovaný výstup** to zaručí cez **constrained decoding**. Pri losovaní ďalšieho tokenu ([teplota a top-k](3_trening-a-inferencia.md#teplota-a-prečo-rovnaká-otázka-dáva-rôzne-odpovede)) sa logity tokenov, ktoré by porušili zadanú JSON schému, nastavia na −∞. Po softmaxe majú nulovú pravdepodobnosť a nikdy sa nevylosujú. Ak schéma hovorí, že ďalej musí prísť `"`, model nemôže napísať nič iné.

- V Claude API sa zapína cez `output_config.format` (JSON schéma odpovede) alebo `"strict": true` pri nástroji (argumenty zaručene zodpovedajú schéme, ako v cvičení).
- Zaručený je **formát**, nie **obsah**. JSON bude platný, ale hodnoty v ňom môžu byť stále halucinácia.
- Hodí sa na extrakciu dát, klasifikáciu a všade, kde výstup modelu číta ďalší program.

## RAG a fine-tuning

Ako dodať modelu znalosti, ktoré nemá vo váhach (vlastné dokumenty, embeddingy, vektorové vyhľadávanie, reranking), a kedy ho radšej doučiť, je v samostatnej [kapitole 6](6_rag-a-fine-tuning.md). Pre agentov je dôležité hlavne to, že **coding agenti RAG väčšinou nepoužívajú**: kód má presné identifikátory, takže ho hľadajú opakovane `grep`om a čítaním súborov (**agentic search**).

## Jedno volanie, workflow, alebo agent?

Agent je najdrahšia a najmenej predvídateľná možnosť. Pri vlastných nadstavbách sa oplatí začať od najjednoduchšej:

| Úroveň | Kto riadi postup | Príklad |
|---|---|---|
| **Jedno volanie** | nikto, jedna otázka, jedna odpoveď | zhrnutie ticketu, klasifikácia e-mailu, extrakcia údajov z faktúry |
| **Workflow** | **váš kód**: pevné kroky, model rieši každý krok zvlášť | review PR: 1. zhrň zmeny, 2. nájdi riziká, 3. napíš komentár |
| **Agent** | **model**: sám rozhoduje, aký nástroj zavolá a kedy skončí | „oprav padajúci test“, keď nie je jasné, kde je chyba |

Agent sa oplatí, keď úloha má veľa krokov, ktoré sa nedajú vopred napísať, a keď sa výsledok dá **overiť** (testy, kompilácia, review). Bez overenia sa chyby agenta prejavia až neskôr (pozri [ai_constraints.md](4_ai_constraints.md#3-regresia-k-priemeru-a-atrofia-zručností), pravidlo o overovaní).

## Evaly: ako vedieť, že zmena pomohla

Model je nedeterministický ([prečo](3_trening-a-inferencia.md#teplota-a-prečo-rovnaká-otázka-dáva-rôzne-odpovede)). Keď zmeníte systémový prompt, popis nástroja alebo model a agent jednu úlohu raz vyrieši, nehovorí to skoro nič. Mohla to byť náhoda.

**Eval** je sada úloh s automatickou kontrolou výsledku:

1. Zbierka 20 – 50 realistických úloh (napr. bugy z histórie projektu a testy, ktoré ich odhalia).
2. Kontrola, ktorá nepotrebuje človeka: prešli testy, JSON zodpovedá očakávaniu, odpoveď obsahuje správne číslo.
3. Každú úlohu spustiť viackrát a merať **úspešnosť**, **spotrebu tokenov** a **čas**.
4. Pri každej zmene promptu, nástrojov alebo modelu spustiť eval znova a porovnať.

Ak sa výsledok nedá overiť programom (kvalita textu, štýl), používa sa **LLM ako sudca**: iný model hodnotí odpoveď podľa presných kritérií. Je to lacné, ale sudca má vlastné chyby, preto treba jeho hodnotenia na vzorke skontrolovať človekom.

Bez evalu sa vlastný agent ladí naslepo. Pri Claude Code a Copilote spravili eval poskytovatelia. Pri vlastných skilloch, pamäťových súboroch a hookoch ho však robíte vy, aspoň neformálne: rovnaká úloha pred zmenou a po nej, niekoľkokrát.

## Zhrnutie

| Čo sme sa naučili o modeli | Čo to znamená pre agenta |
|---|---|
| model generuje iba tokeny | volanie nástroja je text, vykonáva ho program okolo modelu |
| model je bezstavový | agent posiela v každom kroku celú históriu, cena a kontext rastú |
| attention sa delí medzi všetky tokeny | menej, ale relevantného kontextu je lepšie ako veľa |
| všetko v kontexte je jeden prúd tokenov | obsah súborov a webu môže obsahovať pokyny (prompt injection) |
| model píše pravdepodobný text | výsledky treba overovať testami, nie dôverou |
| výber tokenu je náhodný | jedna úspešná skúška nestačí, merajte evalom |
