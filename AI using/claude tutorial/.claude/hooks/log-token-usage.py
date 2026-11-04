#!/usr/bin/env python3
"""Koľko tokenov minula jedna session (= jedna úloha), vrátane subagentov.

Dva spôsoby použitia:
  hook SessionEnd     pripíše riadok do ~/.claude/token-log.csv
  ručne               log-token-usage.py [cesta/k/session.jsonl]
                      (bez argumentu vezme poslednú session aktuálneho projektu)

Čísla berie z transcriptu: každá odpoveď modelu má pole message.usage.
Jedna odpoveď môže byť v transcripte vo viacerých riadkoch (text, tool_use),
preto sa sčítava podľa message.id. Subagenti majú vlastné súbory
v <session-id>/subagents/agent-*.jsonl.

Ukladá len čísla, názov session a vetvu. Žiadny obsah konverzácie.
"""
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

LOG = Path(os.environ.get("TOKEN_LOG", Path.home() / ".claude" / "token-log.csv"))
FIELDS = ["input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"]
HEADER = ["datum", "session", "nazov", "vetva", "model", "requesty",
          "vstup", "zapis_cache", "citanie_cache", "vystup", "subagenti_vystup"]


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def summarize(transcript):
    transcript = Path(transcript)
    files = [transcript] + sorted(transcript.with_suffix("").glob("subagents/*.jsonl"))
    seen, per_model, sub_out = set(), {}, 0
    meta = {"nazov": "", "vetva": ""}
    for path in files:
        is_sub = path != transcript
        for e in read_jsonl(path):
            if e.get("type") == "custom-title":
                meta["nazov"] = e.get("customTitle", "")
            elif e.get("type") == "ai-title" and not meta["nazov"]:
                meta["nazov"] = e.get("aiTitle", "")
            if not meta["vetva"] and e.get("gitBranch"):
                meta["vetva"] = e["gitBranch"]
            msg = e.get("message") or {}
            usage = msg.get("usage")
            if e.get("type") != "assistant" or not usage or msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            m = per_model.setdefault(msg.get("model", "?"), dict.fromkeys(FIELDS, 0) | {"requesty": 0})
            m["requesty"] += 1
            for k in FIELDS:
                m[k] += usage.get(k) or 0
            if is_sub:
                sub_out += usage.get("output_tokens") or 0
    return meta, per_model, sub_out


def latest_transcript():
    project = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
    files = sorted(project.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not files:
        sys.exit(f"Žiadny transcript v {project}")
    return files[-1]


def main():
    if len(sys.argv) > 1:
        transcript, hook = sys.argv[1], False
    elif not sys.stdin.isatty():
        transcript, hook = json.load(sys.stdin)["transcript_path"], True
    else:
        transcript, hook = latest_transcript(), False

    meta, per_model, sub_out = summarize(transcript)
    session = Path(transcript).stem
    rows = [[datetime.now().strftime("%Y-%m-%d %H:%M"), session[:8], meta["nazov"], meta["vetva"], model,
             m["requesty"], m["input_tokens"], m["cache_creation_input_tokens"],
             m["cache_read_input_tokens"], m["output_tokens"], sub_out]
            for model, m in per_model.items()]

    if hook:
        if not rows:
            return
        new = not LOG.exists()
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(HEADER)
            w.writerows(rows)
        return

    print(f"session {session[:8]}  {meta['nazov']}  ({meta['vetva']})")
    for model, m in per_model.items():
        total_in = m["input_tokens"] + m["cache_creation_input_tokens"] + m["cache_read_input_tokens"]
        hit = m["cache_read_input_tokens"] / total_in if total_in else 0
        print(f"  {model}: {m['requesty']} requestov, vstup {total_in:,} "
              f"(z cache {hit:.0%}, zápis {m['cache_creation_input_tokens']:,}), výstup {m['output_tokens']:,}")
    if sub_out:
        print(f"  z toho výstup subagentov: {sub_out:,}")


if __name__ == "__main__":
    main()
