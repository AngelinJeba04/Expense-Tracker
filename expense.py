"""Expense domain model and constants."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Health",
    "Entertainment",
    "Education",
    "Travel",
    "Investment",
    "Others",
]

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Debit Card",
    "Credit Card",
    "Bank Transfer",
    "Wallet",
]


@dataclass
class Expense:
    """Represents a single expense entry."""

    expense_id: str
    date: str
    category: str
    description: str
    amount: float
    payment_method: str
    notes: str = ""

    def __post_init__(self) -> None:
        self.expense_id = str(self.expense_id).strip()
        self.date = str(self.date).strip()
        self.category = str(self.category).strip()
        self.description = str(self.description).strip()
        self.payment_method = str(self.payment_method).strip()
        self.notes = str(self.notes).strip()
        self.amount = float(self.amount)
        self.validate()

    def validate(self) -> None:
        """Validate all expense fields."""
        if not self.expense_id:
            raise ValueError("Expense ID cannot be empty.")

        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Date must be in YYYY-MM-DD format.") from exc

        if self.category not in CATEGORIES:
            raise ValueError(f"Invalid category: {self.category}")

        if not self.description:
            raise ValueError("Description cannot be empty.")

        if self.amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if self.payment_method not in PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method: {self.payment_method}")

    def to_dict(self) -> Dict[str, str]:
        """Serialize expense to a dictionary compatible with CSV/JSON."""
        return {
            "expense_id": self.expense_id,
            "date": self.date,
            "category": self.category,
            "description": self.description,
            "amount": f"{self.amount:.2f}",
            "payment_method": self.payment_method,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Expense":
        """Create an Expense object from a dictionary."""
        return cls(
            expense_id=str(payload.get("expense_id", "")).strip(),
            date=str(payload.get("date", "")).strip(),
            category=str(payload.get("category", "")).strip(),
            description=str(payload.get("description", "")).strip(),
            amount=float(payload.get("amount", 0)),
            payment_method=str(payload.get("payment_method", "")).strip(),
            notes=str(payload.get("notes", "")).strip(),
        )
