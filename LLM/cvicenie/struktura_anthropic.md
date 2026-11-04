# Štruktúra Anthropic Messages API

> **Súvisí s:** [Cvičenie: vlastný mini-agent](mini-agent.md) · **Kód:** [mini-agent/agent.py](mini-agent/agent.py)

Messages API nie je „otázka → odpoveď“. Je to **zoznam správ, kde obsah každej správy je pole typovaných blokov**.
Práve preto sa dá nad ním postaviť agent: model do odpovede vloží blok `tool_use`, program ho vykoná a vráti blok `tool_result`.

Ak si chcete pozrieť reálne dáta, spustite mini-agenta a otvorte `api_log.json` — pre každý krok je tam celý
`request` aj celá `response`.

---

## 1. Request

```json
{
  "model": "claude-opus-5-5",
  "max_tokens": 16000,
  "system": "Si programátorský agent ...",
  "tools": [ { "name": "read_file", "description": "...", "input_schema": { ... } } ],
  "messages": [
    { "role": "user", "content": "Oprav chybu, kvôli ktorej padajú testy." }
  ]
}
```

| Pole | Význam | Use case |
|---|---|---|
| `model` | identifikátor modelu | prepínanie silnejší/lacnejší model v evaloch |
| `max_tokens` | strop **výstupu** jedného volania | ochrana proti nekonečnej odpovedi; pri prekročení príde `stop_reason: max_tokens` |
| `system` | systémový prompt (rola, pravidlá, formát) | stabilné správanie naprieč krokmi, bez opakovania v každej správe |
| `tools` | zoznam nástrojov so schémou vstupu | model sa podľa nich rozhodne, čo zavolať — **popis je prompt** |
| `messages` | celá história konverzácie | pamäť agenta; model je bezstavový a dostáva ju celú znova |
| `output_config` | nastavenia výstupu: `effort` (koľko má model „premýšľať“, `low` … `max`) a `format` (JSON schéma odpovede) | `agent.py` posiela `{"effort": "medium"}`; nižší effort = menej tokenov a krokov |

### Role

Základné sú dve: `user` a `assistant`, ktoré sa striedajú (viac správ rovnakej roly za sebou API spojí do jednej). Novšie modely (napr. Opus 5.5) prijímajú aj správu s rolou `system` uprostred `messages`: prevádzkovateľ tak môže pridať pokyn počas konverzácie bez zmeny horného `system` a bez zneplatnenia prompt cache.

- `user` — zadanie od človeka **aj výsledky nástrojov**
- `assistant` — čokoľvek vyprodukoval model

> Dôležité: výsledok nástroja má rolu `user`. Z pohľadu modelu je to vstup zvonka, nie jeho vlastná vedomosť —
> a teda potenciálne nedôveryhodné dáta (pozri prompt injection).

### Definícia nástroja

```json
{
  "name": "read_file",
  "description": "Vráti obsah textového súboru z projektu.",
  "strict": true,
  "input_schema": {
    "type": "object",
    "properties": { "path": { "type": "string", "description": "relatívna cesta, napr. faktura.py" } },
    "required": ["path"],
    "additionalProperties": false
  }
}
```

- Model vidí **iba meno, popis a schému** — nikdy nie implementáciu.
- `input_schema` je JSON Schema; `strict: true` + `additionalProperties: false` vynúti presný tvar vstupu.
- **Use case:** kvalitný popis (kedy nástroj použiť, čo nerobiť, formát parametrov) je najlacnejší spôsob,
  ako zmeniť správanie agenta — bez zásahu do kódu.

---

## 2. Response

```json
{
  "id": "msg_01...",
  "role": "assistant",
  "stop_reason": "tool_use",
  "content": [
    { "type": "thinking", "thinking": "...", "signature": "..." },
    { "type": "text", "text": "Pozriem sa na súbory projektu." },
    { "type": "tool_use", "id": "toolu_01A", "name": "list_files", "input": {} },
    { "type": "tool_use", "id": "toolu_01B", "name": "read_file", "input": { "path": "faktura.py" } }
  ],
  "usage": { "input_tokens": 1234, "output_tokens": 210, "cache_read_input_tokens": 0 }
}
```

`content` je **pole**, nie string. Preto sa v `agent.py` cyklí `for block in response.content`.

### Typy blokov

| Typ | Kde vzniká | Obsah | Use case |
|---|---|---|---|
| `text` | assistant | text pre používateľa | vysvetlenia, záverečné zhrnutie |
| `thinking` | assistant | interná úvaha + `signature` (na Opus 5.5 je thinking vždy zapnutý a text je predvolene prázdny, `display: "omitted"`) | lepšie uvažovanie pri zložitých úlohách; **posiela sa späť nezmenené**, inak sa reťaz úvah pretrhne |
| `tool_use` | assistant | `id`, `name`, `input` | požiadavka na vykonanie nástroja |
| `tool_result` | user | `tool_use_id`, `content`, `is_error` | odpoveď programu modelu |
| `image` / `document` | user | base64 alebo URL | screenshoty, PDF, logy ako príloha |

