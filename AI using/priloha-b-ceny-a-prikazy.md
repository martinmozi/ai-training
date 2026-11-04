[Obsah](ai-coding-agenti.md)

<a id="priloha-b-ceny-a-prikazy-stav-k-102026"></a>

# Príloha B: Ceny a príkazy (stav k 10/2026)

<a id="b1-prompt-caching-ceny"></a>

### B.1 Prompt caching: ceny

Anthropic, voči cene bežného vstupného tokenu: zápis do cache ~1,25× (TTL 5 min) alebo ~2× (TTL 1 h), **čítanie ~0,1×**, výstupný token ~5×. OpenAI a Google cachujú prefixy automaticky so zľavou typicky 50–90 %.

**Copilot** účtuje premium requesty: každý tvoj prompt v prémiovom modeli sa odpočíta z mesačnej kvóty s násobičom podľa modelu (0× až 1× a viac). Volania nástrojov sa nerátajú.

<a id="b2-prikazy-a-meranie"></a>

### B.2 Príkazy a meranie

| Akcia | Claude Code | Copilot (VS Code) | Codex CLI | Aider |
|---|---|---|---|---|
| plánovanie | `Shift+Tab` | agent „Plan“ | `read-only` sandbox | `/ask`, `--architect` |
| návrat späť | `Esc Esc`, `/rewind` | „Restore checkpoint“ | git | `/undo` |
| nová session | `/clear` | nový chat | `/new` | `/clear` |
| kompakcia | `/compact <pokyn>` | automatická | `/compact` | — |
| čo je v kontexte | `/context` | — | `/status` | `/tokens` |
| spotreba | `/cost`, `/usage`, transcript ([B.4](#b4-spotreba-na-jednu-ulohu)) | usage dashboard | `/status` | po každej odpovedi |

<a id="b3-umiestnenie-konfiguracie"></a>

### B.3 Umiestnenie konfigurácie

| Čo | Claude Code | GitHub Copilot | Codex |
|---|---|---|---|
| pamäť | `CLAUDE.md` | `.github/copilot-instructions.md` | `AGENTS.md` |
| skills | `.claude/skills/<name>/SKILL.md` | `.github/skills/` | `.agents/skills/` |
| commands | `.claude/commands/` | `.github/prompts/*.prompt.md` | `~/.codex/prompts/` |
| subagenti | `.claude/agents/` | `.github/agents/` | — |
| hooks | `.claude/settings.json` | `.github/hooks/` | `config.toml` |
| MCP | `.mcp.json` | `.vscode/mcp.json` | `~/.codex/config.toml` |

<a id="b4-spotreba-na-jednu-ulohu"></a>

### B.4 Spotreba na jednu úlohu

Na vlastné účely (porovnať dva postupy, zistiť, čo je drahé) netreba telemetriu ani dashboard. Stačí dodržať jedno pravidlo: **jedna úloha = jedna session**. Pred úlohou `/clear` alebo nová session, pomenuj ju (`/rename BUG-142`) a po skončení odčítaj čísla.

**Počas session (Claude Code):**

| Čo | Ako |
|---|---|
| tokeny a odhad ceny aktuálnej session | `/cost` (pri predplatnom je cena len orientačná, limity ukáže `/usage`) |
| čo práve zaberá kontext | `/context` |
| stále na očiach | status line, dostáva JSON s `cost.total_cost_usd` a súčtami tokenov (`/statusline`) |
| úloha bez interakcie | `claude -p "..." --output-format json`, výsledok obsahuje `usage` a `total_cost_usd` |

**Po skončení: z transcriptu.** Claude Code ukladá každú session do `~/.claude/projects/<cesta-projektu>/<session-id>.jsonl` a subagentov do `<session-id>/subagents/`. Každá odpoveď modelu tam má `message.usage`:

```json
{"input_tokens": 2, "cache_creation_input_tokens": 12637, "cache_read_input_tokens": 24187, "output_tokens": 187}
```

Skutočný vstup requestu je súčet prvých troch polí. Jedna odpoveď je v súbore vo viacerých riadkoch (text, volanie nástroja), preto treba sčítavať podľa `message.id`, inak vyjde niekoľkonásobok. Skript [`log-token-usage.py`](claude%20tutorial/.claude/hooks/log-token-usage.py) to robí aj so subagentmi:

```text
$ log-token-usage.py            # posledná session v aktuálnom projekte
session 0872e3f5  Export do PDF  (pdf-export)
  claude-opus-5-5: 283 requestov, vstup 40,816,990 (z cache 97%, zápis 1,380,501), výstup 151,089
  z toho výstup subagentov: 9,537
```

Ako hook `SessionEnd` pripíše po každej session riadok do `~/.claude/token-log.csv` (dátum, názov, vetva, model, tokeny). Keďže je to pre teba, nie pre tím, patrí do `~/.claude/settings.json` alebo `.claude/settings.local.json`, nie do zdieľaného `.claude/settings.json`. Skript skopíruj do `~/.claude/hooks/`:

```json
{ "hooks": { "SessionEnd": [ { "hooks": [
  { "type": "command", "command": "python3 ~/.claude/hooks/log-token-usage.py" }
] } ] } }
```

**Ako čísla čítať:**
- **Rozhoduje počet requestov × kontext, nie výstup.** Výstup býva 1 % tokenov ([2.1](02-kontext.md#21-slucka-a-cena-requestu)). Ak je úloha drahá, pozri počet requestov a veľkosť kontextu.
- **Pomer z cache** pod ~80 % znamená, že sa prefix často menil: prepínanie modelu, úprava pamäťového súboru alebo MCP počas session, pauzy dlhšie než TTL ([2.2](02-kontext.md#22-prompt-caching)).
- **Porovnávaj rovnaké úlohy.** Zmysel to má pri otázkach typu „ušetril subagent hlavný kontext?“ alebo „stojí plán najprv menej opráv?“, nie ako absolútne číslo.
- Na súhrny za deň či mesiac existuje komunitný nástroj `npx ccusage`, ktorý číta tie isté súbory. Firemné meranie pre tím rieši OpenTelemetry (`CLAUDE_CODE_ENABLE_TELEMETRY=1`), to je už iná úroveň.

**Iné nástroje:** Codex CLI ukáže tokeny session cez `/status`, Aider po každej odpovedi vypíše tokeny a cenu. Copilot meria premium requesty, nie tokeny: spotrebu vidíš v nastaveniach GitHub účtu (Billing and licensing → Usage), na jednu úlohu ju odhadneš podľa počtu promptov × násobič modelu ([B.1](#b1-prompt-caching-ceny)).

<a id="b5-claude-code-a-github-copilot"></a>

### B.5 Claude Code a GitHub Copilot

Hlavné príkazy z textu a ich náprotivky. Copilot CLI je overený v dokumentácii GitHubu (*Copilot CLI command reference*, 10/2026). VS Code sa mení s každým vydaním, prázdne políčko znamená, že priamy ekvivalent nie je alebo sa robí cez UI.

| Čo | Claude Code | Copilot CLI | Copilot vo VS Code |
|---|---|---|---|
| plán pred kódom | `Shift+Tab` → plan | `/plan`, `--plan`, `Shift+Tab` | agent „Plan“ |
| nová session | `/clear` | `/clear`, `/new` | nový chat |
| pokračovať v session | `claude -c`, `claude --resume`, `/resume` | `--continue`, `--resume`, `/resume` | história chatov |
| návrat späť | `Esc Esc`, `/rewind` | `/rewind`, `/undo` | „Restore checkpoint“ |
| kompakcia | `/compact <pokyn>` | `/compact <pokyn>` | automatická |
| čo je v kontexte | `/context` | `/context` | |
| spotreba | `/cost`, `/usage` | `/usage` | premium requests v nastaveniach účtu |
| výber modelu | `/model`, `--model` | `/model`, `--model` | výber v okne chatu |
| pamäťový súbor | `/init` → `CLAUDE.md` | `/init`, `copilot init` → vlastné inštrukcie v `.github/` | |
| režim povolení | `Shift+Tab`, `defaultMode` | `/permissions` (`default`, `assisted`, `allow-all`) | schvaľovanie nástrojov v chate |
| bez pýtania | `bypassPermissions` | `--allow-all`, `/yolo` | |
| povoliť / zakázať nástroj | `permissions.allow` / `deny`, `--allowedTools` / `--disallowedTools` | `--allow-tool` / `--deny-tool` | |
| sandbox | `/sandbox` | `/sandbox` | |
| ďalší adresár | `/add-dir`, `--add-dir` | `/add-dir`, `--add-dir` | pridať priečinok do workspace |
| headless | `claude -p "..." --output-format json` | `copilot -p "..." --output-format json` | |
| vlastný agent | `@agent-meno`, `claude --agent meno` (`.claude/agents/`) | `--agent meno` (`.github/agents/`) | výber agenta v chate (`.github/agents/`) |
| skills | `.claude/skills/` | `/skills` (`.github/skills/`) | `.github/skills/` |
| MCP | `/mcp`, `.mcp.json` | `/mcp`, `~/.copilot/mcp-config.json` | `.vscode/mcp.json` |
| review zmien | `/code-review`, `/security-review` | `/review`, `/diff` | Copilot code review v PR |
| práca v cloude | claude.ai/code, `@claude` v PR | `/delegate` | coding agent (issue → PR) |
| paralelne vo worktree | `claude --worktree` | `/new worktree` | |

Najväčší rozdiel nie je v príkazoch, ale v platbe ([B.1](#b1-prompt-caching-ceny)): Copilot účtuje prompty, Claude Code tokeny alebo limity predplatného. V Copilote preto menej záleží na veľkosti kontextu pre cenu, ale rovnako pre kvalitu ([2.3](02-kontext.md#23-context-rot-preco-sa-dlha-session-zhorsuje)).

<a id="b6-ovladanie-claude-code"></a>

### B.6 Ovládanie Claude Code

Skratky a príkazy, ktoré robia z bežného používateľa rýchleho. Úplný zoznam: `/help` a dokumentácia *Interactive mode*.

| Klávesy | Čo robí |
|---|---|
| `Esc` | zastaví agenta uprostred kroku, hotová práca zostane |
| `Esc Esc` | pri prázdnom vstupe otvorí `/rewind` (návrat kódu aj konverzácie, [2.4](02-kontext.md#24-kompakcia-a-checkpointy)) |
| `Shift+Tab` | prepína režimy: manual, acceptEdits, plan, auto ([4.2](04-bezpecnost.md#42-rezimy-povoleni)) |
| `Ctrl+B` | pošle bežiaci príkaz alebo subagenta na pozadie |
| `Ctrl+O` | podrobný prepis session: čo agent volal a čo dostal |
| `Ctrl+T` | zoznam úloh, ktoré si agent naplánoval |
| `Ctrl+R` | hľadanie v histórii promptov |
| `Ctrl+G` | prompt v textovom editore (dlhé zadania) |
| `Ctrl+V` | vloží obrázok zo schránky |
| `Ctrl+S` | odloží rozpísaný prompt, druhým stlačením ho vráti |
| `!príkaz` | spustí príkaz v shelli a výstup pridá do session |
| `@súbor` | odkaz na súbor s doplňovaním, `@agent-meno` spustí subagenta |

| Príkaz | Na čo |
|---|---|
| `/context`, `/cost`, `/usage` | čo zaberá kontext, koľko stojí session, limity predplatného |
| `/clear`, `/compact <pokyn>`, `/rewind` | nová session, riadená kompakcia, návrat späť |
| `/model`, `/effort`, `/fast` | model a effort ([2.6](02-kontext.md#26-vyber-modelu-a-effort)) |
| `/permissions`, `/sandbox` | pravidlá a sandbox ([4.3](04-bezpecnost.md#43-pravidla-allow-ask-deny), [4.4](04-bezpecnost.md#44-sandbox-a-kontajner)) |
| `/mcp`, `/plugin`, `/agents`, `/hooks`, `/memory` | prehľad a správa rozšírení |
| `/init` | kostra `CLAUDE.md` ([3.4](03-building-blocks.md#34-pamatove-subory-agentsmd-claudemd-a-copilot-instructionsmd)) |
| `/rename`, `/resume` | pomenovanie session a návrat k nej |
| `/btw <otázka>` | otázka bokom bez zápisu do konverzácie |
| `/code-review`, `/security-review` | review zmien pred commitom ([5.2](05-postup-prace.md#52-tdd-a-overenie-pred-dokoncenim)) |
| `/statusline` | vlastný stavový riadok, napr. s kontextom a cenou |
| `/doctor` | kontrola inštalácie a konfigurácie |

---

[← Príloha A: Nástroje](priloha-a-nastroje.md) · [Obsah](ai-coding-agenti.md) · [Príloha C: Setup tímu Claude Code →](priloha-c-setup-timu-claude-code.md)
