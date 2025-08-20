import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import random
import string
import datetime
import csv
import re
from PIL import Image, ImageTk
from fpdf import FPDF

# ---------------- DB CONNECTION ----------------
# --- IMPORTANT ---
# Replace with your actual MySQL database credentials.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # <-- Set your MySQL password here
    "database": "railway_system"  # <-- Your database name
}

SEATS_PER_COACH = 72  # Change this if your coach size differs

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None

# ---------------- DATABASE UTILITIES ----------------
def db_execute(query, params=(), fetch=None):
    """
    Executes a database query and returns the result.
    'fetch' can be 'one', 'all', or None for commit.
    """
    conn = get_db_connection()
    if not conn:
        return None if fetch else False

    result = None
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'all':
                result = cursor.fetchall()
            else:
                conn.commit()
                result = True
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if fetch:
            return None
        return False
    finally:
        if conn.is_connected():
            conn.close()
    return result

# ---------------- GENERAL UTILITIES ----------------
def generate_pnr():
    """Generates a random 8-character PNR."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def is_int(s):
    """Checks if a string can be converted to an integer."""
    try:
        int(s)
        return True
    except (ValueError, TypeError):
        return False

def parse_id_from_combo(text):
    """Extracts the ID from a 'ID - Name' formatted string."""
    try:
        return int(text.split(" - ")[0])
    except (ValueError, IndexError):
        return None

# ---------------- DATA LOOKUPS ----------------
def get_station_name_by_id(station_id):
    """Fetches a station name by its ID."""
    row = db_execute("SELECT station_name FROM stations WHERE station_id=%s", (station_id,), fetch='one')
    return row[0] if row else str(station_id)

def get_train_name_by_id(train_id):
    """Fetches a train name by its ID."""
    row = db_execute("SELECT train_name FROM trains WHERE train_id=%s", (train_id,), fetch='one')
    return row[0] if row else str(train_id)

def get_stations_for_combobox():
    """Fetches all stations for combobox display."""
    rows = db_execute("SELECT station_id, station_name FROM stations ORDER BY station_name", fetch='all')
    return [f"{r[0]} - {r[1]}" for r in rows] if rows else []

def get_trains_for_combobox():
    """Fetches all trains for combobox display."""
    rows = db_execute("SELECT train_id, train_name FROM trains ORDER BY train_name", fetch='all')
    return [f"{r[0]} - {r[1]}" for r in rows] if rows else []

def search_trains_between_stations(from_station_id, to_station_id):
    """
    Finds all trains that travel from a given station to a destination station.
    Ensures the 'from' station appears before the 'to' station in the schedule.
    """
    query = """
    SELECT
        t.train_id,
        t.train_name,
        t.train_type,
        s1.departure_time,
        s2.arrival_time
    FROM trains AS t
    JOIN train_schedule AS s1 ON t.train_id = s1.train_id
    JOIN train_schedule AS s2 ON t.train_id = s2.train_id
    WHERE
        s1.station_id = %s AND
        s2.station_id = %s AND
        s1.sequence < s2.sequence
    GROUP BY t.train_id, t.train_name, t.train_type, s1.departure_time, s2.arrival_time
    """
    return db_execute(query, (from_station_id, to_station_id), fetch='all')

# ---------------- SEAT ALLOCATION LOGIC ----------------
def get_next_available_seat(train_id):
    """
    Calculates and returns the next available seat string (e.g., 'S1-23').
    Returns None if the train is full.
    """
    train_info = db_execute("SELECT total_seats FROM trains WHERE train_id=%s", (train_id,), fetch='one')
    if not train_info:
        return None
    total_seats = train_info[0]

    tickets = db_execute("SELECT seat_number FROM tickets WHERE train_id=%s AND status='Confirmed'", (train_id,), fetch='all')
    if tickets is None:
        return None # DB Error

    used_seats = set()
    seat_pattern = re.compile(r"^S(\d+)-(\d+)$", re.IGNORECASE)

    for (seat_num,) in tickets:
        if not seat_num:
            continue
        match = seat_pattern.match(str(seat_num).strip())
        if match:
            coach = int(match.group(1))
            seat_in_coach = int(match.group(2))
            linear_seat = (coach - 1) * SEATS_PER_COACH + seat_in_coach
            used_seats.add(linear_seat)

    for n in range(1, total_seats + 1):
        if n not in used_seats:
            coach_no = (n - 1) // SEATS_PER_COACH + 1
            seat_in_coach = (n - 1) % SEATS_PER_COACH + 1
            return f"S{coach_no}-{seat_in_coach}"

    return None # Train is full

# ---------------- BASE WINDOW CLASS ----------------
class BaseWindow(tk.Toplevel):
    """Base class for all application windows to ensure consistent styling."""
    def __init__(self, title, geometry):
        super().__init__()
        self.title(title)
        self.geometry(geometry)
        self.configure(bg="#2c3e50") # Dark blue background
        self.center_window()

    def center_window(self):
        """Centers the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

# ---------------- STYLED WIDGETS ----------------
def create_styled_button(parent, text, command, style="TButton"):
    """Creates a styled button."""
    return ttk.Button(parent, text=text, command=command, style=style, width=20)

def create_styled_entry(parent, show=None):
    """Creates a styled entry widget."""
    return ttk.Entry(parent, show=show, font=('Segoe UI', 10))

def create_styled_label(parent, text):
    """Creates a styled label."""
    return ttk.Label(parent, text=text, font=('Segoe UI', 10))

