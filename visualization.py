"""Visualization module for expense charts using matplotlib."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from expense import Expense
from manager import ExpenseManager


class VisualizationManager:
    """Generates expense charts and saves image files."""

    def __init__(self, manager: ExpenseManager, charts_dir: Path) -> None:
        self.manager = manager
        self.charts_dir = Path(charts_dir)
        self.charts_dir.mkdir(parents=True, exist_ok=True)

    def _output_path(self, name: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.charts_dir / f"{name}_{timestamp}.png"

    @staticmethod
    def _has_data(values: Iterable[float]) -> bool:
        return any(value > 0 for value in values)

    def bar_chart_by_category(self) -> Path:
        summary = self.manager.category_summary()
        if not self._has_data(summary.values()):
            raise ValueError("Not enough data to generate category bar chart.")

        plt.figure(figsize=(10, 6))
        plt.bar(summary.keys(), summary.values(), color="#2A9D8F")
        plt.title("Expense by Category")
        plt.ylabel("Amount (INR)")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        path = self._output_path("bar_category")
        plt.savefig(path)
        plt.close()
        return path

    def pie_chart_by_category(self) -> Path:
        summary = self.manager.category_summary()
        if not self._has_data(summary.values()):
            raise ValueError("Not enough data to generate category pie chart.")

        plt.figure(figsize=(8, 8))
        plt.pie(
            summary.values(),
            labels=summary.keys(),
            autopct="%1.1f%%",
            startangle=140,
        )
        plt.title("Category Distribution")
        plt.tight_layout()

        path = self._output_path("pie_category")
        plt.savefig(path)
        plt.close()
        return path

    def monthly_trend_line(self) -> Path:
        summary = self.manager.monthly_summary()
        if not self._has_data(summary.values()):
            raise ValueError("Not enough data to generate monthly trend line.")

        months = list(summary.keys())
        amounts = list(summary.values())

        plt.figure(figsize=(10, 6))
        plt.plot(months, amounts, marker="o", linestyle="-", color="#E76F51")
        plt.title("Monthly Spending Trend")
        plt.xlabel("Month")
        plt.ylabel("Amount (INR)")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        path = self._output_path("monthly_trend")
        plt.savefig(path)
        plt.close()
        return path

    def payment_method_distribution(self) -> Path:
        summary = self.manager.payment_method_summary()
        if not self._has_data(summary.values()):
            raise ValueError("Not enough data to generate payment distribution chart.")

        plt.figure(figsize=(10, 6))
        plt.bar(summary.keys(), summary.values(), color="#264653")
        plt.title("Payment Method Distribution")
        plt.ylabel("Amount (INR)")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        path = self._output_path("payment_distribution")
        plt.savefig(path)
        plt.close()
        return path

    def generate_all_charts(self) -> Dict[str, Path]:
        """Generate all required charts and return their paths."""
        return {
            "bar": self.bar_chart_by_category(),
            "pie": self.pie_chart_by_category(),
            "trend": self.monthly_trend_line(),
            "payment": self.payment_method_distribution(),
        }
