[Obsah](ai-coding-agenti.md)

<a id="priloha-a-nastroje-stav-k-102026"></a>

# Príloha A: Nástroje (stav k 10/2026)

> Zastaráva najrýchlejšie. Pred použitím over v dokumentácii ([Zdroje](ai-coding-agenti.md#zdroje)).

Nástroje sa líšia v troch veciach: **kde beží slučka** (IDE, terminál, cloud), **kto určuje kontext** (ty alebo agent) a **ako sa platí** (requesty alebo tokeny).

<a id="a1-github-copilot"></a>

### A.1 GitHub Copilot

- **IDE** (VS Code, JetBrains, Visual Studio…): inline completions, chat a agent mode s terminálom a MCP.
- **Copilot CLI:** terminálový agent s MCP, vlastnými agentmi a `AGENTS.md`.
- **Coding agent (cloud):** priradíš mu issue, pracuje v GitHub Actions runneri a otvorí draft PR. Prostredie sa pripravuje cez `.github/workflows/copilot-setup-steps.yml`, bez neho často nevie spustiť ani testy. Odchádzajúca sieť je štandardne obmedzená firewallom.

Silný v integrácii s GitHubom (issue → PR → review) a vo firemnej správe (policies, výber modelov, audit).

<a id="a2-claude-code"></a>

### A.2 Claude Code

Terminálový agent od Anthropicu (CLI, IDE rozšírenia, desktop, web). Malé jadro, skoro všetko sa nastavuje súbormi v repe: `CLAUDE.md`, commands, skills, subagenti, hooks, MCP, plugins.
- Hľadá v kóde agenticky (grep, čítanie), bez vektorového indexu. Tím uvádza, že index skúšali a agentické hľadanie vyšlo lepšie, lebo nezastaráva.
- Povolenia allow/deny (`Bash(npm test *)`), režimy vrátane plan a auto, sandbox.
- Headless režim (`claude -p`), Agent SDK, GitHub Action (`@claude` v PR).

<a id="a3-openai-codex"></a>

### A.3 OpenAI Codex

- **Codex CLI:** open source (Apache-2.0, Rust), OS-level sandbox s dvoma nastaveniami: `sandbox_mode` (`read-only`, `workspace-write`, `danger-full-access`) a `approval_policy` (kedy sa pýtať).
- **Codex cloud:** paralelné úlohy v kontajneroch, výsledok je diff alebo PR. **Code review** PR.
- Konfigurácia `~/.codex/config.toml`, pamäť `AGENTS.md`.

<a id="a4-aider-a-dalsie-open-source-nastroje"></a>

### A.4 Aider a ďalšie open source nástroje

[Aider](https://aider.chat) pracuje s kontextom opačne než ostatní: **čo v ňom je, určuješ ty** (`/add`, `/read-only`, `/drop`, `/tokens`).

- **Repo map:** tree-sitter vyparsuje repo na symboly a PageRank nad grafom referencií vyberie najdôležitejšie tak, aby sa zmestili do rozpočtu (`--map-tokens`). Model vidí štruktúru repa za zlomok tokenov.
- **Edit formáty** (`diff`, `whole`, `udiff`) namiesto tool-callingu, preto funguje aj s modelmi, ktoré tool-calling zvládajú zle, čo je prípad mnohých lokálnych.
- **Architect režim:** silný model navrhne zmenu, lacný ju prepíše na presné edity.
- Každá zmena je git commit, `/undo` je `git reset`.

Ďalšie: **Cline** (VS Code agent s vlastným API kľúčom, Plan/Act), **Continue** (IDE asistent pre vlastné modely), **OpenHands** (autonómny agent v Dockeri), **opencode**, **Goose**.

<a id="a5-lokalne-modely"></a>

### A.5 Lokálne modely

Ollama, LM Studio alebo llama.cpp na desktope, vLLM či SGLang na serveri, s OpenAI-kompatibilným API pre Aider, Cline, Continue alebo Codex CLI. V agentovom kódovaní obstoja väčšie open-weight modely (Qwen3-Coder, Devstral, gpt-oss, GLM, Kimi K2, DeepSeek). Modely do 14B zvládnu doplňovanie, v dlhých slučkách blúdia.

- **Ollama má štandardne malé `num_ctx`.** Agent „zabúda“, lebo sa kontext potichu orezáva. Nastav ho explicitne.
- **Kvantizácia Q4** zhoršuje presnosť tool-callov a diffov.
- **Prefill je pomalý:** 50 000 tokenov kontextu trvá na lokálnom hardvéri desiatky sekúnd. Kapitola 2 tu platí ešte viac.
- **Lokálny je len model.** Agent okolo neho môže mať shell, sieť, MCP a tajomstvá. Ak dáta nesmú von, obmedz aj nástroje a sieť.

<a id="a6-porovnanie"></a>

### A.6 Porovnanie

| | Copilot | Claude Code | Codex | Aider | Lokálne modely |
|---|---|---|---|---|---|
| **Kde** | IDE + GitHub | terminál (+IDE, web) | terminál + cloud | terminál | cez iný nástroj |
| **Cloud agent → PR** | 🏆 Actions | ✅ | ✅ | ❌ | ❌ |
| **Inline completions** | 🏆 | ❌ | ❌ | ❌ | ✅ (Continue) |
| **Dlhé autonómne úlohy** | ✅ | 🏆 | 🏆 | ⚠️ | ⚠️ |
| **Rozšíriteľnosť** | ✅ | 🏆 | ✅ | ⚠️ | podľa nástroja |
| **Bezpečný default** | ✅ cloud izolácia | ✅ povolenia + sandbox | 🏆 OS sandbox | ⚠️ git | ⚠️ nástroje a sieť zvlášť |
| **Kontrola nad kontextom** | stredná | stredná | stredná | 🏆 explicitná | podľa nástroja |
| **Výber modelov** | 🏆 viac výrobcov | Claude | OpenAI | 🏆 ľubovoľný | open-weight |
| **Platba** | predplatné + premium requesty | predplatné / tokeny | predplatné / tokeny | tokeny | hardvér |

---

[← 7. Ťahák](07-tahak.md) · [Obsah](ai-coding-agenti.md) · [Príloha B: Ceny a príkazy →](priloha-b-ceny-a-prikazy.md)
