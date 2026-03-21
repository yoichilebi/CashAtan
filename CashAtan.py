import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ==========================================
# 1. DATABASE INITIALIZATION
# ==========================================
def init_db():
    connection = sqlite3.connect("cashatan.db")
    cursor = connection.cursor()

    # Users Table: Secure entry point data [cite: 55-58]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Transactions Table: Organized records of income and expenses [cite: 82-85, 94-97]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL, -- 'Income' or 'Expense'
            amount REAL NOT NULL,
            category TEXT,
            date TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # Budget Goals Table: Supports budget overview and savings goals [cite: 124, 129]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            monthly_income REAL DEFAULT 0.0,
            savings_goal REAL DEFAULT 0.0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()

# ==========================================
# 2. MAIN APPLICATION CONTROLLER
# ==========================================
class CashAtanApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("CashAtan - Personal Expense Tracker")
        self.geometry("900x650")
        
        # This stores the ID of the user currently logged in
        self.current_user_id = None 

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Registering all pages from the proposal 
        for F in (LoginPage, SignUpPage, DashboardPage, AddExpensePage, 
                  AddIncomePage, ViewTransactionsPage, BudgetOverviewPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        """Switches to the specified page [cite: 79]"""
        frame = self.frames[page_name]
        frame.tkraise()

# ==========================================
# 3. PAGE CLASS TEMPLATES
# ==========================================

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="LOGIN / SIGN UP", font=("Arial", 18, "bold")).pack(pady=20) # [cite: 44]
        
        tk.Label(self, text="Username:").pack() # [cite: 45]
        self.user_entry = tk.Entry(self)
        self.user_entry.pack(pady=5)
        
        tk.Label(self, text="Password:").pack() # [cite: 46]
        self.pass_entry = tk.Entry(self, show="*")
        self.pass_entry.pack(pady=5)
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Login", width=10, 
                  command=lambda: controller.show_frame("DashboardPage")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Sign Up", width=10, 
                  command=lambda: controller.show_frame("SignUpPage")).pack(side="left", padx=10)

class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="SIGN UP", font=("Arial", 18, "bold")).pack(pady=20) # [cite: 54]
        
        # Fields: Full Name, Email, Username, Password [cite: 55-58]
        fields = ["Full Name:", "Email:", "Username:", "Password:"]
        for field in fields:
            tk.Label(self, text=field).pack()
            tk.Entry(self).pack(pady=2)
            
        tk.Button(self, text="Register", command=lambda: controller.show_frame("LoginPage")).pack(pady=10) # [cite: 59]
        tk.Button(self, text="Back to Login", command=lambda: controller.show_frame("LoginPage")).pack() # [cite: 60]

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="DASHBOARD", font=("Arial", 18, "bold")).pack(pady=10) # [cite: 65]
        
        nav_frame = tk.Frame(self)
        nav_frame.pack(side="left", padx=20, fill="y")
        
        # Navigation Hub buttons [cite: 66, 67, 68, 71, 72]
        tk.Button(nav_frame, text="ADD EXPENSE", width=20, command=lambda: controller.show_frame("AddExpensePage")).pack(pady=5)
        tk.Button(nav_frame, text="ADD INCOME", width=20, command=lambda: controller.show_frame("AddIncomePage")).pack(pady=5)
        tk.Button(nav_frame, text="VIEW TRANSACTIONS", width=20, command=lambda: controller.show_frame("ViewTransactionsPage")).pack(pady=5)
        tk.Button(nav_frame, text="BUDGET OVERVIEW", width=20, command=lambda: controller.show_frame("BudgetOverviewPage")).pack(pady=5)
        tk.Button(nav_frame, text="LOGOUT", width=20, command=lambda: controller.show_frame("LoginPage")).pack(pady=20)

class AddExpensePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="ADD EXPENSE", font=("Arial", 18, "bold")).pack(pady=20) # [cite: 81]
        
        # Input fields for spending details [cite: 82-85]
        for field in ["Date:", "Category:", "Amount:", "Notes:"]:
            tk.Label(self, text=field).pack()
            tk.Entry(self).pack(pady=2)
            
        tk.Button(self, text="SAVE EXPENSE", command=None).pack(pady=10) # [cite: 86]
        tk.Button(self, text="BACK TO DASHBOARD", command=lambda: controller.show_frame("DashboardPage")).pack() # [cite: 87]

class AddIncomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="ADD INCOME", font=("Arial", 18, "bold")).pack(pady=20) # [cite: 93]
        
        # Input fields for earnings [cite: 94-97]
        for field in ["Date:", "Income Source:", "Amount:", "Notes:"]:
            tk.Label(self, text=field).pack()
            tk.Entry(self).pack(pady=2)

        tk.Button(self, text="SAVE BUDGET", command=None).pack(pady=10) # [cite: 98]
        tk.Button(self, text="BACK TO DASHBOARD", command=lambda: controller.show_frame("DashboardPage")).pack() # [cite: 99]

class ViewTransactionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="VIEW TRANSACTIONS", font=("Arial", 18, "bold")).pack(pady=10) # [cite: 105]
        
        # Table for financial history [cite: 115]
        cols = ("Date", "Category", "Amount", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10)
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Delete Expense", command=None).pack(side="left", padx=5) # [cite: 110]
        tk.Button(btn_frame, text="Edit Expense", command=None).pack(side="left", padx=5) # [cite: 111]
        tk.Button(btn_frame, text="Back to Dashboard", command=lambda: controller.show_frame("DashboardPage")).pack(side="left", padx=5) # [cite: 112]

class BudgetOverviewPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="BUDGET OVERVIEW", font=("Arial", 18, "bold")).pack(pady=10) # [cite: 118]
        
        # Labels for summary metrics [cite: 124, 126, 129, 131]
        metrics = ["Monthly Income:", "Savings Goal:", "Total Expenses:", "Remaining Budget:"]
        for m in metrics:
            tk.Label(self, text=m, font=("Arial", 12)).pack(anchor="w", padx=50)
            
        tk.Button(self, text="Back to Dashboard", command=lambda: controller.show_frame("DashboardPage")).pack(pady=20) # [cite: 142]

# ==========================================
# 4. START THE APP
# ==========================================
if __name__ == "__main__":
    init_db()
    app = CashAtanApp()
    app.mainloop()
