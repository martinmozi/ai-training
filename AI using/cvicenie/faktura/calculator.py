from decimal import ROUND_HALF_UP, Decimal

from faktura.models import Coupon, Invoice, InvoiceLine, Order

VOLUME_DISCOUNT_MIN_QUANTITY = 10
VOLUME_DISCOUNT_RATE = Decimal("0.10")
MAX_COUPON_PERCENT = Decimal("50")
VAT_RATE = Decimal("0.20")
SHIPPING_FEE = Decimal("5.00")
FREE_SHIPPING_THRESHOLD = Decimal("100.00")

CENT = Decimal("0.01")


def to_cents(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


class LinePricing:
    def __init__(self, line: InvoiceLine):
        self.line = line

    def gross(self) -> Decimal:
        return self.line.unit_price * self.line.quantity

    def volume_discount(self) -> Decimal:
        if self.line.quantity > VOLUME_DISCOUNT_MIN_QUANTITY:
            return self.gross() * VOLUME_DISCOUNT_RATE
        return Decimal("0")


class CouponPolicy:
    def __init__(self, coupon: Coupon | None):
        self.coupon = coupon

    def is_applicable(self, order_date) -> bool:
        return self.coupon is not None and order_date < self.coupon.valid_until

    def discount(self, amount: Decimal, order_date) -> Decimal:
        if not self.is_applicable(order_date):
            return Decimal("0")
        percent = min(self.coupon.percent_off, MAX_COUPON_PERCENT)
        return amount * percent / Decimal("100")


class InvoiceCalculator:
    def calculate(self, order: Order) -> Invoice:
        pricings = [LinePricing(line) for line in order.lines]
        subtotal = sum((p.gross() for p in pricings), Decimal("0"))
        volume_discount = sum((p.volume_discount() for p in pricings), Decimal("0"))

        after_volume = subtotal - volume_discount
        coupon_discount = CouponPolicy(order.coupon).discount(after_volume, order.order_date)
        discount = to_cents(volume_discount + coupon_discount)
        base = to_cents(subtotal) - discount

        shipping = to_cents(Decimal("0") if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE)
        vat = to_cents(base * VAT_RATE)

        return Invoice(
            subtotal=to_cents(subtotal),
            discount=discount,
            shipping=shipping,
            vat=vat,
            total=base + vat + shipping,
        )
