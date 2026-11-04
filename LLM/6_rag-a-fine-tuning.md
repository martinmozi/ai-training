# RAG a fine-tuning – ako dať modelu nové znalosti

Po tréningu sú váhy modelu zmrazené ([prečo](4_ai_constraints.md#keď-sa-doučí-niečo-nové-zabudne-niečo-iné)). Model nepozná vaše interné dokumenty, tickety ani nič, čo vzniklo po jeho tréningu. Nové znalosti sa dajú dodať dvoma spôsobmi:

- **do kontextu** – pred otázkou vyhľadať relevantné texty a vložiť ich do promptu (**RAG**),
- **do váh** – model doučiť na vlastných dátach (**fine-tuning**).

Kapitola najprv vysvetlí, ako sa texty vyhľadávajú podľa významu (embedding modely, BERT, reranker), potom celý RAG a nakoniec fine-tuning. Pojmy sú v [slovníku](slovnik.md).

## Embedding textu: jeden vektor pre celý odsek

V [kapitole 2](2_transformer-topology.md#tokeny-a-embeddingy) mal každý **token** svoj vektor. **Embedding model** robí to isté pre celý **text**: z vety alebo odseku vyrobí jeden vektor (napr. 1024 čísel). Texty s podobným významom majú podobné vektory, aj keď nezdieľajú ani jedno slovo („faktúra po splatnosti“ a „neuhradený doklad“).

Podobnosť sa meria **kosínusovou podobnosťou**, teda uhlom medzi vektormi:

```
cos(a, b) = (a · b) / (|a| · |b|)       1 = rovnaký smer, 0 = nesúvisia
```

Embedding modely vektory väčšinou normalizujú na dĺžku 1. Potom je kosínusová podobnosť obyčajný skalárny súčin a porovnanie otázky s miliónom textov je jedno násobenie maticou.

Príklad s 3-rozmernými vektormi (skutočné majú stovky až tisícky čísel):

| Text | Vektor | cos s otázkou |
|---|---|---|
| otázka: „ako zaplatiť faktúru po splatnosti?“ | (0,8; 0,6; 0,0) | – |
| „Neuhradený doklad uhraďte do 7 dní…“ | (0,7; 0,7; 0,1) | **0,98** |
| „Dovolenka sa žiada cez portál…“ | (0,0; 0,2; 0,98) | 0,12 |

Jednotlivé čísla vektora nemajú ľudský význam. Význam má iba **vzdialenosť** medzi vektormi.

## Ako funguje embedding model

Embedding model je **transformer**, rovnaké bloky (attention + FFN) ako v [kapitole 2](2_transformer-topology.md). Líši sa v troch veciach:

| | LLM (decoder-only) | Embedding model (encoder, BERT) |
|---|---|---|
| Attention | kauzálna maska, token vidí iba doľava | **obojsmerná**, každý token vidí celý text |
| Výstup | LM head → pravdepodobnosti ďalšieho tokenu | **pooling** → jeden vektor za celý text |
| Tréning | predpovedať ďalší token | **kontrastívne**: podobné texty k sebe, rôzne od seba |
| Veľkosť | miliardy parametrov | typicky 20M – 600M, novšie až 8B |

### BERT: encoder, ktorý vidí oboma smermi

**BERT** (Google, 2018) je transformer bez kauzálnej masky. Predtrénuje sa úlohou **MLM** (*masked language modeling*): v texte sa náhodne zakryje ~15 % tokenov a model ich háda.

```
vstup:   Faktúru treba [MASK] do konca mesiaca.
cieľ:    [MASK] = uhradiť
```

Na uhádnutie potrebuje model vidieť slová **pred aj za** maskou. Preto má každý výstupný vektor informáciu z celej vety. Na generovanie textu sa BERT nehodí, na porozumenie a porovnávanie textu áno.

### Pooling: z n vektorov jeden

Transformer vráti pre text s *n* tokenmi maticu **n × d** (vektor pre každý token). Embedding potrebuje jeden vektor, preto sa robí **pooling**:

- **mean pooling** – priemer vektorov všetkých tokenov (najčastejšie),
- **[CLS] token** – BERT pridá na začiatok špeciálny token `[CLS]`, ktorý cez attention „zbiera“ informáciu z celej vety, a použije sa jeho vektor,
- **posledný token** – pri embedding modeloch z decoder-only LLM (vidí všetky predchádzajúce tokeny, takže iba on má informáciu z celého textu).

### Kontrastívny tréning: čo znamená „podobný“

Samotný BERT po MLM dáva na porovnávanie viet zlé vektory. Zlom priniesol **Sentence-BERT** (2019): model sa doučí na pároch textov, ktoré k sebe patria:

```
(otázka, odsek s odpoveďou)        (nadpis, článok)        (dve parafrázy tej istej vety)
```

Jeden krok tréningu s dávkou 4 párov:

```
                 dok1   dok2   dok3   dok4
otázka1   →     [0,9]   0,2    0,1    0,3      cieľ: najvyššie skóre na diagonále
otázka2   →      0,1   [0,8]   0,4    0,2
otázka3   →      0,3    0,1   [0,7]   0,5
otázka4   →      0,2    0,3    0,6   [0,4]   ← chyba, dok3 je bližšie ako správny dok4
```

Každý riadok je kosínusová podobnosť otázky so všetkými dokumentmi v dávke. Na riadok sa použije [softmax a cross-entropy](cvicenie/softmax-cross-entropy.md) so správnou triedou na diagonále. Gradient priťahuje správne páry k sebe a ostatné (**negatívy**) od seba. Ostatné dokumenty v dávke slúžia ako negatívy zadarmo (*in-batch negatives*), preto sa trénuje s veľkými dávkami. Najviac sa model naučí z **ťažkých negatívov**, textov podobných, ale nesprávnych („faktúra za elektrinu“ vs. „faktúra za plyn“).

Moderné embedding modely prejdú dvoma fázami: kontrastívny tréning na stovkách miliónov párov z webu (otázky a odpovede z fór, nadpisy a články) a doladenie na menšom kvalitnom datasete s ťažkými negatívmi.

### Embedding modely z LLM

Novšie najlepšie modely nevychádzajú z BERT, ale z **decoder-only LLM** (Qwen, Mistral). Zoberie sa malý LLM, odstráni sa LM head, ako embedding sa použije vektor posledného tokenu a model sa kontrastívne doučí. Výhoda: LLM už „rozumie“ mnohým jazykom a doménam. Nevýhoda: je väčší a pomalší.

| Model | Základ | Parametre | Rozmer vektora | Poznámka |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | BERT | 22M | 384 | malý, rýchly, iba angličtina |
| multilingual-e5-large | XLM-RoBERTa (BERT) | 560M | 1024 | viacjazyčný, aj slovenčina |
| BGE-M3 | XLM-RoBERTa (BERT) | 568M | 1024 | viacjazyčný, vstup do 8192 tokenov |
| Qwen3-Embedding | Qwen3 (LLM) | 0,6B / 4B / 8B | 1024 / 2560 / 4096 | špička benchmarku MTEB |
| text-embedding-3-small / large | OpenAI, cez API | neuvedené | 1536 / 3072 | platí sa za token |

Pri výbere modelu treba myslieť na:

- **Jazyk.** Anglický model na slovenských textoch funguje zle. Pre slovenčinu treba viacjazyčný model.
- **Maximálna dĺžka vstupu.** Klasický BERT spracuje 512 tokenov, zvyšok **potichu oreže**.
- **Prefixy otázky a dokumentu.** Niektoré modely chcú `query: …` a `passage: …` (e5) alebo inštrukciu pred otázkou (Qwen3). Bez nich sú výsledky horšie.
- **Rovnaký model pre otázky aj dokumenty.** Vektory rôznych modelov sa nedajú porovnať. Zmena modelu = znova prepočítať celý index.

## Bi-encoder a cross-encoder (reranker)

Embedding model, ktorý zakóduje otázku a dokument **zvlášť**, sa volá **bi-encoder**. Vektory dokumentov sa vypočítajú raz vopred, pri otázke sa počíta iba jeden vektor. Je to rýchle, ale otázka a dokument sa v attention nikdy „nestretnú“. Celý odsek sa musí stlačiť do jedného vektora a detaily sa stratia.

**Cross-encoder** (**reranker**) dostane otázku a dokument **spolu** v jednom vstupe a vráti jedno číslo, mieru relevantnosti:

```
bi-encoder:     [otázka]  → BERT → vektor ┐
                                          ├→ kosínus → skóre
                [dokument]→ BERT → vektor ┘       (dokumenty vopred)

cross-encoder:  [CLS] otázka [SEP] dokument → BERT → [CLS] → skóre
                (attention medzi každým slovom otázky a dokumentu)
```

Cross-encoder je výrazne presnejší, lebo attention porovná priamo slová otázky so slovami dokumentu. Nedá sa však nič predpočítať, pre každý pár treba celý prechod modelom. Na milión dokumentov je príliš pomalý.

Preto sa v praxi kombinujú dva kroky:

1. **Retrieval** – bi-encoder (a BM25, pozri nižšie) rýchlo nájde 50 – 100 kandidátov z miliónov.
2. **Reranking** – cross-encoder ich preskóruje a ponechá 3 – 10 najlepších.

Príklady rerankerov: `bge-reranker-v2-m3` (viacjazyčný, open), Cohere Rerank, Voyage Rerank (cez API).

## Vektorová databáza

Pri tisícoch až stovkách tisíc kúskov stačí porovnať otázku so všetkými (jedno násobenie maticou, milisekundy). Pri miliónoch sa používa **približné vyhľadávanie** (ANN, *approximate nearest neighbors*). Najbežnejší je **HNSW**: vektory tvoria graf, v ktorom je každý prepojený s niekoľkými blízkymi susedmi, a hľadanie po ňom „skáče“ k otázke. Nájde takmer vždy tie isté výsledky ako úplné porovnanie, ale stokrát rýchlejšie.

Bežné riešenia: **pgvector** (rozšírenie PostgreSQL), Qdrant, Chroma, FAISS (knižnica), Elasticsearch/OpenSearch. Ku každému vektoru sa ukladá aj pôvodný text a **metadáta** (zdroj, dátum, oprávnenia), podľa ktorých sa dá filtrovať.

## Hybridné vyhľadávanie: vektory + kľúčové slová

Embeddingy sú slabé na **presné reťazce**: kódy chýb (`ERR-4711`), čísla zmlúv, mená, identifikátory. Vektor zachytí „je to o chybe“, ale nie konkrétne číslo. Klasické fulltextové vyhľadávanie **BM25** (skóre podľa toho, koľkokrát sa slovo otázky v texte vyskytuje a aké je vzácne) ich nájde spoľahlivo.

**Hybridné vyhľadávanie** spustí oboje a poradia spojí, najčastejšie cez **RRF** (*reciprocal rank fusion*):

```
skóre(dokument) = 1 / (60 + poradie vo vektorovom hľadaní) + 1 / (60 + poradie v BM25)
```

Dokument, ktorý je vysoko v oboch zoznamoch, vyhrá. Hybrid je v praxi takmer vždy lepší než samotné vektory.

## RAG krok po kroku

**RAG (Retrieval-Augmented Generation)** spája všetko vyššie:

```
PRÍPRAVA (raz)                         OTÁZKA (vždy)
dokumenty                              otázka používateľa
   ↓ rozdelenie na kúsky (chunking)       ↓ (prepis na samostatnú otázku)
kúsky                                  embedding otázky
   ↓ embedding model                      ↓ hybridné hľadanie → top 50
vektory + text + metadáta                 ↓ reranker → top 5
   ↓                                      ↓
vektorová databáza  ─────────────────→  prompt: pokyny + kúsky + otázka
                                          ↓
                                        LLM → odpoveď s citáciami
```

1. **Chunking (rozdelenie na kúsky).** Typicky 200 – 800 tokenov s malým prekryvom, najlepšie podľa štruktúry (nadpisy, odseky), nie naslepo po znakoch. Príliš malý kúsok nemá kontext („Lehota je 7 dní.“ – aká lehota?). Príliš veľký mieša viac tém a jeho vektor je „rozmazaný“. Pomáha pridať ku každému kúsku názov dokumentu a nadpis kapitoly.
2. **Indexovanie.** Každý kúsok sa premení na vektor a uloží sa s textom a metadátami.
3. **Prepis otázky.** V konverzácii je otázka často neúplná („a koľko to stojí?“). Model ju najprv prepíše na samostatnú otázku, až potom sa hľadá.
4. **Vyhľadanie a reranking.** Hybridné hľadanie, reranker, filter podľa metadát (napr. iba dokumenty, ku ktorým má používateľ prístup).
5. **Generovanie.** Nájdené kúsky sa vložia do kontextu s pokynom „odpovedz iba z týchto textov, cituj zdroj, a ak tam odpoveď nie je, povedz to“.

Model potom fakt nemusí „vytiahnuť z váh“, stačí ho prečítať cez attention. To je najúčinnejšia ochrana proti halucináciám (pozri [čo pomáha](4_ai_constraints.md#čo-pomáha)).

Jadro retrievalu s knižnicou `sentence-transformers`:

```python
from sentence_transformers import SentenceTransformer, CrossEncoder

emb = SentenceTransformer("intfloat/multilingual-e5-large")
rerank = CrossEncoder("BAAI/bge-reranker-v2-m3")

docs = [...]                                        # kúsky textu
D = emb.encode(["passage: " + d for d in docs], normalize_embeddings=True)

def hladaj(otazka, k=50, top=5):
    q = emb.encode("query: " + otazka, normalize_embeddings=True)
    kandidati = (D @ q).argsort()[::-1][:k]         # kosínus = skalárny súčin
    skore = rerank.predict([(otazka, docs[i]) for i in kandidati])
    return [docs[kandidati[i]] for i in skore.argsort()[::-1][:top]]
```

### Kde RAG zlyháva

- **Vyhľadanie netrafí.** Ak správny kúsok nie je medzi nájdenými, model odpovie z váh alebo si vymyslí. Väčšina chýb RAG je v retrievale, nie v modeli. Preto treba merať zvlášť **retrieval** (je správny kúsok v top 5? metrika *recall@k*) a zvlášť **odpoveď** (pozri [evaly](5_od-modelu-k-agentovi.md#evaly-ako-vedieť-že-zmena-pomohla)).
- **Otázky na agregáciu.** „Koľko ticketov sme mali v marci?“ RAG nájde 5 kúskov, nie všetky tickety. Na to patrí SQL alebo nástroj, nie vektory.
- **Zastarané a protichodné dokumenty.** Ak sú v indexe dve verzie smernice, model môže citovať starú. Pomáha dátum v metadátach a čistenie zdrojov.
- **Oprávnenia.** Vyhľadávanie musí filtrovať podľa práv používateľa, inak RAG vyzradí, čo by vidieť nemal.
- **Prompt injection.** Nájdené dokumenty sú nedôveryhodný vstup a môžu obsahovať pokyny (pozri [prompt injection](4_ai_constraints.md#5-prompt-injection--model-nerozlišuje-pokyn-od-dát)).

### Prečo coding agenti RAG väčšinou nepoužívajú

Kód obsahuje presné identifikátory, takže `grep` nájde `def zlava` spoľahlivejšie ako vektorová podobnosť. Agent navyše môže hľadať opakovane: nájde funkciu, prečíta ju, uvidí volanie inej funkcie a hľadá ďalej. Tomu sa hovorí **agentic search** (pozri [agentová slučka](5_od-modelu-k-agentovi.md#agentová-slučka)). RAG sa hodí na veľké zbierky dokumentov (wiki, manuály, tickety), ktoré sa do kontextu nezmestia a nedajú sa prehľadávať `grep`om. Dá sa to aj kombinovať: RAG ako jeden z nástrojov agenta (`search_docs`), ktorý agent volá, keď ho potrebuje.

## Fine-tuning: zmena váh

**Fine-tuning** je pokračovanie tréningu natrénovaného modelu na vlastných dátach. Technicky je to to isté ako [SFT](3_trening-a-inferencia.md#instruct-tréning-ako-sa-z-dopĺňača-textu-stane-asistent): príklady „vstup → požadovaný výstup“, cross-entropy na tokenoch odpovede, gradient, Adam. Bežne stačí stovky až tisíce príkladov.

### Plný fine-tuning a LoRA

Plný fine-tuning mení všetky váhy. Potrebuje ~16 B pamäte na parameter (váhy, gradienty, stavy Adamu), 7B model teda 110 GB+ ([výpočet](priloha_olmo.md#koľko-stojí-tréning)).

**LoRA** (*Low-Rank Adaptation*) pôvodné váhy zmrazí a ku každej vybranej matici W pridá malú opravu ako súčin dvoch úzkych matíc:

```
W' = W + B · A          W: 4096 × 4096  (zmrazená, 16,8M čísel)
                        B: 4096 × 16,  A: 16 × 4096  (trénujú sa, spolu 131k čísel)
```

Číslo 16 je **rank** *r* (bežne 8 – 64). Trénuje sa menej než 1 % parametrov, gradienty a stavy Adamu sú iba pre ne. Výsledný „adaptér“ má desiatky MB, dá sa prepínať nad jedným základným modelom a pri inferencii sa dá k W pripočítať, takže nič nespomalí.

**QLoRA** navyše drží zmrazený základný model [kvantizovaný](2_transformer-topology.md#dve-varianty-ktoré-stretnete-v-praxi) na 4 bity. 7B model sa tak dá doučiť na jednej spotrebiteľskej GPU s 24 GB.

### Na čo sa fine-tuning hodí a na čo nie

| Hodí sa | Nehodí sa |
|---|---|
| **forma**: štýl, tón, pevný formát výstupu | **nové fakty**: model sa ich z pár príkladov učí zle a viac halucinuje |
| **úzka opakovaná úloha**: klasifikácia, extrakcia údajov | **meniace sa dáta**: každá zmena = nový tréning |
| **menší a lacnejší model**, ktorý napodobní veľký na jednej úlohe (destilácia) | **citácie zdrojov**: z váh sa nedá povedať, odkiaľ fakt pochádza |
| **doménový jazyk**: odborné skratky, interný žargón | **oprávnenia**: čo je vo váhach, vidí každý používateľ |

Štúdia Gekhman a kol. (2024) ukázala, že keď sa model fine-tuningom učí fakty, ktoré z pretrainingu nepoznal, učí sa ich pomaly a zároveň začne viac halucinovať aj pri ostatných otázkach. Fine-tuning mení skôr **ako** model odpovedá, nie **čo** vie.

**Riziká:**

- **Katastrofické zabúdanie** – zlepšenie na novej úlohe zhorší iné schopnosti ([kapitola 4](4_ai_constraints.md#keď-sa-doučí-niečo-nové-zabudne-niečo-iné)). LoRA ho zmierňuje, ale neodstraňuje.
- **Strata bezpečnostného správania** – už fine-tuning na pár desiatkach neškodných príkladov dokáže oslabiť odmietanie škodlivých požiadaviek (Qi a kol., 2023).
- **Preučenie** – pri malom datasete sa model naučí príklady naspamäť ([kapitola 1](1_neuronove-siete.md#generalizácia-a-preučenie)).

Pri uzavretých modeloch (Claude, GPT) je fine-tuning cez API obmedzený alebo nedostupný. Claude Code ani Copilot si nefine-tunujete, ich správanie meníte promptom, pamäťovými súbormi, skillmi a nástrojmi.

### Fine-tuning embedding modelu a rerankera

Často najlacnejšie zlepšenie RAG nie je doučiť LLM, ale **embedding model alebo reranker** na vlastnej doméne. Stačí niekoľko tisíc párov (otázka, správny kúsok), ktoré sa dajú aj vygenerovať: LLM ku každému kúsku dokumentácie napíše otázky, na ktoré odpovedá. Tréning je ten istý kontrastívny ako vyššie a model s 500M parametrami sa doučí na jednej GPU za desiatky minút.

## Prompt, RAG alebo fine-tuning?

Začnite od najjednoduchšieho a ďalší krok pridajte, až keď ho eval ukáže ako potrebný:

| Potreba | Riešenie |
|---|---|
| model nevie, ako má odpovedať (formát, rola, pravidlá) | **prompt**, príklady v prompte (*few-shot*), štruktúrovaný výstup |
| model nepozná vaše dokumenty, ktoré sa zmestia do kontextu | vložiť ich celé do **kontextu** (+ prompt caching) |
| dokumentov je priveľa alebo sa často menia | **RAG** |
| odpovede treba citovať a overovať | **RAG** |
| úloha je úzka, opakuje sa miliónkrát a prompt je drahý alebo pomalý | **fine-tuning** menšieho modelu |
| RAG nenachádza správne kúsky v špecifickej doméne | **fine-tuning embedding modelu / rerankera** |

RAG a fine-tuning sa nevylučujú: fine-tuning naučí model formu a prácu so zdrojmi, RAG mu dodá aktuálne fakty.

## Zhrnutie

| Pojem | V jednej vete |
|---|---|
| embedding textu | transformer (BERT alebo LLM) + pooling → jeden vektor, podobný význam = malý uhol |
| kontrastívny tréning | páry, ktoré k sebe patria, sa priťahujú, ostatné v dávke sa odpudzujú |
| bi-encoder | otázka a dokument zvlášť, dokumenty vopred → rýchly, menej presný |
| cross-encoder (reranker) | otázka a dokument spolu cez attention → presný, iba na desiatky kandidátov |
| hybridné hľadanie | vektory na význam + BM25 na presné reťazce, spojené cez RRF |
| RAG | nájdi správne kúsky, vlož ich do kontextu, odpovedaj s citáciami |
| fine-tuning / LoRA | doučenie váh, mení skôr formu než znalosti, riziko zabúdania |
