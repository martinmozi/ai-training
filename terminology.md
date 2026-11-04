# Terminológia školenia

Prehľad hlavných častí školenia cez pojmy: čo ktorý pojem znamená, kam patrí a s čím sa najčastejšie zamieňa. Úplný abecedný zoznam pojmov a skratiek je v [slovníku](LLM/slovnik.md), podrobné vysvetlenia v kapitolách, na ktoré sa odkazuje.

## Vrstvy: od matice čísel po Claude Code

Väčšina nedorozumení vzniká tým, že sa pojmy z rôznych vrstiev miešajú. Školenie ide zdola nahor:

| Vrstva | Čo to je | Príklad | Kde |
|---|---|---|---|
| **Neurónová sieť** | funkcia s miliónmi až biliónmi naučených čísel (váh) | sieť na rozpoznávanie číslic | [LLM 1](LLM/1_neuronove-siete.md) |
| **Model (LLM)** | neurónová sieť typu transformer, ktorá z tokenov predpovedá ďalší token | Claude Opus, Llama, OLMo | [LLM 2](LLM/2_transformer-topology.md), [LLM 3](LLM/3_trening-a-inferencia.md) |
| **API** | služba, ktorá model spúšťa (inferencia) a prijíma requesty | Anthropic Messages API | [LLM 5](LLM/5_od-modelu-k-agentovi.md) |
| **Agent** | program, ktorý v slučke volá API a vykonáva nástroje, ktoré si model vyžiada | mini-agent z cvičenia | [LLM 5](LLM/5_od-modelu-k-agentovi.md) |
| **Produkt** | agent s nástrojmi, povoleniami, pamäťou a rozhraním | Claude Code, GitHub Copilot | [AI using](AI%20using/README.md) |

Model sám nič nečíta, nespúšťa ani si nepamätá. To všetko robí agent okolo neho.

## Časť 1: Ako fungujú LLM

### Neurónové siete ([kapitola 1](LLM/1_neuronove-siete.md))

- **Váha / parameter** – jedno naučené číslo. „7B model“ má 7 miliárd váh.
- **Neurón, vrstva** – vážený súčet vstupov + aktivačná funkcia. Vrstva je v praxi násobenie maticou.
- **Loss** – číslo, ktoré hovorí, ako veľmi sa model mýli. Tréning ho znižuje.
- **Gradient, backpropagation** – ktorým smerom pohnúť každou váhou, aby loss klesol, a ako sa to spočíta od výstupu späť.
- **Optimalizátor (SGD, Adam)** – pravidlo, ako podľa gradientu váhy naozaj zmeniť.
- **Overfitting** – sieť si zapamätá trénovacie príklady namiesto pravidiel. Preto sa meria na dátach, ktoré pri tréningu nevidela.

### Transformer ([kapitola 2](LLM/2_transformer-topology.md))

- **Token** – kúsok textu (zvyčajne časť slova), nie slovo ani znak. V tokenoch sa meria kontext aj cena.
- **Embedding** – vektor, ktorým model reprezentuje token.
- **Attention** – jediné miesto, kde si tokeny navzájom odovzdávajú informácie.
- **FFN** – časť bloku, ktorá spracuje každý token samostatne. Obsahuje väčšinu parametrov.
- **Kontextové okno** – koľko tokenov model spracuje naraz. Patrí doň všetko: systémový prompt, definície nástrojov, história, odpoveď.
- **KV cache** – uložené medzivýsledky už spracovaných tokenov, aby sa pri generovaní nepočítali znova. Na nej stojí **prompt caching**.
- **MoE, kvantizácia** – spôsoby, ako zmenšiť výpočet alebo pamäť: použiť len časť modelu na token / uložiť váhy s menej bitmi.

### Tréning a inferencia ([kapitola 3](LLM/3_trening-a-inferencia.md))

Toto je najdôležitejšie rozlíšenie celého školenia:

