"""Storage layer for CSV persistence, JSON import/export, and backups."""

from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from expense import Expense

CSV_HEADERS = [
    "expense_id",
    "date",
    "category",
    "description",
    "amount",
    "payment_method",
    "notes",
]


class StorageManager:
    """Manages reading/writing expenses and project artifacts."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.backup_dir = self.project_root / "backup"
        self.exports_dir = self.project_root / "exports"
        self.reports_dir = self.project_root / "reports"
        self.charts_dir = self.project_root / "charts"
        self.report_charts_dir = self.reports_dir / "charts"
        self.csv_path = self.data_dir / "expenses.csv"
        self.config_path = self.data_dir / "config.json"
        self._ensure_layout()

    def _ensure_layout(self) -> None:
        for folder in [
            self.data_dir,
            self.backup_dir,
            self.exports_dir,
            self.reports_dir,
            self.charts_dir,
            self.report_charts_dir,
        ]:
            folder.mkdir(parents=True, exist_ok=True)

        if not self.csv_path.exists():
            with self.csv_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
                writer.writeheader()

        if not self.config_path.exists():
            self.save_budget(None)

    def load_expenses(self) -> Tuple[List[Expense], List[str]]:
        """Load expenses from CSV and return tuple of records and warnings."""
        expenses: List[Expense] = []
        warnings: List[str] = []

        if not self.csv_path.exists():
            self._ensure_layout()
            return expenses, warnings

        try:
            with self.csv_path.open("r", newline="", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                if not reader.fieldnames:
                    raise ValueError("CSV file is empty or corrupted.")

                missing_fields = [
                    field for field in CSV_HEADERS if field not in reader.fieldnames
                ]
                if missing_fields:
                    raise ValueError(
                        "CSV file is missing required columns: "
                        + ", ".join(missing_fields)
                    )

                for row_number, row in enumerate(reader, start=2):
                    try:
                        expense = Expense.from_dict(row)
                        expenses.append(expense)
                    except Exception as exc:
                        warnings.append(
                            f"Skipped invalid row {row_number}: {exc}"
                        )
        except Exception as exc:
            warnings.append(f"Unable to read CSV: {exc}")

        return expenses, warnings

    def save_expenses(self, expenses: List[Expense]) -> None:
        """Persist expenses to CSV atomically."""
        temp_path = self.csv_path.with_suffix(".tmp")
        with temp_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for expense in expenses:
                writer.writerow(expense.to_dict())
        temp_path.replace(self.csv_path)

    def create_backup(self) -> Path:
        """Create a timestamped CSV backup and return its path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"expenses_backup_{timestamp}.csv"
        shutil.copy2(self.csv_path, backup_path)
        return backup_path

    def export_csv(self, expenses: List[Expense]) -> Path:
        """Export expenses to exports folder as CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = self.exports_dir / f"expenses_export_{timestamp}.csv"
        with export_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for expense in expenses:
                writer.writerow(expense.to_dict())
        return export_path

    def export_json(self, expenses: List[Expense]) -> Path:
        """Export expenses to exports folder as JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = self.exports_dir / f"expenses_export_{timestamp}.json"
        payload = [expense.to_dict() for expense in expenses]
        with export_path.open("w", encoding="utf-8") as json_file:
            json.dump(payload, json_file, indent=2)
        return export_path

    def import_json(self, json_path: Path) -> List[Expense]:
        """Import expenses from a JSON file and return parsed records."""
        try:
            with Path(json_path).open("r", encoding="utf-8") as json_file:
                payload = json.load(json_file)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON format: {exc}") from exc
        except OSError as exc:
            raise ValueError(f"Unable to read JSON file: {exc}") from exc

        if not isinstance(payload, list):
            raise ValueError("JSON root must be a list of expense objects.")

        expenses: List[Expense] = []
        for index, record in enumerate(payload, start=1):
            if not isinstance(record, dict):
                raise ValueError(f"Invalid record at position {index}: expected object.")
            expenses.append(Expense.from_dict(record))
        return expenses

    def load_budget(self) -> Optional[float]:
        """Load budget from config file."""
        try:
            with self.config_path.open("r", encoding="utf-8") as config_file:
                payload: Dict[str, Optional[float]] = json.load(config_file)
            budget = payload.get("budget")
            if budget is None:
                return None
            amount = float(budget)
            if amount <= 0:
                return None
            return amount
        except (json.JSONDecodeError, OSError, ValueError, TypeError):
            return None

    def save_budget(self, budget: Optional[float]) -> None:
        """Save budget to config file."""
        with self.config_path.open("w", encoding="utf-8") as config_file:
            json.dump({"budget": budget}, config_file, indent=2)
