# Poznámky pre lektora: ako fungujú LLM

> Účastníkom netreba. Druhá časť školenia má vlastné poznámky v [AI using/tutor.md](../AI%20using/tutor.md).

## Časový plán (celý deň, asi 7 hodín)

| Čas | Blok | Materiál |
|---|---|---|
| 0:00 | Úvod, cieľ, osnova | [README](README.md), `ai_practically.pptx` |
| 0:10 | Neurónové siete: neurón, vrstva, loss, backpropagation, Adam | [1](1_neuronove-siete.md) |
| 0:50 | **Live demo:** rozpoznávanie číslic | [rozpoznavanie-obrazkov.md](cvicenie/rozpoznavanie-obrazkov.md) (30–40 min) |
| 1:30 | *Prestávka* | |
| 1:40 | Softmax a cross-entropy (voliteľne, pre technickejšie publikum) | [softmax-cross-entropy.md](cvicenie/softmax-cross-entropy.md) (15 min) |
| 1:55 | Transformer: tokeny, attention, FFN, kontextové okno, KV cache, MoE | [2](2_transformer-topology.md), čísla v [prílohe OLMo](priloha_olmo.md) |
| 2:45 | *Obed* | |
| 3:30 | Tréning a inferencia: teplota, instruct tréning, jazyky, reasoning | [3](3_trening-a-inferencia.md) |
| 4:10 | Hranice AI: halucinácie, prompt injection, štúdie, otvorené problémy | [4](4_ai_constraints.md) |
| 4:55 | *Prestávka* | |
| 5:05 | Od modelu k agentovi: API, nástroje, slučka, kontext, evaly | [5](5_od-modelu-k-agentovi.md) |
| 5:30 | RAG a fine-tuning: embeddingy, BERT, reranker, RAG pipeline, LoRA | [6](6_rag-a-fine-tuning.md) |
| 6:00 | **Cvičenie:** vlastný mini-agent | [mini-agent.md](cvicenie/mini-agent.md), [mini-agent-lektor.md](cvicenie/mini-agent-lektor.md) (45–60 min) |
| 6:55 | Otázky, most k druhej časti (Claude Code, Copilot) | [AI using](../AI%20using/README.md) |

**Skrátená verzia (pol dňa):** kapitoly 1 a 2 bez MoE a kvantizácie, demo len kroky 3, 5 a 6, kapitola 4 body 4 a 5, kapitola 5 bez evalov, kapitolu 6 vynechaj (stačí veta o agentic search v kapitole 5). Mini-agent ukáž naživo namiesto cvičenia (kroky 2, 3 a 7).

## Príprava

- **Demo s číslicami:** Python 3.12+, `numpy`, `Pillow`, `matplotlib`, `PyQt5` (alebo `uv sync` v `cvicenie/image-recognition/`). Súbory MNIST v `mnist/` a záloha `feed_forward_trained.npy` nie sú v gite, treba ich mať lokálne. Kontrolný zoznam je na začiatku [dema](cvicenie/rozpoznavanie-obrazkov.md#príprava-pred-demom-checklist).
- **Mini-agent:** Python 3.12+, `anthropic` a `truststore`, prístup k Claude API (kľúč, `ant auth login` alebo firemná gateway). Jeden beh vyskúšaj deň vopred, najmä za firemným proxy.
- **Konfigurácie vo VS Code** (`.vscode/launch.json`) sú pre Windows (`.venv/Scripts/python.exe`). Na Linuxe a macOS spúšťaj príkazy z dema priamo v termináli.

## Na čo upozorniť

- **Kapitola 1:** pointa nie je vzorec, ale že sieť sa naučí rozloženie dát. Demo to ukáže v kroku 6 (vlastná trojka bez predspracovania).
- **Kapitola 2:** čísla sú pre OLMo 2 7B. Pri otázke „a koľko má Claude?“ odpovedz, že komerční poskytovatelia architektúru nezverejňujú, a ukáž porovnanie v [prílohe OLMo](priloha_olmo.md#porovnanie-s-malým-a-veľkým-modelom).
- **Kapitola 3:** pri teplote spomeň, že Claude API od 10/2026 `temperature` neprijíma a správanie riadi `effort`.
- **Kapitola 4:** štúdie v bode 6 sú väčšinou na malých vzorkách. Prezentuj ich ako varovné signály, nie ako dôkaz.
- **Kapitola 5:** tabuľka „mini-agent vs. Claude Code“ je most k druhej časti. Pri cvičení nechaj účastníkov otvoriť `posledny_kontext.json`, to je moment, keď pochopia, že agent nemá inú pamäť než kontext.
- **Kapitola 6:** hlavná pointa je, že väčšina chýb RAG je v retrievale, nie v LLM, a že fine-tuning mení formu, nie znalosti. Matica podobností pri kontrastívnom tréningu nadväzuje na softmax a cross-entropy z kapitoly 1.

## Zdroje čísel

Čísla o modeloch sú z `config.json` modelov na Hugging Face a z technických reportov (stav 10/2026). Ceny a parametre API sa menia najrýchlejšie, pred školením ich over v dokumentácii poskytovateľa.
