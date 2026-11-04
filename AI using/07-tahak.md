[Obsah](ai-coding-agenti.md)

<a id="7-tahak"></a>

# 7. Ťahák

```text
PRED ÚLOHOU      Kde hľadať, čo sa má stať, kedy je hotovo, čo sa nemení?
                 Bude diff mať viac než pár riadkov? Najprv plán.

VOĽBA MODELU     Plán, ladenie, nejasné zadanie: opus, effort high.
                 Mechanika a prieskum v subagentovi: haiku alebo sonnet, low.
                 Model meniť medzi úlohami, nie uprostred.

POČAS            Čo mi zaberá kontext?
                 Dva neúspechy: späť a lepší prompt, nie tretia oprava.
                 Veľký prieskum: subagent.
                 Dlhá úloha: stav do PLAN.md, kompakciu spustiť sám medzi krokmi.
                 Ide zlým smerom: Esc hneď, nie po desiatich krokoch.
                 Otázka bokom: /btw. Paralelne: claude --worktree.

LADENIE          Reprodukcia → všetky výskyty skriptom → dve hypotézy → experiment
                 → test na príčinu → oprava → skript znova, nula rozdielov.

PO               Testy, build a lint som spustil sám?
                 Diff testov som čítal ako prvý? Padal nový test pred opravou?
                 Malý commit. Poučenie do pamäte. Nová session.
                 Koľko to stálo? /cost alebo token-log.csv (B.4).

RAZ NA PROJEKT   Deny na tajomstvá, sandbox so zoznamom domén.
                 Cudzie repo: najprv dôvera, v skriptoch --setting-sources user.
                 Presety v ~/.bashrc (3.8): cc bez MCP, ccm <server> s MCP, cc0 na ladenie.

BEZ DOZORU       claude -p s dontAsk a --allowedTools, --max-turns, --bare.
                 Výsledok je PR alebo komentár, merguje človek.

RAZ ZA MESIAC    Prínos (5.7): čas do merge, veľkosť PR a reverty, s agentom vs. bez, oproti baseline.
                 MCP servery, pamäťový súbor a auto memory: treba to ešte?
                 Opakovaný prompt prerobiť na skill. Rovnaké nastavenia vo viac repách: plugin.
                 Pravidlo, ktoré agent porušuje, vynútiť hookom.
```

---

[← 6. Záverečné cvičenie](06-zaverecne-cvicenie.md) · [Obsah](ai-coding-agenti.md) · [Príloha A: Nástroje →](priloha-a-nastroje.md)
