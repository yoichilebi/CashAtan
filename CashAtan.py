import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageOps
import sqlite3
from tkcalendar import DateEntry
from datetime import date

# ==========================================
# 1. DATABASE INITIALIZATION
# ==========================================

# This function initializes the local database file and creates the necessary tables if they do not exist
def init_db():
    with sqlite3.connect("cashatan.db") as connection:
        cursor = connection.cursor()
        # This line ensures that the database respects relationships between different tables
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 1. Users Table: Stores account information like name, email, and login credentials
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            profile_pic TEXT
        )''')

        # 2. Transactions Table: Stores every income and expense entry linked to a specific user
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

        # 3. Budgets Table: Stores the user's specific financial goals and income settings
        cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
            budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            monthly_income REAL DEFAULT 0.0,
            savings_goal REAL DEFAULT 0.0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )''')
        
        connection.commit()

# This function handles the logic for creating a new account and checks for duplicate usernames or emails
def register_user(full_name, email, username, password):
    """Inserts a new user. Returns True if successful, False if duplicate."""
    try:
        connection = sqlite3.connect("cashatan.db")
        cursor = connection.cursor()
        # This code enables the system to save the user's details into the database
        cursor.execute('''
            INSERT INTO users (full_name, email, username, password)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, username, password))
        connection.commit()
        connection.close()
        return True
    except sqlite3.IntegrityError:
        # Returns False if the email or username is already registered in the system
        return False


# This function enables the system to verify if the login credentials provided match an existing user
def authenticate_user(username, password):
    """Checks credentials. Returns the user tuple if found, else None."""
    connection = sqlite3.connect("cashatan.db")
    cursor = connection.cursor()
    # This code enables the database to search for a specific user based on their credentials
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    connection.close()
    return user

# This function adds interactive animations by changing button colors when the mouse enters or leaves
def bind_hover(button, hover_color="#1C2541", normal_color="#3A506B"):
    """Adds a smooth color change effect on hover."""
    # This code enables the button to change color when the mouse pointer is moved over it
    button.bind("<Enter>", lambda e: button.config(bg=hover_color))
    # This code enables the button to return to its original color when the mouse pointer leaves
    button.bind("<Leave>", lambda e: button.config(bg=normal_color))


# ==========================================
# 2. MAIN APPLICATION CONTROLLER
# ==========================================
# This class acts as the "brain" of the application, managing window settings and page switching
class CashAtanApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        # This code initializes the base Tkinter window
        super().__init__(*args, **kwargs)

        # This code sets the title that appears on the window's top bar
        self.title("CashAtan - Personal Expense Tracker")
        
        # This code defines the starting width and height of the application window
        self.geometry("900x650")
        
        # This code initializes a global variable to track which user is logged in across all pages
        self.current_user_id = None 

        # This code creates a main container frame where all the different pages will be stacked
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # This code ensures that the pages inside the container expand to fill the entire window space
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # This code creates a dictionary to store and easily access the different page instances
        self.frames = {}

        # This code loops through all the page classes to register and build them within the application
        for F in (LoginPage, SignUpPage, DashboardPage, AddExpensePage, 
                  AddIncomePage, ViewTransactionsPage, BudgetOverviewPage):
            page_name = F.__name__
            
            # This code creates the actual page object and links it to this main controller
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            
            # This code stacks the pages on top of each other in the same grid position
            frame.grid(row=0, column=0, sticky="nsew")

        # This code ensures that the LoginPage is the first screen shown when the app starts
        self.show_frame("LoginPage")

    # This function enables the application to switch from one screen to another
    def show_frame(self, page_name):
        """Switches to the specified page and refreshes data if needed."""
        # This code retrieves the requested page from the dictionary of registered frames
        frame = self.frames[page_name]
        
        # This code checks if the page has a function to refresh its data from the database
        if hasattr(frame, "load_data"):
            # This code triggers the data refresh to ensure the user sees updated information
            frame.load_data()
            
        # This code brings the requested page to the very front so the user can see it
        frame.tkraise()

# ==========================================
# 3. PAGE CLASS TEMPLATES
# ==========================================

# --- 1. LANDING PAGE (LOGIN / SIGN UP) ---
# This class defines the visual layout and logic for the Login screen
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        # This code initializes the frame and links it to the main application controller
        super().__init__(parent)
        self.controller = controller
        # This code applies the deep navy background color to the entire page
        self.configure(bg="#0B132B") 

        # --- HEADER SECTION ---
        # This code creates a container for the top title of the page
        header_frame = tk.Frame(self, bg="#0B132B")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # This code displays the main "LOGIN / SIGN UP" text in bold white
        tk.Label(header_frame, text="LOGIN / SIGN UP", font=("Arial", 24, "bold"), 
                  bg="#0B132B", fg="#FFFFFF").pack()
        
        # This code draws the steel blue decorative divider line under the header
        tk.Frame(self, height=2, bg="#3A506B").pack(fill="x", padx=20, pady=(0, 5))

        # --- MAIN CONTENT WRAPPER ---
        # This code acts as a central container to hold both the logo and the input forms
        self.content_wrapper = tk.Frame(self, bg="#0B132B")
        self.content_wrapper.pack(fill="x", pady=(10, 0)) 

        # --- LOGO SECTION (300x300) ---
        # This code sets up the area where the application logo is displayed
        self.logo_frame = tk.Frame(self.content_wrapper, bg="#0B132B")
        self.logo_frame.pack(pady=(0, 10)) 

        self.logo_label = tk.Label(self.logo_frame, bg="#0B132B")
        self.logo_label.pack()
        # This code triggers the function to load and display the branding image
        self.set_logo("logo.png") 

        # --- FORM SECTION ---
        # This code creates the container for the username and password input fields
        form_container = tk.Frame(self.content_wrapper, bg="#0B132B")
        form_container.pack() 

        # This code manages the state of the "Show Password" checkbox
        self.var_show_pass = tk.BooleanVar(value=False)
        label_font = ("Arial", 14)
        
        # This code sets up the Username label and entry box
        tk.Label(form_container, text="Username:", font=label_font, 
                  bg="#0B132B", fg="#FFFFFF").grid(row=0, column=0, sticky="e", pady=10, padx=10)
        
        self.username_entry = tk.Entry(form_container, font=("Arial", 12), width=30, 
                                        relief="solid", borderwidth=1, 
                                        bg="#1C2541", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.username_entry.grid(row=0, column=1, pady=10)

        # This code sets up the Password label and entry box
        tk.Label(form_container, text="Password:", font=label_font, 
                  bg="#0B132B", fg="#FFFFFF").grid(row=1, column=0, sticky="e", pady=10, padx=10)
        
        self.password_entry = tk.Entry(form_container, font=("Arial", 12), width=30, show="*", 
                                        relief="solid", borderwidth=1, 
                                        bg="#1C2541", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.password_entry.grid(row=1, column=1, pady=10)

        # This code creates the checkbox that allows users to reveal their password
        tk.Checkbutton(form_container, text="Show Password", variable=self.var_show_pass, 
                        bg="#0B132B", fg="#FFFFFF", font=("Arial", 10), 
                        selectcolor="#1C2541", activebackground="#0B132B", 
                        activeforeground="#FFFFFF", command=self.toggle_password).grid(row=2, column=1, sticky="w")

        # --- BUTTON SECTION ---
        # This code creates the area at the bottom for navigation buttons
        btn_frame = tk.Frame(self, bg="#0B132B")
        btn_frame.pack(side="bottom", pady=40)

        # This code defines the shared visual style for the Login and Sign Up buttons
        dark_btn_style = {
            "font": ("Arial", 11, "bold"), "bg": "#3A506B", "fg": "white", 
            "relief": "flat", "activebackground": "#1C2541", "activeforeground": "white",
            "width": 18, "height": 2
        }

        # This code sets up the Login button and its hover animation
        btn_login = tk.Button(btn_frame, text="LOGIN", command=self.login_action, **dark_btn_style)
        btn_login.pack(side="left", padx=10)
        bind_hover(btn_login, hover_color="#1C2541", normal_color="#3A506B")
        
        # This code sets up the Sign Up button and its hover animation
        btn_signup = tk.Button(btn_frame, text="SIGN UP", command=lambda: controller.show_frame("SignUpPage"), **dark_btn_style)
        btn_signup.pack(side="left", padx=10)
        bind_hover(btn_signup, hover_color="#1C2541", normal_color="#3A506B")

        # This code enables the page to automatically adjust its layout if the window is resized
        self.bind("<Configure>", self.adjust_position)

    # This function enables the UI to be responsive by adding padding on larger screens
    def adjust_position(self, event=None):
        if self.winfo_height() > 800:
            self.content_wrapper.pack_configure(pady=(80, 0)) 
        else:
            self.content_wrapper.pack_configure(pady=(5, 0)) 

    # This function enables the system to load the branding logo or display fallback text if the file is missing
    def set_logo(self, path):
        try:
            img = Image.open(path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(img)
            self.logo_label.config(image=self.logo_photo)
        except Exception as e:
            # Fallback if image not found
            self.logo_label.config(text="CASHATAN", fg="#00FFCC", font=("Arial", 32, "bold"))

    # This function enables the user to switch between masking and showing the password text
    def toggle_password(self):
        self.password_entry.config(show="" if self.var_show_pass.get() else "*")

    # This function enables the system to verify user credentials and navigate to the dashboard
    def login_action(self):
        # This code calls the authentication logic to check the database
        user = authenticate_user(self.username_entry.get(), self.password_entry.get())
        if user:
            # This code stores the logged-in user's ID and switches to the Dashboard
            self.controller.current_user_id = user[0] 
            messagebox.showinfo("Login Success", f"Welcome back, {user[3]}!")
            self.controller.show_frame("DashboardPage")
        else:
            # This code displays an error message if the credentials don't match
            messagebox.showerror("Error", "Invalid username or password.")

# --- 2. SIGN UP PAGE ---
# This class defines the visual layout and logic for the account registration screen
class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        # This code initializes the page and links it to the main application controller
        super().__init__(parent)
        self.controller = controller
        # This code sets the main background color to midnight navy
        self.configure(bg="#0B132B")

        # --- HEADER SECTION ---
        # This code creates a top frame to house the page title
        header_frame = tk.Frame(self, bg="#0B132B")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # This code displays the "SIGN UP" title in bold white text
        tk.Label(header_frame, text="SIGN UP", font=("Arial", 24, "bold"), 
                  bg="#0B132B", fg="#FFFFFF").pack()
        
        # This code creates the steel-blue decorative divider line below the title
        tk.Frame(self, height=2, bg="#3A506B").pack(fill="x", padx=20, pady=(0, 5))

        # --- MAIN CONTENT WRAPPER ---
        # This code serves as a container for the logo and form fields for easier positioning
        self.content_wrapper = tk.Frame(self, bg="#0B132B")
        self.content_wrapper.pack(fill="x") 

        # --- LOGO SECTION ---
        # This code sets up the frame for the branding logo
        self.logo_frame = tk.Frame(self.content_wrapper, bg="#0B132B")
        self.logo_frame.pack(pady=(0, 5))

        self.logo_label = tk.Label(self.logo_frame, bg="#0B132B")
        self.logo_label.pack()
        # This code calls the function to load and display the logo image
        self.set_logo("logo.png") 

        # --- FORM SECTION ---
        # This code creates a dedicated container for the user input fields
        form_container = tk.Frame(self.content_wrapper, bg="#0B132B")
        form_container.pack() 

        # This code initializes a dictionary to store the user input data
        self.entries = {}
        fields = [("Full Name:", "full_name"), ("Email:", "email"), 
                  ("Username:", "username"), ("Password:", "password")]
        
        # This code manages the state of the password visibility toggle
        self.var_show_pass = tk.BooleanVar(value=False)

        # This loop enables the dynamic creation of labels and entry boxes for each field
        for i, (label_text, key_name) in enumerate(fields):
            tk.Label(form_container, text=label_text, font=("Arial", 12), 
                      bg="#0B132B", fg="#FFFFFF").grid(row=i, column=0, sticky="e", pady=5, padx=10)
            
            # This code ensures password fields use masking characters by default
            show_char = "*" if "Password" in label_text else None
            entry_widget = tk.Entry(form_container, font=("Arial", 12), width=30, show=show_char, 
                                     relief="solid", borderwidth=1, 
                                     bg="#1C2541", fg="#FFFFFF", insertbackground="#FFFFFF")
            entry_widget.grid(row=i, column=1, pady=5)
            # This code saves each entry widget so its data can be retrieved later
            self.entries[key_name] = entry_widget 

        # This code creates a checkbox that allows the user to see what they are typing in the password field
        tk.Checkbutton(form_container, text="Show Password", variable=self.var_show_pass, 
                        bg="#0B132B", fg="#FFFFFF", font=("Arial", 10), 
                        selectcolor="#1C2541", activebackground="#0B132B", 
                        activeforeground="#FFFFFF", command=self.toggle_password).grid(row=len(fields), column=1, sticky="w")

        # --- BUTTON SECTION ---
        # This code creates a bottom-aligned frame for navigation buttons
        btn_frame = tk.Frame(self, bg="#0B132B")
        btn_frame.pack(side="bottom", pady=30)

        # This code defines the global style for the action buttons
        dark_btn_style = {
            "font": ("Arial", 11, "bold"), "bg": "#3A506B", "fg": "white", 
            "relief": "flat", "activebackground": "#1C2541", "activeforeground": "white",
            "width": 18, "height": 2
        }

        # This code creates the Register button and applies the hover animation
        btn_register = tk.Button(btn_frame, text="REGISTER", command=self.signup_action, **dark_btn_style)
        btn_register.pack(side="left", padx=10)
        bind_hover(btn_register, hover_color="#1C2541", normal_color="#3A506B")
        
        # This code creates the Back button to return the user to the login screen
        btn_back = tk.Button(btn_frame, text="BACK", command=lambda: controller.show_frame("LoginPage"), **dark_btn_style)
        btn_back.pack(side="left", padx=10)
        bind_hover(btn_back, hover_color="#1C2541", normal_color="#3A506B")

        # This code enables the page to respond to changes in window size
        self.bind("<Configure>", self.adjust_position)

    # This function enables the UI to remain aesthetically balanced when the window is resized
    def adjust_position(self, event=None):
        if self.winfo_height() > 800:
            self.content_wrapper.pack_configure(pady=(60, 0)) 
        else:
            self.content_wrapper.pack_configure(pady=(0, 0))  

    # This function handles loading the logo image or displays text if the file is missing
    def set_logo(self, path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS) 
            self.logo_photo = ImageTk.PhotoImage(img)
            self.logo_label.config(image=self.logo_photo)
        except Exception:
            # This code provides a fallback text label if the logo image cannot be loaded
            self.logo_label.config(text="CASHATAN", fg="#00FFCC", font=("Arial", 32, "bold"))

    # This function enables the switching of password visibility between hidden and plain text
    def toggle_password(self):
        pw_entry = self.entries['password']
        pw_entry.config(show="" if self.var_show_pass.get() else "*")

    # This function validates the entered data and attempts to create a new user account
    def signup_action(self):
        # This code retrieves the current text from all input fields
        name = self.entries['full_name'].get()
        email = self.entries['email'].get()
        user = self.entries['username'].get()
        pw = self.entries['password'].get()

        # This code enables the system to check if all required data fields are filled
        if not all([name, email, user, pw]):
            messagebox.showwarning("Incomplete", "Please fill in all fields.")
            return

        # This code interacts with the database to register the user and handles the result
        if register_user(name, email, user, pw):
            messagebox.showinfo("Success", "Registration complete! You can now log in.")
            # This code sends the user back to the login screen upon successful registration
            self.controller.show_frame("LoginPage")
        else:
            # This code alerts the user if the username or email is already taken
            messagebox.showerror("Error", "Username or Email already exists.")

# --- 3. DASHBOARD (CENTRAL HUB) ---
# This class acts as the main user interface where the user can see their profile and access all app features
class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        # This code initializes the dashboard frame and links it to the main application controller
        super().__init__(parent)
        self.controller = controller
        # This code sets the background color of the dashboard to the midnight navy theme
        self.configure(bg="#0B132B") 

        # --- HEADER SECTION ---
        # This code creates a container for the top title of the dashboard
        header_frame = tk.Frame(self, bg="#0B132B")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # This code displays the "DASHBOARD" title in bold white text
        tk.Label(header_frame, text="DASHBOARD", font=("Arial", 28, "bold"), 
                  bg="#0B132B", fg="white").pack() 
        
        # This code draws the steel blue decorative divider line under the header
        tk.Frame(self, height=2, bg="#3A506B").pack(fill="x", padx=20, pady=(0, 20))

        # This code enables the main content to be organized horizontally (Sidebar on left, Profile on right)
        main_container = tk.Frame(self, bg="#0B132B")
        main_container.pack(fill="both", expand=True, padx=20)

        # --- LEFT SIDE: COMPACT NAVIGATION ---
        # This code creates a scrollable canvas for the navigation menu to handle many buttons if needed
        self.nav_canvas = tk.Canvas(main_container, bg="#0B132B", highlightthickness=0, width=280)
        self.nav_canvas.pack(side="left", fill="y", padx=(0, 20))

        # This code enables the use of a scrollbar for the navigation sidebar
        self.scrollbar = tk.Scrollbar(main_container, orient="vertical", command=self.nav_canvas.yview)
        self.nav_canvas.configure(yscrollcommand=self.scrollbar.set)

        # This code creates an internal frame inside the canvas to hold the actual buttons
        self.nav_inner_frame = tk.Frame(self.nav_canvas, bg="#0B132B")
        self.canvas_window = self.nav_canvas.create_window((0, 0), window=self.nav_inner_frame, anchor="nw")

        # LOGO
        # This code displays the app's branding logo at the top of the navigation bar
        self.logo_label = tk.Label(self.nav_inner_frame, bg="#0B132B")
        self.logo_label.pack(pady=(0, 10))
        self.set_logo("logo.png") 

        # This code defines the visual style for the sidebar menu buttons
        nav_btn_style = {
            "width": 25, "height": 2, "font": ("Arial", 11, "bold"),
            "bg": "#3A506B", "fg": "white", "relief": "flat",
            "activebackground": "#1C2541", "activeforeground": "#00FFCC"
        }

        # List of navigation targets
        btns = [
            ("ADD EXPENSE", "AddExpensePage"),
            ("ADD INCOME", "AddIncomePage"),
            ("VIEW TRANSACTIONS", "ViewTransactionsPage"),
            ("BUDGET OVERVIEW", "BudgetOverviewPage")
        ]

        # This loop enables the automatic creation of all navigation buttons with hover animations
        for text, page in btns:
            btn = tk.Button(self.nav_inner_frame, text=text, 
                            command=lambda p=page: controller.show_frame(p), **nav_btn_style)
            btn.pack(pady=3) 
            bind_hover(btn, hover_color="#1C2541", normal_color="#3A506B")

        # This code creates the Logout button that returns the user to the login screen
        btn_logout = tk.Button(self.nav_inner_frame, text="LOGOUT", width=25, height=2, 
                                font=("Arial", 11, "bold"), bg="#1C2541", fg="#FF007F", 
                                relief="flat", command=lambda: controller.show_frame("LoginPage"))
        btn_logout.pack(pady=10)
        bind_hover(btn_logout, hover_color="#3A506B", normal_color="#1C2541")

        # --- RIGHT SIDE: PROFILE SECTION ---
        # This code creates a stylized card container to display user info and financial stats
        profile_frame = tk.LabelFrame(main_container, text="Profile", bg="#1C2541", 
                                       fg="white", font=("Arial", 16, "bold"), padx=25, pady=25)
        profile_frame.pack(side="right", fill="both", expand=True)

        # This code sets up the layout for the top part of the profile card (Photo and Name)
        top_row = tk.Frame(profile_frame, bg="#1C2541")
        top_row.pack(fill="x")

        # This code enables the display of the user's profile picture with a solid border
        self.img_label = tk.Label(top_row, bg="#0B132B", relief="solid", borderwidth=2)
        self.img_label.grid(row=0, column=0, rowspan=4, padx=(0, 25), sticky="nsew")

        # This code sets up a default grey placeholder image if no photo has been uploaded yet
        placeholder = Image.new('RGB', (150, 150), color = '#0B132B')
        self.ph_img = ImageTk.PhotoImage(placeholder)
        self.img_label.config(image=self.ph_img)

        # Variables to dynamically update the displayed username and current date
        self.username_var = tk.StringVar(value="username")
        self.date_var = tk.StringVar(value=date.today().strftime("%m/%d/%Y"))
        
        # This code displays the user's name and the current date on the profile card
        tk.Label(top_row, textvariable=self.username_var, font=("Arial", 20, "bold"), 
                anchor="w", bg="#1C2541", fg="#FFFFFF").grid(row=0, column=1, pady=2, padx=10, sticky="w")
        
        tk.Label(top_row, textvariable=self.date_var, font=("Arial", 13), 
                fg="#bdbdbd", anchor="w", bg="#1C2541").grid(row=1, column=1, pady=2, padx=10, sticky="w")
        
        # This code creates a section where the user can input their desired monthly budget goal
        goal_input_frame = tk.Frame(top_row, bg="#1C2541")
        goal_input_frame.grid(row=2, column=1, pady=8, padx=10, sticky="w")

        tk.Label(goal_input_frame, text="Budget Goal: ₱", font=("Arial", 13), 
                  bg="#1C2541", fg="#FFFFFF").pack(side="left")
        
        # Entry field for the budget amount
        self.goal_entry = tk.Entry(goal_input_frame, width=15, font=("Arial", 13),
                                    bg="#0B132B", fg="#00FFCC", insertbackground="white")
        self.goal_entry.pack(side="left", padx=5)

        # Button to save the new budget goal to the database
        btn_set = tk.Button(goal_input_frame, text="Set", font=("Arial", 9, "bold"), 
                   bg="#3A506B", fg="#00FFCC", relief="flat", command=self.save_goal, width=5)
        btn_set.pack(side="left", padx=5)
        bind_hover(btn_set, hover_color="#1C2541", normal_color="#3A506B")

        # Button that enables the user to upload a custom profile picture
        btn_upload_photo = tk.Button(top_row, text="Upload Photo", font=("Arial", 9), bg="#3A506B", 
                     fg="white", relief="flat", command=self.upload_photo, padx=10)
        btn_upload_photo.grid(row=3, column=1, pady=5, padx=10, sticky="w")
        bind_hover(btn_upload_photo, hover_color="#1C2541", normal_color="#3A506B")

        # This section creates large summary bars for real-time financial tracking
        stats_frame = tk.Frame(profile_frame, bg="#1C2541")
        stats_frame.pack(fill="x", pady=20, anchor="w")

        # Variables to store calculated totals from the database
        self.expense_var = tk.StringVar(value="Total Expenses: ₱0.00")
        self.savings_var = tk.StringVar(value="Current Savings: ₱0.00")

        # This code enables the display of total expenses with a pink color highlight
        tk.Label(stats_frame, textvariable=self.expense_var, bg="#0B132B", fg="#FF007F",
                width=40, anchor="w", padx=20, font=("Arial", 13, "bold"),
                relief="solid", borderwidth=2, height=1).pack(pady=8, anchor="w")           
        
        # This code enables the display of current savings with a green color highlight
        tk.Label(stats_frame, textvariable=self.savings_var, bg="#0B132B", fg="#7ED321",
                width=40, anchor="w", padx=20, font=("Arial", 13, "bold"),
                relief="solid", borderwidth=2, height=1).pack(pady=8, anchor="w")

    # This function enables the internal frame to adjust the scrolling area based on content size
    def on_frame_configure(self, event):
        self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))

    # This function enables the responsive resizing of the canvas window to match the parent container
    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.nav_canvas.itemconfig(self.canvas_window, width=canvas_width)

    # This function enables the loading and formatting of the application logo image
    def set_logo(self, path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img = img.resize((120, 120), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(img)
            self.logo_label.config(image=self.logo_photo)
        except Exception:
            # Fallback text if the image file is missing
            self.logo_label.config(text="CASHATAN", fg="#00FFCC", font=("Arial", 18, "bold"))

    # This function enables the user to select an image file and save its path as their profile picture
    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            u_id = self.controller.current_user_id
            try:
                # This code enables the database to update the user's profile picture column
                with sqlite3.connect("cashatan.db") as connection:
                    connection.execute("UPDATE users SET profile_pic = ? WHERE user_id = ?", (file_path, u_id))
                    connection.commit()
                messagebox.showinfo("Success", "Profile picture updated!")
                # This code refreshes the dashboard to show the new picture
                self.load_data() 
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Could not save image path: {e}")

    # This function enables the dashboard to pull the latest information from the database upon opening
    def load_data(self):
        u_id = getattr(self.controller, 'current_user_id', None)
        if u_id is None: return
        try:
            with sqlite3.connect("cashatan.db") as connection:
                cursor = connection.cursor()
                
                # This code retrieves the username and the profile picture path for the current user
                cursor.execute("SELECT username, profile_pic FROM users WHERE user_id = ?", (u_id,))
                user_info = cursor.fetchone()
                if user_info:
                    self.username_var.set(user_info[0])
                    # This code enables the loading of the custom profile picture if one exists
                    if user_info[1]: 
                        try:
                            img = Image.open(user_info[1])
                            img = img.resize((150, 150), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            self.img_label.config(image=photo)
                            self.img_label.image = photo 
                        except Exception: pass
                
                # This code retrieves the savings goal from the budgets table
                cursor.execute("SELECT savings_goal FROM budgets WHERE user_id = ?", (u_id,))
                goal_result = cursor.fetchone()
                self.goal_entry.delete(0, tk.END)
                if goal_result: self.goal_entry.insert(0, f"{goal_result[0]:.2f}")
                else: self.goal_entry.insert(0, "0.00")
                
                # This code enables the calculation of total income vs total expenses to find current savings
                cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY type", (u_id,))
                totals = dict(cursor.fetchall())
                actual_income = totals.get('Income', 0.0)
                actual_expense = totals.get('Expense', 0.0)
                current_savings = actual_income - actual_expense
                
                # Update the displayed labels with the calculated financial figures
                self.expense_var.set(f"Total Expenses: ₱{actual_expense:,.2f}")
                self.savings_var.set(f"Current Savings: ₱{current_savings:,.2f}")
        except Exception as e: print(f"Error loading dashboard: {e}")
        
    # This function enables the user to update their monthly savings goal in the database
    def save_goal(self):
        u_id = getattr(self.controller, 'current_user_id', None)
        new_goal = self.goal_entry.get()
        if not u_id:
            messagebox.showerror("Error", "User not found. Please log in again.")
            return
        try:
            # This code enables the system to check if the entered goal is a valid number
            goal_value = float(new_goal)
            with sqlite3.connect("cashatan.db") as connection:
                cursor = connection.cursor()
                # This code enables the "Upsert" logic: inserts a new goal or updates the existing one
                query = """INSERT INTO budgets (user_id, savings_goal) 
                           VALUES (?, ?) 
                           ON CONFLICT(user_id) DO UPDATE SET savings_goal = excluded.savings_goal"""
                cursor.execute(query, (u_id, goal_value))
                connection.commit()
            messagebox.showinfo("Success", f"Budget Goal set to ₱{goal_value:,.2f}")
            # Refresh data to reflect any changes in balance logic
            self.load_data()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for your goal.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving goal: {e}")

# --- 4. FORM TEMPLATE (ADD EXPENSE/INCOME) ---
# This class defines the interface for users to record their spending
class AddExpensePage(tk.Frame):
    def __init__(self, parent, controller):
        # This code initializes the frame and connects it to the main controller
        super().__init__(parent)
        self.controller = controller
        # This code sets the background to the theme's deep navy
        self.configure(bg="#0B132B")

        # --- HEADER SECTION ---
        header_frame = tk.Frame(self, bg="#0B132B")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # This code displays the page title in bold white text
        tk.Label(header_frame, text="ADD EXPENSE", font=("Arial", 24, "bold"), 
                  bg="#0B132B", fg="white").pack()
        
        # This code creates a steel blue divider for visual separation
        tk.Frame(self, height=2, bg="#3A506B").pack(fill="x", padx=20, pady=(0, 40))

        # --- FORM CONTAINER ---
        # This code creates a central container to hold all input fields
        form_container = tk.Frame(self, bg="#0B132B")
        form_container.pack(expand=True)

        # These are the labels we need for the expense form
        fields = ["Date:", "Category:", "Amount:", "Notes:"]
        # This dictionary enables us to store and access the entry widgets by their field name
        self.entries = {} 
        categories = ["Food", "Transportation", "Bills", "Groceries", "Entertainment", "Health", "Others"]

        label_font = ("Arial", 12, "bold")

        # This loop enables the dynamic creation of labels and input widgets for each field
        for i, field in enumerate(fields):
            tk.Label(form_container, text=field, font=label_font, 
                      bg="#0B132B", fg="white").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            
            # This code creates a specialized calendar widget for date selection
            if field == "Date:":
                entry = DateEntry(form_container, width=28, font=("Arial", 12),
                                  background='#FF007F', foreground='#1C2541',
                                  borderwidth=1, relief="solid", date_pattern='y-mm-dd')
            
            # This code creates a dropdown menu (Combobox) for category selection
            elif field == "Category:":
                entry = ttk.Combobox(form_container, values=categories, width=28, 
                                      font=("Arial", 12), state="readonly")
                entry.set("Select Category") 
            
            # This code creates a multi-line text area for the Notes field
            elif field == "Notes:":
                entry = tk.Text(form_container, font=("Arial", 12), width=30, height=1,
                                 bg="#1C2541", fg="white", relief="solid",
                                 borderwidth=1, insertbackground="white")
                
            # This code creates a standard single-line entry for the Amount
            elif field == "Amount:":
                entry = tk.Entry(form_container, font=("Arial", 12), width=30, 
                                  bg="#1C2541", fg="#FF007F", relief="solid", 
                                  borderwidth=1, insertbackground="white")
            
            # This code places the widget in the grid and stores it in our dictionary
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            self.entries[field] = entry

        # --- FOOTER BUTTONS ---
        btn_frame = tk.Frame(self, bg="#0B132B")
        btn_frame.pack(side="bottom", pady=30)

        dark_btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#3A506B",     
            "fg": "white",
            "relief": "flat",
            "height": 2,
            "width": 20
        }

        # This code sets up the Save button and attaches the hover animation
        btn_saveExp = tk.Button(btn_frame, text="SAVE EXPENSE", command=self.save_to_db, **dark_btn_style)
        btn_saveExp.pack(side="left", padx=10)
        bind_hover(btn_saveExp, hover_color="#1C2541", normal_color="#3A506B")
        
        # This code sets up the Back button to navigate to the Dashboard
        btn_backToDsh = tk.Button(btn_frame, text="BACK TO DASHBOARD", command=lambda: controller.show_frame("DashboardPage"), **dark_btn_style)
        btn_backToDsh.pack(side="left", padx=10)
        bind_hover(btn_backToDsh, hover_color="#1C2541", normal_color="#3A506B")

    # This function enables the system to validate user input and save the expense to the database
    def save_to_db(self):
        # This code retrieves all information entered into the form
        date = self.entries["Date:"].get()
        category = self.entries["Category:"].get()
        amount = self.entries["Amount:"].get()
        # notes field uses "1.0" to tk.END because it is a multi-line Text widget
        notes = self.entries["Notes:"].get("1.0", tk.END).strip()
        # This code retrieves the session ID of the currently logged-in user
        u_id = getattr(self.controller, 'current_user_id', None) 
        
        # This code checks if a user session exists before allowing a save
        if u_id is None:
            messagebox.showerror("Error", "No user logged in!")
            return

        # This code ensures the user has selected a valid category from the list
        if category == "Select Category":
            messagebox.showwarning("Selection Required", "Please select a valid Category.")
            return

        # This code ensures that required fields (Date and Amount) are not left blank
        if not date or not amount:
            messagebox.showwarning("Input Error", "Please fill in the required fields.")
            return

        try:
            # This code connects to the database and executes the SQL INSERT command
            with sqlite3.connect("cashatan.db", timeout=10) as connection:
                cursor = connection.cursor()
                query = "INSERT INTO transactions (user_id, type, amount, category, date, notes) VALUES (?, ?, ?, ?, ?, ?)"
                # This code converts the 'amount' string into a number (float) before saving
                cursor.execute(query, (u_id, 'Expense', float(amount), category, date, notes))
                connection.commit()

            messagebox.showinfo("Success", "Expense saved successfully!")
            # This code triggers the reset function to prepare the form for a new entry
            self.clear_entries()
        except ValueError:
            # This code enables the system to catch errors if the user types letters into the Amount box
            messagebox.showerror("Error", "Amount must be a number.")

    # This function enables the system to wipe the form clean after a successful save
    def clear_entries(self):
        """Resets the form without crashing on the multi-line Notes field."""
        for field, widget in self.entries.items():
            # This code resets dropdowns to their default placeholder text
            if field == "Category:" or field == "Source:":
                widget.set("Select " + field[:-1])
            # This code handles the specific deletion method for the multi-line Text widget
            elif field == "Notes:":
                widget.delete("1.0", tk.END)
            # This code clears standard entry boxes while leaving the Date as is
            elif field != "Date:":
                widget.delete(0, tk.END)


# This class follows the same logic as AddExpense but targets 'Income' transactions
class AddIncomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#0B132B")

        # --- HEADER SECTION ---
        header_frame = tk.Frame(self, bg="#0B132B")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(header_frame, text="ADD INCOME", font=("Arial", 24, "bold"), 
                  bg="#0B132B", fg="white").pack()
        
        tk.Frame(self, height=2, bg="#3A506B").pack(fill="x", padx=20, pady=(0, 40))

        # --- FORM CONTAINER ---
        form_container = tk.Frame(self, bg="#0B132B")
        form_container.pack(expand=True)

        fields = ["Date:", "Source:", "Amount:", "Notes:"]
        self.entries = {} 
        income_sources = ["Salary", "Freelance", "Allowance", "Gift", "Investment", "Others"]

        label_font = ("Arial", 12, "bold")

        # This loop enables the consistent setup of form fields (Date, Source, Amount, Notes)
        for i, field in enumerate(fields):
            tk.Label(form_container, text=field, font=label_font, 
                      bg="#0B132B", fg="white").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            
            # This code enables a Green highlight for Income dates to contrast with Expense pages
            if field == "Date:":
                entry = DateEntry(form_container, width=28, font=("Arial", 12), 
                                  background='#7ED321', foreground='white', 
                                  borderwidth=1, relief="solid", date_pattern='y-mm-dd')
            
            elif field == "Source:":
                entry = ttk.Combobox(form_container, values=income_sources, width=28, 
                                      font=("Arial", 12), state="readonly")
                entry.set("Select Source")
            
            # Amount field for Income
            elif field == "Amount:":
                entry = tk.Entry(form_container, font=("Arial", 12), width=30, 
                                  bg="#1C2541", fg="#7ED321", relief="solid", 
                                  borderwidth=1, insertbackground="white")
            
            # Notes field for Income
            elif field == "Notes:":
                    entry = tk.Text(form_container, font=("Arial", 12), width=30, height=1,
                                     bg="#1C2541", fg="white", relief="solid",
                                     borderwidth=1, insertbackground="white")
            
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            self.entries[field] = entry

        # --- FOOTER BUTTONS ---
        btn_frame = tk.Frame(self, bg="#0B132B")
        btn_frame.pack(side="bottom", pady=30) 

        dark_btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#3A506B",     
            "fg": "white",
            "relief": "flat",
            "height": 2,
            "width": 20
        }

        # Save button for Income logic
        btn_saveInc = tk.Button(btn_frame, text="SAVE INCOME", command=self.save_income_to_db, **dark_btn_style)
        btn_saveInc.pack(side="left", padx=10)
        bind_hover(btn_saveInc, hover_color="#1C2541", normal_color="#3A506B")
        
        # Back button
        btn_backToDsh = tk.Button(btn_frame, text="BACK TO DASHBOARD", command=lambda: controller.show_frame("DashboardPage"), **dark_btn_style)
        btn_backToDsh.pack(side="left", padx=10)
        bind_hover(btn_backToDsh, hover_color="#1C2541", normal_color="#3A506B")

    # This function enables the system to save Income records into the same 'transactions' table
    def save_income_to_db(self):
        # Retrieve values from widgets
        date = self.entries["Date:"].get()
        source = self.entries["Source:"].get()
        amount = self.entries["Amount:"].get()
        notes = self.entries["Notes:"].get("1.0", tk.END).strip()
        u_id = getattr(self.controller, 'current_user_id', None) 
        
        if u_id is None:
            messagebox.showerror("Error", "No user logged in!")
            return

        # Selection validation
        if source == "Select Source":
            messagebox.showwarning("Selection Required", "Please select a valid Income Source.")
            return

        # Blank field validation
        if not date or not amount:
            messagebox.showwarning("Input Error", "Please fill in Date and Amount.")
            return

        try:
            # This code creates the connection and records the transaction as 'Income' type
            with sqlite3.connect("cashatan.db", timeout=10) as connection:
                cursor = connection.cursor()
                query = "INSERT INTO transactions (user_id, type, amount, category, date, notes) VALUES (?, ?, ?, ?, ?, ?)"
                # We reuse the 'category' column to store the 'source' for income
                cursor.execute(query, (u_id, 'Income', float(amount), source, date, notes))
                connection.commit()

            messagebox.showinfo("Success", "Income added successfully!")
            self.clear_entries()
        except ValueError:
            # Data type validation
            messagebox.showerror("Error", "Amount must be a number.")

    # This function resets the form by calling the same logic as AddExpensePage
    def clear_entries(self):
        """Resets the form without crashing on the multi-line Notes field."""
        for field, widget in self.entries.items():
            if field == "Category:" or field == "Source:":
                widget.set("Select " + field[:-1])
            elif field == "Notes:":
                widget.delete("1.0", tk.END)      
            elif field != "Date:":
                widget.delete(0, tk.END)

# --- 5. DATA TABLE TEMPLATE (VIEW TRANSACTIONS) ---
# This class enables the user to see, delete, and modify their transaction history in a table format
class ViewTransactionsPage(tk.Frame):
    def __init__(self, parent, controller):
        # This code initializes the page and links it to the main application controller
        super().__init__(parent)
        self.controller = controller
        # This code sets the background to the theme's deepest navy color
        self.config(bg="#0B132B") 
        
        # This code displays the page title at the top
        tk.Label(self, text="VIEW TRANSACTIONS", font=("Arial", 26, "bold"), 
                  bg="#0B132B", fg="white").pack(pady=(20, 10))
        
        # This code draws a decorative divider line
        tk.Frame(self, height=2, bg="#3A506B").pack(fill="x", padx=20)

        # --- UI STYLE: DARK THEME TREEVIEW ---
        # This code enables the customization of the table's visual appearance
        style = ttk.Style()
        style.theme_use("clam") 
        
        # This code styles the table headers with the theme's steel blue color
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), 
                        background="#3A506B", foreground="white", 
                        borderwidth=1, relief="solid")
        
        # This code sets the font and row height for the data inside the table
        style.configure("Treeview", font=("Arial", 11), rowheight=35, 
                        background="#1C2541", fieldbackground="#1C2541", 
                        foreground="white", borderwidth=1, relief="solid")
        
        # This code changes the color of a row when a user clicks on it
        style.map("Treeview", background=[('selected', '#3A506B')])

        # 1. Table Setup
        # This code defines the columns that will be stored in the table
        cols = ("ID", "Type", "Date", "Category", "Amount", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", style="Treeview")
        
        # This code creates color "tags" to distinguish between Income (Green) and Expense (Pink)
        self.tree.tag_configure('income_even', background="#0B132B", foreground="#7ED321")
        self.tree.tag_configure('income_odd', background="#1C2541", foreground="#7ED321")
        self.tree.tag_configure('expense_even', background="#0B132B", foreground="#FF007F")
        self.tree.tag_configure('expense_odd', background="#1C2541", foreground="#FF007F")

        # This code enables the text labels for the column headers
        self.tree.heading("Type", text="Type")
        self.tree.heading("Date", text="Date:")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Notes", text="Notes")

        # This code sets the width and text alignment for each column
        self.tree.column("Type", width=100, anchor="center")
        self.tree.column("Date", width=120, anchor="center")
        self.tree.column("Category", width=150, anchor="center")
        self.tree.column("Amount", width=100, anchor="center")
        self.tree.column("Notes", width=250, anchor="center")

        # This code enables the table to hide the database ID while still keeping it for logic purposes
        self.tree["displaycolumns"] = ("Type", "Date", "Category", "Amount", "Notes")
        self.tree.pack(fill="both", expand=True, padx=30, pady=10)
        
        # --- FOOTER BUTTONS ---
        # This code creates a container for the action buttons at the bottom
        btn_frame = tk.Frame(self, bg="#0B132B")
        btn_frame.pack(pady=30)
        
        base_btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#3A506B",
            "relief": "flat",
            "height": 2,
            "width": 22 
        }
        
        # This code creates the Delete button with a red text warning
        btn_del = tk.Button(btn_frame, text="DELETE", fg="#FF1F1F", 
                  command=self.delete_transaction, **base_btn_style)
        btn_del.pack(side="left", padx=10)
        bind_hover(btn_del, hover_color="#1C2541", normal_color="#3A506B")
        
        # This code creates the Edit button
        btn_edit = tk.Button(btn_frame, text="EDIT", fg="white", 
                  command=self.edit_transaction, **base_btn_style)
        btn_edit.pack(side="left", padx=10)
        bind_hover(btn_edit, hover_color="#1C2541", normal_color="#3A506B")

        # This code creates the Back button to navigate to the dashboard
        btn_backToDsh = tk.Button(btn_frame, text="BACK TO DASHBOARD", fg="white",
                  command=lambda: controller.show_frame("DashboardPage"), **base_btn_style)
        btn_backToDsh.pack(side="left", padx=10)
        bind_hover(btn_backToDsh, hover_color="#1C2541", normal_color="#3A506B")

    # This function enables the table to fetch and display the latest data from the database
    def load_data(self):
        # This code clears the table before reloading to prevent duplicate rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # This code ensures only the transactions of the logged-in user are shown
        u_id = getattr(self.controller, 'current_user_id', None)
        if u_id is None: return

        try:
            # This code connects to the database and fetches all transactions sorted by date
            with sqlite3.connect("cashatan.db") as conn:
                cursor = conn.cursor()
                query = "SELECT transaction_id, type, date, category, amount, notes FROM transactions WHERE user_id = ? ORDER BY date DESC"
                cursor.execute(query, (u_id,))
                
                # This code enables zebra-striping and color-coding while inserting data into the table
                for i, row in enumerate(cursor.fetchall()):
                    t_type = row[1]
                    is_even = (i % 2 == 0)
                    
                    # This code applies the color tags based on whether the row is Income or Expense
                    if t_type == 'Income':
                        tag = 'income_even' if is_even else 'income_odd'
                    else:
                        tag = 'expense_even' if is_even else 'expense_odd'
                    
                    # This code inserts the row into the visual table with the correct styling
                    self.tree.insert("", "end", values=row, tags=(tag,))
                        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Could not load data: {e}")

    # This function enables the system to permanently remove a selected transaction record
    def delete_transaction(self):
        # This code identifies which row the user has selected
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection", "Please select a row to delete.")
            return

        # This code displays a confirmation box to prevent accidental deletions
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            # This code retrieves the unique Database ID of the selected transaction
            t_id = self.tree.item(selected_item)['values'][0]
            with sqlite3.connect("cashatan.db") as conn:
                # This code executes the SQL DELETE command
                conn.execute("DELETE FROM transactions WHERE transaction_id = ?", (t_id,))
            # This code refreshes the table so the deleted record disappears
            self.load_data()

    # This function enables a popup window to edit the details of an existing transaction
    def edit_transaction(self):
        # This code checks if a row is selected before opening the edit window
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection", "Please select a row to edit.")
            return

        # This code pulls the current values from the table to pre-fill the edit form
        item_data = self.tree.item(selected_item)['values']
        t_id, t_type, t_date, t_cat, t_amt, t_notes = item_data

        # This code creates a new "top-level" window for the edit form
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Transaction")
        edit_win.geometry("400x450")
        edit_win.config(bg="#0B132B")

        # This code displays which transaction type is being edited
        tk.Label(edit_win, text=f"EDITING {t_type.upper()}", font=("Arial", 14, "bold"), 
                  bg="#0B132B", fg="white").pack(pady=20)

        # This code creates a container for the input fields in the popup
        fields_frame = tk.Frame(edit_win, bg="#0B132B")
        fields_frame.pack(pady=10)

        label_font = ("Arial", 10, "bold")

        # This code sets up the Date input field in the popup
        tk.Label(fields_frame, text="Date:", bg="#0B132B", fg="white", font=label_font).grid(row=0, column=0, pady=8, padx=5, sticky="e")
        ent_date = DateEntry(fields_frame, width=20, date_pattern='y-mm-dd', background="#3A506B")
        ent_date.set_date(t_date) 
        ent_date.grid(row=0, column=1, pady=8)

        # --- DYNAMIC CATEGORY LOGIC ---
        # This code enables the system to show relevant categories based on the transaction type
        tk.Label(fields_frame, text="Category/Source:", bg="#0B132B", fg="white", font=label_font).grid(row=1, column=0, pady=8, padx=5, sticky="e")
        
        # This code checks if the transaction is Income or Expense to load the correct list
        if t_type == "Income":
            categories = ["Allowance", "Salary", "Gift", "Investment", "Others"]
        else: # Expense
            categories = ["Food", "Transport", "Bills", "Groceries", "Rent", "Others"]

        ent_cat = ttk.Combobox(fields_frame, values=categories, width=21, state="readonly")
        ent_cat.set(t_cat) 
        ent_cat.grid(row=1, column=1, pady=8)

        # This code sets up the Amount input field in the popup
        tk.Label(fields_frame, text="Amount:", bg="#0B132B", fg="white", font=label_font).grid(row=2, column=0, pady=8, padx=5, sticky="e")
        ent_amt = tk.Entry(fields_frame, width=23, relief="solid", bg="#1C2541", fg="white", insertbackground="white")
        ent_amt.insert(0, t_amt) 
        ent_amt.grid(row=2, column=1, pady=8)

        # This code sets up the Notes input field in the popup
        tk.Label(fields_frame, text="Notes:", bg="#0B132B", fg="white", font=label_font).grid(row=3, column=0, pady=8, padx=5, sticky="e")
        ent_notes = tk.Entry(fields_frame, width=23, relief="solid", bg="#1C2541", fg="white", insertbackground="white")
        ent_notes.insert(0, t_notes) 
        ent_notes.grid(row=3, column=1, pady=8)

        # This internal function enables the saving of updated information back to the database
        def save_changes():
            try:
                # This code retrieves the new values from the edit form
                new_date = ent_date.get()
                new_cat = ent_cat.get()
                new_amt = float(ent_amt.get())
                new_notes = ent_notes.get()

                # This code executes the SQL UPDATE command to modify the record in the database
                with sqlite3.connect("cashatan.db") as conn:
                    query = "UPDATE transactions SET date=?, category=?, amount=?, notes=? WHERE transaction_id=?"
                    conn.execute(query, (new_date, new_cat, new_amt, new_notes, t_id))
                
                # This code closes the popup and refreshes the main table upon success
                messagebox.showinfo("Success", "Transaction updated!")
                edit_win.destroy()
                self.load_data() 
            except ValueError:
                # This code catches errors if the user enters letters instead of numbers for the amount
                messagebox.showerror("Error", "Amount must be a number.")

        # This code creates the button to finalize the edit
        btn_saveChanges = tk.Button(edit_win, text="SAVE CHANGES", width=20, 
                  font=("Arial", 11, "bold"), bg="#3A506B", fg="white", 
                  relief="flat", command=save_changes)
        btn_saveChanges.pack(pady=30)
        # This code applies the hover animation to the popup button
        bind_hover(btn_saveChanges, hover_color="#1C2541", normal_color="#3A506B")

# --- 6. SUMMARY TEMPLATE (BUDGET OVERVIEW) ---
# This class acts as the "Analytical Hub" where data is turned into visual charts and progress bars
class BudgetOverviewPage(tk.Frame):
    def __init__(self, parent, controller):
        # This code enables the page to be initialized and linked to the main app controller
        super().__init__(parent)
        self.controller = controller
        # This code enables the application to apply the consistent dark navy theme
        self.config(bg="#0B132B")

        # --- HEADER SECTION ---
        header_frame = tk.Frame(self, bg="#0B132B")
        header_frame.pack(fill="x", padx=20, pady=10)

        user_info = tk.Frame(header_frame, bg="#0B132B")
        user_info.pack(side="left")
        
        # This code enables a dedicated space for the circular profile image
        self.canvas_user = tk.Canvas(user_info, width=40, height=40, bg="#0B132B", highlightthickness=0)
        self.canvas_user.pack(side="left")
        
        # This code enables the display of the current user's name in the header
        self.lbl_username = tk.Label(user_info, text="username", font=("Arial", 14), bg="#0B132B", fg="white")
        self.lbl_username.pack(side="left", padx=10)

        # This code enables the main title and current date to be displayed at the top
        tk.Label(header_frame, text="BUDGET OVERVIEW", font=("Arial", 28, "bold"), bg="#0B132B", fg="white").place(relx=0.5, anchor="n")
        tk.Label(header_frame, text=date.today().strftime("%m/%d/%Y"), font=("Arial", 14), bg="#0B132B", fg="white").pack(side="right")

        # This code enables a visual separation between the header and the data area
        tk.Frame(self, height=2, bg="#3A506B").pack(fill="x", padx=20)

        # --- MAIN CONTENT AREA ---
        content_frame = tk.Frame(self, bg="#0B132B")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        # This code enables a 2-column layout for the dashboard analytics
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        # BOXES (Stats, Summary, Progress)
        # This code enables a card-like container for high-level financial statistics
        stats_box = tk.Frame(content_frame, bg="#1C2541", padx=15, pady=15, relief="solid", borderwidth=1)
        stats_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        # These labels enable the display of monthly totals and goals fetched from the database
        self.lbl_monthly_inc = tk.Label(stats_box, text="Monthly Income: ₱0", font=("Arial", 11, "bold"), bg="#0B132B", fg="white", relief="solid", borderwidth=1, anchor="w", padx=5)
        self.lbl_monthly_inc.pack(fill="x", pady=2)
        self.lbl_savings_goal = tk.Label(stats_box, text="Savings Goal: ₱0", font=("Arial", 11, "bold"), bg="#0B132B", fg="white", relief="solid", borderwidth=1, anchor="w", padx=5)
        self.lbl_savings_goal.pack(fill="x", pady=2)
        self.lbl_avail_exp = tk.Label(stats_box, text="Available for Expenses: ₱0", font=("Arial", 11, "bold"), bg="#3A506B", fg="white", relief="solid", borderwidth=1, anchor="w", padx=5)
        self.lbl_avail_exp.pack(fill="x", pady=2)

        # This code enables the organization of the Expense Summary and Progress Gauge in the top right
        top_right_container = tk.Frame(content_frame, bg="#0B132B")
        top_right_container.grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        top_right_container.columnconfigure(0, weight=1)
        top_right_container.columnconfigure(1, weight=1)

        summary_box = tk.Frame(top_right_container, bg="#1C2541", relief="solid", borderwidth=1, padx=10, pady=5)
        summary_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        tk.Label(summary_box, text="Expense Summary", font=("Arial", 11, "bold"), bg="#3A506B", fg="white", relief="solid", borderwidth=1).pack(fill="x", pady=(0, 5))
        self.lbl_total_exp = tk.Label(summary_box, text="Total Expenses: ₱0", bg="#1C2541", fg="white", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_total_exp.pack(fill="x", pady=5)
        self.lbl_remain_bud = tk.Label(summary_box, text="Remaining Budget: ₱0", bg="#1C2541", fg="white", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_remain_bud.pack(fill="x", pady=5)

        # This code enables the circular Progress Gauge to show how close the user is to their savings goal
        progress_box = tk.Frame(top_right_container, bg="#1C2541", relief="solid", borderwidth=1, padx=10, pady=5)
        progress_box.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        tk.Label(progress_box, text="Savings Progress", font=("Arial", 11, "bold"), bg="#3A506B", fg="white", relief="solid", borderwidth=1).pack(fill="x", pady=(0, 5))
        
        self.gauge_canvas = tk.Canvas(progress_box, width=80, height=80, bg="#1C2541", highlightthickness=0)
        self.gauge_canvas.pack(side="left")
        self.lbl_progress_text = tk.Label(progress_box, text="0% of Goal\nAchieved", font=("Arial", 10, "bold"), bg="#1C2541", fg="white", justify="left")
        self.lbl_progress_text.pack(side="left", padx=5)

        # BREAKDOWNS
        # This code enables a detailed list of where money came from and where it went
        breakdown_container = tk.Frame(content_frame, bg="#0B132B")
        breakdown_container.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        self.expense_box = tk.Frame(breakdown_container, bg="#1C2541", relief="solid", borderwidth=1)
        self.expense_box.pack(fill="both", expand=True, pady=(0, 5))
        tk.Label(self.expense_box, text="Expense Breakdown", font=("Arial", 11, "bold"), bg="#3A506B", fg="white", relief="solid", borderwidth=1).pack(fill="x")
        self.expense_rows = tk.Frame(self.expense_box, bg="#1C2541")
        self.expense_rows.pack(fill="both", expand=True)

        self.income_box = tk.Frame(breakdown_container, bg="#1C2541", relief="solid", borderwidth=1)
        self.income_box.pack(fill="both", expand=True, pady=(5, 0))
        tk.Label(self.income_box, text="Income Breakdown", font=("Arial", 11, "bold"), bg="#3A506B", fg="white", relief="solid", borderwidth=1).pack(fill="x")
        self.income_rows = tk.Frame(self.income_box, bg="#1C2541")
        self.income_rows.pack(fill="both", expand=True)

        # CHARTS
        # This code enables the rendering of a custom-drawn Pie Chart and Line Graph
        charts_box = tk.Frame(content_frame, bg="#1C2541", relief="solid", borderwidth=1)
        charts_box.grid(row=1, column=1, sticky="nsew") 
        tk.Label(charts_box, text="Expenses Analytics", font=("Arial", 11, "bold"), bg="#3A506B", fg="white", relief="solid", borderwidth=1).pack(fill="x")
        
        charts_inner = tk.Frame(charts_box, bg="#1C2541", padx=10, pady=10)
        charts_inner.pack(fill="both", expand=True)
        self.chart_canvas = tk.Canvas(charts_inner, bg="#1C2541", highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)
        # This code enables the charts to redraw themselves if the window is resized
        self.chart_canvas.bind("<Configure>", lambda event: self.load_data())

        # FOOTER
        footer_frame = tk.Frame(self, bg="#0B132B")
        footer_frame.pack(side="bottom", pady=20)
        dark_btn_style = {"font": ("Arial", 11, "bold"), "bg": "#3A506B", "fg": "white", "relief": "flat", "height": 2, "width": 20}

        # These buttons enable quick navigation to entry forms or the dashboard
        tk.Button(footer_frame, text="ADD INCOME", command=lambda: controller.show_frame("AddIncomePage"), **dark_btn_style).pack(side="left", padx=10)
        tk.Button(footer_frame, text="ADD EXPENSE", command=lambda: controller.show_frame("AddExpensePage"), **dark_btn_style).pack(side="left", padx=10)
        tk.Button(footer_frame, text="BACK TO DASHBOARD", command=lambda: controller.show_frame("DashboardPage"), **dark_btn_style).pack(side="left", padx=10)

    # This function enables the calculation of all financial data and the drawing of all charts
    def load_data(self):
        # This code retrieves the current user session ID
        u_id = getattr(self.controller, 'current_user_id', None)
        if not u_id: return

        # This code enables the application to calculate exact pixel dimensions before drawing graphics
        self.update_idletasks()
        canvas_w = self.chart_canvas.winfo_width()
        if canvas_w < 10: canvas_w = 450 

        # This code clears the profile canvas to prepare for a fresh image render
        self.canvas_user.delete("all")
        self.canvas_user.create_oval(5, 5, 35, 35, fill="#3A506B", outline="white")

        try:
            # This code enables the connection to the database to pull real-time financial records
            with sqlite3.connect("cashatan.db") as connection:
                cursor = connection.cursor()
                
                # --- 1. USER PROFILE (CIRCLE FIX) ---
                # This code enables the system to fetch the user's profile picture and crop it into a circle
                cursor.execute("SELECT username, profile_pic FROM users WHERE user_id=?", (u_id,))
                user = cursor.fetchone()
                if user:
                    self.lbl_username.config(text=user[0])
                    if user[1]:
                        try:
                            size = (32, 32)
                            img = Image.open(user[1]).convert("RGBA")
                            # This code enables the circular cropping logic using an Image Mask
                            img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
                            mask = Image.new('L', size, 0)
                            draw = ImageDraw.Draw(mask)
                            draw.ellipse((0, 0, size[0], size[1]), fill=255)
                            img.putalpha(mask)
                            self.profile_photo = ImageTk.PhotoImage(img)
                            self.canvas_user.create_image(20, 20, image=self.profile_photo)
                        except Exception as e:
                            print(f"Image Load Error: {e}")

                # --- 2. FINANCIAL CALCULATIONS ---
                # This code enables the retrieval of the user's monthly goal
                cursor.execute("SELECT savings_goal FROM budgets WHERE user_id=?", (u_id,))
                goal_data = cursor.fetchone()
                goal = goal_data[0] if goal_data else 0.0
                
                # This code enables the calculation of Total Income and Total Expenses using SQL SUM
                cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id=? GROUP BY type", (u_id,))
                totals = dict(cursor.fetchall())
                total_income = totals.get('Income', 0.0)
                total_expenses = totals.get('Expense', 0.0)

                # This code enables the calculation of the available balance and savings percentage
                avail_for_exp = total_income - total_expenses
                progress_pct = (avail_for_exp / goal * 100) if goal > 0 else 0
                # This code ensures the progress percentage stays between 0 and 100 for the UI
                progress_pct = max(0, min(progress_pct, 100))

                # This code enables the updating of all visual labels with formatted currency figures
                self.lbl_monthly_inc.config(text=f"Total Monthly Income: ₱{total_income:,.2f}")
                self.lbl_savings_goal.config(text=f"Monthly Savings Goal: ₱{goal:,.2f}")
                self.lbl_avail_exp.config(text=f"Available for Expenses: ₱{avail_for_exp:,.2f}")
                self.lbl_total_exp.config(text=f"Total Expenses: ₱{total_expenses:,.2f}")
                self.lbl_remain_bud.config(text=f"Remaining Budget: ₱{avail_for_exp:,.2f}")

                # --- 3. BREAKDOWNS ---
                # This code enables the list of expense categories to be dynamically updated
                for w in self.expense_rows.winfo_children(): w.destroy()
                cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE user_id=? AND type='Expense' GROUP BY category", (u_id,))
                exp_cats = cursor.fetchall()
                for cat, amt in exp_cats:
                    row = tk.Frame(self.expense_rows, bg="#1C2541")
                    row.pack(fill="x", padx=10, pady=2)
                    tk.Label(row, text=cat, bg="#1C2541", fg="white").pack(side="left")
                    tk.Label(row, text=f"₱{amt:,.0f}", bg="#1C2541", fg="#00FFCC", font=("Arial", 10, "bold")).pack(side="right")

                # This code enables the list of income sources to be dynamically updated
                for w in self.income_rows.winfo_children(): w.destroy()
                cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE user_id=? AND type='Income' GROUP BY category", (u_id,))
                for src, amt in cursor.fetchall():
                    row = tk.Frame(self.income_rows, bg="#1C2541")
                    row.pack(fill="x", padx=10, pady=2)
                    tk.Label(row, text=src, bg="#1C2541", fg="white").pack(side="left")
                    tk.Label(row, text=f"₱{amt:,.0f}", bg="#1C2541", fg="#7ED321", font=("Arial", 10, "bold")).pack(side="right")

                # --- 4. PROGRESS GAUGE ---
                # This code enables the drawing of a neon orange progress arc on the canvas
                self.gauge_canvas.delete("all")
                self.gauge_canvas.create_oval(10, 10, 70, 70, outline="#3A506B", width=4)
                # Mathematical formula to convert percentage into a circle's degree (360 degrees)
                extent = -(progress_pct / 100) * 359.9
                self.gauge_canvas.create_arc(10, 10, 70, 70, start=90, extent=extent, outline="#FF9F1C", width=5, style="arc")
                self.gauge_canvas.create_text(40, 40, text=f"{int(progress_pct)}%", font=("Arial", 10, "bold"), fill="white")
                self.lbl_progress_text.config(text=f"{int(progress_pct)}% of Goal\nAchieved")

                # --- 5. GRAPHS & CHARTS ---
                # This code enables the rendering of the analytical charts using pixel coordinates
                self.chart_canvas.delete("all")
                canvas_h = self.chart_canvas.winfo_height()
                if canvas_h <= 1: canvas_h = 300

                # These math variables enable the charts to remain centered regardless of window size
                pie_cx, pie_cy = canvas_w * 0.70, canvas_h * 0.45 
                pie_r = min(canvas_w * 0.10, canvas_h * 0.20)
                title_y = canvas_h * 0.10
                line_x_start, line_x_end = canvas_w * 0.05, canvas_w * 0.45
                line_y_bottom, line_y_top = canvas_h * 0.85, canvas_h * 0.25

                # This code enables the text titles for the analytical section
                title_font = ("Arial", 10, "bold")
                self.chart_canvas.create_text((line_x_start + line_x_end) / 2, title_y, text="Expenses Over Time", font=title_font, fill="white")
                self.chart_canvas.create_text(pie_cx, title_y, text="Expenses Categories", font=title_font, fill="white")

                vibrant_colors = ["#00FFCC", "#FF007F", "#7ED321", "#FFD700", "#BD10E0", "#50E3C2", "#F5A623"]

                # PIE CHART LOGIC
                # This code enables the creation of a multi-colored pie chart based on spending categories
                if total_expenses > 0:
                    start_ang = 90
                    for i, (cat, amt) in enumerate(exp_cats):
                        # This code enables the calculation of each pie slice's size
                        extent = -(amt / total_expenses) * 359.9
                        color = vibrant_colors[i % len(vibrant_colors)]
                        self.chart_canvas.create_arc(pie_cx - pie_r, pie_cy - pie_r, pie_cx + pie_r, pie_cy + pie_r, 
                                                     start=start_ang, extent=extent, fill=color, outline="#1C2541")
                        
                        # Legend logic
                        lx, ly = pie_cx + pie_r + 20, (pie_cy - pie_r) + (i * 20)
                        self.chart_canvas.create_rectangle(lx, ly, lx + 10, ly + 10, fill=color, outline="white")
                        self.chart_canvas.create_text(lx + 15, ly + 5, text=cat, font=("Arial", 8, "bold"), anchor="w", fill="white")
                        start_ang += extent

                # LINE CHART LOGIC
                # This code enables the tracking of spending trends across the last 5 transactions
                cursor.execute("SELECT date, amount FROM transactions WHERE user_id=? AND type='Expense' ORDER BY date DESC LIMIT 5", (u_id,))
                data_points = cursor.fetchall()[::-1]
                if data_points:
                    # This code enables the scaling of data points so the line stays within the chart boundaries
                    max_v = max(float(d[1]) for d in data_points) if data_points else 1
                    pts = []
                    spacing = (line_x_end - line_x_start) / 4 
                    for i, (t_date, val) in enumerate(data_points):
                        x = line_x_start + (i * spacing)
                        y = line_y_bottom - (float(val) / (max_v if max_v > 0 else 1) * (line_y_bottom - line_y_top))
                        pts.extend([x, y])
                    if len(pts) > 2:
                        # This code enables the drawing of a smooth neon blue line connecting the data points
                        self.chart_canvas.create_line(pts, width=3, fill="#00E5FF", smooth=True) 
                
                # This code enables the drawing of the X and Y axes for the line graph
                self.chart_canvas.create_line(line_x_start - 5, line_y_bottom, line_x_end + 10, line_y_bottom, fill="white") 
                self.chart_canvas.create_line(line_x_start - 5, line_y_top, line_x_start - 5, line_y_bottom, fill="white")

        except Exception as e:
            # This code enables error reporting if the data load fails
            print(f"Error updating Overview: {e}")

# ==========================================
# 4. START THE APP
# ==========================================
# This code enables the script to check if it is being run directly as the main program
if __name__ == "__main__":
    # This code enables the system to prepare the database and tables before the UI opens
    init_db()
    
    # This code enables the creation of the main application window object
    app = CashAtanApp()
    
    # This code enables the application to stay running and listen for user inputs like clicks
    app.mainloop()
