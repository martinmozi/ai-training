from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class InvoiceLine:
    product: str
    unit_price: Decimal
    quantity: int


@dataclass(frozen=True)
class Coupon:
    code: str
    percent_off: Decimal
    valid_until: date


@dataclass
class Order:
    lines: list[InvoiceLine]
    coupon: Coupon | None = None
    order_date: date = field(default_factory=date.today)


@dataclass(frozen=True)
class Invoice:
    subtotal: Decimal
    discount: Decimal
    shipping: Decimal
    vat: Decimal
    total: Decimal
