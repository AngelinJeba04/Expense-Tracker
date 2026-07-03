"""Report generation module for expense analytics."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from expense import Expense
from manager import ExpenseManager


class ReportGenerator:
    """Generates textual reports and saves them into reports folder."""

    def __init__(self, manager: ExpenseManager, reports_dir: Path) -> None:
        self.manager = manager
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _write_report(self, name: str, lines: List[str]) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.reports_dir / f"{name}_{timestamp}.txt"
        with path.open("w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return path

    def monthly_report(self) -> Path:
        summary = self.manager.monthly_summary()
        lines = ["Monthly Report", "=" * 40]
        if not summary:
            lines.append("No expense data available.")
        else:
            for month, total in summary.items():
                lines.append(f"{month}: INR {total:,.2f}")
        return self._write_report("monthly_report", lines)

    def category_report(self) -> Path:
        summary = self.manager.category_summary()
        lines = ["Category-wise Report", "=" * 40]
        if not summary:
            lines.append("No expense data available.")
        else:
            for category, total in summary.items():
                lines.append(f"{category}: INR {total:,.2f}")
        return self._write_report("category_report", lines)

    def payment_method_report(self) -> Path:
        summary = self.manager.payment_method_summary()
        lines = ["Payment Method Report", "=" * 40]
        if not summary:
            lines.append("No expense data available.")
        else:
            for method, total in summary.items():
                lines.append(f"{method}: INR {total:,.2f}")
        return self._write_report("payment_method_report", lines)

    def top10_report(self) -> Path:
        top_expenses = self.manager.top_expenses(10)
        lines = ["Top 10 Expenses", "=" * 40]
        if not top_expenses:
            lines.append("No expense data available.")
        else:
            for expense in top_expenses:
                lines.append(
                    f"{expense.expense_id} | {expense.date} | "
                    f"{expense.category} | {expense.description} | "
                    f"INR {expense.amount:,.2f}"
                )
        return self._write_report("top10_report", lines)

    def budget_report(self) -> Path:
        budget, spent, remaining, exceeded = self.manager.budget_status()
        lines = ["Budget Report", "=" * 40]
        if budget is None:
            lines.append("Budget not set.")
            lines.append(f"Current month spend: INR {spent:,.2f}")
        else:
            lines.append(f"Budget: INR {budget:,.2f}")
            lines.append(f"Current month spend: INR {spent:,.2f}")
            lines.append(f"Remaining: INR {remaining:,.2f}")
            lines.append(f"Status: {'Exceeded' if exceeded else 'Within Budget'}")
        return self._write_report("budget_report", lines)

    def overall_statistics_report(self) -> Path:
        highest: Optional[Expense] = self.manager.highest_expense()
        lowest: Optional[Expense] = self.manager.lowest_expense()
        lines = ["Overall Statistics", "=" * 40]
        lines.append(f"Total spending: INR {self.manager.total_spending():,.2f}")
        lines.append(f"Average expense: INR {self.manager.average_expense():,.2f}")
        if highest:
            lines.append(
                "Highest expense: "
                f"{highest.expense_id} ({highest.description}) - INR {highest.amount:,.2f}"
            )
        else:
            lines.append("Highest expense: N/A")
        if lowest:
            lines.append(
                "Lowest expense: "
                f"{lowest.expense_id} ({lowest.description}) - INR {lowest.amount:,.2f}"
            )
        else:
            lines.append("Lowest expense: N/A")

        lines.append("\nDaily Spending Summary")
        lines.append("-" * 40)
        for day, total in self.manager.daily_summary().items():
            lines.append(f"{day}: INR {total:,.2f}")

        lines.append("\nWeekly Spending Summary")
        lines.append("-" * 40)
        for week, total in self.manager.weekly_summary().items():
            lines.append(f"{week}: INR {total:,.2f}")

        lines.append("\nMonthly Spending Summary")
        lines.append("-" * 40)
        for month, total in self.manager.monthly_dashboard().items():
            lines.append(f"{month}: INR {total:,.2f}")

        return self._write_report("overall_statistics_report", lines)

    def generate_all_reports(self) -> Dict[str, Path]:
        """Generate all configured reports and return their paths."""
        return {
            "monthly": self.monthly_report(),
            "category": self.category_report(),
            "payment": self.payment_method_report(),
            "top10": self.top10_report(),
            "budget": self.budget_report(),
            "overall": self.overall_statistics_report(),
        }
