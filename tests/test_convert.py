import unittest
from unittest.mock import patch

from currency_cli import rates

TABLE = {"bank": "ecb", "rate_date": "2026-09-02", "rates": [
    {"base": "EUR", "quote": "USD", "type": "reference", "value": 1.25},
    {"base": "EUR", "quote": "GBP", "type": "reference", "value": 0.8},
]}


class ConvertTests(unittest.TestCase):
    def setUp(self):
        self.p = patch("currency_cli.rates.latest_table", return_value=TABLE)
        self.p.start()

    def tearDown(self):
        self.p.stop()

    def test_published(self):
        r = rates.convert(10, "EUR", "USD")
        self.assertEqual((r["result"], r["method"]), (12.5, "published"))

    def test_inverse(self):
        r = rates.convert(12.5, "USD", "EUR")
        self.assertEqual((r["result"], r["method"]), (10.0, "inverse"))

    def test_cross(self):
        r = rates.convert(100, "USD", "GBP")
        self.assertEqual(r["result"], 64.0)
        self.assertTrue(r["method"].startswith("cross"))

    def test_unknown(self):
        with self.assertRaises(ValueError):
            rates.convert(1, "USD", "XXX")


if __name__ == "__main__":
    unittest.main()
