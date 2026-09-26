import unittest
from datetime import date

from ledgerly_api.reminders import reminders_due

TODAY = date(2026, 8, 4)


def invoice(number, due_on, status="sent"):
    return {"number": number, "due_on": due_on, "status": status}


class RemindersTest(unittest.TestCase):
    def test_overdue_and_upcoming(self):
        invoices = [invoice("LDG-1", "2026-08-01"), invoice("LDG-2", "2026-08-06"), invoice("LDG-3", "2026-08-20")]
        self.assertEqual(reminders_due(invoices, TODAY), ["LDG-1", "LDG-2"])

    def test_includes_invoices_due_today(self):
        invoices = [invoice("LDG-6", "2026-08-04"), invoice("LDG-7", "2026-08-07"), invoice("LDG-8", "2026-08-08")]
        self.assertEqual(reminders_due(invoices, TODAY), ["LDG-6", "LDG-7"])

    def test_skips_paid_and_void(self):
        invoices = [invoice("LDG-4", "2026-08-01", "paid"), invoice("LDG-5", "2026-08-01", "void")]
        self.assertEqual(reminders_due(invoices, TODAY), [])


if __name__ == "__main__":
    unittest.main()