def setup_styles():
    """Sets up modern ttk styles for the application."""
    style = ttk.Style()
    style.theme_use('clam')

    # Define colors
    BG_COLOR = "#2c3e50"
    FG_COLOR = "#ecf0f1"
    HEADER_COLOR = "#34495e"
    BTN_COLOR = "#3498db"
    BTN_ACTIVE_COLOR = "#2980b9"
    ENTRY_BG = "#34495e"
    TREE_HEADING_BG = "#34495e"

    # General widget styling
    style.configure(".", background=BG_COLOR, foreground=FG_COLOR, font=('Segoe UI', 10), borderwidth=0)
    style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=('Segoe UI', 10))
    style.configure("TButton", font=('Segoe UI', 10, 'bold'), padding=10, background=BTN_COLOR, foreground="white", borderwidth=0)
    style.map("TButton", background=[('active', BTN_ACTIVE_COLOR)])
    style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=FG_COLOR, font=('Segoe UI', 10), padding=5, borderwidth=1)
    style.configure("TCombobox", fieldbackground=ENTRY_BG, foreground=FG_COLOR, font=('Segoe UI', 10), padding=5)
    style.map('TCombobox', fieldbackground=[('readonly', ENTRY_BG)], foreground=[('readonly', FG_COLOR)])
    style.configure("Treeview", background=ENTRY_BG, fieldbackground=ENTRY_BG, foreground=FG_COLOR, font=('Segoe UI', 10), rowheight=25)
    style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background=TREE_HEADING_BG, foreground=FG_COLOR, padding=5)
    style.map("Treeview.Heading", background=[('active', BTN_COLOR)])
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabelframe", background=BG_COLOR, foreground=FG_COLOR, font=('Segoe UI', 11, 'bold'))
    style.configure("TLabelframe.Label", background=BG_COLOR, foreground=FG_COLOR)

# ---------------- APPLICATION CLASS ----------------
class RailwayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() # Hide the main root window initially
        setup_styles()
        self.show_login_window()
        self.root.mainloop()

    def show_login_window(self):
        """Displays the login window."""
        LoginWindow(self)

    def show_main_menu(self, role, user_id, username):
        """Displays the main menu after successful login."""
        MainMenu(self, role, user_id, username)

