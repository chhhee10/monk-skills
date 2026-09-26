"""Invoice lines, totals and payment terms. All amounts are integer paise."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

GST_PERCENT = 18


@dataclass(frozen=True)
class Line:
    description: str
    quantity: int
    unit_paise: int
    gst_percent: int = GST_PERCENT


def line_tax(line: Line) -> int:
    """GST for one line, rounded half-up to the paisa per line (as the GST portal does)."""
    tax = Decimal(line.quantity * line.unit_paise) * line.gst_percent / 100
    return int(tax.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def totals(lines: list[Line]) -> dict[str, int]:
    """Subtotal, GST and total in paise."""
    for line in lines:
        if line.quantity <= 0:
            raise ValueError(f"quantity must be positive: {line.description!r}")
    subtotal = sum(line.quantity * line.unit_paise for line in lines)
    gst = sum(line_tax(line) for line in lines)
    return {"subtotal": subtotal, "gst": gst, "total": subtotal + gst}
