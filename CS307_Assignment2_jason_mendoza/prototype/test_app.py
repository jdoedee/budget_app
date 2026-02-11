"""
Basic tests for CS 307 Assignment 2 prototype.
Run (optional):
  python -m unittest test_app.py
"""

import unittest
from pathlib import Path

from app import TransactionRepository, ReportService, ExpenseService


class TestAddExpenseFeature(unittest.TestCase):
    def setUp(self):
        self.tmp = Path("test_data.json")
        if self.tmp.exists():
            self.tmp.unlink()
        self.repo = TransactionRepository(self.tmp)
        self.reporter = ReportService(self.repo)
        self.service = ExpenseService(self.repo, self.reporter)

    def tearDown(self):
        if self.tmp.exists():
            self.tmp.unlink()

    def test_add_expense_saves_transaction_and_updates_totals(self):
        result = self.service.add_expense(
            user_id="jason",
            amount_str="10.00",
            category="Groceries",
            date_str="2026-02-10",
            note="milk"
        )
        self.assertTrue(result["transaction_id"].startswith("TX-"))
        totals = self.reporter.monthly_totals("jason", 2026, 2)
        self.assertEqual(str(totals["expense"]), "10.00")

    def test_validation_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            self.service.add_expense(
                user_id="jason",
                amount_str="-5",
                category="Groceries",
                date_str="2026-02-10"
            )

    def test_validation_rejects_blank_category(self):
        with self.assertRaises(ValueError):
            self.service.add_expense(
                user_id="jason",
                amount_str="5.00",
                category="   ",
                date_str="2026-02-10"
            )


if __name__ == "__main__":
    unittest.main()