# ---------------- LOGIN WINDOW ----------------
class LoginWindow(BaseWindow):
    def __init__(self, app):
        super().__init__("Railway System Login", "1000x600")
        self.app = app
        self.protocol("WM_DELETE_WINDOW", self.app.root.destroy) # Close app on exit
        self.create_widgets()

    def create_widgets(self):
        bg_image = Image.open("bg.jpeg") # Ensure bg.jpeg is in the same directory
        bg_image = bg_image.resize((1000, 600))
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self, image=self.bg_photo, borderwidth=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Login Frame
        login_frame = ttk.Frame(self, style="TFrame", padding=40)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_label = ttk.Label(login_frame, text="Railway Reservation System", font=('Segoe UI', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))

        create_styled_label(login_frame, "Username").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.entry_username = create_styled_entry(login_frame)
        self.entry_username.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky="ew")

        create_styled_label(login_frame, "Password").grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.entry_password = create_styled_entry(login_frame, show="*")
        self.entry_password.grid(row=4, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        login_button = create_styled_button(login_frame, "Login", self.login)
        login_button.grid(row=5, column=0, columnspan=2, sticky="ew")

        self.entry_username.focus_set()
        self.bind('<Return>', lambda event: self.login())

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showerror("Login Failed", "Username and Password are required.")
            return

        user_data = db_execute(
            "SELECT user_id, role, password, username FROM users WHERE username=%s",
            (username,),
            fetch='one'
        )

        if user_data and user_data[2] == password:
            user_id, role, _, uname = user_data
            messagebox.showinfo("Login Success", f"Welcome, {uname}!")
            self.destroy()
            self.app.show_main_menu(role, user_id, uname)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

# ---------------- MAIN MENU -----------------
class MainMenu(BaseWindow):
    def __init__(self, app, role, user_id, username):
        super().__init__("Dashboard", "800x600")
        self.resizable(False, False)
        self.app = app
        self.role = role
        self.user_id = user_id
        self.username = username
        self.protocol("WM_DELETE_WINDOW", self.logout)
        self.create_widgets()

    def create_widgets(self):
        # --- 1. SET THE BACKGROUND IMAGE ---
        try:
            bg_image = Image.open("bg.jpeg")
            bg_image = bg_image.resize((800, 600))
            self.bg_photo = ImageTk.PhotoImage(bg_image)
        except FileNotFoundError:
            self.bg_photo = None
            print("Warning: dashboard_bg.jpg not found. Using default background color.")

        bg_label = tk.Label(self, image=self.bg_photo, borderwidth=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- 2. PLACE HEADER WIDGETS DIRECTLY ON THE WINDOW ---
        # Welcome message placed at the top-left
        welcome_text = "Welcome, Have Fun Travelling"
        ttk.Label(
            self,
            text=welcome_text,
            font=('Segoe UI', 16, 'bold'),
            background="#34495e", 
            foreground="white",
            padding=10
        ).place(relx=0.5, rely=0.1, anchor="n")

        # --- Logout button REMOVED from the top-right corner ---
        # logout_button = ttk.Button(self, text="Logout", command=self.logout, style="TButton")
        # logout_button.place(relx=0.95, rely=0.05, anchor="ne")

        # --- 3. DEFINE AND PLACE BUTTONS IN A GRID-LIKE LAYOUT ---
        buttons = []
        if self.role.lower() == 'admin':
            buttons.extend([
                ("Manage Users", self.manage_users),
                ("Train Master", self.train_master),
                ("Station Master", self.station_master),
                ("Train Schedule", self.train_schedule),
                ("Fare Master", self.fare_master),
                ("View Reports", self.reports)
            ])
        
        buttons.extend([
            ("Book a Ticket", self.ticket_reservation),
            ("Cancel a Ticket", self.ticket_cancellation),
            ("My Bookings", self.my_bookings),
            ("Logout", self.logout) # --- Logout button ADDED to the end of the list ---
        ])
        
        # --- Layout Customization ---
        # You can easily change these values to adjust the button layout
        num_columns = 2
        start_x = 0.27  # Starting horizontal position (27% from the left)
        start_y = 0.25  # Starting vertical position (25% from the top)
        x_increment = 0.46 # Horizontal gap between columns
        y_increment = 0.12 # Vertical gap between rows
        
        for i, (text, command) in enumerate(buttons):
            btn = create_styled_button(self, text, command)
            
            # Calculate row and column for grid placement
            row = i // num_columns
            col = i % num_columns
            
            # Calculate relative coordinates
            rel_x = start_x + (col * x_increment)
            rel_y = start_y + (row * y_increment)
            
            # Place the button
            btn.place(relx=rel_x, rely=rel_y, anchor="center", relwidth=0.4, relheight=0.08)

    # --- NO CHANGES to the methods below ---
    def manage_users(self): ManageUsersWindow()
    def train_master(self): TrainMasterWindow()
    def station_master(self): StationMasterWindow()
    def train_schedule(self): TrainScheduleWindow()
    def fare_master(self): FareMasterWindow()
    def reports(self): ReportsWindow()
    def ticket_reservation(self): TicketReservationWindow(self.user_id)
    def ticket_cancellation(self): TicketCancellationWindow()
    def my_bookings(self): MyBookingsWindow(self.user_id)

    def logout(self):
        self.destroy()
        self.app.show_login_window()
# ---------------- GENERIC CRUD WINDOW ----------------
class CrudWindow(BaseWindow):
    """A generic base class for CRUD (Create, Read, Update, Delete) windows."""
    def __init__(self, title, geometry, columns, form_fields):
        super().__init__(title, geometry)
        self.columns = columns
        self.form_fields = form_fields
        self.entries = {}
        self.selected_id = None
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # Form Frame
        form_frame = ttk.LabelFrame(self, text="Add / Edit Entry", padding=15)
        form_frame.pack(fill="x", padx=10, pady=10)

        for i, (label, widget_type) in enumerate(self.form_fields.items()):
            create_styled_label(form_frame, label).grid(row=i // 2, column=(i % 2) * 2, padx=5, pady=5, sticky="e")
            if widget_type == 'entry':
                entry = create_styled_entry(form_frame)
            elif widget_type == 'password':
                entry = create_styled_entry(form_frame, show='*')
            elif isinstance(widget_type, list): # Combobox
                entry = ttk.Combobox(form_frame, values=widget_type, state='readonly')
            entry.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=5, sticky="ew")
            self.entries[label] = entry
        
        # Buttons Frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(self.form_fields) // 2, column=2, columnspan=2, pady=10, sticky='e')
        create_styled_button(button_frame, "Save", self.save_entry).pack(side="left", padx=5)
        create_styled_button(button_frame, "Clear", self.clear_form).pack(side="left", padx=5)

        # Treeview Frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, anchor="center", width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Delete Button
        delete_button = create_styled_button(self, "Delete Selected", self.delete_selected)
        delete_button.pack(pady=10, padx=10, anchor="e")

    def clear_form(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set('')
            else:
                entry.delete(0, tk.END)
        self.selected_id = None
        if list(self.entries.values()):
            list(self.entries.values())[0].focus_set()

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        self.selected_id = values[0]

        for i, (label, entry) in enumerate(self.entries.items()):
            value = values[i + 1] if len(values) > i + 1 else ""
            
            if self.form_fields[label] == 'password':
                entry.delete(0, tk.END)
                continue

            if isinstance(entry, ttk.Combobox):
                # Find the matching value in combobox items
                for item_val in entry['values']:
                    if str(value) in str(item_val):
                        entry.set(item_val)
                        break
            else:
                entry.delete(0, tk.END)
                entry.insert(0, value if value is not None else "")


    def save_entry(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def refresh_table(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def delete_selected(self):
        raise NotImplementedError("This method should be overridden by subclasses")


# ---------------- MANAGE USERS ----------------
class ManageUsersWindow(CrudWindow):
    def __init__(self):
        columns = ("user_id", "username", "role", "email", "phone")
        form_fields = {
            "Username": "entry", "Password": "password",
            "Role": ["admin", "user", "agent"], "Email": "entry",
            "Phone": "entry"
        }
        super().__init__("Manage Users", "900x600", columns, form_fields)

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        rows = db_execute("SELECT user_id, username, role, email, phone FROM users ORDER BY user_id", fetch='all')
        if rows:
            for row in rows: self.tree.insert("", "end", values=row)

    def save_entry(self):
        vals = {label: entry.get().strip() for label, entry in self.entries.items()}
        if not (vals["Username"] and vals["Role"]):
            messagebox.showerror("Validation Error", "Username and Role are required."); return
        if self.selected_id is None and not vals["Password"]:
            messagebox.showerror("Validation Error", "Password is required for new users."); return
        if vals["Phone"] and not vals["Phone"].isdigit():
            messagebox.showerror("Validation Error", "Phone number must be numeric."); return

        if self.selected_id is None: # Insert
            if db_execute("SELECT 1 FROM users WHERE username=%s", (vals["Username"],), fetch='one'):
                messagebox.showerror("Error", "Username already exists."); return
            query = "INSERT INTO users (username, password, role, email, phone) VALUES (%s, %s, %s, %s, %s)"
            params = (vals["Username"], vals["Password"], vals["Role"], vals["Email"], vals["Phone"])
        else: # Update
            if vals["Password"]: # Only update password if a new one is provided
                query = "UPDATE users SET username=%s, password=%s, role=%s, email=%s, phone=%s WHERE user_id=%s"
                params = (vals["Username"], vals["Password"], vals["Role"], vals["Email"], vals["Phone"], self.selected_id)
            else: # Don't update password
                query = "UPDATE users SET username=%s, role=%s, email=%s, phone=%s WHERE user_id=%s"
                params = (vals["Username"], vals["Role"], vals["Email"], vals["Phone"], self.selected_id)
        
        if db_execute(query, params):
            messagebox.showinfo("Success", f"User {'updated' if self.selected_id else 'added'} successfully.")
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("Database Error", "Failed to save user.")

    def delete_selected(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Please select a user to delete."); return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user ID {self.selected_id}?"):
            if db_execute("DELETE FROM users WHERE user_id=%s", (self.selected_id,)):
                messagebox.showinfo("Success", "User deleted.")
                self.clear_form()
                self.refresh_table()
            else:
                messagebox.showerror("Database Error", "Failed to delete user.")

# ---------------- TRAIN MASTER ----------------
class TrainMasterWindow(CrudWindow):
    def __init__(self):
        columns = ("train_id", "train_name", "train_type", "total_seats")
        form_fields = {"Train Name": "entry", "Train Type": "entry", "Total Seats": "entry"}
        super().__init__("Train Master", "900x600", columns, form_fields)

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        rows = db_execute("SELECT train_id, train_name, train_type, total_seats FROM trains ORDER BY train_id", fetch='all')
        if rows:
            for row in rows: self.tree.insert("", "end", values=row)

    def save_entry(self):
        vals = {label: entry.get().strip() for label, entry in self.entries.items()}
        if not all(vals.values()):
            messagebox.showerror("Validation Error", "All fields are required."); return
        if not is_int(vals["Total Seats"]) or int(vals["Total Seats"]) <= 0:
            messagebox.showerror("Validation Error", "Total seats must be a positive integer."); return

        if self.selected_id is None:
            query = "INSERT INTO trains (train_name, train_type, total_seats) VALUES (%s, %s, %s)"
            params = (vals["Train Name"], vals["Train Type"], int(vals["Total Seats"]))
        else:
            query = "UPDATE trains SET train_name=%s, train_type=%s, total_seats=%s WHERE train_id=%s"
            params = (vals["Train Name"], vals["Train Type"], int(vals["Total Seats"]), self.selected_id)
        
        if db_execute(query, params):
            messagebox.showinfo("Success", "Train data saved.")
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("Database Error", "Failed to save train data.")

    def delete_selected(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Please select a train to delete."); return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete train ID {self.selected_id}?"):
            if db_execute("DELETE FROM trains WHERE train_id=%s", (self.selected_id,)):
                messagebox.showinfo("Success", "Train deleted.")
                self.clear_form()
                self.refresh_table()
            else:
                messagebox.showerror("Database Error", "Failed to delete train.")

# ---------------- STATION MASTER ----------------
class StationMasterWindow(CrudWindow):
    def __init__(self):
        columns = ("station_id", "station_name", "station_code", "city", "state")
        form_fields = {"Station Name": "entry", "Station Code": "entry", "City": "entry", "State": "entry"}
        super().__init__("Station Master", "900x600", columns, form_fields)

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        rows = db_execute("SELECT station_id, station_name, station_code, city, state FROM stations ORDER BY station_id", fetch='all')
        if rows:
            for row in rows: self.tree.insert("", "end", values=row)

    def save_entry(self):
        vals = {label: entry.get().strip() for label, entry in self.entries.items()}
        if not all(vals.values()):
            messagebox.showerror("Validation Error", "All fields are required."); return
        
        code = vals["Station Code"].upper()
        if self.selected_id is None:
            if db_execute("SELECT 1 FROM stations WHERE station_code=%s", (code,), fetch='one'):
                messagebox.showerror("Error", "Station code already exists."); return
            query = "INSERT INTO stations (station_name, station_code, city, state) VALUES (%s, %s, %s, %s)"
            params = (vals["Station Name"], code, vals["City"], vals["State"])
        else:
            query = "UPDATE stations SET station_name=%s, station_code=%s, city=%s, state=%s WHERE station_id=%s"
            params = (vals["Station Name"], code, vals["City"], vals["State"], self.selected_id)
        
        if db_execute(query, params):
            messagebox.showinfo("Success", "Station data saved.")
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("Database Error", "Failed to save station data.")

    def delete_selected(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Please select a station to delete."); return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete station ID {self.selected_id}?"):
            if db_execute("DELETE FROM stations WHERE station_id=%s", (self.selected_id,)):
                messagebox.showinfo("Success", "Station deleted.")
                self.clear_form()
                self.refresh_table()
            else:
                messagebox.showerror("Database Error", "Failed to delete station.")

# ---------------- FARE MASTER ----------------
class FareMasterWindow(CrudWindow):
    def __init__(self):
        stations = get_stations_for_combobox()
        columns = ("fare_id", "from_station", "to_station", "class_type", "fare_amount")
        form_fields = {
            "From Station": stations, "To Station": stations,
            "Class Type": ["Sleeper", "AC", "General"], "Fare Amount": "entry"
        }
        super().__init__("Fare Master", "1000x600", columns, form_fields)

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        rows = db_execute("SELECT fare_id, from_station, to_station, class_type, fare_amount FROM fare_master ORDER BY fare_id", fetch='all')
        if rows:
            for r in rows:
                from_name = get_station_name_by_id(r[1])
                to_name = get_station_name_by_id(r[2])
                self.tree.insert("", "end", values=(r[0], f"{r[1]} - {from_name}", f"{r[2]} - {to_name}", r[3], f"{float(r[4]):.2f}"))

    def save_entry(self):
        vals = {label: entry.get().strip() for label, entry in self.entries.items()}
        if not all(vals.values()):
            messagebox.showerror("Validation Error", "All fields are required."); return
        
        try:
            fare = float(vals["Fare Amount"])
            if fare < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Fare must be a positive number."); return

        from_id = parse_id_from_combo(vals["From Station"])
        to_id = parse_id_from_combo(vals["To Station"])
        class_type = vals["Class Type"]

        if from_id is None or to_id is None:
            messagebox.showerror("Validation Error", "Invalid station selected."); return

        if self.selected_id is None:
            if db_execute("SELECT 1 FROM fare_master WHERE from_station=%s AND to_station=%s AND class_type=%s", (from_id, to_id, class_type), fetch='one'):
                messagebox.showerror("Error", "Fare entry for this route and class already exists."); return
            query = "INSERT INTO fare_master (from_station, to_station, class_type, fare_amount) VALUES (%s, %s, %s, %s)"
            params = (from_id, to_id, class_type, fare)
        else:
            query = "UPDATE fare_master SET from_station=%s, to_station=%s, class_type=%s, fare_amount=%s WHERE fare_id=%s"
            params = (from_id, to_id, class_type, fare, self.selected_id)

        if db_execute(query, params):
            messagebox.showinfo("Success", "Fare data saved.")
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("Database Error", "Failed to save fare data.")
    
    def delete_selected(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Please select a fare to delete."); return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete fare ID {self.selected_id}?"):
            if db_execute("DELETE FROM fare_master WHERE fare_id=%s", (self.selected_id,)):
                messagebox.showinfo("Success", "Fare deleted.")
                self.clear_form()
                self.refresh_table()
            else:
                messagebox.showerror("Database Error", "Failed to delete fare.")

# ---------------- TRAIN SCHEDULE ----------------
class TrainScheduleWindow(BaseWindow):
    def __init__(self):
        super().__init__("Train Schedule", "1100x700")
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        form = ttk.LabelFrame(self, text="Add Schedule Entry", padding=15)
        form.pack(fill="x", padx=10, pady=10)

        # Form fields
        create_styled_label(form, "Train").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cb_train = ttk.Combobox(form, values=get_trains_for_combobox(), width=30, state='readonly')
        self.cb_train.grid(row=0, column=1, padx=5, pady=5)

        create_styled_label(form, "Station").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.cb_station = ttk.Combobox(form, values=get_stations_for_combobox(), width=30, state='readonly')
        self.cb_station.grid(row=0, column=3, padx=5, pady=5)

        create_styled_label(form, "Arrival (HH:MM)").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.e_arr = create_styled_entry(form)
        self.e_arr.grid(row=1, column=1, padx=5, pady=5)

        create_styled_label(form, "Departure (HH:MM)").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.e_dep = create_styled_entry(form)
        self.e_dep.grid(row=1, column=3, padx=5, pady=5)

        create_styled_label(form, "Sequence").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.e_seq = create_styled_entry(form)
        self.e_seq.grid(row=2, column=1, padx=5, pady=5)

        add_button = create_styled_button(form, "Add Entry", self.add_schedule)
        add_button.grid(row=2, column=3, padx=5, pady=10, sticky="e")

        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        cols = ("schedule_id", "train", "station", "arrival_time", "departure_time", "sequence")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, anchor="center", width=150)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        delete_button = create_styled_button(self, "Delete Selected", self.delete_selected)
        delete_button.pack(pady=10, padx=10, anchor="e")

    def add_schedule(self):
        train_id = parse_id_from_combo(self.cb_train.get())
        station_id = parse_id_from_combo(self.cb_station.get())
        seq = self.e_seq.get().strip()
        arr = self.e_arr.get().strip() or None
        dep = self.e_dep.get().strip() or None

        if not (train_id and station_id and seq):
            messagebox.showerror("Error", "Train, Station, and Sequence are required."); return
        if not is_int(seq):
            messagebox.showerror("Error", "Sequence must be an integer."); return
        
        query = "INSERT INTO train_schedule (train_id, station_id, arrival_time, departure_time, sequence) VALUES (%s, %s, %s, %s, %s)"
        if db_execute(query, (train_id, station_id, arr, dep, int(seq))):
            messagebox.showinfo("Success", "Schedule entry added.")
            self.refresh_table()
        else:
            messagebox.showerror("Database Error", "Failed to add schedule entry.")

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        query = """SELECT schedule_id, train_id, station_id, arrival_time, departure_time, sequence
                   FROM train_schedule ORDER BY train_id, sequence"""
        rows = db_execute(query, fetch='all')
        if rows:
            for r in rows:
                tname = get_train_name_by_id(r[1])
                sname = get_station_name_by_id(r[2])
                arr_time = str(r[3]) if r[3] else "N/A"
                dep_time = str(r[4]) if r[4] else "N/A"
                self.tree.insert("", "end", values=(r[0], f"{r[1]} - {tname}", f"{r[2]} - {sname}", arr_time, dep_time, r[5]))

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a schedule entry to delete."); return
        
        schedule_id = self.tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete schedule ID {schedule_id}?"):
            if db_execute("DELETE FROM train_schedule WHERE schedule_id=%s", (schedule_id,)):
                messagebox.showinfo("Success", "Schedule entry deleted.")
                self.refresh_table()
            else:
                messagebox.showerror("Database Error", "Failed to delete entry.")

# ---------------- PASSENGER DETAILS WINDOW ----------------
class PassengerDetailsWindow(BaseWindow):
    def __init__(self, parent, callback):
        super().__init__("Enter Passenger Details", "600x500")
        self.parent = parent
        self.callback = callback
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill="both")

        create_styled_label(frame, "Full Name").pack(pady=(0, 5))
        self.name_entry = create_styled_entry(frame)
        self.name_entry.pack(pady=(0, 15), ipady=4, fill='x')

        create_styled_label(frame, "Age").pack(pady=(0, 5))
        self.age_entry = create_styled_entry(frame)
        self.age_entry.pack(pady=(0, 15), ipady=4, fill='x')

        create_styled_label(frame, "Gender").pack(pady=(0, 5))
        self.gender_combo = ttk.Combobox(frame, values=["Male", "Female", "Other"], state='readonly')
        self.gender_combo.pack(pady=(0, 20), ipady=4, fill='x')

        create_styled_button(frame, "Confirm Details", self.submit_details).pack(pady=10, ipady=5, fill='x')

    def submit_details(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        gender = self.gender_combo.get()

        if not (name and age and gender):
            messagebox.showerror("Error", "All fields are required.", parent=self)
            return
        if not is_int(age) or not (0 < int(age) < 120):
            messagebox.showerror("Error", "Please enter a valid age.", parent=self)
            return

        details = {"name": name, "age": age, "gender": gender}
        self.destroy()
        self.callback(details)

# ---------------- TICKET RESERVATION (NEW VERSION) ----------------
class TicketReservationWindow(BaseWindow):
    def __init__(self, passenger_id):
        super().__init__("Search Trains & Book Ticket", "900x700")
        self.passenger_id = passenger_id
        self.selected_train_data = None  # To store details of the selected train
        self.create_widgets()

    def create_widgets(self):
        # --- Search Frame ---
        search_frame = ttk.LabelFrame(self, text="Search for Trains", padding=15)
        search_frame.pack(fill="x", padx=10, pady=10)

        create_styled_label(search_frame, "From Station").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cb_from = ttk.Combobox(search_frame, values=get_stations_for_combobox(), width=30, state='readonly')
        self.cb_from.grid(row=0, column=1, padx=5, pady=5)

        create_styled_label(search_frame, "To Station").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.cb_to = ttk.Combobox(search_frame, values=get_stations_for_combobox(), width=30, state='readonly')
        self.cb_to.grid(row=0, column=3, padx=5, pady=5)

        search_button = create_styled_button(search_frame, "Search Trains", self.search_trains)
        search_button.grid(row=0, column=4, padx=15, pady=5)

        # --- Results Frame ---
        results_frame = ttk.LabelFrame(self, text="Available Trains", padding=15)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("train_id", "train_name", "type", "departs", "arrives", "availability")
        self.tree = ttk.Treeview(results_frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, anchor="center", width=120)
        
        self.tree.column("train_id", width=60) # Make ID column smaller
        self.tree.column("train_name", width=200, anchor="w") # Name column wider
        
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_train_select)

        # --- Booking Frame ---
        booking_frame = ttk.Frame(self, padding=10)
        booking_frame.pack(fill="x")

        create_styled_label(booking_frame, "Class Type:").pack(side="left", padx=(10, 5))
        self.cb_class = ttk.Combobox(booking_frame, values=["Sleeper", "AC", "General"], width=20, state='readonly')
        self.cb_class.pack(side="left", pady=(0, 10))

        self.book_button = create_styled_button(booking_frame, "Book Selected Train", self.get_passenger_details)
        self.book_button.pack(side="right", padx=10, pady=(0, 10))
        self.book_button.state(['disabled']) # Initially disabled

    def search_trains(self):
        # Clear previous results and selection
        for i in self.tree.get_children(): self.tree.delete(i)
        self.selected_train_data = None
        self.book_button.state(['disabled'])

        from_station = self.cb_from.get()
        to_station = self.cb_to.get()

        if not from_station or not to_station:
            messagebox.showerror("Error", "Please select both 'From' and 'To' stations.")
            return
        if from_station == to_station:
            messagebox.showerror("Error", "'From' and 'To' stations cannot be the same.")
            return

        from_id = parse_id_from_combo(from_station)
        to_id = parse_id_from_combo(to_station)

        trains = search_trains_between_stations(from_id, to_id)

        if not trains:
            messagebox.showinfo("No Trains Found", "Sorry, no direct trains were found for the selected route.")
            return

        for train in trains:
            train_id, train_name, train_type, dep, arr = train
            # Check availability
            total_seats_row = db_execute("SELECT total_seats FROM trains WHERE train_id=%s", (train_id,), fetch='one')
            total_seats = total_seats_row[0] if total_seats_row else 0
            booked_count_row = db_execute("SELECT COUNT(*) FROM tickets WHERE train_id=%s AND status='Confirmed'", (train_id,), fetch='one')
            booked_count = booked_count_row[0] if booked_count_row else 0
            available = max(0, total_seats - booked_count)
            
            self.tree.insert("", "end", values=(train_id, train_name, train_type, dep or 'N/A', arr or 'N/A', f"{available} seats"))

    def on_train_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.selected_train_data = {
            "train_id": values[0],
            "train_name": values[1]
        }
        self.book_button.state(['!disabled']) # Enable the book button

    def get_passenger_details(self):
        if not self.selected_train_data:
            messagebox.showerror("Error", "Please select a train from the list first."); return
        if not self.cb_class.get():
            messagebox.showerror("Error", "Please select a class type."); return

        PassengerDetailsWindow(self, self.book_ticket)

    def book_ticket(self, passenger_details):
        train_id = self.selected_train_data['train_id']
        from_id = parse_id_from_combo(self.cb_from.get())
        to_id = parse_id_from_combo(self.cb_to.get())
        class_type = self.cb_class.get()

        seat_string = get_next_available_seat(train_id)
        if not seat_string:
            messagebox.showerror("Booking Failed", "Sorry, no seats are available on this train."); return
        
        fare_row = db_execute("SELECT fare_amount FROM fare_master WHERE from_station=%s AND to_station=%s AND class_type=%s", (from_id, to_id, class_type), fetch='one')
        fare = float(fare_row[0]) if fare_row else 0.0
        if fare == 0.0:
            messagebox.showwarning("Fare Warning", "Fare for this route and class is not set. It will be recorded as 0.00.")

        pnr = generate_pnr()
        booking_date = datetime.date.today()
        
        query = """INSERT INTO tickets (pnr, train_id, passenger_id, from_station, to_station, seat_number, class_type, booking_date, status, passenger_name, passenger_age, passenger_gender)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Confirmed', %s, %s, %s)"""
        params = (pnr, train_id, self.passenger_id, from_id, to_id, seat_string, class_type, booking_date, 
                  passenger_details['name'], passenger_details['age'], passenger_details['gender'])
        
        if db_execute(query, params):
            ticket_data = {
                'pnr': pnr,
                'passenger_name': passenger_details['name'],
                'passenger_age': passenger_details['age'],
                'passenger_gender': passenger_details['gender'],
                'train_name': self.selected_train_data['train_name'],
                'from_station': get_station_name_by_id(from_id),
                'to_station': get_station_name_by_id(to_id),
                'booking_date': booking_date,
                'class_type': class_type,
                'seat_number': seat_string,
                'fare': fare
            }
            
            self.destroy()
            TicketDetailsWindow(ticket_data)
        else:
            messagebox.showerror("Database Error", "Failed to book ticket.")

# ---------------- TICKET DETAILS WINDOW ----------------
class TicketDetailsWindow(BaseWindow):
    def __init__(self, ticket_data):
        super().__init__("Booking Confirmation - Ticket Details", "500x650")
        self.ticket_data = ticket_data
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=25)
        main_frame.pack(expand=True, fill="both")

        title = ttk.Label(main_frame, text="E-Ticket", font=('Segoe UI', 20, 'bold'))
        title.pack(pady=(0, 20))

        details_frame = ttk.Frame(main_frame, style="TFrame")
        details_frame.pack(pady=10, padx=10, fill='x')

        details_map = {
            "PNR Number:": self.ticket_data['pnr'],
            "Passenger Name:": self.ticket_data['passenger_name'],
            "Age:": self.ticket_data['passenger_age'],
            "Gender:": self.ticket_data['passenger_gender'],
            "Train:": self.ticket_data['train_name'],
            "From:": self.ticket_data['from_station'],
            "To:": self.ticket_data['to_station'],
            "Booking Date:": str(self.ticket_data['booking_date']),
            "Class:": self.ticket_data['class_type'],
            "Seat Number:": self.ticket_data['seat_number'],
            "Fare:": f"₹{self.ticket_data['fare']:.2f}",
            "Status:": "CONFIRMED"
        }

        for i, (label_text, value_text) in enumerate(details_map.items()):
            label = ttk.Label(details_frame, text=label_text, font=('Segoe UI', 11, 'bold'))
            label.grid(row=i, column=0, sticky='w', pady=6, padx=5)
            value = ttk.Label(details_frame, text=str(value_text), font=('Segoe UI', 11))
            value.grid(row=i, column=1, sticky='w', pady=6, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)

        create_styled_button(button_frame, "Print to PDF", self.print_ticket_as_pdf).pack(side="left", padx=10)
        create_styled_button(button_frame, "Close", self.destroy).pack(side="left", padx=10)

    def print_ticket_as_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"ticket_{self.ticket_data['pnr']}.pdf",
            title="Download Ticket"
        )
        if not path:
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 20)
            
            # Header
            pdf.cell(0, 15, "Railway E-Ticket", 0, 1, 'C')
            pdf.ln(10)

            # Ticket Details
            pdf.set_font("Arial", 'B', 12)
            details = self.ticket_data
            
            def add_detail_row(label, value):
                pdf.cell(50, 10, label, 0, 0)
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, str(value), 0, 1)
                pdf.set_font("Arial", 'B', 12)

            add_detail_row("PNR Number:", details['pnr'])
            add_detail_row("Status:", "CONFIRMED")
            pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Passenger Details", 0, 1)
            pdf.set_font("Arial", 'B', 12)
            add_detail_row("Name:", details['passenger_name'])
            add_detail_row("Age:", details['passenger_age'])
            add_detail_row("Gender:", details['passenger_gender'])
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Journey Details", 0, 1)
            pdf.set_font("Arial", 'B', 12)
            add_detail_row("Train:", details['train_name'])
            add_detail_row("From:", details['from_station'])
            add_detail_row("To:", details['to_station'])
            add_detail_row("Booking Date:", str(details['booking_date']))
            add_detail_row("Class:", details['class_type'])
            add_detail_row("Seat Number:", details['seat_number'])
            add_detail_row("Fare:", f"Rs. {details['fare']:.2f}")
            pdf.ln(10)

            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, "Thank you for choosing our service. Happy journey!", 0, 1, 'C')

            pdf.output(path)
            messagebox.showinfo("Success", f"Ticket saved as PDF to:\n{path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {e}")


