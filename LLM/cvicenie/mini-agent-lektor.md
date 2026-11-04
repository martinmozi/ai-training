**Očakávaná oprava:** v `zlava()` chýba delenie stom (`suma * percento / 100`). Testy s 10 % a 80 % zľavou potom prejdú.

**Na čo upozorniť počas behu:**
- Rastúci vstup vs. malý výstup: rovnaký pomer je pri Claude Code a vysvetľuje, prečo cenu tvorí najmä kontext.
- Ak model zavolá viac nástrojov naraz, všetky výsledky idú späť v **jednej** správe.
- `stop_reason == "refusal"`: ak bezpečnostný klasifikátor požiadavku odmietne, agent iba vypíše hlásenie a skončí. Pri tomto cvičení sa to stať nemá. Produkčný kód by požiadavku zopakoval na inom modeli (parameter `fallbacks` v Claude API).

**Rozšírenia pre rýchlejších:**
- **Prompt caching:** pridajte do requestu `cache_control={"type": "ephemeral"}` a sledujte `cache_read_input_tokens` v `response.usage`.
- **Effort:** porovnajte `output_config={"effort": "low"}` a `"high"`. Mení sa počet krokov, tokenov a úspešnosť?
- **Kompakcia:** keď vstup prekročí napríklad 20 000 tokenov, nahraďte staršie výsledky nástrojov textom „[výstup vynechaný]“. Ako to ovplyvní agenta?
- **Štruktúrovaný záver:** po skončení slučky sa modelu opýtajte na zhrnutie cez `output_config.format` s JSON schémou `{zmenene_subory: [...], pricina: "...", testy_presli: bool}`.
- **Hook:** pred `write_file` spustite kontrolu (napr. zákaz meniť `test_*.py`) a pri porušení vráťte modelu chybu. Presne takto fungujú `PreToolUse` hooky v Claude Code.