### `stop_reason`

| Hodnota | Čo znamená | Čo s tým v slučke |
|---|---|---|
| `tool_use` | model chce zavolať nástroj | vykonaj nástroje, pošli `tool_result`, pokračuj |
| `end_turn` | model dokončil odpoveď | ukonči slučku |
| `max_tokens` | odpoveď narazila na limit | zvýš `max_tokens` alebo rozdeľ úlohu |
| `refusal` | model požiadavku odmietol | preformuluj zadanie |
| `stop_sequence` | trafila sa zadaná stop sekvencia | vlastné ukončovanie formátov |
| `pause_turn` | server pozastavil dlhý ťah so serverovými nástrojmi (napr. web search) | pošli odpoveď späť a model pokračuje |
| `model_context_window_exceeded` | došlo kontextové okno | skráť alebo skompaktuj históriu |

**Use case:** `stop_reason` je jediný riadiaci signál agentovej slučky. Všetko ostatné je obsah.

### `usage`

`input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`.

- Vstup rastie s každým krokom, lebo sa posiela celá história → **sledovanie nákladov a dôvod na kompakciu kontextu**.
- Cache polia ukazujú, koľko kontextu sa čítalo z prompt cache (lacnejšie) — merateľný prínos stabilného prefixu
  (`system` + `tools` na začiatku).

---

## 3. Párovanie tool_use ↔ tool_result

Jeden celý cyklus v `messages`:

```json
[
  { "role": "user", "content": "Oprav chybu, kvôli ktorej padajú testy." },

  { "role": "assistant", "content": [
      { "type": "tool_use", "id": "toolu_01A", "name": "read_file", "input": { "path": "faktura.py" } }
  ]},

  { "role": "user", "content": [
      { "type": "tool_result", "tool_use_id": "toolu_01A", "content": "def zlava(...): ...", "is_error": false }
  ]},

  { "role": "assistant", "content": [ { "type": "text", "text": "Chyba je v delení ..." } ] }
]
```

Pravidlá:

1. Každý `tool_use` **musí** mať zodpovedajúci `tool_result` s rovnakým `tool_use_id` v nasledujúcej `user` správe.
2. Ak model vyžiada viac nástrojov naraz, všetky výsledky idú v **jednej** `user` správe (poradie blokov nemusí sedieť,
   párovanie je cez `id`).
3. Chyba nástroja sa nevyhadzuje von — vráti sa ako `tool_result` s `is_error: true` a textom chyby.
   **Use case:** zamietnuté povolenie („používateľ zápis zamietol“) je pre model len ďalší výsledok nástroja;
   presne takto fungujú povolenia v Claude Code.
4. Assistant odpoveď sa do histórie vracia **bez úprav** (vrátane `thinking` a `tool_use`).

---

## 4. Typické use casy podľa štruktúry

| Potreba | Čo v API použiť |
|---|---|
| Jednorazová odpoveď | `messages` s jednou `user` správou, žiadne `tools` |
| Chat | pridávaj `user`/`assistant` správy do rovnakého poľa |
| Agent | slučka nad `stop_reason == "tool_use"` + `tool_result` (toto robí `agent.py`) |
| Štruktúrovaný výstup | `output_config.format` s JSON schémou (formát je zaručený). Starší trik s vynúteným volaním nástroja (`tool_choice`) novšie modely ako Opus 5.5 nepodporujú; pri nástrojoch zaručí tvar argumentov `strict: true` |
| Dlhý stabilný kontext | konštantný prefix `system` + `tools` → prompt cache, viditeľné v `usage` |
| Obmedzenie nákladov | `max_tokens`, `effort`, skracovanie `tool_result` (v `agent.py` `MAX_VYSTUP`) |
| Bezpečnosť | validácia `input` v kóde (`cesta_v_projekte`), potvrdzovanie zápisov — nie dôvera v prompt |
| Ladenie a audit | log celých requestov a responses (`api_log.json`) |

---

## 5. Čo si odniesť

1. Obsah správy je **pole blokov**, nie text. Agent je možný práve vďaka tomu.
2. Model **nič nevykonáva** — vyprodukuje `tool_use` blok, vykoná ho váš kód.
3. Model je **bezstavový**: pamäť = pole `messages`, ktoré posielate celé pri každom kroku.
4. `tool_result` má rolu `user` → je to nedôveryhodný vstup, nie fakt.
5. `stop_reason` riadi slučku; `usage` ukazuje cenu.
