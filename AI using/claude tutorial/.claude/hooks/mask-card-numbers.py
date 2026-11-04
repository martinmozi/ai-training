#!/usr/bin/env python3
"""Čísla platobných kariet (PAN) sa nedostanú do kontextu modelu.

Jeden skript pre štyri udalosti, podľa hook_event_name:
  UserPromptSubmit          prompt s číslom karty sa neodošle
  PreToolUse  Read          súbor s číslami kariet nečítaj priamo, choď cez Bash
  PreToolUse  Edit|Write    skutočné číslo karty sa nezapíše do kódu
  PostToolUse Bash|Grep|mcp__.*
                            výstup nástroja sa pred modelom zamaskuje (411111******1111)

Za číslo karty sa považuje 13 až 19 číslic (aj s medzerami alebo pomlčkami),
ktoré prejdú Luhnovou kontrolou. Verejné testovacie karty sa nechávajú.
"""
import json
import re
import sys

PAN = re.compile(r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)")
# Skladané po skupinách, aby súbor sám neobsahoval celé PAN (DLP proxy ho inak zablokuje).
TEST_PANS = {
    "".join(groups)
    for groups in (
        ("4111", "1111", "1111", "1111"),
        ("4242", "4242", "4242", "4242"),
        ("5555", "5555", "5555", "4444"),
        ("3782", "822463", "10005"),
    )
}


def luhn_ok(digits):
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2:
            n = n * 2 - 9 if n > 4 else n * 2
        total += n
    return total % 10 == 0


def mask(text):
    """Vráti (zamaskovaný text, počet nájdených čísel kariet)."""
    found = 0

    def repl(m):
        nonlocal found
        digits = re.sub(r"\D", "", m.group())
        if digits in TEST_PANS or not luhn_ok(digits):
            return m.group()
        found += 1
        # PCI DSS dovoľuje zobraziť najviac prvých 6 a posledné 4 číslice.
        return digits[:6] + "*" * (len(digits) - 10) + digits[-4:]

    return PAN.sub(repl, text), found


def mask_all(value):
    """Zamaskuje všetky texty vo výstupe ľubovoľného nástroja (Bash, Grep, MCP).

    Prejde slovníky a zoznamy do hĺbky a mení len reťazce, takže tvar výstupu ostane.
    Vráti (upravená hodnota, počet nájdených čísel kariet).
    """
    if isinstance(value, str):
        return mask(value)
    if isinstance(value, dict):
        pairs = [(k, *mask_all(v)) for k, v in value.items()]
        return {k: v for k, v, _ in pairs}, sum(n for _, _, n in pairs)
    if isinstance(value, list):
        items = [mask_all(v) for v in value]
        return [v for v, _ in items], sum(n for _, n in items)
    return value, 0


def block(message):
    print(message, file=sys.stderr)
    sys.exit(2)


event = json.load(sys.stdin)
name = event["hook_event_name"]
tool = event.get("tool_name")
tool_input = event.get("tool_input") or {}

if name == "UserPromptSubmit":
    if mask(event["prompt"])[1]:
        print(json.dumps({
            "decision": "block",
            "reason": "Prompt obsahuje číslo platobnej karty, preto sa neodoslal. Nahraď ho maskou (411111******1111) alebo testovacou kartou.",
            # Inak by sa pôvodný text zobrazil v hláške a zapísal do transcriptu.
            "hookSpecificOutput": {"hookEventName": name, "suppressOriginalPrompt": True},
        }))

elif name == "PreToolUse" and tool == "Read":
    path = tool_input.get("file_path", "")
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            has_pan = mask(f.read())[1] > 0
    except OSError:
        has_pan = False
    if has_pan:
        block(f"Súbor {path} obsahuje čísla platobných kariet. Nečítaj ho cez Read, "
              f"použi Bash (napr. head -n 50 {path}), jeho výstup sa automaticky zamaskuje.")

elif name == "PreToolUse" and tool in ("Edit", "Write"):
    text = tool_input.get("content") or tool_input.get("new_string") or ""
    if mask(text)[1]:
        block("Do súboru sa chystáš zapísať skutočné číslo platobnej karty. V kóde a testoch "
              "používaj len verejné testovacie karty (napr. Visa 4111…1111) alebo masku.")

elif name == "PostToolUse":
    out, n = mask_all(event.get("tool_response"))
    if n:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": name,
            # Tvar musí sedieť s výstupom nástroja, inak sa zmena ignoruje.
            # mask_all mení len texty, štruktúru výstupu nechá.
            "updatedToolOutput": out,
            "additionalContext": f"Počet zamaskovaných čísel kariet vo výstupe: {n}.",
        }}))

sys.exit(0)
