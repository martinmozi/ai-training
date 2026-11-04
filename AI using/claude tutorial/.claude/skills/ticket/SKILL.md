---
name: ticket
description: Work on a ticket from tickets/ (BUG-xxx, FEAT-xxx) with the plan-first, test-first workflow. Use when the user asks to implement or fix a ticket.
argument-hint: <ticket-id>
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash(python -m pytest *) Bash(git diff *) Bash(git status *) Bash(git log *)
---
Pracuješ na tickete **$ARGUMENTS** (súbor `tickets/$ARGUMENTS.md`).

## Stav repa

!`git status --short`

!`git log --oneline -5`

## Postup

1. **Pochop zadanie.** Prečítaj ticket a body `SPEC.md`, na ktoré odkazuje alebo ktorých sa týka. Ak SPEC hovorí niečo, čo ticket nespomína, uveď to.
2. **Plán, nie kód.** Navrhni: ktoré súbory a funkcie zmeníš, aké hraničné hodnoty otestuješ, čo sa nemení. Potom **zastav a počkaj na schválenie**.
3. **Najprv test.** Po schválení napíš nové testy do nového súboru (commitnuté testovacie súbory nemeň, pomocné funkcie z nich importuj), spusti `python -m pytest -q` a ukáž, že nové testy padajú zo správneho dôvodu (`AssertionError`, `DID NOT RAISE`), nie na `ImportError`.
4. **Oprava.** Najmenšia zmena, ktorá testy opraví. `SPEC.md` ani existujúce testy nemeň. Žiadny refaktor navyše.
5. **Dôkaz.** Spusti `python -m pytest -q`, `git status --short` a `git diff --stat` (nové súbory sú len v `git status`). Zhrň na pár riadkov: čo si zmenil, prečo, ako je to overené a čo ostalo otvorené.
