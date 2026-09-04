# SanBudget

> Spend with clarity.

SanBudget is a desktop personal expense tracker built with Python, Tkinter,
and SQLite. It provides a focused interface for recording income and expenses,
reviewing monthly activity, searching transaction history, and exporting
reports—without requiring an internet connection or third-party packages.

![SanBudget dashboard](https://vbelgar9.github.io/sanbadguetdashboard.png)

## Features

- Add income and expense transactions
- Edit or delete existing transactions
- View live totals for income, expenses, and current balance
- Filter transactions by month
- Search transaction descriptions and categories
- Export the currently displayed transactions to CSV
- Validate dates, descriptions, and monetary amounts
- Store all data locally in SQLite
- Run entirely with Python's standard library

## Technologies

- **Python 3** — application logic
- **Tkinter** — desktop graphical interface
- **SQLite** — local transaction database
- **`sqlite3`** — communication between Python and SQLite
- **`csv`** — transaction-report export
- **Git and GitHub** — version control and source-code hosting

## Download

Download the latest source code as a ZIP file:

[Download SanBudget](https://github.com/vbelgar9/SanBudget/archive/refs/heads/main.zip)

After downloading, extract the ZIP file and follow the instructions below.

## Getting Started

### Requirements

- Python 3.10 or newer
- Git, if you want to clone the repository

No third-party Python packages are required.

### Clone the repository

```bash
git clone https://github.com/vbelgar9/SanBudget.git
cd SanBudget
```

### Run the application

```bash
python app.py
```

On some systems, use `python3 app.py` instead.

## How to Use

1. Enter the transaction date in `YYYY-MM-DD` format.
2. Add a description and select a category.
3. Choose whether the transaction is income or an expense.
4. Enter the amount and select **Add transaction**.
5. Use the month filter or search box to find transactions.
6. Select **Export CSV** to save the currently filtered transaction list.

## Data Storage

SanBudget creates an `expenses.db` SQLite database beside the application
when it first runs. Your financial data remains on your computer and is not
sent to an online service.

To start with an empty database, close SanBudget and delete `expenses.db`.
This permanently removes the locally stored transactions, so make a backup
first if you may need them later.

## Project Structure

```text
SanBudget/
├── app.py        # Interface, validation, and database logic
├── README.md     # Project documentation
├── .gitignore    # Files excluded from version control
└── expenses.db   # Generated automatically when the app first runs
```

## Project Purpose

I built SanBudget to practice creating a complete desktop application with
a clear interface and dependable local data storage. The project strengthened
my experience with CRUD operations, input validation, event-driven interfaces,
database filtering, search, and file exports.

## Author

**Vee Belgar**

- [GitHub profile](https://github.com/vbelgar9)
- [Developer portfolio](https://vbelgar9.github.io/)

## License

This project is available for personal and educational use.
