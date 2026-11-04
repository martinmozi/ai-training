"""Načítanie objednávok z exportu e-shopu.

Export je CSV s oddeľovačom ";" a desatinnou čiarkou:
    objednavka;datum;produkt;cena;mnozstvo
    2026-1001;2026-09-01;widget;12,50;3

Spustenie: python -m faktura.importer data/objednavky-2026-09.csv
"""
import csv
import sys
from datetime import date
from decimal import Decimal

from faktura.calculator import InvoiceCalculator
from faktura.models import InvoiceLine, Order


def parse_amount(raw: str) -> Decimal:
    # e-shop posiela sumy s desatinnou čiarkou ("12,50"), niekedy aj s bodkou
    return Decimal(float(raw.strip().replace(",", ".")))


def load_orders(path) -> dict[str, Order]:
    orders: dict[str, Order] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            order = orders.setdefault(
                row["objednavka"], Order(lines=[], order_date=date.fromisoformat(row["datum"]))
            )
            order.lines.append(
                InvoiceLine(
                    product=row["produkt"],
                    unit_price=parse_amount(row["cena"]),
                    quantity=int(row["mnozstvo"]),
                )
            )
    return orders


def main(path):
    calculator = InvoiceCalculator()
    print("objednavka;medzisucet;zlava;doprava;dph;spolu")
    for number, order in load_orders(path).items():
        inv = calculator.calculate(order)
        print(f"{number};{inv.subtotal};{inv.discount};{inv.shipping};{inv.vat};{inv.total}")


if __name__ == "__main__":
    main(sys.argv[1])
