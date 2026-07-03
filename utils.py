"""General utilities for input handling, formatting, and console output."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, Sequence


class InputCancelledError(Exception):
    """Raised when user cancels the application input flow."""


def supports_color() -> bool:
    """Return True if colorama is available and initialized."""
    try:
        from colorama import init

        init(autoreset=True)
        return True
    except Exception:
        return False


_COLOR_ENABLED = supports_color()


class Colors:
    """Simple color wrapper with graceful fallback."""

    GREEN = "\033[92m" if _COLOR_ENABLED else ""
    YELLOW = "\033[93m" if _COLOR_ENABLED else ""
    RED = "\033[91m" if _COLOR_ENABLED else ""
    BLUE = "\033[94m" if _COLOR_ENABLED else ""
    CYAN = "\033[96m" if _COLOR_ENABLED else ""
    RESET = "\033[0m" if _COLOR_ENABLED else ""


def color_text(text: str, color: str) -> str:
    """Return colored text if coloring is enabled."""
    return f"{color}{text}{Colors.RESET}" if _COLOR_ENABLED else text


def print_header(title: str) -> None:
    """Print a stylized section header."""
    line = "=" * 38
    print(color_text(line, Colors.CYAN))
    print(color_text(title.center(38), Colors.CYAN))
    print(color_text(line, Colors.CYAN))


def print_info(message: str) -> None:
    """Print informational message."""
    print(color_text(message, Colors.BLUE))


def print_success(message: str) -> None:
    """Print success message."""
    print(color_text(message, Colors.GREEN))


def print_warning(message: str) -> None:
    """Print warning message."""
    print(color_text(message, Colors.YELLOW))


def print_error(message: str) -> None:
    """Print error message."""
    print(color_text(message, Colors.RED))


def safe_input(prompt: str, allow_empty: bool = False) -> str:
    """Read user input safely and handle interrupt conditions."""
    try:
        value = input(prompt).strip()
    except (KeyboardInterrupt, EOFError) as exc:
        raise InputCancelledError("Input cancelled by user.") from exc

    if not allow_empty and not value:
        raise ValueError("Input cannot be empty.")
    return value


def parse_date(date_text: str) -> str:
    """Validate and normalize date string as YYYY-MM-DD."""
    return datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y-%m-%d")


def parse_amount(amount_text: str) -> float:
    """Validate amount and return positive float value."""
    try:
        amount = Decimal(amount_text)
    except InvalidOperation as exc:
        raise ValueError("Amount must be numeric.") from exc

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return float(amount)


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"INR {amount:,.2f}"


def format_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    """Build a plain-text table for console display."""
    row_list: List[List[str]] = [[str(cell) for cell in row] for row in rows]
    widths = [len(str(h)) for h in headers]

    for row in row_list:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    sep = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    header_line = "| " + " | ".join(
        str(h).ljust(widths[i]) for i, h in enumerate(headers)
    ) + " |"

    table_lines = [sep, header_line, sep]
    for row in row_list:
        table_lines.append(
            "| "
            + " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            + " |"
        )
    table_lines.append(sep)
    return "\n".join(table_lines)


def choose_from_list(title: str, options: Sequence[str]) -> str:
    """Prompt user to select one item from a list."""
    print_header(title)
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")

    while True:
        try:
            value = safe_input("Choose an option number: ")
            position = int(value)
            if 1 <= position <= len(options):
                return options[position - 1]
            print_warning("Invalid selection. Try again.")
        except ValueError:
            print_warning("Please enter a valid number.")