| | **Tréning** | **Inferencia** |
|---|---|---|
| čo sa deje | váhy sa menia, aby model lepšie predpovedal ďalší token | model s pevnými váhami generuje odpoveď |
| kto to robí | výrobca modelu, raz za mesiace | API pri každom requeste |
| cena | milióny dolárov, tisíce GPU | centy za request, platí sa za tokeny |
| čo si model „zapamätá“ | všetko, čo sa dostalo do váh | nič, po requeste je všetko preč |

**Inferencia LLM** teda znamená: prompt sa rozdelí na tokeny, model ho spracuje naraz (**prefill**), potom generuje po jednom tokene (**decode**), kým nevygeneruje `<eos>` alebo nenarazí na `max_tokens`. Každý nový token sa pridá na vstup a celý krok sa opakuje. Keď Claude Code „premýšľa“ alebo „píše kód“, beží inferencia.

Ďalšie pojmy tejto kapitoly:

- **Pretraining → base model** – tréning na biliónoch tokenov textu. Výsledok vie dopĺňať text, ale nie je asistent.
- **Post-training (SFT, DPO, RL) → instruct model** – doučenie, z ktorého vznikne asistent, ktorý plní pokyny.
- **Chat šablóna** – rozhovor sa modelu podáva ako jeden text so špeciálnymi tokenmi pre role (systém, používateľ, asistent, nástroj).
- **Teplota, top-p** – miera náhody pri výbere ďalšieho tokenu. Preto rovnaká otázka dáva rôzne odpovede.
- **Reasoning (thinking), effort** – model pred odpoveďou generuje „premýšľacie“ tokeny. Je to stále inferencia, len dlhšia, a tieto tokeny sa platia.

### Hranice AI ([kapitola 4](LLM/4_ai_constraints.md))

- **Halucinácia** – presvedčivo napísaná, ale nepravdivá odpoveď. Nie je to chyba, ktorá sa dá „opraviť“, ale dôsledok toho, že model generuje pravdepodobný text.
- **Prompt injection** – pokyn schovaný v dátach (súbor, web, issue), ktorý model vykoná, lebo pokyn od dát nerozlišuje.
- **Sykofancia** – model súhlasí s používateľom, aj keď sa mýli.
- **Kalibrácia** – či istota modelu zodpovedá tomu, ako často má pravdu.
- **In-context learning** – model sa „naučí“ z príkladov v prompte, ale váhy sa nemenia. Nie je to tréning.

### Od modelu k agentovi ([kapitola 5](LLM/5_od-modelu-k-agentovi.md))

- **Systémový prompt, správy, nástroje** – tri časti každého API requestu.
- **Tool / nástroj** – funkcia s menom, popisom a schémou. Model ju **nevykoná**, iba vygeneruje požiadavku `tool_use`. Vykoná ju agent a vráti `tool_result`.
- **Agentová slučka** – model → volanie nástroja → vykonanie → výsledok do kontextu → znova model, kým `stop_reason` nepovie, že je hotovo.
- **Štruktúrovaný výstup** – odpoveď, ktorá zaručene spĺňa JSON schému (vďaka constrained decoding).
- **Embedding textu, RAG** – vyhľadanie relevantných dokumentov podľa významu a ich vloženie do kontextu.
- **Agentic search** – agent namiesto RAG hľadá opakovane nástrojmi (grep, čítanie súborov). Tak pracuje Claude Code.
- **Eval** – sada úloh s kontrolou výsledku, podľa ktorej sa meria, či zmena pomohla.

## Časť 2: AI coding agenti v praxi

### Kontext ([kapitola 2](AI%20using/02-kontext.md))

- **Session** – jeden rozhovor s agentom. Celá jeho história sa posiela modelu pri každom kroku slučky.
- **Context rot** – kvalita klesá, keď je kontext dlhý a plný nepotrebného, aj keď sa do okna zmestí.
- **Kompakcia** – nahradenie histórie zhrnutím, aby sa uvoľnil kontext.
- **Checkpoint / rewind** – návrat kódu a konverzácie do skoršieho stavu.
- **Prompt caching** – opakovaný začiatok kontextu sa účtuje lacnejšie. Zmena na začiatku (napr. `CLAUDE.md`) cache zneplatní.

