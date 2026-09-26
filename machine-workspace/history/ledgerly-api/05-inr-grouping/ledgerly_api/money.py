"""Money is stored as integer paise; these helpers convert and format it."""

from decimal import ROUND_HALF_UP, Decimal


def to_paise(amount: str | int | Decimal) -> int:
    """'1499.50' -> 149950. Rounds half-up to the nearest paisa."""
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_inr(paise: int) -> str:
    """149950 -> '₹1,499.50'; 10000000 -> '₹1,00,000.00' (Indian grouping: lakhs and crores)."""
    sign = "-" if paise < 0 else ""
    rupees, rest = divmod(abs(paise), 100)
    digits = str(rupees)
    head, groups = digits[:-3], [digits[-3:]]
    while head:
        groups.insert(0, head[-2:])
        head = head[:-2]
    return f"{sign}₹{','.join(groups)}.{rest:02d}"
