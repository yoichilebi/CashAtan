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
        self.controller = controller
        
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
            self.controller = controller

            # Page Title
            tk.Label(self, text="DASHBOARD", font=("Arial", 24, "bold")).pack(pady=20)

            # Main Layout Container
            main_container = tk.Frame(self)
            main_container.pack(fill="both", expand=True, padx=20)

            # --- LEFT SIDE: NAVIGATION BUTTONS ---
            nav_frame = tk.Frame(main_container)
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
            profile_frame = tk.LabelFrame(main_container, text="Profile", font=("Arial", 12, "bold"), padx=20, pady=20)
            profile_frame.pack(side="right", fill="both", expand=True)

            # Top section: Image and Username/Date/Goal
            top_row = tk.Frame(profile_frame)
            top_row.pack(fill="x")

            # Profile Image Slot
            # Inside your DashboardPage __init__
            self.img_label = tk.Label(top_row, bg="#ddd", relief="solid", borderwidth=1)
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
                    anchor="w").grid(row=0, column=1, pady=2, padx=10, sticky="w")
            
            # row=1: Date (No box)
            tk.Label(top_row, textvariable=self.date_var, font=("Arial", 10), 
                    fg="gray", anchor="w").grid(row=1, column=1, pady=2, padx=10, sticky="w")
            
            # row=2: Budget Goal Input Section
            goal_input_frame = tk.Frame(top_row)
            goal_input_frame.grid(row=2, column=1, pady=5, padx=10, sticky="w")

            tk.Label(goal_input_frame, text="Budget Goal: ₱", font=("Arial", 10)).pack(side="left")
            
            # This is where the user types the number
            self.goal_entry = tk.Entry(goal_input_frame, width=15, font=("Arial", 10))
            self.goal_entry.pack(side="left", padx=2)

            # Small button to save the goal to the database
            tk.Button(goal_input_frame, text="Set", font=("Arial", 8, "bold"), 
                  bg="#2196F3", fg="white", command=self.save_goal).pack(side="left", padx=5)
            
            # row=3: Upload Button
            tk.Button(top_row, text="Upload Photo", font=("Arial", 8), 
                    command=self.upload_photo).grid(row=3, column=1, pady=5, padx=10, sticky="w")


            # Bottom section: Financial Stats
            stats_frame = tk.Frame(profile_frame)
            
            stats_frame.pack(fill="x", pady=20, anchor="w")

            self.expense_var = tk.StringVar(value="Total Expenses: ₱0.00")
            self.savings_var = tk.StringVar(value="Total Savings: ₱0.00")

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
        """Fetches profile info and financial totals."""
        u_id = getattr(self.controller, 'current_user_id', None)
        if u_id is None: return

        try:
            # Using 'connection' as requested
            with sqlite3.connect("cashatan.db") as connection:
                cursor = connection.cursor()
                
                # 1. Get User Details
                cursor.execute("SELECT username, profile_pic FROM users WHERE user_id = ?", (u_id,))
                user_info = cursor.fetchone()
                
                if user_info:
                    self.username_var.set(user_info[0])
                    # Load Image from the saved path
                    if user_info[1]:
                        try:
                            img = Image.open(user_info[1])
                            img = img.resize((120, 120), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            self.img_label.config(image=photo, text="")
                            self.img_label.image = photo 
                        except Exception:
                            self.img_label.config(image='', text="Image Error")

                # 2. Get Budget Goal (From budgets table)
                cursor.execute("SELECT savings_goal FROM budgets WHERE user_id = ?", (u_id,))
                goal_result = cursor.fetchone()
                
                # Clear the box and put the existing goal in it
                self.goal_entry.delete(0, tk.END)
                if goal_result:
                    self.goal_entry.insert(0, f"{goal_result[0]:.2f}")
                else:
                    self.goal_entry.insert(0, "0.00")

                # 3. Calculate Totals (From transactions table)
                cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY type", (u_id,))
                totals = dict(cursor.fetchall())
                income = totals.get('Income', 0.0)
                expense = totals.get('Expense', 0.0)
                savings = income - expense

                self.expense_var.set(f"Total Expenses: ₱{expense:,.2f}")
                self.savings_var.set(f"Total Savings: ₱{savings:,.2f}")

        except Exception as e:
            # This helps catch that 'no such column' error if the DB isn't updated
            print(f"Error loading dashboard: {e}")
        
        def save_goal(self):
            """Saves the typed budget goal into the budgets table."""
            u_id = getattr(self.controller, 'current_user_id', None)
            new_goal = self.goal_entry.get()

            if not u_id:
                messagebox.showerror("Error", "User not found.")
                return

            try:
                # Convert input to a float number
                goal_value = float(new_goal)
                
                with sqlite3.connect("cashatan.db") as connection:
                    cursor = connection.cursor()
                    # 'INSERT OR REPLACE' updates the row if the user_id already exists
                    query = """INSERT INTO budgets (user_id, savings_goal) 
                            VALUES (?, ?) 
                            ON CONFLICT(user_id) DO UPDATE SET savings_goal = excluded.savings_goal"""
                    cursor.execute(query, (u_id, goal_value))
                    connection.commit()
                
                messagebox.showinfo("Success", f"Budget Goal set to ₱{goal_value:,.2f}")
                self.load_data() # Refresh the profile stats

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for your goal.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error saving goal: {e}")

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




# --- 5. DATA TABLE TEMPLATE (VIEW TRANSACTIONS) [cite: 114] ---
class ViewTransactionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="VIEW TRANSACTIONS", font=("Arial", 18, "bold")).pack(pady=10)
        
        # 1. Table Setup
        cols = ("ID", "Type", "Date", "Category", "Amount", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree["displaycolumns"] = ("Type", "Date", "Category", "Amount", "Notes")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 2. Buttons Container (The 3 Buttons you requested)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="DELETE", width=18,
                  command=self.delete_transaction).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="EDIT", width=18,
                  command=self.edit_transaction).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="BACK TO DASHBOARD", width=22, 
                  command=lambda: controller.show_frame("DashboardPage")).pack(side="left", padx=5)

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
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=row)
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

        # Get existing values
        item_data = self.tree.item(selected_item)['values']
        t_id, t_type, t_date, t_cat, t_amt, t_notes = item_data

        # Create Popup Window
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Transaction")
        edit_win.geometry("400x450")

        tk.Label(edit_win, text=f"EDITING {t_type.upper()}", font=("Arial", 12, "bold")).pack(pady=10)

        # Fields (Date, Category, Amount, Notes)
        # Note: We reuse the same logic from your Add pages for consistency
        fields_frame = tk.Frame(edit_win)
        fields_frame.pack(pady=10)

        tk.Label(fields_frame, text="Date:").grid(row=0, column=0, pady=5, sticky="e")
        ent_date = DateEntry(fields_frame, width=20, date_pattern='y-mm-dd')
        ent_date.set_date(t_date) # Pre-fill existing date
        ent_date.grid(row=0, column=1, pady=5)

        tk.Label(fields_frame, text="Category/Source:").grid(row=1, column=0, pady=5, sticky="e")
        ent_cat = tk.Entry(fields_frame, width=23)
        ent_cat.insert(0, t_cat) # Pre-fill existing category
        ent_cat.grid(row=1, column=1, pady=5)

        tk.Label(fields_frame, text="Amount:").grid(row=2, column=0, pady=5, sticky="e")
        ent_amt = tk.Entry(fields_frame, width=23)
        ent_amt.insert(0, t_amt) # Pre-fill existing amount
        ent_amt.grid(row=2, column=1, pady=5)

        tk.Label(fields_frame, text="Notes:").grid(row=3, column=0, pady=5, sticky="e")
        ent_notes = tk.Entry(fields_frame, width=23)
        ent_notes.insert(0, t_notes) # Pre-fill existing notes
        ent_notes.grid(row=3, column=1, pady=5)

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
                self.load_data() # Refresh main table
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number.")

        tk.Button(edit_win, text="SAVE CHANGES", width=20, command=save_changes).pack(pady=20)

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
