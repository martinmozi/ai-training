# FEAT-150: Odmietnuť neplatné riadky faktúry

**Nahlásil:** tím objednávok
**Priorita:** stredná

Z importu objednávok nám občas príde riadok s množstvom `0` alebo so zápornou cenou. Kalkulačka ho teraz potichu spracuje a faktúra má nezmyselné sumy.

Požadované správanie je v `SPEC.md`, bod 8.
