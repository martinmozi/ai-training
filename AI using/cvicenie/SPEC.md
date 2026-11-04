# Špecifikácia výpočtu faktúry

1. **Medzisúčet** = súčet `jednotková cena × množstvo` za všetky riadky.
2. **Množstevná zľava:** riadok s množstvom **10 ks a viac** má zľavu 10 % z ceny riadku.
3. **Kupón** sa uplatní na sumu po množstevnej zľave.
   - Platí **vrátane** dňa `valid_until`.
   - Zľava je najviac 50 %.
4. **Doprava** stojí 5,00 €. Je zadarmo, ak suma **po všetkých zľavách** (bez DPH) je aspoň 100,00 €. Doprava sa nezdaňuje.
5. **DPH** 20 % sa počíta zo sumy po všetkých zľavách.
6. **Zaokrúhľovanie** na centy, matematicky (ROUND_HALF_UP). Medzisúčet a celková zľava (množstevná + kupón spolu) sa zaokrúhlia každá raz, medzivýsledky riadkov sa nezaokrúhľujú. **Základ** = zaokrúhlený medzisúčet − zaokrúhlená zľava. DPH sa počíta zo základu a zaokrúhli sa.
7. **Celkom** = základ + DPH + doprava. Sčítavajú sa už zaokrúhlené sumy, takže faktúra sa vždy presne sčíta: medzisúčet − zľava + DPH + doprava = celkom.
8. **Neplatný riadok:** množstvo menšie než 1 alebo záporná jednotková cena. Takýto riadok sa nedá vytvoriť, vyhodí `ValueError` so správou, ktorá uvádza produkt.
