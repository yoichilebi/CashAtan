import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3
from tkcalendar import DateEntry
from datetime import date

# ==========================================
# 1. DATABASE INITIALIZATION
# ==========================================
def init_db():
    with sqlite3.connect("cashatan.db") as connection:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 1. Users Table
        # Fixed: Added missing comma after password
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            profile_pic TEXT
        )''')

        # 2. Transactions Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
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
        """Switches to the specified page and refreshes data if needed."""
        frame = self.frames[page_name]
        
        # This is the "Engine" that loads your data!
        if hasattr(frame, "load_data"):
            frame.load_data()
            
        frame.tkraise()

# ==========================================
# 3. PAGE CLASS TEMPLATES
# ==========================================

# --- 1. LANDING PAGE (LOGIN/SIGN UP) [cite: 50] ---
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white") # Match Budget Overview background

        # --- HEADER SECTION ---
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(header_frame, text="LOGIN / SIGN UP", font=("Arial", 24, "bold"), bg="white").pack()
        # The iconic black divider line
        tk.Frame(self, height=2, bg="black").pack(fill="x", padx=20, pady=(0, 40))

        # --- FORM SECTION ---
        form_container = tk.Frame(self, bg="white")
        form_container.pack(expand=True)

        self.var_show_pass = tk.BooleanVar(value=False)

        # Labels and Entries with consistent styling
        label_font = ("Arial", 14)
        tk.Label(form_container, text="Username:", font=label_font, bg="white").grid(row=0, column=0, sticky="e", pady=10, padx=10)
        self.username_entry = tk.Entry(form_container, font=("Arial", 12), width=30, relief="solid", borderwidth=1)
        self.username_entry.grid(row=0, column=1, pady=10)

        tk.Label(form_container, text="Password:", font=label_font, bg="white").grid(row=1, column=0, sticky="e", pady=10, padx=10)
        self.password_entry = tk.Entry(form_container, font=("Arial", 12), width=30, show="*", relief="solid", borderwidth=1)
        self.password_entry.grid(row=1, column=1, pady=10)

        tk.Checkbutton(form_container, text="Show Password", variable=self.var_show_pass, 
                       bg="white", font=("Arial", 10), command=self.toggle_password).grid(row=2, column=1, sticky="w")


        # --- BUTTON SECTION ---
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(side="bottom", pady=50)

        # THE "LOGOUT STYLE" BUTTON CONFIGURATION
        dark_btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#333",       # Dark Charcoal
            "fg": "white",      # White Text
            "relief": "flat",   # Clean flat look
            "activebackground": "#555", # Slight highlight when clicked
            "activeforeground": "white",
            "width": 18,
            "height": 2
        }

        tk.Button(btn_frame, text="LOGIN", command=self.login_action, **dark_btn_style).pack(side="left", padx=10)
        tk.Button(btn_frame, text="SIGN UP", command=lambda: controller.show_frame("SignUpPage"), **dark_btn_style).pack(side="left", padx=10)

    def toggle_password(self):
        self.password_entry.config(show="" if self.var_show_pass.get() else "*")

    def login_action(self):
        user = authenticate_user(self.username_entry.get(), self.password_entry.get())
        if user:
            self.controller.current_user_id = user[0] 
            messagebox.showinfo("Login Success", f"Welcome back, {user[3]}!")
            self.controller.show_frame("DashboardPage")
        else:
            messagebox.showerror("Error", "Invalid username or password.")
    

# --- 2. SIGN UP PAGE [cite: 61] ---
class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        # --- HEADER SECTION ---
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(header_frame, text="SIGN UP", font=("Arial", 24, "bold"), bg="white").pack()
        tk.Frame(self, height=2, bg="black").pack(fill="x", padx=20, pady=(0, 40))

        # --- FORM SECTION ---
        form_container = tk.Frame(self, bg="white")
        form_container.pack(expand=True)

        self.entries = {}
        fields = [("Full Name:", "full_name"), ("Email:", "email"), 
                  ("Username:", "username"), ("Password:", "password")]
        
        self.var_show_pass = tk.BooleanVar(value=False)

        for i, (label_text, key_name) in enumerate(fields):
            tk.Label(form_container, text=label_text, font=("Arial", 12), bg="white").grid(row=i, column=0, sticky="e", pady=8, padx=10)
            
            show_char = "*" if "Password" in label_text else None
            entry_widget = tk.Entry(form_container, font=("Arial", 12), width=30, show=show_char, relief="solid", borderwidth=1)
            entry_widget.grid(row=i, column=1, pady=8)
            self.entries[key_name] = entry_widget 

        tk.Checkbutton(form_container, text="Show Password", variable=self.var_show_pass, 
                       bg="white", font=("Arial", 10), command=self.toggle_password).grid(row=len(fields), column=1, sticky="w")


       # --- BUTTON SECTION ---
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(side="bottom", pady=50)

        # REUSING THE DARK STYLE
        dark_btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#333",
            "fg": "white",
            "relief": "flat",
            "width": 18,
            "height": 2
        }

        tk.Button(btn_frame, text="REGISTER", command=self.signup_action, **dark_btn_style).pack(side="left", padx=10)
        tk.Button(btn_frame, text="BACK", command=lambda: controller.show_frame("LoginPage"), **dark_btn_style).pack(side="left", padx=10)

    def toggle_password(self):
        pw_entry = self.entries['password']
        pw_entry.config(show="" if self.var_show_pass.get() else "*")

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
            self.controller = controller
            self.configure(bg="white") # Set background to white

            # --- HEADER SECTION (New Style) ---
            header_frame = tk.Frame(self, bg="white")
            header_frame.pack(fill="x", padx=20, pady=(20, 10))

            # Bold, centered Title matching Budget Overview
            tk.Label(header_frame, text="DASHBOARD", font=("Arial", 28, "bold"), bg="white").pack()
            
            # The Signature Black Divider Line
            tk.Frame(self, height=2, bg="black").pack(fill="x", padx=20, pady=(0, 20))

            # Main Layout Container
            main_container = tk.Frame(self, bg="white")
            main_container.pack(fill="both", expand=True, padx=20)

            # --- LEFT SIDE: NAVIGATION BUTTONS ---
            nav_frame = tk.Frame(main_container, bg="white")
            nav_frame.pack(side="left", fill="y", padx=(0, 30))

            btns = [
                ("ADD EXPENSE", "AddExpensePage"),
                ("ADD INCOME", "AddIncomePage"),
                ("VIEW TRANSACTIONS", "ViewTransactionsPage"),
                ("BUDGET OVERVIEW", "BudgetOverviewPage")
            ]

            for text, page in btns:
                tk.Button(nav_frame, text=text, width=25, height=2, font=("Arial", 11, "bold"),
                        command=lambda p=page: controller.show_frame(p)).pack(pady=10)

            tk.Button(nav_frame, text="LOGOUT", width=25, height=2, font=("Arial", 11, "bold"),
                    bg="#333", fg="white", command=lambda: controller.show_frame("LoginPage")).pack(pady=20)

            # --- RIGHT SIDE: MINI PROFILE ---
            profile_frame = tk.LabelFrame(main_container, text="Profile", bg="white", font=("Arial", 12, "bold" ), padx=20, pady=20)
            profile_frame.pack(side="right", fill="both", expand=True)

            # Top section: Image and Username/Date/Goal
            top_row = tk.Frame(profile_frame, bg="white")
            top_row.pack(fill="x")

            # Profile Image Slot
            # Inside your DashboardPage __init__
            self.img_label = tk.Label(top_row, bg="white", relief="solid", borderwidth=1)
            self.img_label.grid(row=0, column=0, rowspan=4, padx=(0, 20), sticky="nsew")

            # Create a "blank" square image to hold the space if no photo is uploaded yet
            placeholder = Image.new('RGB', (150, 150), color = '#ddd')
            self.ph_img = ImageTk.PhotoImage(placeholder)
            self.img_label.config(image=self.ph_img)


            # Identity Variables
            self.username_var = tk.StringVar(value="username")
            self.date_var = tk.StringVar(value=date.today().strftime("%m/%d/%Y"))
            self.goal_var = tk.StringVar(value="Budget Goal: ₱0.00")

            # row=0: Username (No box)
            tk.Label(top_row, textvariable=self.username_var, font=("Arial", 12, "bold"), 
                    anchor="w", bg="white").grid(row=0, column=1, pady=2, padx=10, sticky="w")
            
            # row=1: Date (No box)
            tk.Label(top_row, textvariable=self.date_var, font=("Arial", 10), 
                    fg="gray", anchor="w", bg="white").grid(row=1, column=1, pady=2, padx=10, sticky="w")
            
            # row=2: Budget Goal Input Section
            goal_input_frame = tk.Frame(top_row, bg="white")
            goal_input_frame.grid(row=2, column=1, pady=5, padx=10, sticky="w")

            tk.Label(goal_input_frame, text="Budget Goal: ₱", font=("Arial", 10), bg="white").pack(side="left")
            
            # This is where the user types the number
            self.goal_entry = tk.Entry(goal_input_frame, width=15, font=("Arial", 10))
            self.goal_entry.pack(side="left", padx=2)

            # Small button to save the goal to the database
            tk.Button(goal_input_frame, text="Set", font=("Arial", 8, "bold"), 
                  bg="#2196F3", fg="white", command=self.save_goal).pack(side="left", padx=5)
            
            # row=3: Upload Button
            tk.Button(top_row, text="Upload Photo", font=("Arial", 8), 
                    command=self.upload_photo).grid(row=3, column=1, pady=5, padx=10, sticky="w")


            # --- BOTTOM SECTION: FINANCIAL STATS ---
            stats_frame = tk.Frame(profile_frame, bg="white")
            stats_frame.pack(fill="x", pady=20, anchor="w")

            self.expense_var = tk.StringVar(value="Total Expenses: ₱0.00")
            # Changed the label text here to "Current Savings"
            self.savings_var = tk.StringVar(value="Current Savings: ₱0.00")

            tk.Label(stats_frame, textvariable=self.expense_var, bg="#ccc", 
                    width=45, anchor="w", padx=10, font=("Arial", 10, "bold")).pack(pady=5, anchor="w")           
            tk.Label(stats_frame, textvariable=self.savings_var, bg="#ccc", 
                    width=45, anchor="w", padx=10, font=("Arial", 10, "bold")).pack(pady=5, anchor="w")

    #fpr dashboard profile picture upload
    def upload_photo(self):
        """Allows user to pick an image and saves the path to the DB."""
        # This now works because of the updated import
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        
        if file_path:
            u_id = self.controller.current_user_id
            try:
                # Using 'connection' as requested
                with sqlite3.connect("cashatan.db") as connection:
                    connection.execute("UPDATE users SET profile_pic = ? WHERE user_id = ?", (file_path, u_id))
                    connection.commit()
                
                messagebox.showinfo("Success", "Profile picture updated!")
                self.load_data() # Refresh to show the new image
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Could not save image path: {e}")

    def load_data(self):
        """Fetches profile info and actual financial totals from the ledger."""
        u_id = getattr(self.controller, 'current_user_id', None)
        if u_id is None: return

        try:
            with sqlite3.connect("cashatan.db") as connection:
                cursor = connection.cursor()
                
                # 1. Load Profile Details
                cursor.execute("SELECT username, profile_pic FROM users WHERE user_id = ?", (u_id,))
                user_info = cursor.fetchone()
                
                if user_info:
                    self.username_var.set(user_info[0])
                    # Only try to load a custom photo if the path exists
                    if user_info[1]: 
                        try:
                            img = Image.open(user_info[1])
                            img = img.resize((150, 150), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            self.img_label.config(image=photo)
                            self.img_label.image = photo # Update reference to the new photo
                        except Exception:
                            # If file is missing, keep the placeholder
                            pass

                # 2. Get Budget Goal (Show it in the entry box)
                cursor.execute("SELECT savings_goal FROM budgets WHERE user_id = ?", (u_id,))
                goal_result = cursor.fetchone()
                self.goal_entry.delete(0, tk.END)
                if goal_result:
                    self.goal_entry.insert(0, f"{goal_result[0]:.2f}")
                else:
                    self.goal_entry.insert(0, "0.00")

                # 3. ACTUAL MONEY LOGIC (Total Income - Total Expense)
                # We ignore the 'monthly_income' field from the budgets table here.
                cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY type", (u_id,))
                totals = dict(cursor.fetchall())
                
                actual_income = totals.get('Income', 0.0)
                actual_expense = totals.get('Expense', 0.0)
                
                # Current Savings is only what you actually have.
                current_savings = actual_income - actual_expense

                self.expense_var.set(f"Total Expenses: ₱{actual_expense:,.2f}")
                self.savings_var.set(f"Current Savings: ₱{current_savings:,.2f}")

        except Exception as e:
            print(f"Error loading dashboard: {e}")
        
        
    def save_goal(self):
        """Saves the typed budget goal into the budgets table."""
        # 1. Get the current user ID and the typed goal
        u_id = getattr(self.controller, 'current_user_id', None)
        new_goal = self.goal_entry.get()

        if not u_id:
            messagebox.showerror("Error", "User not found. Please log in again.")
            return

        try:
            # 2. Convert the input to a number
            goal_value = float(new_goal)
            
            # 3. Save to database using your 'connection' naming
            with sqlite3.connect("cashatan.db") as connection:
                cursor = connection.cursor()
                
                # This SQL command updates the goal if the user_id exists, 
                # or creates a new row if it doesn't.
                query = """INSERT INTO budgets (user_id, savings_goal) 
                           VALUES (?, ?) 
                           ON CONFLICT(user_id) DO UPDATE SET savings_goal = excluded.savings_goal"""
                
                cursor.execute(query, (u_id, goal_value))
                connection.commit()
            
            messagebox.showinfo("Success", f"Budget Goal set to ₱{goal_value:,.2f}")
            
            # 4. Refresh the dashboard so all numbers update
            self.load_data()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for your goal.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving goal: {e}")

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
        """Clears the entry boxes and resets the dropdown selection."""
        for field, widget in self.entries.items():
            if field == "Category:":
                # Reset the dropdown to the placeholder text
                widget.set("Select Category")
            elif field != "Date:":
                # Clear standard text entries (Amount and Notes)
                widget.delete(0, tk.END)


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

# --- 5. DATA TABLE TEMPLATE (VIEW TRANSACTIONS) ---
class ViewTransactionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg="white") 
        
        # Header
        tk.Label(self, text="VIEW TRANSACTIONS", font=("Arial", 26, "bold"), 
                 bg="white", fg="black").pack(pady=(20, 10))
        
        # --- UI UPDATED: FORCED GRID LINES & COLORS ---
        style = ttk.Style()
        style.theme_use("clam") 
        
        # Header style with borders
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), 
                        background="#d9d9d9", foreground="black", 
                        borderwidth=1, relief="solid")
        
        # Row style with visible grid lines
        style.configure("Treeview", font=("Arial", 11), rowheight=35, 
                        background="white", fieldbackground="white", 
                        borderwidth=1, relief="solid")
        
        style.map("Treeview", background=[('selected', '#bcbcbc')])

        # 1. Table Setup
        cols = ("ID", "Type", "Date", "Category", "Amount", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", style="Treeview")
        
        # Alternating row colors (Zebra stripes)
        self.tree.tag_configure('oddrow', background="white")
        self.tree.tag_configure('evenrow', background="#f2f2f2") 

        # Define Headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Date", text="Date:")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Notes", text="Notes")

        # Column formatting
        self.tree.column("Type", width=100, anchor="center")
        self.tree.column("Date", width=120, anchor="center")
        self.tree.column("Category", width=150, anchor="center")
        self.tree.column("Amount", width=100, anchor="center")
        self.tree.column("Notes", width=250, anchor="w")

        self.tree["displaycolumns"] = ("Type", "Date", "Category", "Amount", "Notes")
        self.tree.pack(fill="both", expand=True, padx=30, pady=10)
        
        # --- FOOTER BUTTONS ---
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=30)
        
        btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#333",       
            "fg": "white",         
            "relief": "solid",     
            "borderwidth": 1,
            "activebackground": "#555",
            "activeforeground": "white", 
            "height": 2
        }
        
        tk.Button(btn_frame, text="Delete Expense", width=20,
                  command=self.delete_transaction, **btn_style).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Edit Expense", width=20,
                  command=self.edit_transaction, **btn_style).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Back to Dashboard", width=22, 
                  command=lambda: controller.show_frame("DashboardPage"), **btn_style).pack(side="left", padx=10)

    def load_data(self):
        """Refreshes the list from the database."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        u_id = getattr(self.controller, 'current_user_id', None)
        if u_id is None: return

        try:
            with sqlite3.connect("cashatan.db") as conn:
                cursor = conn.cursor()
                query = "SELECT transaction_id, type, date, category, amount, notes FROM transactions WHERE user_id = ? ORDER BY date DESC"
                cursor.execute(query, (u_id,))
                
                for i, row in enumerate(cursor.fetchall()):
                    if i % 2 == 0:
                        self.tree.insert("", "end", values=row, tags=('evenrow',))
                    else:
                        self.tree.insert("", "end", values=row, tags=('oddrow',))
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Could not load data: {e}")

    def delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection", "Please select a row to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            t_id = self.tree.item(selected_item)['values'][0]
            with sqlite3.connect("cashatan.db") as conn:
                conn.execute("DELETE FROM transactions WHERE transaction_id = ?", (t_id,))
            self.load_data()

    def edit_transaction(self):
        """Opens a popup window to edit the selected transaction."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection", "Please select a row to edit.")
            return

        item_data = self.tree.item(selected_item)['values']
        t_id, t_type, t_date, t_cat, t_amt, t_notes = item_data

        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Transaction")
        edit_win.geometry("400x450")
        edit_win.config(bg="white")

        tk.Label(edit_win, text=f"EDITING {t_type.upper()}", font=("Arial", 14, "bold"), 
                 bg="white").pack(pady=20)

        fields_frame = tk.Frame(edit_win, bg="white")
        fields_frame.pack(pady=10)

        label_font = ("Arial", 10, "bold")

        # Date Field
        tk.Label(fields_frame, text="Date:", bg="white", font=label_font).grid(row=0, column=0, pady=8, padx=5, sticky="e")
        ent_date = DateEntry(fields_frame, width=20, date_pattern='y-mm-dd')
        ent_date.set_date(t_date) 
        ent_date.grid(row=0, column=1, pady=8)

        # UPDATED: Category Field now uses a Combobox
        tk.Label(fields_frame, text="Category/Source:", bg="white", font=label_font).grid(row=1, column=0, pady=8, padx=5, sticky="e")
        
        # Define your category list here
        categories = ["Food", "Transport", "Bills", "Allowance", "Groceries", "Salary", "Others"]
        ent_cat = ttk.Combobox(fields_frame, values=categories, width=21, state="readonly")
        ent_cat.set(t_cat) # Pre-fill with existing category
        ent_cat.grid(row=1, column=1, pady=8)

        # Amount Field
        tk.Label(fields_frame, text="Amount:", bg="white", font=label_font).grid(row=2, column=0, pady=8, padx=5, sticky="e")
        ent_amt = tk.Entry(fields_frame, width=23, relief="solid")
        ent_amt.insert(0, t_amt) 
        ent_amt.grid(row=2, column=1, pady=8)

        # Notes Field
        tk.Label(fields_frame, text="Notes:", bg="white", font=label_font).grid(row=3, column=0, pady=8, padx=5, sticky="e")
        ent_notes = tk.Entry(fields_frame, width=23, relief="solid")
        ent_notes.insert(0, t_notes) 
        ent_notes.grid(row=3, column=1, pady=8)

        def save_changes():
            try:
                new_date = ent_date.get()
                new_cat = ent_cat.get()
                new_amt = float(ent_amt.get())
                new_notes = ent_notes.get()

                with sqlite3.connect("cashatan.db") as conn:
                    query = "UPDATE transactions SET date=?, category=?, amount=?, notes=? WHERE transaction_id=?"
                    conn.execute(query, (new_date, new_cat, new_amt, new_notes, t_id))
                
                messagebox.showinfo("Success", "Transaction updated!")
                edit_win.destroy()
                self.load_data() 
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number.")

        tk.Button(edit_win, text="SAVE CHANGES", width=20, 
                  font=("Arial", 11, "bold"), bg="#d9d9d9", relief="solid", 
                  borderwidth=1, command=save_changes).pack(pady=30)

# --- 6. SUMMARY TEMPLATE (BUDGET OVERVIEW) [cite: 143] ---
class BudgetOverviewPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg="white")

        # --- HEADER SECTION (Keep as is) ---
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", padx=20, pady=10)

        user_info = tk.Frame(header_frame, bg="white")
        user_info.pack(side="left")
        
        self.canvas_user = tk.Canvas(user_info, width=40, height=40, bg="white", highlightthickness=0)
        self.canvas_user.pack(side="left")
        
        self.lbl_username = tk.Label(user_info, text="username", font=("Arial", 14), bg="white")
        self.lbl_username.pack(side="left", padx=10)

        tk.Label(header_frame, text="BUDGET OVERVIEW", font=("Arial", 28, "bold"), bg="white").place(relx=0.5, anchor="n")
        tk.Label(header_frame, text=date.today().strftime("%m/%d/%Y"), font=("Arial", 14), bg="white").pack(side="right")

        tk.Frame(self, height=2, bg="black").pack(fill="x", padx=20)

        # --- MAIN CONTENT AREA ---
        content_frame = tk.Frame(self, bg="white")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        # BOXES (Stats, Summary, Progress)
        stats_box = tk.Frame(content_frame, bg="#d9d9d9", padx=15, pady=15, relief="solid", borderwidth=1)
        stats_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        self.lbl_monthly_inc = tk.Label(stats_box, text="Monthly Income: ₱0", font=("Arial", 11, "bold"), bg="white", relief="solid", borderwidth=1, anchor="w", padx=5)
        self.lbl_monthly_inc.pack(fill="x", pady=2)
        self.lbl_savings_goal = tk.Label(stats_box, text="Savings Goal: ₱0", font=("Arial", 11, "bold"), bg="white", relief="solid", borderwidth=1, anchor="w", padx=5)
        self.lbl_savings_goal.pack(fill="x", pady=2)
        self.lbl_avail_exp = tk.Label(stats_box, text="Available for Expenses: ₱0", font=("Arial", 11, "bold"), bg="#b3b3b3", relief="solid", borderwidth=1, anchor="w", padx=5)
        self.lbl_avail_exp.pack(fill="x", pady=2)

        top_right_container = tk.Frame(content_frame, bg="white")
        top_right_container.grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        top_right_container.columnconfigure(0, weight=1)
        top_right_container.columnconfigure(1, weight=1)

        summary_box = tk.Frame(top_right_container, bg="white", relief="solid", borderwidth=1, padx=10, pady=5)
        summary_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        tk.Label(summary_box, text="Expense Summary", font=("Arial", 11, "bold"), bg="#d9d9d9", relief="solid", borderwidth=1).pack(fill="x", pady=(0, 5))
        self.lbl_total_exp = tk.Label(summary_box, text="Total Expenses: ₱0", bg="white", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_total_exp.pack(fill="x", pady=5)
        self.lbl_remain_bud = tk.Label(summary_box, text="Remaining Budget: ₱0", bg="white", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_remain_bud.pack(fill="x", pady=5)

        progress_box = tk.Frame(top_right_container, bg="white", relief="solid", borderwidth=1, padx=10, pady=5)
        progress_box.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        tk.Label(progress_box, text="Savings Progress", font=("Arial", 11, "bold"), bg="#d9d9d9", relief="solid", borderwidth=1).pack(fill="x", pady=(0, 5))
        self.gauge_canvas = tk.Canvas(progress_box, width=80, height=80, bg="white", highlightthickness=0)
        self.gauge_canvas.pack(side="left")
        self.lbl_progress_text = tk.Label(progress_box, text="0% of Goal\nAchieved", font=("Arial", 10, "bold"), bg="white", justify="left")
        self.lbl_progress_text.pack(side="left", padx=5)

        # BREAKDOWNS
        breakdown_container = tk.Frame(content_frame, bg="white")
        breakdown_container.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        self.expense_box = tk.Frame(breakdown_container, bg="white", relief="solid", borderwidth=1)
        self.expense_box.pack(fill="both", expand=True, pady=(0, 5))
        tk.Label(self.expense_box, text="Expense Breakdown", font=("Arial", 11, "bold"), bg="#d9d9d9", relief="solid", borderwidth=1).pack(fill="x")
        self.expense_rows = tk.Frame(self.expense_box, bg="white")
        self.expense_rows.pack(fill="both", expand=True)

        self.income_box = tk.Frame(breakdown_container, bg="white", relief="solid", borderwidth=1)
        self.income_box.pack(fill="both", expand=True, pady=(5, 0))
        tk.Label(self.income_box, text="Income Breakdown", font=("Arial", 11, "bold"), bg="#d9d9d9", relief="solid", borderwidth=1).pack(fill="x")
        self.income_rows = tk.Frame(self.income_box, bg="white")
        self.income_rows.pack(fill="both", expand=True)

        # --- CHARTS AREA WITH DYNAMIC BINDING ---
        # ROW 1, COL 1: Charts Area (Expense Analytics Container)
        charts_box = tk.Frame(content_frame, bg="#d9d9d9", relief="solid", borderwidth=1)
        charts_box.grid(row=1, column=1, sticky="nsew") 
        
        # --- NEW SECTION HEADER: Expense Analytics ---
        tk.Label(charts_box, text="Expenses Analytics", font=("Arial", 11, "bold"), 
                 bg="white", relief="solid", borderwidth=1).pack(fill="x")
        
        # Inner Frame to provide padding for the actual content
        charts_inner = tk.Frame(charts_box, bg="#d9d9d9", padx=10, pady=10)
        charts_inner.pack(fill="both", expand=True)

        # The Canvas now lives inside charts_inner
        self.chart_canvas = tk.Canvas(charts_inner, bg="#d9d9d9", highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)

        # Re-bind the resize event to the new container
        self.chart_canvas.bind("<Configure>", lambda event: self.load_data())


        # --- FOOTER SECTION (Modern Dark Style) ---
        footer_frame = tk.Frame(self, bg="white")
        footer_frame.pack(fill="x", side="bottom", pady=20)

        # The "Logout" Style Button Configuration
        dark_btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#333",               # Dark Charcoal
            "fg": "white",              # White Text
            "relief": "flat",           # Clean flat look
            "activebackground": "#555", # Hover color
            "activeforeground": "white",
            "height": 2,
            "width": 22
        }

        tk.Button(footer_frame, text="ADD INCOME", 
                  command=lambda: controller.show_frame("AddIncomePage"), **dark_btn_style).pack(side="left", expand=True, padx=5)
        
        tk.Button(footer_frame, text="ADD EXPENSE", 
                  command=lambda: controller.show_frame("AddExpensePage"), **dark_btn_style).pack(side="left", expand=True, padx=5)
        
        tk.Button(footer_frame, text="BACK TO DASHBOARD", 
                  command=lambda: controller.show_frame("DashboardPage"), **dark_btn_style).pack(side="left", expand=True, padx=5)

    def load_data(self):
        u_id = getattr(self.controller, 'current_user_id', None)
        if not u_id: return

        # Force Tkinter to refresh current dimensions so we get the REAL width
        self.update_idletasks()
        canvas_w = self.chart_canvas.winfo_width()
        
        # Default fallback for initial load
        if canvas_w < 10: canvas_w = 450 

        # Reset Header Icon
        self.canvas_user.delete("all")
        self.canvas_user.create_oval(5, 5, 35, 35, fill="black")

        try:
            with sqlite3.connect("cashatan.db") as connection:
                cursor = connection.cursor()
                
                # 1. Header Profile
                cursor.execute("SELECT username, profile_pic FROM users WHERE user_id=?", (u_id,))
                user = cursor.fetchone()
                if user:
                    self.lbl_username.config(text=user[0])
                    if user[1]:
                        try:
                            img = Image.open(user[1]).resize((30, 30), Image.Resampling.LANCZOS)
                            self.profile_photo = ImageTk.PhotoImage(img)
                            self.canvas_user.create_image(20, 20, image=self.profile_photo)
                        except: pass

                # 2. Financial Logic
                cursor.execute("SELECT savings_goal FROM budgets WHERE user_id=?", (u_id,))
                goal_data = cursor.fetchone()
                goal = goal_data[0] if goal_data else 0.0
                
                cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id=? GROUP BY type", (u_id,))
                totals = dict(cursor.fetchall())
                total_income = totals.get('Income', 0.0)
                total_expenses = totals.get('Expense', 0.0)

                avail_for_exp = total_income - total_expenses
                progress_pct = (avail_for_exp / goal * 100) if goal > 0 else 0
                progress_pct = max(0, min(progress_pct, 100))

                # Labels
                self.lbl_monthly_inc.config(text=f"Total Monthly Income: ₱{total_income:,.2f}")
                self.lbl_savings_goal.config(text=f"Monthly Savings Goal: ₱{goal:,.2f}")
                self.lbl_avail_exp.config(text=f"Available for Expenses (Savings): ₱{avail_for_exp:,.2f}")
                self.lbl_total_exp.config(text=f"Total Expenses: ₱{total_expenses:,.2f}")
                self.lbl_remain_bud.config(text=f"Remaining Budget (Savings): ₱{avail_for_exp:,.2f}")

                # 3. Breakdowns
                for w in self.expense_rows.winfo_children(): w.destroy()
                cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE user_id=? AND type='Expense' GROUP BY category", (u_id,))
                exp_cats = cursor.fetchall()
                for cat, amt in exp_cats:
                    row = tk.Frame(self.expense_rows, bg="white")
                    row.pack(fill="x", padx=10, pady=2)
                    tk.Label(row, text=cat, bg="white").pack(side="left")
                    tk.Label(row, text=f"₱{amt:,.0f}", bg="white", font=("Arial", 10, "bold")).pack(side="right")

                for w in self.income_rows.winfo_children(): w.destroy()
                cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE user_id=? AND type='Income' GROUP BY category", (u_id,))
                for src, amt in cursor.fetchall():
                    row = tk.Frame(self.income_rows, bg="white")
                    row.pack(fill="x", padx=10, pady=2)
                    tk.Label(row, text=src, bg="white").pack(side="left")
                    tk.Label(row, text=f"₱{amt:,.0f}", bg="white", font=("Arial", 10, "bold")).pack(side="right")

                # 4. Progress Gauge
                self.gauge_canvas.delete("all")
                self.gauge_canvas.create_oval(10, 10, 70, 70, outline="#d9d9d9", width=4)
                extent = -(progress_pct / 100) * 359.9
                self.gauge_canvas.create_arc(10, 10, 70, 70, start=90, extent=extent, outline="black", width=4, style="arc")
                self.gauge_canvas.create_text(40, 40, text=f"{int(progress_pct)}%", font=("Arial", 10, "bold"))
                self.lbl_progress_text.config(text=f"{int(progress_pct)}% of Goal\nAchieved")

                # --- 5. FULLY RESPONSIVE DYNAMIC CHARTS ---
                # --- 5. BALANCED RESPONSIVE CHARTS ---
                self.chart_canvas.delete("all")
                
                # Measure current canvas size
                self.update_idletasks()
                canvas_w = self.chart_canvas.winfo_width()
                canvas_h = self.chart_canvas.winfo_height()
                
                if canvas_w <= 1: canvas_w, canvas_h = 500, 300

                # --- 1. COORDINATE MATH (Balanced Sizing) ---
                num_cats = len(exp_cats)
                
                # PIE POSITIONING: Shifted left of center (60% across)
                # to guarantee room for the legend on the right.
                pie_cx = canvas_w * 0.60
                pie_cy = canvas_h * 0.45 
                
                # RADIUS: Reduced multipliers (12% of width / 20% of height)
                # This prevents it from "exploding" in smaller windows.
                pie_r = min(canvas_w * 0.12, canvas_h * 0.20)
                
                # TITLES: Anchored relative to height
                title_y = canvas_h * 0.08

                # LINE CHART: Stays on the left side
                line_x_start, line_x_end = canvas_w * 0.08, canvas_w * 0.40
                line_y_bottom = canvas_h * 0.75
                line_y_top = canvas_h * 0.20
                line_center_x = (line_x_start + line_x_end) / 2

                # --- 2. DRAW DYNAMIC TITLES ---
                title_font = ("Arial", max(9, int(canvas_h * 0.04)), "bold")
                self.chart_canvas.create_text(line_center_x, title_y, text="Expenses Over Time", font=title_font)
                self.chart_canvas.create_text(pie_cx, title_y, text="Expenses Categories", font=title_font)

                # --- 3. DYNAMIC PIE CHART & SIDE LEGEND ---
                if total_expenses > 0:
                    start_ang = 90
                    colors = ["#333", "#555", "#777", "#999", "#bbb", "#ddd", "#888"]
                    
                    # Legend Row Height
                    line_height = max(12, int(canvas_h * 0.045))
                    
                    for i, (cat, amt) in enumerate(exp_cats):
                        extent = -(amt / total_expenses) * 359.9
                        percentage = (amt / total_expenses) * 100
                        
                        # Draw Pie (Smaller radius for better fit)
                        self.chart_canvas.create_arc(pie_cx - pie_r, pie_cy - pie_r, 
                                                     pie_cx + pie_r, pie_cy + pie_r, 
                                                     start=start_ang, extent=extent, 
                                                     fill=colors[i % len(colors)], outline="white", width=1)
                        
                        # --- SIDE LEGEND POSITIONING ---
                        # lx starts right after the pie circle
                        lx = pie_cx + pie_r + 15
                        # ly stacks vertically starting near the top of the pie
                        ly = (pie_cy - pie_r) + (i * line_height)
                        
                        sq_size = max(8, int(line_height * 0.6))
                        self.chart_canvas.create_rectangle(lx, ly, lx + sq_size, ly + sq_size, 
                                                           fill=colors[i % len(colors)], outline="black")
                        
                        # Legend Text (Smaller font for safety)
                        font_size = max(7, int(canvas_h * 0.028))
                        self.chart_canvas.create_text(lx + sq_size + 8, ly + (sq_size/2), 
                                                      text=f"{cat}: ({percentage:.1f}%)", 
                                                      font=("Arial", font_size, "bold"), anchor="w")
                        start_ang += extent

                # --- 4. DYNAMIC LINE CHART (Kept as is) ---
                cursor.execute("SELECT date, amount FROM transactions WHERE user_id=? AND type='Expense' ORDER BY date DESC LIMIT 5", (u_id,))
                data_points = cursor.fetchall()[::-1]
                if data_points:
                    max_v = max(float(d[1]) for d in data_points) if max(float(d[1]) for d in data_points) > 0 else 1
                    pts = []
                    spacing = (line_x_end - line_x_start) / 4 
                    for i, (t_date, val) in enumerate(data_points):
                        x = line_x_start + (i * spacing)
                        y = line_y_bottom - (float(val) / max_v * (line_y_bottom - line_y_top))
                        pts.extend([x, y])
                        self.chart_canvas.create_text(x, line_y_bottom + 20, text=t_date[-5:], 
                                                      font=("Arial", max(6, int(canvas_h * 0.025))), angle=45)
                    if len(pts) > 2:
                        self.chart_canvas.create_line(pts, width=3, fill="black", smooth=True)
                
                # Draw Axis
                self.chart_canvas.create_line(line_x_start - 5, line_y_bottom, line_x_end + 10, line_y_bottom) 
                self.chart_canvas.create_line(line_x_start - 5, line_y_top, line_x_start - 5, line_y_bottom)

        except Exception as e:
            print(f"Error updating Overview: {e}")

# ==========================================
# 4. START THE APP
# ==========================================
if __name__ == "__main__":
    init_db()
    app = CashAtanApp()
    app.mainloop()
