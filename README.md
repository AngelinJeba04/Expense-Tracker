# Expense Tracker (CSV/JSON)

A professional, offline-first Python Expense Tracker application to record, manage, analyze, and visualize personal expenses.

## Project Overview

This application helps you:
- Track expenses with robust validation and auto-generated IDs.
- Edit, delete, search, filter, and sort expenses.
- Generate summary reports and visual charts.
- Set monthly budgets and receive over-budget warnings.
- Auto-save data in CSV with JSON import/export support.
- Create automatic and manual backups.

## Intern  Details
Intern ID:     CITS4930
Name:          J.Angelin Jeba
NO. Of Weeks:  4
Project name:  Expense Tracker

## Features

### Core Features
- Add, view, edit, delete expenses
- Search by keyword
- Filter by category, payment method, and date
- Sort by date, amount, and alphabetical description
- Monthly summary and category summary
- Total, highest, lowest, and average expense analytics
- Budget setup and budget-exceeded warning
- Automatic data loading and saving
- Automatic backup creation on data changes

### Bonus Features
- Recent transactions panel
- Expense statistics dashboard
- Daily, weekly, and monthly spending summaries
- Pretty console formatting
- Confirmation before deletion
- Colored terminal output when `colorama` is available

## Folder Structure

```text
Expense_Tracker/
├── main.py
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── src/
│   ├── expense.py
│   ├── manager.py
│   ├── reports.py
│   ├── storage.py
│   ├── utils.py
│   └── visualization.py
├── data/
│   └── expenses.csv (auto-created)
├── backup/
├── exports/
├── reports/
│   └── charts/
└── charts/
```

## Installation

1. Ensure Python 3.10+ is installed.
2. Open terminal in the project folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

Main menu:

```text
======================================
            Expense Tracker
======================================
1. Add Expense
2. View Expenses
3. Edit Expense
4. Delete Expense
5. Search
6. Filter
7. Reports
8. Charts
9. Budget
10. Export
11. Backup
12. Exit
```

## Reports Generated

Saved inside `reports/`:
- Monthly Report
- Category-wise Report
- Payment Method Report
- Top 10 Expenses
- Budget Report
- Overall Statistics Report

## Charts Generated

Saved inside `reports/charts/`:
- Category Bar Chart
- Category Pie Chart
- Monthly Trend Line
- Payment Method Distribution

## Screenshots

- Main Menu: *(placeholder)*
- Expense Table View: *(placeholder)*
- Reports Output: *(placeholder)*
- Generated Charts: *(placeholder)*

## Example Output

```text
Expense added with ID: EXP-000001
Budget warning: current month spending exceeded budget by INR 1,250.00.
Report generated: reports/monthly_report_20260703_101530.txt
Chart generated: reports/charts/bar_category_20260703_101605.png
```

## Technologies Used

- Python 3
- CSV and JSON for storage/export
- Matplotlib for chart generation
- Colorama (optional, auto-detected)

## Error Handling

The app gracefully handles:
- Invalid date and amount formats
- Negative/zero amounts
- Duplicate IDs
- Invalid menu choices
- Missing files and folders
- Corrupted CSV and JSON inputs
- KeyboardInterrupt and unexpected exceptions

## Future Improvements

- GUI version (Tkinter or PySide)
- Multi-user profiles
- Recurring expenses and reminders
- Password-protected ledger
- Automated tests with pytest

## License

This project is licensed under the MIT License. See `LICENSE` for details.
