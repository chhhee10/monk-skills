"""Invoice lines, totals and payment terms. All amounts are integer paise."""

import calendar
from dataclasses import dataclass
from datetime import date
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


def due_date(issued_on: date, net_days: int) -> date:
    """Due date for 'Net N' payment terms (Net 7, 15, 30, 45)."""
    if net_days < 0:
        raise ValueError("net_days must not be negative")
    day = issued_on.day + net_days
    days_in_month = calendar.monthrange(issued_on.year, issued_on.month)[1]
    if day > days_in_month:
        return issued_on.replace(month=issued_on.month + 1, day=day - days_in_month)
    return issued_on.replace(day=day)
