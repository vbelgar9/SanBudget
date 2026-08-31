# PocketLedger

PocketLedger is a desktop personal expense tracker built with Python, Tkinter, SQLite, and a lot of attention to the small details that make everyday software pleasant to use.

## Features

- Add, edit, and delete income or expense transactions
- Store data locally in SQLite
- Filter transactions by month
- Search descriptions and categories
- View live totals for income, expenses, and balance
- Export the current filtered view to CSV
- Validate dates, descriptions, and amounts
- Responsive desktop layout with no third-party packages

## Run the application

1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/).
2. Open a terminal in this folder.
3. Run:

   ```powershell
   python app.py
   ```

The `expenses.db` database is created automatically beside the application. Delete that file if you want to start with an empty database.

## Portfolio description

> I built PocketLedger, a desktop personal-finance application that helps users record income and expenses, review monthly activity, search their transaction history, and export reports. I designed the interface in Tkinter and implemented persistent local storage with SQLite. The project strengthened my skills in database CRUD operations, input validation, event-driven interfaces, filtering, and file exports.

## Project structure

```text
personal-expense-tracker/
├── app.py          # Interface, validation, and database layer
├── README.md       # Setup and portfolio documentation
└── expenses.db     # Created automatically when first run
```

## License

This project is available for personal and educational use.