# ---------------- TICKET CANCELLATION ----------------
class TicketCancellationWindow(BaseWindow):
    def __init__(self):
        super().__init__("Ticket Cancellation", "500x350")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill="both")

        create_styled_label(frame, "Enter PNR to Cancel").pack(pady=(0, 5))
        self.e_pnr = create_styled_entry(frame)
        self.e_pnr.pack(pady=(0, 15), ipady=4, fill='x')

        self.info_label = ttk.Label(frame, text="Ticket details will be shown here.", wraplength=450, justify='center')
        self.info_label.pack(pady=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        create_styled_button(btn_frame, "View Ticket", self.view_ticket).pack(side="left", padx=10)
        create_styled_button(btn_frame, "Cancel Ticket", self.cancel_ticket).pack(side="left", padx=10)

    def view_ticket(self):
        pnr = self.e_pnr.get().strip()
        if not pnr: messagebox.showerror("Error", "PNR is required."); return
        
        query = """SELECT status, train_id, seat_number, from_station, to_station
                   FROM tickets WHERE pnr=%s"""
        row = db_execute(query, (pnr,), fetch='one')

        if not row:
            self.info_label.config(text="Invalid PNR. Please check and try again.")
            return
        
        status, tid, seat, fs, ts = row
        info = f"Train: {get_train_name_by_id(tid)}\nSeat: {seat}\nFrom: {get_station_name_by_id(fs)}\nTo: {get_station_name_by_id(ts)}\nStatus: {status}"
        self.info_label.config(text=info)

    def cancel_ticket(self):
        pnr = self.e_pnr.get().strip()
        if not pnr: messagebox.showerror("Error", "PNR is required."); return

        status_row = db_execute("SELECT status FROM tickets WHERE pnr=%s", (pnr,), fetch='one')
        if not status_row:
            messagebox.showerror("Error", "Invalid PNR."); return
        if status_row[0] == 'Cancelled':
            messagebox.showinfo("Info", "This ticket has already been cancelled."); return

        if messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this ticket?"):
            if db_execute("UPDATE tickets SET status='Cancelled' WHERE pnr=%s", (pnr,)):
                messagebox.showinfo("Success", "Ticket has been cancelled successfully.")
                self.destroy()
            else:
                messagebox.showerror("Database Error", "Failed to cancel ticket.")

# ---------------- MY BOOKINGS ----------------
class MyBookingsWindow(BaseWindow):
    def __init__(self, user_id):
        super().__init__("My Bookings", "1200x600")
        self.user_id = user_id
        self.create_widgets()
        self.load_bookings()

    def create_widgets(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols = ("PNR", "Passenger", "Train", "From", "To", "Seat", "Class", "Booking Date", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_bookings(self):
        query = """SELECT pnr, passenger_name, train_id, from_station, to_station, seat_number, class_type, booking_date, status
                   FROM tickets WHERE passenger_id=%s ORDER BY booking_date DESC"""
        rows = db_execute(query, (self.user_id,), fetch='all')
        if rows:
            for r in rows:
                values = (
                    r[0], r[1], get_train_name_by_id(r[2]), get_station_name_by_id(r[3]),
                    get_station_name_by_id(r[4]), r[5], r[6], str(r[7]), r[8]
                )
                self.tree.insert("", "end", values=values)

# ---------------- REPORTS ----------------
class ReportsWindow(BaseWindow):
    def __init__(self):
        super().__init__("Booking Reports", "1200x700")
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        filter_frame = ttk.LabelFrame(self, text="Filters", padding=15)
        filter_frame.pack(fill="x", padx=10, pady=10)

        create_styled_label(filter_frame, "Train ID").grid(row=0, column=0, padx=5, pady=5)
        self.e_train = create_styled_entry(filter_frame)
        self.e_train.grid(row=0, column=1, padx=5, pady=5)

        create_styled_label(filter_frame, "Status").grid(row=0, column=2, padx=5, pady=5)
        self.cb_status = ttk.Combobox(filter_frame, values=["", "Confirmed", "Cancelled"], state='readonly')
        self.cb_status.grid(row=0, column=3, padx=5, pady=5)

        create_styled_label(filter_frame, "From (YYYY-MM-DD)").grid(row=0, column=4, padx=5, pady=5)
        self.e_from = create_styled_entry(filter_frame)
        self.e_from.grid(row=0, column=5, padx=5, pady=5)
        
        create_styled_label(filter_frame, "To (YYYY-MM-DD)").grid(row=0, column=6, padx=5, pady=5)
        self.e_to = create_styled_entry(filter_frame)
        self.e_to.grid(row=0, column=7, padx=5, pady=5)

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=0, column=8, padx=20)
        create_styled_button(btn_frame, "Apply Filter", self.load_data).pack(side="left", padx=5)
        create_styled_button(btn_frame, "Export CSV", self.export_csv).pack(side="left", padx=5)

        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        cols = ("PNR", "Passenger", "Train", "From", "To", "Seat", "Class", "Status", "Booking Date")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c); self.tree.column(c, anchor="center", width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        query = "SELECT pnr, passenger_name, train_id, from_station, to_station, seat_number, class_type, status, booking_date FROM tickets"
        filters, params = [], []

        if self.e_train.get().strip():
            if not is_int(self.e_train.get().strip()):
                messagebox.showerror("Error", "Train ID must be an integer."); return
            filters.append("train_id=%s"); params.append(int(self.e_train.get().strip()))
        if self.cb_status.get():
            filters.append("status=%s"); params.append(self.cb_status.get())
        if self.e_from.get().strip():
            filters.append("booking_date >= %s"); params.append(self.e_from.get().strip())
        if self.e_to.get().strip():
            filters.append("booking_date <= %s"); params.append(self.e_to.get().strip())

        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY booking_date DESC"
        
        rows = db_execute(query, tuple(params), fetch='all')
        if rows:
            for r in rows:
                values = (
                    r[0], r[1], get_train_name_by_id(r[2]), get_station_name_by_id(r[3]),
                    get_station_name_by_id(r[4]), r[5], r[6], r[7], str(r[8])
                )
                self.tree.insert("", "end", values=values)

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile="booking_report.csv")
        if not path: return
        
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.tree['columns']) # header
                for iid in self.tree.get_children():
                    writer.writerow(self.tree.item(iid)['values'])
            messagebox.showinfo("Export Successful", f"Report saved to {path}")
        except IOError as e:
            messagebox.showerror("Export Failed", f"Could not save file: {e}")

# ---------------- START APP ----------------
if __name__ == "__main__":
    # Check DB connection on startup
    if get_db_connection():
        app = RailwayApp()
    else:
        print("Application cannot start without a database connection.")
