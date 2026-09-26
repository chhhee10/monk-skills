import unittest
from datetime import date

from ledgerly_api.invoices import Line, due_date, line_tax, totals


class TotalsTest(unittest.TestCase):
    def test_single_line(self):
        t = totals([Line("Growth plan, 5 seats", 5, 99900)])
        self.assertEqual(t, {"subtotal": 499500, "gst": 89910, "total": 589410})

    def test_gst_rounds_per_line(self):
        # 18% of 125 paise is 22.5 -> 23 per line; rounding the total instead would give 45.
        lines = [Line("SMS pack", 1, 125), Line("SMS pack", 1, 125)]
        self.assertEqual(line_tax(lines[0]), 23)
        self.assertEqual(totals(lines)["gst"], 46)

    def test_zero_gst_line(self):
        t = totals([Line("Exempt training", 1, 100000, gst_percent=0)])
        self.assertEqual(t["gst"], 0)

    def test_credit_note(self):
        t = totals([Line("Refund: 2 unused seats", -2, 99900)])
        self.assertEqual(t, {"subtotal": -199800, "gst": -35964, "total": -235764})

    def test_credit_note_rounds_away_from_zero(self):
        self.assertEqual(line_tax(Line("SMS pack refund", -1, 125)), -23)

    def test_rejects_zero_quantity(self):
        with self.assertRaises(ValueError):
            totals([Line("Nothing", 0, 100)])


class DueDateTest(unittest.TestCase):
    def test_same_month(self):
        self.assertEqual(due_date(date(2026, 8, 1), 15), date(2026, 8, 16))

    def test_rolls_into_next_month(self):
        self.assertEqual(due_date(date(2026, 8, 20), 15), date(2026, 9, 4))

    def test_net_30(self):
        self.assertEqual(due_date(date(2026, 8, 10), 30), date(2026, 9, 9))

    def test_rejects_negative_terms(self):
        with self.assertRaises(ValueError):
            due_date(date(2026, 8, 1), -1)


if __name__ == "__main__":
    unittest.main()
