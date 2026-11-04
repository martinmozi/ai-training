from datetime import date
from decimal import Decimal

from faktura.calculator import InvoiceCalculator
from faktura.models import Coupon, InvoiceLine, Order

TODAY = date(2026, 10, 14)


def line(price: str, quantity: int) -> InvoiceLine:
    return InvoiceLine(product="widget", unit_price=Decimal(price), quantity=quantity)


def calculate(lines, coupon=None):
    return InvoiceCalculator().calculate(Order(lines=lines, coupon=coupon, order_date=TODAY))


def test_simple_order_pays_shipping_and_vat():
    invoice = calculate([line("10.00", 2)])

    assert invoice.subtotal == Decimal("20.00")
    assert invoice.discount == Decimal("0.00")
    assert invoice.shipping == Decimal("5.00")
    assert invoice.vat == Decimal("4.00")
    assert invoice.total == Decimal("29.00")


def test_large_quantity_gets_volume_discount():
    invoice = calculate([line("10.00", 20)])

    assert invoice.discount == Decimal("20.00")


def test_valid_coupon_is_applied():
    coupon = Coupon(code="JESEN", percent_off=Decimal("10"), valid_until=date(2026, 12, 31))

    invoice = calculate([line("50.00", 1)], coupon)

    assert invoice.discount == Decimal("5.00")


def test_coupon_is_capped_at_fifty_percent():
    coupon = Coupon(code="CHYBA", percent_off=Decimal("80"), valid_until=date(2026, 12, 31))

    invoice = calculate([line("40.00", 1)], coupon)

    assert invoice.discount == Decimal("20.00")
