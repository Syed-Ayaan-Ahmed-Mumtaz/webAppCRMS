import pyodbc
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# --- SQL Server Connection ---
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-MVS0USN\\SQLEXPRESS;'
    'DATABASE=RECORDS;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# --- Backend Functions ---
def login(username, password):
    cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (username, password))
    return cursor.fetchone() is not None

def fetch_all_crimes():
    cursor.execute("SELECT RecordID, Name, Description, Status, CrimeDate FROM CriminalRecords")
    return cursor.fetchall()

def insert_crime(name, desc, status, date):
    cursor.execute("""
        INSERT INTO CriminalRecords (Name, Description, Status, CrimeDate)
        VALUES (?, ?, ?, ?)
    """, (name, desc, status, date))
    conn.commit()

# --- GUI Windows ---
def show_login_page():
    login_win = tk.Tk()
    login_win.title("Login")

    tk.Label(login_win, text="Username").grid(row=0, column=0)
    tk.Label(login_win, text="Password").grid(row=1, column=0)

    username_entry = tk.Entry(login_win)
    password_entry = tk.Entry(login_win, show='*')
    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)

    def handle_login():
        if login(username_entry.get(), password_entry.get()):
            login_win.destroy()
            show_manage_records_page()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")

    tk.Button(login_win, text="Login", command=handle_login).grid(row=2, column=1)
    login_win.mainloop()

def show_manage_records_page():
    manage_win = tk.Tk()
    manage_win.title("Manage Records")

    tk.Button(manage_win, text="Go To Records Page", command=lambda:[manage_win.destroy(), show_records_page()]).pack(pady=10)
    tk.Button(manage_win, text="Log Out", command=lambda:[manage_win.destroy(), show_login_page()]).pack(pady=10)

    manage_win.mainloop()

def show_records_page():
    records_win = tk.Tk()
    records_win.title("Criminal Records")

    cols = ('ID', 'Name', 'Description', 'Status', 'Date')
    tree = ttk.Treeview(records_win, columns=cols, show='headings')

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    records = fetch_all_crimes()
    for row in records:
        tree.insert("", tk.END, values=row)

    tree.pack(expand=True, fill='both')
    tk.Button(records_win, text="Log Out", command=lambda:[records_win.destroy(), show_login_page()]).pack(pady=10)

    records_win.mainloop()

# --- Start App ---
show_login_page()