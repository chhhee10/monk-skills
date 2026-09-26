"""Which invoices get a payment reminder email today."""

from datetime import date, timedelta

REMIND_DAYS_BEFORE = 3


def reminders_due(invoices: list[dict], today: date) -> list[str]:
    """Numbers of sent (unpaid) invoices that are overdue or due within REMIND_DAYS_BEFORE days."""
    horizon = today + timedelta(days=REMIND_DAYS_BEFORE)
    due_numbers = []
    for invoice in invoices:
        if invoice["status"] != "sent":
            continue
        due_on = date.fromisoformat(invoice["due_on"])
        if due_on < today or today < due_on <= horizon:
            due_numbers.append(invoice["number"])
    return due_numbers
