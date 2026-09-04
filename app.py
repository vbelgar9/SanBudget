from __future__ import annotations

import csv
import sqlite3
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "expenses.db"
CATEGORIES = ("Food", "Transport", "Housing", "Utilities", "Health", "Education", "Entertainment", "Shopping", "Salary", "Other")


class ExpenseDatabase:
    def __init__(self, path: Path = DB_PATH) -> None:
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                transaction_type TEXT NOT NULL CHECK(transaction_type IN ('Expense', 'Income')),
                amount REAL NOT NULL CHECK(amount > 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.connection.commit()

    def add(self, values: tuple[str, str, str, str, float]) -> None:
        self.connection.execute(
            "INSERT INTO transactions (transaction_date, description, category, transaction_type, amount) VALUES (?, ?, ?, ?, ?)",
            values,
        )
        self.connection.commit()

    def update(self, transaction_id: int, values: tuple[str, str, str, str, float]) -> None:
        self.connection.execute(
            "UPDATE transactions SET transaction_date=?, description=?, category=?, transaction_type=?, amount=? WHERE id=?",
            (*values, transaction_id),
        )
        self.connection.commit()

    def delete(self, transaction_id: int) -> None:
        self.connection.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        self.connection.commit()

    def list(self, month: str = "All", search: str = "") -> list[sqlite3.Row]:
        clauses, params = [], []
        if month != "All":
            clauses.append("substr(transaction_date, 1, 7) = ?")
            params.append(month)
        if search:
            clauses.append("(description LIKE ? OR category LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        return self.connection.execute(
            f"SELECT * FROM transactions {where} ORDER BY transaction_date DESC, id DESC", params
        ).fetchall()

    def months(self) -> list[str]:
        rows = self.connection.execute(
            "SELECT DISTINCT substr(transaction_date, 1, 7) AS month FROM transactions ORDER BY month DESC"
        ).fetchall()
        return [row["month"] for row in rows]

    def close(self) -> None:
        self.connection.close()


class ExpenseTracker(tk.Tk):
    COLORS = {"navy": "#14213d", "orange": "#fca311", "paper": "#f7f8fa", "white": "#ffffff", "muted": "#667085", "green": "#12805c", "red": "#c83e4d", "line": "#e3e7ed"}

    def __init__(self) -> None:
        super().__init__()
        self.db = ExpenseDatabase()
        self.selected_id: int | None = None
        self.title("SanBudget — Personal Expense Tracker")
        self.geometry("1120x720")
        self.minsize(920, 620)
        self.configure(bg=self.COLORS["paper"])
        self._configure_styles()
        self._build_ui()
        self.refresh()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=self.COLORS["white"], fieldbackground=self.COLORS["white"], rowheight=31, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=self.COLORS["navy"], foreground="white", relief="flat", padding=8, font=("Segoe UI Semibold", 10))
        style.map("Treeview", background=[("selected", "#dce7f8")], foreground=[("selected", self.COLORS["navy"])])
        style.configure("TCombobox", padding=6)

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg=self.COLORS["navy"], height=78)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="SanBudget", bg=self.COLORS["navy"], fg="white", font=("Segoe UI Semibold", 23)).pack(side="left", padx=(28, 8))
        tk.Label(header, text="Spend with clarity.", bg=self.COLORS["navy"], fg="#b8c2d8", font=("Segoe UI", 11)).pack(side="left", pady=(9, 0))
        tk.Button(header, text="Export CSV", command=self.export_csv, bg=self.COLORS["orange"], fg=self.COLORS["navy"], activebackground="#ffb43b", relief="flat", padx=16, pady=8, font=("Segoe UI Semibold", 10), cursor="hand2").pack(side="right", padx=28)

        body = tk.Frame(self, bg=self.COLORS["paper"])
        body.pack(fill="both", expand=True, padx=24, pady=20)
        self._build_summary(body)

        content = tk.Frame(body, bg=self.COLORS["paper"])
        content.pack(fill="both", expand=True, pady=(16, 0))
        self._build_form(content)
        self._build_transactions(content)

    def _build_summary(self, parent: tk.Widget) -> None:
        row = tk.Frame(parent, bg=self.COLORS["paper"])
        row.pack(fill="x")
        self.summary_labels: dict[str, tk.Label] = {}
        for key, title, color in (("income", "TOTAL INCOME", self.COLORS["green"]), ("expense", "TOTAL EXPENSES", self.COLORS["red"]), ("balance", "BALANCE", self.COLORS["navy"])):
            card = tk.Frame(row, bg="white", highlightbackground=self.COLORS["line"], highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12) if key != "balance" else 0)
            tk.Label(card, text=title, bg="white", fg=self.COLORS["muted"], font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=18, pady=(13, 2))
            label = tk.Label(card, text="₱0.00", bg="white", fg=color, font=("Segoe UI Semibold", 21))
            label.pack(anchor="w", padx=18, pady=(0, 13))
            self.summary_labels[key] = label

    def _build_form(self, parent: tk.Widget) -> None:
        panel = tk.Frame(parent, bg="white", width=290, highlightbackground=self.COLORS["line"], highlightthickness=1)
        panel.pack(side="left", fill="y", padx=(0, 16))
        panel.pack_propagate(False)
        tk.Label(panel, text="Add transaction", bg="white", fg=self.COLORS["navy"], font=("Segoe UI Semibold", 16)).pack(anchor="w", padx=20, pady=(18, 12))
        form = tk.Frame(panel, bg="white")
        form.pack(fill="x", padx=20)

        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.description_var = tk.StringVar()
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.type_var = tk.StringVar(value="Expense")
        self.amount_var = tk.StringVar()
        self._entry(form, "Date (YYYY-MM-DD)", self.date_var)
        self._entry(form, "Description", self.description_var)
        self._combo(form, "Category", self.category_var, CATEGORIES)
        self._combo(form, "Type", self.type_var, ("Expense", "Income"))
        self._entry(form, "Amount", self.amount_var)

        self.save_button = tk.Button(form, text="Add transaction", command=self.save_transaction, bg=self.COLORS["navy"], fg="white", activebackground="#263b68", activeforeground="white", relief="flat", pady=10, font=("Segoe UI Semibold", 10), cursor="hand2")
        self.save_button.pack(fill="x", pady=(12, 7))
        tk.Button(form, text="Clear form", command=self.clear_form, bg="white", fg=self.COLORS["muted"], activebackground="white", relief="flat", pady=5, cursor="hand2").pack(fill="x")

    def _entry(self, parent: tk.Widget, label: str, variable: tk.StringVar) -> None:
        tk.Label(parent, text=label, bg="white", fg=self.COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(7, 3))
        tk.Entry(parent, textvariable=variable, relief="solid", bd=1, font=("Segoe UI", 10), highlightcolor=self.COLORS["orange"], highlightthickness=1).pack(fill="x", ipady=6)

    def _combo(self, parent: tk.Widget, label: str, variable: tk.StringVar, values: tuple[str, ...]) -> None:
        tk.Label(parent, text=label, bg="white", fg=self.COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(7, 3))
        ttk.Combobox(parent, textvariable=variable, values=values, state="readonly").pack(fill="x")

    def _build_transactions(self, parent: tk.Widget) -> None:
        panel = tk.Frame(parent, bg="white", highlightbackground=self.COLORS["line"], highlightthickness=1)
        panel.pack(side="left", fill="both", expand=True)
        toolbar = tk.Frame(panel, bg="white")
        toolbar.pack(fill="x", padx=16, pady=13)
        tk.Label(toolbar, text="Transactions", bg="white", fg=self.COLORS["navy"], font=("Segoe UI Semibold", 16)).pack(side="left")
        self.search_var = tk.StringVar()
        search = tk.Entry(toolbar, textvariable=self.search_var, width=22, relief="solid", bd=1, font=("Segoe UI", 9))
        search.pack(side="right", ipady=5)
        search.insert(0, "")
        search.bind("<KeyRelease>", lambda _event: self.refresh())
        tk.Label(toolbar, text="Search", bg="white", fg=self.COLORS["muted"]).pack(side="right", padx=(0, 7))
        self.month_var = tk.StringVar(value="All")
        self.month_combo = ttk.Combobox(toolbar, textvariable=self.month_var, state="readonly", width=10)
        self.month_combo.pack(side="right", padx=12)
        self.month_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        tk.Label(toolbar, text="Month", bg="white", fg=self.COLORS["muted"]).pack(side="right")

        columns = ("date", "description", "category", "type", "amount")
        self.tree = ttk.Treeview(panel, columns=columns, show="headings", selectmode="browse")
        widths = {"date": 92, "description": 190, "category": 100, "type": 80, "amount": 95}
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=widths[col], anchor="e" if col == "amount" else "w")
        self.tree.pack(fill="both", expand=True, padx=16)
        self.tree.tag_configure("expense", foreground=self.COLORS["red"])
        self.tree.tag_configure("income", foreground=self.COLORS["green"])
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

        actions = tk.Frame(panel, bg="white")
        actions.pack(fill="x", padx=16, pady=12)
        self.status_label = tk.Label(actions, text="0 transactions", bg="white", fg=self.COLORS["muted"], font=("Segoe UI", 9))
        self.status_label.pack(side="left")
        tk.Button(actions, text="Delete", command=self.delete_selected, bg="white", fg=self.COLORS["red"], relief="flat", cursor="hand2").pack(side="right")
        tk.Button(actions, text="Edit", command=self.load_selected, bg="white", fg=self.COLORS["navy"], relief="flat", cursor="hand2").pack(side="right", padx=8)

    def _validated_values(self) -> tuple[str, str, str, str, float] | None:
        try:
            parsed_date = datetime.strptime(self.date_var.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid date", "Use the date format YYYY-MM-DD.")
            return None
        description = self.description_var.get().strip()
        if not description:
            messagebox.showerror("Missing description", "Enter a short description.")
            return None
        try:
            amount = round(float(self.amount_var.get()), 2)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter an amount greater than zero.")
            return None
        return parsed_date.isoformat(), description, self.category_var.get(), self.type_var.get(), amount

    def save_transaction(self) -> None:
        values = self._validated_values()
        if values is None:
            return
        if self.selected_id is None:
            self.db.add(values)
        else:
            self.db.update(self.selected_id, values)
        self.clear_form()
        self.refresh()

    def load_selected(self, _event: tk.Event | None = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        self.selected_id = int(item_id)
        self.date_var.set(values[0])
        self.description_var.set(values[1])
        self.category_var.set(values[2])
        self.type_var.set(values[3])
        self.amount_var.set(str(values[4]).replace("₱", "").replace(",", ""))
        self.save_button.configure(text="Save changes", bg=self.COLORS["orange"], fg=self.COLORS["navy"])

    def delete_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Select a transaction", "Choose a transaction to delete.")
            return
        if messagebox.askyesno("Delete transaction", "Delete the selected transaction? This cannot be undone."):
            self.db.delete(int(selection[0]))
            self.clear_form()
            self.refresh()

    def clear_form(self) -> None:
        self.selected_id = None
        self.date_var.set(date.today().isoformat())
        self.description_var.set("")
        self.category_var.set(CATEGORIES[0])
        self.type_var.set("Expense")
        self.amount_var.set("")
        self.save_button.configure(text="Add transaction", bg=self.COLORS["navy"], fg="white")
        for selected in self.tree.selection():
            self.tree.selection_remove(selected)

    def refresh(self) -> None:
        current_month = self.month_var.get()
        months = ["All", *self.db.months()]
        self.month_combo.configure(values=months)
        if current_month not in months:
            current_month = "All"
            self.month_var.set("All")
        rows = self.db.list(current_month, self.search_var.get().strip())
        for item in self.tree.get_children():
            self.tree.delete(item)
        income = expense = 0.0
        for row in rows:
            amount = float(row["amount"])
            if row["transaction_type"] == "Income":
                income += amount
            else:
                expense += amount
            self.tree.insert("", "end", iid=str(row["id"]), values=(row["transaction_date"], row["description"], row["category"], row["transaction_type"], f"₱{amount:,.2f}"), tags=(row["transaction_type"].lower(),))
        self.summary_labels["income"].configure(text=f"₱{income:,.2f}")
        self.summary_labels["expense"].configure(text=f"₱{expense:,.2f}")
        balance = income - expense
        self.summary_labels["balance"].configure(text=f"₱{balance:,.2f}", fg=self.COLORS["green"] if balance >= 0 else self.COLORS["red"])
        self.status_label.configure(text=f"{len(rows)} transaction{'s' if len(rows) != 1 else ''}")

    def export_csv(self) -> None:
        rows = self.db.list(self.month_var.get(), self.search_var.get().strip())
        if not rows:
            messagebox.showinfo("Nothing to export", "There are no transactions in the current view.")
            return
        path = filedialog.asksaveasfilename(title="Export transactions", defaultextension=".csv", filetypes=(("CSV files", "*.csv"),), initialfile="transactions.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(("Date", "Description", "Category", "Type", "Amount"))
            writer.writerows((r["transaction_date"], r["description"], r["category"], r["transaction_type"], f"{r['amount']:.2f}") for r in rows)
        messagebox.showinfo("Export complete", f"Saved {len(rows)} transactions.")

    def _on_close(self) -> None:
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    ExpenseTracker().mainloop()
