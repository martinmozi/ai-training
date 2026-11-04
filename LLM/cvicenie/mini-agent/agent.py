"""Mini-agent: agentová slučka nad Claude API so štyrmi nástrojmi.

Agent pracuje na kópii projektu v priečinku `pracovny/` (vznikne z `projekt/`).

    python agent.py "Oprav chybu, kvôli ktorej padajú testy."
    python agent.py --reset "..."     # začni znova z čistej kópie projektu
    python agent.py --auto "..."      # zápis do súborov bez potvrdzovania
    python agent.py --gateway-url https://gateway.example.com --token XYZ "..."

Gateway URL a token sa dajú zadať aj cez premenné prostredia GATEWAY_URL a GATEWAY_TOKEN.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import anthropic

try:  # dôvera k systémovému úložisku certifikátov (firemný TLS proxy)
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

MODEL = "claude-opus-5-5"
TU = Path(__file__).parent
SABLONA = TU / "projekt"
PRACOVNY = TU / "pracovny"
KONTEXT_SUBOR = TU / "posledny_kontext.json"
LOG_SUBOR = TU / "api_log.json"
MAX_KROKOV = 20
MAX_VYSTUP = 10_000  # koľko znakov z výstupu nástroja pošleme modelu

SYSTEM = """Si programátorský agent a pracuješ v malom Python projekte.
Súbory čítaj a meň iba cez nástroje. Pred dokončením spusti testy.
Na konci stručne napíš, čo si zmenil a prečo."""

# Definície nástrojov. Model z nich vidí iba meno, popis a schému,
# takže popis je prompt: podľa neho sa model rozhodne, kedy a ako nástroj použiť.
TOOLS = [
    {
        "name": "list_files",
        "description": "Vypíše všetky súbory v projekte ako relatívne cesty.",
        "strict": True,
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "read_file",
        "description": "Vráti obsah textového súboru z projektu.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "relatívna cesta, napr. faktura.py"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "write_file",
        "description": "Prepíše celý súbor novým obsahom alebo vytvorí nový súbor. Súbor si pred zápisom prečítaj.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "relatívna cesta"},
                "content": {"type": "string", "description": "celý nový obsah súboru"},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    {
        "name": "run_tests",
        "description": "Spustí unit testy projektu (python -m unittest) a vráti ich výstup.",
        "strict": True,
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


def cesta_v_projekte(relativna):
    """Model môže poslať akúkoľvek cestu, preto ju overíme: nesmie ísť mimo projektu."""
    cesta = (PRACOVNY / relativna).resolve()
    if not cesta.is_relative_to(PRACOVNY.resolve()):
        raise ValueError(f"cesta {relativna} je mimo projektu")
    return cesta


def vykonaj(meno, vstup, auto):
    """Vykoná nástroj, ktorý si model vyžiadal. Model sám nič nespúšťa, robí to tento kód."""
    if meno == "list_files":
        subory = sorted(str(p.relative_to(PRACOVNY)) for p in PRACOVNY.rglob("*") if p.is_file())
        return "\n".join(s for s in subory if "__pycache__" not in s)
    if meno == "read_file":
        return cesta_v_projekte(vstup["path"]).read_text(encoding="utf-8")
    if meno == "write_file":
        cesta = cesta_v_projekte(vstup["path"])
        if not auto:
            print(f"\n----- návrh obsahu {vstup['path']} -----\n{vstup['content']}\n-----")
            if input(f"Povoliť zápis do {vstup['path']}? [a/N] ").strip().lower() != "a":
                raise PermissionError("používateľ zápis zamietol")
        cesta.parent.mkdir(parents=True, exist_ok=True)
        cesta.write_text(vstup["content"], encoding="utf-8")
        return f"Zapísané: {vstup['path']} ({len(vstup['content'])} znakov)"
    if meno == "run_tests":
        beh = subprocess.run(
            [sys.executable, "-m", "unittest", "-v"],
            cwd=PRACOVNY, capture_output=True, text=True, timeout=60,
        )
        return f"exit kód {beh.returncode}\n{beh.stdout}{beh.stderr}"
    raise ValueError(f"neznámy nástroj {meno}")


def _serializuj(obsah):
    if isinstance(obsah, str):
        return obsah
    return [b.model_dump(exclude_none=True) if hasattr(b, "model_dump") else b for b in obsah]


LOG = []


def zaloguj(zaznam):
    """Pridá záznam a prepíše api_log.json ako jedno platné JSON pole."""
    LOG.append(zaznam)
    LOG_SUBOR.write_text(json.dumps(LOG, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def uloz_kontext(messages):
    """Uloží celý kontext posledného behu, aby sa dalo pozrieť, čo model naozaj dostal."""
    data = {
        "system": SYSTEM,
        "tools": TOOLS,
        "messages": [{"role": m["role"], "content": _serializuj(m["content"])} for m in messages],
    }
    KONTEXT_SUBOR.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def spusti(uloha, auto, gateway_url=None, token=None):
    """Agentová slučka, popis v ../../5_od-modelu-k-agentovi.md#agentová-slučka"""
    # None = SDK si hodnotu vezme z ANTHROPIC_BASE_URL / ANTHROPIC_AUTH_TOKEN (resp. ANTHROPIC_API_KEY).
    client = anthropic.Anthropic(base_url=gateway_url, auth_token=token)
    messages = [{"role": "user", "content": uloha}]
    LOG.clear()

    for krok in range(1, MAX_KROKOV + 1):
        # Model je bezstavový: v každom kroku dostane celý kontext odznova.
        poziadavka = {
            "model": MODEL,
            "max_tokens": 16000,
            "system": SYSTEM,
            "tools": TOOLS,
            "messages": [{"role": m["role"], "content": _serializuj(m["content"])} for m in messages],
            "output_config": {"effort": "medium"},
        }
        zaloguj({"krok": krok, "typ": "request", "cas": datetime.now().isoformat(), "telo": poziadavka})
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
            output_config={"effort": "medium"},
        )
        zaloguj({"krok": krok, "typ": "response", "cas": datetime.now().isoformat(), "telo": response.model_dump(exclude_none=True)})
        u = response.usage
        vstup_spolu = u.input_tokens + (u.cache_read_input_tokens or 0) + (u.cache_creation_input_tokens or 0)
        print(f"\n── krok {krok}: stop_reason={response.stop_reason}, "
              f"vstup={vstup_spolu} tokenov, výstup={u.output_tokens} tokenov")
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(block.text)

        if response.stop_reason == "refusal":
            print("Model požiadavku odmietol (stop_reason=refusal). Skúste úlohu preformulovať.")
            break
        if response.stop_reason == "max_tokens":
            print("Odpoveď narazila na limit max_tokens.")
            break

        # Celú odpoveď (aj thinking a tool_use bloky) vrátime do histórie bez úprav.
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            break  # model skončil, nič ďalšie nevolá

        vysledky = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"   → {block.name}({json.dumps(block.input, ensure_ascii=False)[:100]})")
            try:
                vystup = vykonaj(block.name, block.input, auto)
                chyba = False
            except Exception as e:  # chybu nástroja vrátime modelu, nech sa zariadi podľa nej
                vystup = f"Chyba: {e}"
                chyba = True
            vysledky.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": vystup[:MAX_VYSTUP],
                "is_error": chyba,
            })
        # Všetky výsledky nástrojov idú späť v jednej správe s rolou user.
        messages.append({"role": "user", "content": vysledky})
    else:
        print(f"\nDosiahnutý limit {MAX_KROKOV} krokov.")

    uloz_kontext(messages)
    print(f"\nCelý kontext je v {KONTEXT_SUBOR.name}, requesty/response v {LOG_SUBOR.name}.")


def main():
    parser = argparse.ArgumentParser(description="Mini-agent nad Claude API")
    parser.add_argument("uloha", help="zadanie pre agenta")
    parser.add_argument("--reset", action="store_true", help="obnov pracovny/ z projekt/")
    parser.add_argument("--auto", action="store_true", help="zapisovať bez potvrdenia")
    parser.add_argument("--gateway-url", default=os.environ.get("GATEWAY_URL"), help="URL gateway (predvolene z GATEWAY_URL)")
    parser.add_argument("--token", default=os.environ.get("GATEWAY_TOKEN"), help="token pre gateway (predvolene z GATEWAY_TOKEN)")
    args = parser.parse_args()

    if args.reset or not PRACOVNY.exists():
        shutil.rmtree(PRACOVNY, ignore_errors=True)
        shutil.copytree(SABLONA, PRACOVNY)
        print(f"Pracovná kópia projektu: {PRACOVNY}")

    spusti(args.uloha, args.auto, args.gateway_url, args.token)


if __name__ == "__main__":
    main()
