# Updated crime_records_app.py to reflect new normalized SQL schema

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

def fetch_all_cases():
    cursor.execute("""
        SELECT c.CaseID, cr.Name AS CriminalName, o.Name AS OfficerName,
               c.Victim_Name, c.Status
        FROM Case c
        JOIN Criminal cr ON c.CriminalID = cr.CriminalID
        JOIN Officer o ON c.CaseID = o.CaseID
    """)
    return cursor.fetchall()

def insert_case(criminal_name, criminal_age, crime_type, officer_name, rank, department, victim_name, status):
    cursor.execute("INSERT INTO Criminal (Name, Age, Crime_Type) VALUES (?, ?, ?)",
                   (criminal_name, criminal_age, crime_type))
    criminal_id = cursor.execute("SELECT @@IDENTITY").fetchval()

    cursor.execute("INSERT INTO Case (CriminalID, Victim_Name, Status) VALUES (?, ?, ?)",
                   (criminal_id, victim_name, status))
    case_id = cursor.execute("SELECT @@IDENTITY").fetchval()

    cursor.execute("INSERT INTO Officer (Name, Rank, Department, CaseID) VALUES (?, ?, ?, ?)",
                   (officer_name, rank, department, case_id))
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

    # Entry fields for new case
    fields = {
        "Criminal Name": tk.StringVar(),
        "Criminal Age": tk.StringVar(),
        "Crime Type": tk.StringVar(),
        "Officer Name": tk.StringVar(),
        "Rank": tk.StringVar(),
        "Department": tk.StringVar(),
        "Victim Name": tk.StringVar(),
        "Status": tk.StringVar()
    }

    for idx, (label, var) in enumerate(fields.items()):
        tk.Label(manage_win, text=label).grid(row=idx, column=0)
        tk.Entry(manage_win, textvariable=var).grid(row=idx, column=1)

    def handle_submit():
        try:
            insert_case(
                fields["Criminal Name"].get(),
                int(fields["Criminal Age"].get()),
                fields["Crime Type"].get(),
                fields["Officer Name"].get(),
                fields["Rank"].get(),
                fields["Department"].get(),
                fields["Victim Name"].get(),
                fields["Status"].get()
            )
            messagebox.showinfo("Success", "Case added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add case: {e}")

    tk.Button(manage_win, text="Add New Record", command=handle_submit).grid(row=len(fields), column=1, pady=10)
    tk.Button(manage_win, text="Go To Records Page", command=lambda:[manage_win.destroy(), show_records_page()]).grid(row=len(fields)+1, column=1)
    tk.Button(manage_win, text="Log Out", command=lambda:[manage_win.destroy(), show_login_page()]).grid(row=len(fields)+2, column=1)

    manage_win.mainloop()

def show_records_page():
    records_win = tk.Tk()
    records_win.title("Criminal Cases")

    cols = ('CaseID', 'Criminal', 'Officer', 'Victim', 'Status')
    tree = ttk.Treeview(records_win, columns=cols, show='headings')

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    records = fetch_all_cases()
    for row in records:
        tree.insert("", tk.END, values=row)

    tree.pack(expand=True, fill='both')
    tk.Button(records_win, text="Log Out", command=lambda:[records_win.destroy(), show_login_page()]).pack(pady=10)

    records_win.mainloop()

# --- Start App ---
show_login_page()
