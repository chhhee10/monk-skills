import unittest
from datetime import date

from ledgerly_api.handlers import BadRequest, create_invoice


class CreateInvoiceTest(unittest.TestCase):
    def test_preview(self):
        payload = {
            "customer_id": 1017,
            "issued_on": "2026-08-03",
            "net_days": 15,
            "lines": [{"description": "Growth plan, 5 seats", "quantity": 5, "unit_paise": 99900}],
        }
        invoice = create_invoice(payload)
        self.assertEqual(invoice["due_on"], "2026-08-18")
        self.assertEqual(invoice["total"], 589410)
        self.assertEqual(invoice["total_display"], "₹5,894.10")

    def test_defaults_to_today_and_net_15(self):
        payload = {"customer_id": 1017, "lines": [{"description": "Starter", "quantity": 1, "unit_paise": 49900}]}
        invoice = create_invoice(payload, today=date(2026, 8, 3))
        self.assertEqual((invoice["issued_on"], invoice["due_on"]), ("2026-08-03", "2026-08-18"))

    def test_needs_lines(self):
        with self.assertRaises(BadRequest):
            create_invoice({"customer_id": 1017, "lines": []})


if __name__ == "__main__":
    unittest.main()