### Building blocks ([kapitola 3](AI%20using/03-building-blocks.md))

Všetky rozširujú agenta, ale každý inak:

| Pojem | Čo to je | Kedy ide do kontextu | Je vynútené? |
|---|---|---|---|
| **Pamäťový súbor** (`CLAUDE.md`, `AGENTS.md`) | pokyny pre projekt | vždy, na začiatku session | nie, model ho môže ignorovať |
| **Skill** | postup v `SKILL.md` | popis vždy, telo až keď treba | nie |
| **MCP server** | nástroje cudzieho systému (Jira, DB, prehliadač) | definície nástrojov (príp. cez tool search) | nie |
| **Subagent** | samostatný agent s vlastným prázdnym kontextom | do hlavného kontextu ide len jeho výsledok | nie |
| **Hook** | príkaz, ktorý spustí agent pri udalosti | nie je to text pre model | **áno**, vykoná sa vždy |
| **Plugin** | balík vyššie uvedeného na zdieľanie v tíme | podľa obsahu | podľa obsahu |

Pokyn v prompte alebo `CLAUDE.md` je **prosba**, hook alebo povolenie je **pravidlo**.

### Bezpečnosť ([kapitola 4](AI%20using/04-bezpecnost.md))

- **Režim povolení** – na čo sa agent pýta (`default`, `acceptEdits`, `plan`, `auto`, `bypassPermissions`).
- **Pravidlá allow / ask / deny** – konkrétne povolené, potvrdzované a zakázané nástroje a príkazy.
- **Sandbox** – hranica operačného systému okolo príkazov v shelli (súbory, sieť), platí aj pre procesy, ktoré príkaz spustí.
- **Prompt injection** – rovnaký pojem ako v časti 1, tu z pohľadu obrany: čo agent smie, keď ho dáta „presvedčia“.

### Postup práce ([kapitola 5](AI%20using/05-postup-prace.md))

- **Explore → Plan → Code → Commit** – odporúčaný postup, **plan mode** je režim, v ktorom agent iba číta a navrhuje.
- **TDD, overenie** – agent je hotový, až keď to overia testy, nie keď to tvrdí.
- **Worktree** – ďalší pracovný adresár repa na inej vetve, na paralelnú prácu viacerých agentov.
- **Headless režim** – agent bez interaktívneho rozhrania, napr. v CI (`claude -p`).

## Často zamieňané pojmy

| Zamieňa sa | Rozdiel |
|---|---|
| tréning × inferencia | tréning mení váhy, inferencia ich iba používa |
| fine-tuning × RAG × prompt | fine-tuning mení váhy, RAG a prompt menia iba kontext |
| model × agent | model generuje text, agent ho volá v slučke a vykonáva nástroje |
| volanie nástroja × vykonanie nástroja | model vygeneruje požiadavku, agent ju vykoná |
| token × slovo | slovenské slovo býva 2 tokeny, kontext aj cena sa merajú v tokenoch |
| kontextové okno × pamäť | okno je to, čo model vidí v jednom requeste, „pamäť“ agenta sú súbory, ktoré doň vloží |
| base model × instruct model | base dopĺňa text, instruct plní pokyny |
| reasoning × uvažovanie človeka | reasoning sú generované tokeny pred odpoveďou, nie skrytý proces |
| embedding tokenu × embedding textu | vektor jedného tokenu vnútri modelu / vektor celého textu z embedding modelu na vyhľadávanie |
| checkpoint (tréning) × checkpoint (agent) | uložené váhy modelu / uložený stav kódu a konverzácie |
| pokyn v `CLAUDE.md` × hook | pokyn model môže ignorovať, hook sa vykoná vždy |
| subagent × skill | subagent má vlastný kontext, skill sa načíta do toho istého kontextu |
