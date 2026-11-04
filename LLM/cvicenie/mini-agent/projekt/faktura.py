"""Výpočet sumy na faktúre."""

DPH = 0.23


def medzisucet(polozky):
    """Súčet cien položiek bez DPH. Položka je dict s kľúčmi `cena` a `mnozstvo`."""
    return sum(p["cena"] * p["mnozstvo"] for p in polozky)


def zlava(suma, percento):
    """Suma zľavy. Zľava je v percentách a najviac 50 %."""
    percento = min(percento, 50)
    return suma * percento


def celkom(polozky, zlava_percento=0):
    """Suma na úhradu: medzisúčet mínus zľava, plus DPH, zaokrúhlené na centy."""
    zaklad = medzisucet(polozky)
    zaklad -= zlava(zaklad, zlava_percento)
    return round(zaklad * (1 + DPH), 2)
