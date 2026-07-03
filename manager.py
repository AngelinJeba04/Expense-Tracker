"""Business logic for managing expense operations and analytics."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from expense import CATEGORIES, PAYMENT_METHODS, Expense
from storage import StorageManager


class ExpenseManager:
    """High-level service for expense CRUD, filtering, and reporting stats."""

    def __init__(self, project_root: Path) -> None:
        self.storage = StorageManager(project_root)
        self.expenses: List[Expense] = []
        self.load_warnings: List[str] = []
        self.budget: Optional[float] = None
        self._load()

    def _load(self) -> None:
        self.expenses, self.load_warnings = self.storage.load_expenses()
        self._resolve_duplicate_ids()
        self.budget = self.storage.load_budget()

    def _resolve_duplicate_ids(self) -> None:
        seen = set()
        for expense in self.expenses:
            if expense.expense_id in seen:
                expense.expense_id = self._next_id()
            seen.add(expense.expense_id)

    def _next_id(self) -> str:
        max_index = 0
        for expense in self.expenses:
            raw = expense.expense_id.strip().lower()
            if raw.startswith("exp-"):
                suffix = raw.replace("exp-", "")
                if suffix.isdigit():
                    max_index = max(max_index, int(suffix))
        return f"EXP-{max_index + 1:06d}"

    def _persist(self, backup: bool = True) -> None:
        self.storage.save_expenses(self.expenses)
        if backup:
            self.storage.create_backup()

    def add_expense(
        self,
        date: str,
        category: str,
        description: str,
        amount: float,
        payment_method: str,
        notes: str,
    ) -> Expense:
        """Create and persist a new expense record."""
        expense = Expense(
            expense_id=self._next_id(),
            date=date,
            category=category,
            description=description,
            amount=amount,
            payment_method=payment_method,
            notes=notes,
        )
        self.expenses.append(expense)
        self._persist()
        return expense

    def view_expenses(self) -> List[Expense]:
        """Return all expenses sorted by date descending then amount descending."""
        return sorted(
            self.expenses,
            key=lambda item: (item.date, item.amount),
            reverse=True,
        )

    def get_expense(self, expense_id: str) -> Optional[Expense]:
        """Get one expense by ID."""
        target = expense_id.strip().upper()
        for expense in self.expenses:
            if expense.expense_id.upper() == target:
                return expense
        return None

    def edit_expense(self, expense_id: str, **updates: object) -> Expense:
        """Update an expense by ID and persist changes."""
        expense = self.get_expense(expense_id)
        if expense is None:
            raise ValueError("Expense ID not found.")

        merged = expense.to_dict()
        for key, value in updates.items():
            if key in merged and value is not None:
                merged[key] = value

        updated = Expense.from_dict(merged)
        expense.date = updated.date
        expense.category = updated.category
        expense.description = updated.description
        expense.amount = updated.amount
        expense.payment_method = updated.payment_method
        expense.notes = updated.notes
        self._persist()
        return expense

    def delete_expense(self, expense_id: str) -> bool:
        """Delete expense by ID and return whether deletion happened."""
        expense = self.get_expense(expense_id)
        if expense is None:
            return False
        self.expenses.remove(expense)
        self._persist()
        return True

    def search(self, keyword: str) -> List[Expense]:
        """Search expenses by keyword across all text fields."""
        key = keyword.strip().lower()
        if not key:
            return []

        matched = []
        for expense in self.expenses:
            haystack = " ".join(
                [
                    expense.expense_id,
                    expense.date,
                    expense.category,
                    expense.description,
                    expense.payment_method,
                    expense.notes,
                    f"{expense.amount:.2f}",
                ]
            ).lower()
            if key in haystack:
                matched.append(expense)
        return matched

    def filter_expenses(
        self,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        date_value: Optional[str] = None,
    ) -> List[Expense]:
        """Filter expenses by category, payment method, and/or exact date."""
        results = self.expenses
        if category:
            results = [item for item in results if item.category == category]
        if payment_method:
            results = [item for item in results if item.payment_method == payment_method]
        if date_value:
            results = [item for item in results if item.date == date_value]
        return sorted(results, key=lambda item: item.date, reverse=True)

    def sort_expenses(self, sort_key: str) -> List[Expense]:
        """Return sorted expense list by supported key."""
        key = sort_key.lower().strip()
        if key == "date":
            return sorted(self.expenses, key=lambda item: item.date, reverse=True)
        if key == "amount":
            return sorted(self.expenses, key=lambda item: item.amount, reverse=True)
        if key == "alphabetical":
            return sorted(self.expenses, key=lambda item: item.description.lower())
        raise ValueError("Invalid sort option.")

    def total_spending(self) -> float:
        """Return total spending across all expenses."""
        return sum(item.amount for item in self.expenses)

    def highest_expense(self) -> Optional[Expense]:
        """Return highest expense record."""
        if not self.expenses:
            return None
        return max(self.expenses, key=lambda item: item.amount)

    def lowest_expense(self) -> Optional[Expense]:
        """Return lowest expense record."""
        if not self.expenses:
            return None
        return min(self.expenses, key=lambda item: item.amount)

    def average_expense(self) -> float:
        """Return average expense amount."""
        if not self.expenses:
            return 0.0
        return self.total_spending() / len(self.expenses)

    def monthly_summary(self) -> Dict[str, float]:
        """Return month-wise totals keyed as YYYY-MM."""
        summary: Dict[str, float] = defaultdict(float)
        for expense in self.expenses:
            key = expense.date[:7]
            summary[key] += expense.amount
        return dict(sorted(summary.items()))

    def category_summary(self) -> Dict[str, float]:
        """Return totals by category."""
        summary: Dict[str, float] = {category: 0.0 for category in CATEGORIES}
        for expense in self.expenses:
            summary[expense.category] += expense.amount
        return {k: v for k, v in summary.items() if v > 0}

    def payment_method_summary(self) -> Dict[str, float]:
        """Return totals by payment method."""
        summary: Dict[str, float] = {method: 0.0 for method in PAYMENT_METHODS}
        for expense in self.expenses:
            summary[expense.payment_method] += expense.amount
        return {k: v for k, v in summary.items() if v > 0}

    def top_expenses(self, limit: int = 10) -> List[Expense]:
        """Return top N highest expenses."""
        return sorted(self.expenses, key=lambda item: item.amount, reverse=True)[:limit]

    def recent_transactions(self, limit: int = 5) -> List[Expense]:
        """Return most recent expenses by date and id order."""
        return sorted(
            self.expenses,
            key=lambda item: (item.date, item.expense_id),
            reverse=True,
        )[:limit]

    def daily_summary(self) -> Dict[str, float]:
        """Return daily spending summary."""
        summary: Dict[str, float] = defaultdict(float)
        for expense in self.expenses:
            summary[expense.date] += expense.amount
        return dict(sorted(summary.items()))

    def weekly_summary(self) -> Dict[str, float]:
        """Return ISO week spending summary."""
        summary: Dict[str, float] = defaultdict(float)
        for expense in self.expenses:
            dt = datetime.strptime(expense.date, "%Y-%m-%d")
            iso_year, iso_week, _ = dt.isocalendar()
            key = f"{iso_year}-W{iso_week:02d}"
            summary[key] += expense.amount
        return dict(sorted(summary.items()))

    def monthly_dashboard(self) -> Dict[str, float]:
        """Return monthly spending summary for dashboard."""
        return self.monthly_summary()

    def set_budget(self, amount: Optional[float]) -> None:
        """Set or clear budget."""
        if amount is not None and amount <= 0:
            raise ValueError("Budget must be greater than zero.")
        self.budget = amount
        self.storage.save_budget(amount)

    def budget_status(self) -> Tuple[Optional[float], float, float, bool]:
        """Return budget, current month spend, remaining, and exceeded flag."""
        current_month = datetime.now().strftime("%Y-%m")
        spent = sum(item.amount for item in self.expenses if item.date.startswith(current_month))
        if self.budget is None:
            return None, spent, 0.0, False
        remaining = self.budget - spent
        exceeded = spent > self.budget
        return self.budget, spent, remaining, exceeded

    def export_csv(self) -> Path:
        """Export current expenses to CSV."""
        return self.storage.export_csv(self.expenses)

    def export_json(self) -> Path:
        """Export current expenses to JSON."""
        return self.storage.export_json(self.expenses)

    def import_json(self, json_path: Path) -> int:
        """Import expenses from JSON and merge without duplicate IDs."""
        imported = self.storage.import_json(json_path)
        existing_ids = {item.expense_id for item in self.expenses}
        imported_count = 0
        for expense in imported:
            if expense.expense_id in existing_ids:
                expense.expense_id = self._next_id()
            self.expenses.append(expense)
            existing_ids.add(expense.expense_id)
            imported_count += 1
        self._persist()
        return imported_count

    def create_backup(self) -> Path:
        """Create manual backup and return file path."""
        return self.storage.create_backup()
