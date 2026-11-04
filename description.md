# Popis školenia

Školenie má dve nadväzujúce časti:

## 1. Ako fungujú veľké jazykové modely (LLM)

Vysvetľuje, čo sa deje vnútri modelu, aby bolo jasné, čo nástroje ako Claude Code a GitHub Copilot naozaj robia. Prechádza neurónové siete a to, ako sa učia, architektúru transformer (tokeny, attention, kontextové okno, KV cache) a tréning a inferenciu (teplota, instruct tréning, reasoning). Potom sa venuje hraniciam AI, ako sú halucinácie a prompt injection, a končí cestou od modelu k agentovi: volanie nástrojov, agentová slučka, RAG a evaly.

**Cvičenia:** vlastná neurónová sieť na rozpoznávanie číslic (MNIST) a jednoduchý coding agent postavený na Claude API.

## 2. AI coding agenti v praxi

Pre vývojárov, ktorí chcú Claude Code ovládať naplno: dostať od agenta zmeny, ktorým sa dá veriť, vedieť, koľko to stojí, a mať pod kontrolou, čo agent smie robiť. Témy:

- práca s kontextom a jeho cena
- building blocks: MCP, subagenti, hooky, skills, pluginy
- bezpečnosť: povolenia, sandbox, prompt injection
- postup práce: overovanie, debugovanie, worktrees, CI a kedy agenta nepoužiť

**Cvičenia:** na malej aplikácii na faktúry so skutočnými ticketmi (bugy a jedna nová funkcia). Súčasťou je hotová konfigurácia na skopírovanie a ťahák.

**Predpoklady:** základy programovania, git a príkazový riadok.

## Potrebná príprava

Pred školením si prosím priprav:

- **Python 3.12+** s balíkmi `numpy`, `matplotlib`, `pillow`, `pyqt5`, `anthropic`, `truststore` a `pytest` (alebo `uv sync` v priečinku každého cvičenia)
- **dataset mnist** z https://www.kaggle.com/datasets/hojjatk/mnist-dataset
- **Claude Code** nainštalovaný a prihlásený firemným účtom (`claude --version` funguje)
- **prístup ku Claude API** pre cvičenie s mini-agentom: API kľúč – firemná gateway
- **jq**, ktorý používa cvičenie s hookmi (voliteľné)
