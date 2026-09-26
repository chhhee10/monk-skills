"""Request handlers. The HTTP layer (ledgerly-web) maps POST /v1/invoices to create_invoice."""

from datetime import date

from .invoices import Line, due_date, totals
from .money import format_inr

DEFAULT_NET_DAYS = 15


class BadRequest(ValueError):
    """Invalid client input; the HTTP layer answers 400."""


def create_invoice(payload: dict, today: date | None = None) -> dict:
    """Validates a create-invoice payload and returns the invoice the API stores."""
    raw_lines = payload.get("lines") or []
    if not raw_lines:
        raise BadRequest("an invoice needs at least one line")
    lines = [
        Line(raw["description"], int(raw["quantity"]), int(raw["unit_paise"]), int(raw.get("gst_percent", 18)))
        for raw in raw_lines
    ]
    issued = date.fromisoformat(payload["issued_on"]) if payload.get("issued_on") else (today or date.today())
    amounts = totals(lines)
    due = due_date(issued, int(payload.get("net_days", DEFAULT_NET_DAYS)))
    return {
        "customer_id": payload["customer_id"],
        "issued_on": issued.isoformat(),
        "due_on": due.isoformat(),
        **amounts,
        "total_display": format_inr(amounts["total"]),
    }
