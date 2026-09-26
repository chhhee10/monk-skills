import unittest

from ledgerly_api.invoices import Line, line_tax, totals


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

    def test_rejects_zero_quantity(self):
        with self.assertRaises(ValueError):
            totals([Line("Nothing", 0, 100)])


if __name__ == "__main__":
    unittest.main()
