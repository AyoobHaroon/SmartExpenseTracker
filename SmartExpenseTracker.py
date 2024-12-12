import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database Setup
def setup_database():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL
        )
    """)
    conn.commit()
    conn.close()

setup_database()

# Main Application Class
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Expense Tracker")

        # Frame Setup
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        # Widgets for Adding Expense
        tk.Label(self.frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5)
        self.date_entry = tk.Entry(self.frame)
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.frame, text="Category:").grid(row=1, column=0, padx=10, pady=5)
        self.category_entry = tk.Entry(self.frame)
        self.category_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.frame, text="Amount:").grid(row=2, column=0, padx=10, pady=5)
        self.amount_entry = tk.Entry(self.frame)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5)

        self.add_button = tk.Button(self.frame, text="Add Expense", command=self.add_expense)
        self.add_button.grid(row=3, columnspan=2, pady=10)

        # Expense List Display
        self.tree = ttk.Treeview(self.root, columns=("Date", "Category", "Amount"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.pack(pady=20)

        self.refresh_button = tk.Button(self.root, text="Refresh List", command=self.refresh_expenses)
        self.refresh_button.pack(pady=10)

        # Analytics and Visualization
        self.analysis_button = tk.Button(self.root, text="Analyze Expenses", command=self.analyze_expenses)
        self.analysis_button.pack(pady=10)

        self.refresh_expenses()

    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_entry.get()
        amount = self.amount_entry.get()

        if not date or not category or not amount:
            messagebox.showerror("Input Error", "All fields are required!")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number!")
            return

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)", (date, category, amount))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Expense added successfully!")
        self.refresh_expenses()

    def refresh_expenses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, category, amount FROM expenses")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def analyze_expenses(self):
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("No Data", "No expenses to analyze.")
            return

        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        fig, ax = plt.subplots()
        ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        plt.title("Expense Breakdown by Category")

        # Show the chart in Tkinter
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Expense Analysis")

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
