"""
CS 307 - Assignment 2 Prototype
Feature: Add Expense (Transaction entry + validation + persistence)

A small, working prototype that demonstrates:
- input validation (functional correctness)
- saving transactions (persistence)
- updating monthly totals (basic reporting)
- maintainable structure (separation of concerns)

Run:
  python app.py
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import json
from typing import List, Dict, Optional


DATA_FILE = Path("data.json")


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    user_id: str
    amount: Decimal
    category: str
    occurred_on: date
    note: str = ""
    tx_type: str = "EXPENSE"  # "INCOME" or "EXPENSE"

    def to_json(self) -> Dict:
        d = asdict(self)
        d["amount"] = str(self.amount)
        d["occurred_on"] = self.occurred_on.isoformat()
        return d

    @staticmethod
    def from_json(d: Dict) -> "Transaction":
        return Transaction(
            transaction_id=d["transaction_id"],
            user_id=d["user_id"],
            amount=Decimal(d["amount"]),
            category=d["category"],
            occurred_on=date.fromisoformat(d["occurred_on"]),
            note=d.get("note", ""),
            tx_type=d.get("tx_type", "EXPENSE"),
        )


class TransactionRepository:
    """Data access: read/write transactions to a JSON file."""
    def __init__(self, path: Path = DATA_FILE) -> None:
        self.path = path

    def load_all(self) -> List[Transaction]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Transaction.from_json(x) for x in raw.get("transactions", [])]

    def save_all(self, transactions: List[Transaction]) -> None:
        payload = {"transactions": [t.to_json() for t in transactions]}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def append(self, transaction: Transaction) -> None:
        txs = self.load_all()
        txs.append(transaction)
        self.save_all(txs)


class ReportService:
    """Business logic: calculate totals for a month."""
    def __init__(self, repo: TransactionRepository) -> None:
        self.repo = repo

    def monthly_totals(self, user_id: str, year: int, month: int) -> Dict[str, Decimal]:
        txs = self.repo.load_all()
        income = Decimal("0")
        expense = Decimal("0")
        for t in txs:
            if t.user_id != user_id:
                continue
            if t.occurred_on.year == year and t.occurred_on.month == month:
                if t.tx_type.upper() == "INCOME":
                    income += t.amount
                else:
                    expense += t.amount
        return {"income": income, "expense": expense, "net": income - expense}


class ExpenseService:
    """Business logic: validate and create an EXPENSE transaction."""
    def __init__(self, repo: TransactionRepository, reporter: ReportService) -> None:
        self.repo = repo
        self.reporter = reporter

    def add_expense(
        self,
        user_id: str,
        amount_str: str,
        category: str,
        date_str: str,
        note: str = "",
        transaction_id: Optional[str] = None
    ) -> Dict[str, str]:
        amount = self._validate_amount(amount_str)
        category_clean = self._validate_category(category)
        occurred_on = self._validate_date(date_str)

        tx_id = transaction_id or self._new_tx_id()
        tx = Transaction(
            transaction_id=tx_id,
            user_id=user_id,
            amount=amount,
            category=category_clean,
            occurred_on=occurred_on,
            note=note.strip(),
            tx_type="EXPENSE",
        )
        self.repo.append(tx)

        totals = self.reporter.monthly_totals(user_id, occurred_on.year, occurred_on.month)
        return {
            "transaction_id": tx_id,
            "month": f"{occurred_on.year}-{occurred_on.month:02d}",
            "income": str(totals["income"]),
            "expense": str(totals["expense"]),
            "net": str(totals["net"]),
        }

    def _new_tx_id(self) -> str:
        # Simple, readable ID for a prototype (not for production).
        # Using timestamp keeps collisions unlikely for single-user demos.
        return "TX-" + datetime.now().strftime("%H%M%S")

    @staticmethod
    def _validate_amount(amount_str: str) -> Decimal:
        try:
            amount = Decimal(amount_str.strip())
        except (InvalidOperation, AttributeError):
            raise ValueError("Amount must be a valid number (e.g., 12.50).")
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")
        # Round to cents for money.
        return amount.quantize(Decimal("0.01"))

    @staticmethod
    def _validate_category(category: str) -> str:
        if not category or not category.strip():
            raise ValueError("Category is required.")
        if len(category.strip()) > 30:
            raise ValueError("Category must be 30 characters or less.")
        return category.strip()

    @staticmethod
    def _validate_date(date_str: str) -> date:
        try:
            d = date.fromisoformat(date_str.strip())
        except Exception:
            raise ValueError("Date must be in ISO format YYYY-MM-DD.")
        # Light business rule for prototype: no future expenses
        if d > date.today():
            raise ValueError("Date cannot be in the future for an expense entry.")
        return d


def main() -> None:
    # For demo purposes we keep a single user_id.
    user_id = "jason"

    repo = TransactionRepository(DATA_FILE)
    reporter = ReportService(repo)
    service = ExpenseService(repo, reporter)

    print("\n=== Personal Budget App (Prototype) ===")
    print("Feature: Add Expense\n")

    while True:
        try:
            amount = input("Amount (e.g., 45.90): ").strip()
            category = input("Category (e.g., Groceries): ").strip()
            occurred_on = input("Date (YYYY-MM-DD): ").strip()
            note = input("Note (optional): ").strip()

            result = service.add_expense(
                user_id=user_id,
                amount_str=amount,
                category=category,
                date_str=occurred_on,
                note=note
            )

            print("\nSaved ✅")
            print(f"Transaction ID: {result['transaction_id']}")
            print(f"Month: {result['month']}")
            print(f"Totals -> Income: ${result['income']}  Expense: ${result['expense']}  Net: ${result['net']}\n")

        except ValueError as e:
            print(f"\nInput error: {e}\n")

        again = input("Add another expense? (y/n): ").strip().lower()
        if again != "y":
            break

    print("\nDone.\n")


if __name__ == "__main__":
    main()
