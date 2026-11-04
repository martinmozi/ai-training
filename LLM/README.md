# Školenie: ako fungujú veľké jazykové modely (LLM)

Cieľ: pochopiť, ako LLM funguje, natoľko, aby bolo jasné, čo robia Claude Code a GitHub Copilot (ďalšia časť školenia, [AI using](../AI%20using/README.md)) a ako si postaviť vlastnú nadstavbu, napríklad agenta.

Kapitoly na seba nadväzujú, odporúčané poradie:

1. [Neurónové siete](1_neuronove-siete.md) – neurón, váhy, ako sa sieť učí (gradient, backpropagation, Adam), aktivačné funkcie.
   - Cvičenie: [rozpoznávanie číslic vlastnou sieťou](cvicenie/rozpoznavanie-obrazkov.md), všetko z kapitoly naživo v kóde.
   - Doplnok: [softmax a cross-entropy](cvicenie/softmax-cross-entropy.md), výstupná vrstva a loss krok po kroku na 10 výstupoch.
2. [Topológia transformera](2_transformer-topology.md) – tokeny, attention, FFN, kontextové okno a prečo sa dlhý kontext zhoršuje, KV cache, MoE, kvantizácia.
3. [Tréning a inferencia](3_trening-a-inferencia.md) – predpovedanie ďalšieho tokenu, teplota, instruct tréning a chat šablóna, jazyky, reasoning.
4. [Hranice AI](4_ai_constraints.md) – kedy model nepomôže alebo dokonca uškodí, halucinácie, prompt injection.
5. [Od modelu k agentovi](5_od-modelu-k-agentovi.md) – API request, volanie nástrojov, agentová slučka, kontext, štruktúrovaný výstup, evaly.
   - Cvičenie: [vlastný mini-agent](cvicenie/mini-agent.md), coding agent nad Claude API v jednom súbore. Referencia: [štruktúra Anthropic Messages API](cvicenie/struktura_anthropic.md).
6. [RAG a fine-tuning](6_rag-a-fine-tuning.md) – embeddingy textu, BERT a embedding modely z LLM, kontrastívny tréning, bi-encoder vs. reranker, hybridné vyhľadávanie, RAG pipeline, fine-tuning a LoRA, kedy čo použiť.

Prílohy:
- [OLMo](priloha_olmo.md) – plne otvorený model, na ktorom sú ukázané konkrétne čísla (veľkosti, čas a cena tréningu).
- [Slovník](slovnik.md) – všetky pojmy a skratky na jednom mieste.

Pre lektora: [časový plán a príprava](lektor.md).

Obrázky sú v [img/](img/). Obrázky ku kapitole o neurónových sieťach generuje skript [img/gen_ffn_svg.py](img/gen_ffn_svg.py).
