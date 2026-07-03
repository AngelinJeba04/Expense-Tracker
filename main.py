"""Expense Tracker CLI entry point."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from expense import CATEGORIES, PAYMENT_METHODS, Expense
from manager import ExpenseManager
from reports import ReportGenerator
from utils import (
    InputCancelledError,
    choose_from_list,
    format_currency,
    format_table,
    parse_amount,
    parse_date,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
    safe_input,
)
from visualization import VisualizationManager


class ExpenseTrackerCLI:
    """Interactive command-line interface for Expense Tracker."""

    def __init__(self) -> None:
        self.manager = ExpenseManager(PROJECT_ROOT)
        self.report_generator = ReportGenerator(self.manager, PROJECT_ROOT / "reports")
        self.visualization_manager = VisualizationManager(
            self.manager,
            PROJECT_ROOT / "reports" / "charts",
        )

    def run(self) -> None:
        """Start the interactive application loop."""
        self._print_load_warnings()

        while True:
            try:
                self._print_main_menu()
                choice = safe_input("Select an option (1-12): ")
                if choice == "1":
                    self.add_expense_flow()
                elif choice == "2":
                    self.view_expenses_flow()
                elif choice == "3":
                    self.edit_expense_flow()
                elif choice == "4":
                    self.delete_expense_flow()
                elif choice == "5":
                    self.search_flow()
                elif choice == "6":
                    self.filter_flow()
                elif choice == "7":
                    self.reports_flow()
                elif choice == "8":
                    self.charts_flow()
                elif choice == "9":
                    self.budget_flow()
                elif choice == "10":
                    self.export_flow()
                elif choice == "11":
                    self.backup_flow()
                elif choice == "12":
                    print_success("Thank you for using Expense Tracker.")
                    return
                else:
                    print_warning("Invalid menu option. Please choose between 1 and 12.")
            except InputCancelledError:
                print_warning("Input interrupted. Returning to main menu.")
            except KeyboardInterrupt:
                print_warning("Operation cancelled. Returning to main menu.")
            except Exception as exc:
                print_error(f"Unexpected error: {exc}")

    @staticmethod
    def _print_main_menu() -> None:
        print_header("Expense Tracker")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Search")
        print("6. Filter")
        print("7. Reports")
        print("8. Charts")
        print("9. Budget")
        print("10. Export")
        print("11. Backup")
        print("12. Exit")

    def _print_load_warnings(self) -> None:
        if self.manager.load_warnings:
            print_warning("Some records could not be loaded:")
            for warning in self.manager.load_warnings:
                print_warning(f"- {warning}")

    def add_expense_flow(self) -> None:
        """Prompt user and add a new expense."""
        print_header("Add Expense")

        date_text = self._prompt_date(default_today=True)
        category = choose_from_list("Choose Category", CATEGORIES)
        description = safe_input("Description: ")
        amount = self._prompt_amount()
        payment_method = choose_from_list("Choose Payment Method", PAYMENT_METHODS)
        notes = safe_input("Notes (optional): ", allow_empty=True)

        expense = self.manager.add_expense(
            date=date_text,
            category=category,
            description=description,
            amount=amount,
            payment_method=payment_method,
            notes=notes,
        )
        print_success(f"Expense added with ID: {expense.expense_id}")
        self._print_budget_warning()

    def view_expenses_flow(self) -> None:
        """Display expenses, sorting choices, and quick dashboard."""
        print_header("View Expenses")

        sort_choice = choose_from_list(
            "Sort Options",
            ["Date", "Amount", "Alphabetical"],
        )
        sort_key = sort_choice.lower()
        expenses = self.manager.sort_expenses(sort_key)
        self._display_expenses(expenses)

        print_header("Recent Transactions")
        self._display_expenses(self.manager.recent_transactions(limit=5))

        print_header("Statistics Dashboard")
        print(f"Total Spending: {format_currency(self.manager.total_spending())}")
        print(f"Average Expense: {format_currency(self.manager.average_expense())}")

        highest = self.manager.highest_expense()
        lowest = self.manager.lowest_expense()
        print(
            "Highest Expense: "
            + (
                f"{highest.expense_id} ({highest.description}) - "
                f"{format_currency(highest.amount)}"
                if highest
                else "N/A"
            )
        )
        print(
            "Lowest Expense: "
            + (
                f"{lowest.expense_id} ({lowest.description}) - "
                f"{format_currency(lowest.amount)}"
                if lowest
                else "N/A"
            )
        )

    def edit_expense_flow(self) -> None:
        """Prompt and edit an expense."""
        print_header("Edit Expense")
        expense_id = safe_input("Enter Expense ID to edit: ").upper()
        expense = self.manager.get_expense(expense_id)
        if expense is None:
            print_error("Expense ID not found.")
            return

        print_info("Leave a field empty to keep current value.")

        date_input = safe_input(f"Date [{expense.date}]: ", allow_empty=True)
        category_input = safe_input(
            f"Category [{expense.category}] (type exactly): ", allow_empty=True
        )
        description_input = safe_input(
            f"Description [{expense.description}]: ", allow_empty=True
        )
        amount_input = safe_input(
            f"Amount [{expense.amount:.2f}]: ", allow_empty=True
        )
        method_input = safe_input(
            f"Payment Method [{expense.payment_method}] (type exactly): ",
            allow_empty=True,
        )
        notes_input = safe_input(f"Notes [{expense.notes}]: ", allow_empty=True)

        updates: Dict[str, object] = {}
        if date_input:
            updates["date"] = parse_date(date_input)
        if category_input:
            if category_input not in CATEGORIES:
                raise ValueError("Invalid category.")
            updates["category"] = category_input
        if description_input:
            updates["description"] = description_input
        if amount_input:
            updates["amount"] = parse_amount(amount_input)
        if method_input:
            if method_input not in PAYMENT_METHODS:
                raise ValueError("Invalid payment method.")
            updates["payment_method"] = method_input
        if notes_input:
            updates["notes"] = notes_input

        self.manager.edit_expense(expense_id, **updates)
        print_success("Expense updated successfully.")
        self._print_budget_warning()

    def delete_expense_flow(self) -> None:
        """Prompt and delete an expense with confirmation."""
        print_header("Delete Expense")
        expense_id = safe_input("Enter Expense ID to delete: ").upper()
        expense = self.manager.get_expense(expense_id)
        if expense is None:
            print_error("Expense ID not found.")
            return

        self._display_expenses([expense])
        confirm = safe_input("Confirm deletion? (y/n): ").lower()
        if confirm != "y":
            print_info("Deletion cancelled.")
            return

        if self.manager.delete_expense(expense_id):
            print_success("Expense deleted successfully.")
        else:
            print_error("Deletion failed.")

    def search_flow(self) -> None:
        """Search expenses by keyword."""
        print_header("Search")
        keyword = safe_input("Enter keyword: ")
        results = self.manager.search(keyword)
        self._display_expenses(results)

    def filter_flow(self) -> None:
        """Filter expenses by category/payment/date."""
        print_header("Filter")

        use_category = safe_input("Filter by category? (y/n): ").lower() == "y"
        category = choose_from_list("Category", CATEGORIES) if use_category else None

        use_method = safe_input("Filter by payment method? (y/n): ").lower() == "y"
        payment_method = (
            choose_from_list("Payment Method", PAYMENT_METHODS) if use_method else None
        )

        use_date = safe_input("Filter by date? (y/n): ").lower() == "y"
        date_value = self._prompt_date(default_today=False) if use_date else None

        results = self.manager.filter_expenses(
            category=category,
            payment_method=payment_method,
            date_value=date_value,
        )
        self._display_expenses(results)

    def reports_flow(self) -> None:
        """Generate selected reports."""
        print_header("Reports")
        print("1. Monthly Report")
        print("2. Category-wise Report")
        print("3. Payment Method Report")
        print("4. Top 10 Expenses")
        print("5. Budget Report")
        print("6. Overall Statistics")
        print("7. Generate All")

        choice = safe_input("Choose report option: ")
        if choice == "1":
            path = self.report_generator.monthly_report()
            print_success(f"Report generated: {path}")
        elif choice == "2":
            path = self.report_generator.category_report()
            print_success(f"Report generated: {path}")
        elif choice == "3":
            path = self.report_generator.payment_method_report()
            print_success(f"Report generated: {path}")
        elif choice == "4":
            path = self.report_generator.top10_report()
            print_success(f"Report generated: {path}")
        elif choice == "5":
            path = self.report_generator.budget_report()
            print_success(f"Report generated: {path}")
        elif choice == "6":
            path = self.report_generator.overall_statistics_report()
            print_success(f"Report generated: {path}")
        elif choice == "7":
            paths = self.report_generator.generate_all_reports()
            print_success("All reports generated:")
            for key, path in paths.items():
                print_success(f"- {key}: {path}")
        else:
            print_warning("Invalid report option.")

    def charts_flow(self) -> None:
        """Generate selected visual charts."""
        print_header("Charts")
        print("1. Bar Chart")
        print("2. Pie Chart")
        print("3. Monthly Trend Line")
        print("4. Payment Method Distribution")
        print("5. Generate All")

        choice = safe_input("Choose chart option: ")
        try:
            if choice == "1":
                path = self.visualization_manager.bar_chart_by_category()
                print_success(f"Chart generated: {path}")
            elif choice == "2":
                path = self.visualization_manager.pie_chart_by_category()
                print_success(f"Chart generated: {path}")
            elif choice == "3":
                path = self.visualization_manager.monthly_trend_line()
                print_success(f"Chart generated: {path}")
            elif choice == "4":
                path = self.visualization_manager.payment_method_distribution()
                print_success(f"Chart generated: {path}")
            elif choice == "5":
                paths = self.visualization_manager.generate_all_charts()
                print_success("All charts generated:")
                for key, path in paths.items():
                    print_success(f"- {key}: {path}")
            else:
                print_warning("Invalid chart option.")
        except ValueError as exc:
            print_warning(str(exc))

    def budget_flow(self) -> None:
        """Manage and inspect monthly budget."""
        print_header("Budget")
        print("1. View Budget Status")
        print("2. Set Budget")
        print("3. Clear Budget")

        choice = safe_input("Choose budget option: ")
        if choice == "1":
            budget, spent, remaining, exceeded = self.manager.budget_status()
            if budget is None:
                print_info("Budget is not set.")
            else:
                print_info(f"Budget: {format_currency(budget)}")
                print_info(f"Current month spend: {format_currency(spent)}")
                print_info(f"Remaining: {format_currency(remaining)}")
                if exceeded:
                    print_warning("Budget exceeded for current month.")
                else:
                    print_success("Within budget.")
        elif choice == "2":
            amount = self._prompt_amount(prompt="Enter monthly budget amount: ")
            self.manager.set_budget(amount)
            print_success("Budget saved.")
        elif choice == "3":
            self.manager.set_budget(None)
            print_success("Budget cleared.")
        else:
            print_warning("Invalid budget option.")

    def export_flow(self) -> None:
        """Export or import expense data."""
        print_header("Export / Import")
        print("1. Export CSV")
        print("2. Export JSON")
        print("3. Import JSON")

        choice = safe_input("Choose export option: ")
        if choice == "1":
            path = self.manager.export_csv()
            print_success(f"CSV exported: {path}")
        elif choice == "2":
            path = self.manager.export_json()
            print_success(f"JSON exported: {path}")
        elif choice == "3":
            import_path = Path(safe_input("Enter JSON file path to import: "))
            try:
                imported = self.manager.import_json(import_path)
                print_success(f"Imported {imported} expense(s) from JSON.")
                self._print_budget_warning()
            except ValueError as exc:
                print_error(str(exc))
        else:
            print_warning("Invalid export option.")

    def backup_flow(self) -> None:
        """Create manual backup."""
        print_header("Backup")
        path = self.manager.create_backup()
        print_success(f"Backup created: {path}")

    def _display_expenses(self, expenses: Iterable[Expense]) -> None:
        items: List[Expense] = list(expenses)
        if not items:
            print_warning("No expenses found.")
            return

        table = format_table(
            headers=[
                "ID",
                "Date",
                "Category",
                "Description",
                "Amount",
                "Method",
                "Notes",
            ],
            rows=[
                [
                    item.expense_id,
                    item.date,
                    item.category,
                    item.description,
                    f"{item.amount:.2f}",
                    item.payment_method,
                    item.notes,
                ]
                for item in items
            ],
        )
        print(table)

    @staticmethod
    def _prompt_date(default_today: bool = False) -> str:
        while True:
            hint = " (leave empty for today)" if default_today else ""
            raw = safe_input(f"Date (YYYY-MM-DD){hint}: ", allow_empty=default_today)
            if default_today and not raw:
                return datetime.now().strftime("%Y-%m-%d")
            try:
                return parse_date(raw)
            except ValueError:
                print_warning("Invalid date. Please use YYYY-MM-DD.")

    @staticmethod
    def _prompt_amount(prompt: str = "Amount: ") -> float:
        while True:
            raw = safe_input(prompt)
            try:
                return parse_amount(raw)
            except ValueError as exc:
                print_warning(str(exc))

    def _print_budget_warning(self) -> None:
        budget, spent, remaining, exceeded = self.manager.budget_status()
        if budget is not None and exceeded:
            print_warning(
                "Budget warning: current month spending exceeded budget by "
                f"{format_currency(abs(remaining))}."
            )
            print_warning(f"Budget: {format_currency(budget)}, Spent: {format_currency(spent)}")


def main() -> None:
    """Application entry point with robust top-level exception handling."""
    app = ExpenseTrackerCLI()
    try:
        app.run()
    except KeyboardInterrupt:
        print_warning("Application interrupted by user. Exiting safely.")
    except Exception as exc:
        print_error(f"Fatal error: {exc}")


if __name__ == "__main__":
    main()
