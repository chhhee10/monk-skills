import unittest

from ledgerly_api.money import format_inr, to_paise


class ToPaiseTest(unittest.TestCase):
    def test_rupees_and_paise(self):
        self.assertEqual(to_paise("1499.50"), 149950)

    def test_rounds_half_up(self):
        self.assertEqual(to_paise("0.005"), 1)

    def test_integer_rupees(self):
        self.assertEqual(to_paise(12), 1200)


class FormatInrTest(unittest.TestCase):
    def test_small_amount(self):
        self.assertEqual(format_inr(149950), "₹1,499.50")

    def test_paise_only(self):
        self.assertEqual(format_inr(5), "₹0.05")

    def test_negative(self):
        self.assertEqual(format_inr(-50000), "-₹500.00")


if __name__ == "__main__":
    unittest.main()
