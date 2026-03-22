import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry

# ==========================================
# 1. DATABASE INITIALIZATION
# ==========================================
def init_db():
    with sqlite3.connect("cashatan.db") as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            # 1. Users Table
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )''')

            # 2. Transactions Table (Handles both Income & Expenses)
            cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,     -- 'Income' or 'Expense'
                amount REAL NOT NULL,
                category TEXT,
                date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )''')

            # 3. Budgets Table
            cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                monthly_income REAL DEFAULT 0.0,
                savings_goal REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )''')
            connection.commit()
            connection.close()


# for registering new users during sign up
def register_user(full_name, email, username, password):
    """Inserts a new user. Returns True if successful, False if duplicate."""
    try:
        connection = sqlite3.connect("cashatan.db")
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO users (full_name, email, username, password)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, username, password))
        connection.commit()
        connection.close()
        return True
    except sqlite3.IntegrityError:
        return False


# for authenticating users during login
def authenticate_user(username, password):
    """Checks credentials. Returns the user tuple if found, else None."""
    connection = sqlite3.connect("cashatan.db")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    connection.close()
    return user


#for adding transactions (expenses/income) to the database
def init_db():
    connection = sqlite3.connect("cashatan.db")
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table A: Users
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT UNIQUE,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    # Table B: Transactions (This replaces 'expenses')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,     -- 'Income' or 'Expense'
                amount REAL NOT NULL,
                category TEXT,          -- Category for expenses, Source for income
                date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
    
    connection.commit()
    connection.close()

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

# --- 1. LANDING PAGE (LOGIN/SIGN UP) [cite: 50] ---
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="LOGIN / SIGN UP", font=("Arial", 18, "bold")).pack(pady=20)
        
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)
        
        # Variable to track if password should be shown
        self.var_show_pass = tk.BooleanVar(value=False)

        #Username
        tk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="e", pady=5)
        self.username_entry = tk.Entry(form_frame) # <--- Variable name is now 'self.username_entry'
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        #Password
        tk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="e", pady=5)
        self.password_entry = tk.Entry(form_frame, show="*") # <--- Variable name is now 'self.password_entry'
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        #Show Password Checkbox
        tk.Checkbutton(form_frame, text="Show Password", variable=self.var_show_pass, 
                       command=self.toggle_password).grid(row=2, column=1, sticky="w")
        
        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(0, 20))
        tk.Button(btn_frame, text="Login", width=15, 
                  command=lambda: self.login_action()).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Sign Up", width=15, 
                  command=lambda: controller.show_frame("SignUpPage")).pack(side="left", padx=6)

    #for toggling password visibility
    def toggle_password(self):
        """Toggles the 'show' property of the password entry"""
        if self.var_show_pass.get():
            self.password_entry.config(show="") # Show text
        else:
            self.password_entry.config(show="*") # Mask text

    #database interaction for login
    def login_action(self):
        user = authenticate_user(self.username_entry.get(), self.password_entry.get())
        if user:
            # user[0] is the user_id from your database
            self.controller.current_user_id = user[0] 
            
            messagebox.showinfo("Login Success", f"Welcome back, {user[3]}!") # user[3] is username
            self.controller.show_frame("DashboardPage")
        else:
            messagebox.showerror("Error", "Invalid username or password.")
    

# --- 2. SIGN UP PAGE [cite: 61] ---
class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="SIGN UP", font=("Arial", 18, "bold")).pack(pady=20) # [cite: 54]
        

        # Fields: Full Name, Email, Username, Password [cite: 55-58]
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        self.entries = {}
        fields = [("Full Name:", "full_name"), ("Email:", "email"), 
                  ("Username:", "username"), ("Password:", "password")]
        
        # 2. Loop through and use .grid() instead of .pack()
        # Inside SignUpPage __init__
        self.var_show_pass = tk.BooleanVar(value=False) # Tracks the checkbox state

        for i, (label_text, key_name) in enumerate(fields):
            tk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="e", pady=5)
            
            show_char = "*" if "Password" in label_text else None
            entry_widget = tk.Entry(form_frame, width=25, show=show_char)
            entry_widget.grid(row=i, column=1, pady=5, padx=5)
            self.entries[key_name] = entry_widget 

        # 3. SAVE the widget so signup_action can find it
            self.entries[key_name] = entry_widget

        # Add the "Show Password" checkbox right after the loop
        tk.Checkbutton(form_frame, text="Show Password", variable=self.var_show_pass, 
                       command=self.toggle_password).grid(row=len(fields), column=1, sticky="w")
            
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(0, 20))
        tk.Button(btn_frame, text="Register", width=15, 
                  command=lambda: self.signup_action()).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Back to Login", width=15, 
                  command=lambda: controller.show_frame("LoginPage")).pack(side="left", padx=6)

    #showing password
    def toggle_password(self):
        # Grab the password entry widget from our dictionary
        pw_entry = self.entries['password']
        
        if self.var_show_pass.get():
            pw_entry.config(show="") # Empty string means "show text"
        else:
            pw_entry.config(show="*") # Hide text

    #database interaction for sign up
    def signup_action(self):
        name = self.entries['full_name'].get()
        email = self.entries['email'].get()
        user = self.entries['username'].get()
        pw = self.entries['password'].get()

        if not all([name, email, user, pw]):
            messagebox.showwarning("Incomplete", "Please fill in all fields.")
            return

        if register_user(name, email, user, pw):
            messagebox.showinfo("Success", "Registration complete! You can now log in.")
            self.controller.show_frame("LoginPage")
        else:
            messagebox.showerror("Error", "Username or Email already exists.")

# --- 3. DASHBOARD (CENTRAL HUB) [cite: 77, 78] ---
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


# --- 4. FORM TEMPLATE (ADD EXPENSE/INCOME) [cite: 89, 101] ---
class AddExpensePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 1. Title
        tk.Label(self, text="ADD EXPENSE", font=("Arial", 18, "bold")).pack(pady=20)

        # 2. Form Container
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        # 3. Input Fields
        fields = ["Date:", "Category:", "Amount:", "Notes:"]
        self.entries = {} 

        # Define your expense categories here
        categories = ["Food", "Transportation", "Bills", "Groceries", "Entertainment", "Health", "Others"]

        for i, field in enumerate(fields):
            lbl = tk.Label(form_frame, text=field, font=("Arial", 10))
            lbl.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            if field == "Date:":
                entry = DateEntry(form_frame, width=25, background='darkblue', 
                                  foreground='white', borderwidth=2, 
                                  date_pattern='y-mm-dd')
            
            elif field == "Category:":
                # This is your "Dropdown but Radiobutton" replacement
                entry = ttk.Combobox(form_frame, values=categories, width=25, state="readonly")
                entry.set("Select Category") # Default text
            
            else:
                entry = tk.Entry(form_frame, font=("Arial", 10), width=24)
            
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.entries[field] = entry


        # 4. Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=(0, 20))

        tk.Button(button_frame, text="SAVE EXPENSE", 
                  width=18, command=self.save_to_db).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="BACK TO DASHBOARD", 
                  width=18, command=lambda: controller.show_frame("DashboardPage")).pack(side="left", padx=5)

    #database for saving expense data will go here
    def save_to_db(self):
        # 1. Get data from UI (Matching the labels in your loop)
        date = self.entries["Date:"].get()
        category = self.entries["Category:"].get()
        amount = self.entries["Amount:"].get()
        notes = self.entries["Notes:"].get()
    
        # 2. Safety Check for Logged In User
        u_id = getattr(self.controller, 'current_user_id', None) 
        
        if u_id is None:
            messagebox.showerror("Error", "No user logged in! Please restart and log in.")
            return

        if not date or not category or not amount:
            messagebox.showwarning("Input Error", "Please fill in the required fields.")
            return

        try:
            # We use a context manager (with) to ensure the connection closes
            with sqlite3.connect("cashatan.db", timeout=10) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;") 
                
                # 1. Point to 'transactions' instead of 'expenses'
                # 2. Include the 'type' column
                query = """INSERT INTO transactions (user_id, type, amount, category, date, notes) 
                        VALUES (?, ?, ?, ?, ?, ?)"""
                
                # 3. Pass 'Expense' as the type
                cursor.execute(query, (u_id, 'Expense', float(amount), category, date, notes))
                connection.commit()

            messagebox.showinfo("Success", "Expense saved successfully!")
            self.clear_entries()
            
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number (e.g. 100.50).")
        except sqlite3.IntegrityError:
            messagebox.showerror("Database Error", "User session invalid. Please log in again.")

    #for clring the entry fields after saving an expense
    def clear_entries(self):
        """Clears the boxes so you can add another expense immediately"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)


class AddIncomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 1. Title
        tk.Label(self, text="ADD INCOME", font=("Arial", 18, "bold")).pack(pady=20)

        # 2. Form Container (Grid Layout)
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        # 3. Input Fields
        # Note: "Income Source" maps to the 'category' column in your DB
        fields = ["Date:", "Source:", "Amount:", "Notes:"]
        self.entries = {} 

        # Specific categories for Income
        income_sources = ["Salary", "Freelance", "Allowance", "Gift", "Investment", "Others"]

        for i, field in enumerate(fields):
            lbl = tk.Label(form_frame, text=field, font=("Arial", 10))
            lbl.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            if field == "Date:":
                entry = DateEntry(form_frame, width=23, background='darkblue', 
                                  foreground='white', borderwidth=2, 
                                  date_pattern='y-mm-dd')
            
            elif field == "Source:":
                entry = ttk.Combobox(form_frame, values=income_sources, width=23, state="readonly")
                entry.set("Select Source")
            
            else:
                entry = tk.Entry(form_frame, font=("Arial", 10), width=25)
            
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.entries[field] = entry

        # 4. Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=(20, 20))

        tk.Button(button_frame, text="SAVE INCOME", 
                  width=18, command=self.save_income_to_db).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="BACK TO DASHBOARD", 
                  width=18, command=lambda: controller.show_frame("DashboardPage")).pack(side="left", padx=5)

    #database interaction for saving income data to the database
    def save_income_to_db(self):
        """Saves income data specifically to the transactions table."""
        date = self.entries["Date:"].get()
        source = self.entries["Source:"].get()
        amount = self.entries["Amount:"].get()
        notes = self.entries["Notes:"].get()
    
        u_id = getattr(self.controller, 'current_user_id', None) 
        
        if u_id is None:
            messagebox.showerror("Error", "No user logged in!")
            return

        if not date or source == "Select Source" or not amount:
            messagebox.showwarning("Input Error", "Please fill in Date, Source, and Amount.")
            return

        try:
            # Using 'with' to prevent the "database is locked" error
            with sqlite3.connect("cashatan.db", timeout=10) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;") 
                
                # We hardcode 'Income' into the type column
                query = """INSERT INTO transactions (user_id, type, amount, category, date, notes) 
                        VALUES (?, ?, ?, ?, ?, ?)"""
                cursor.execute(query, (u_id, 'Income', float(amount), source, date, notes))
                connection.commit()

            messagebox.showinfo("Success", "Income added successfully!")
            self.clear_entries()
            
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
        except sqlite3.OperationalError:
            messagebox.showerror("Database Error", "Database is busy. Try again in a moment.")

    #for cleraing the entry fields after saving an income
    def clear_entries(self):
        """Resets the form"""
        for field, widget in self.entries.items():
            if field == "Source:":
                widget.set("Select Source")
            elif field != "Date:": # Keep the date as is for convenience
                widget.delete(0, tk.END)




# --- 5. DATA TABLE TEMPLATE (VIEW TRANSACTIONS) [cite: 114] ---
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


# --- 6. SUMMARY TEMPLATE (BUDGET OVERVIEW) [cite: 143] ---
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
