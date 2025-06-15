# updated_crime_records_app.py
# Updated crime_records_app.py to reflect new normalized SQL schema

import pyodbc
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime # Import datetime for date handling

# --- SQL Server Connection ---
# IMPORTANT: Adjusted SERVER name to match Flask app for consistency.
# Ensure 'DESKTOP-MVSQUSI\\SQLEXPRESS' is the correct server name for your setup.
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};' # Ensure you have this driver installed
    'SERVER=DESKTOP-MVSQUSI\\SQLEXPRESS;' # Changed from MVS0USN to MVSQUSI
    'DATABASE=RECORDS;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# --- Backend Functions ---
def login(username, password):
    cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (username, password))
    return cursor.fetchone() is not None

def fetch_all_cases_tk(): # Renamed to avoid clash if both apps run
    # Adjusted to fetch Case Name, Description, Crime Date and Criminal Name for TKinter display
    cursor.execute("""
        SELECT
            c.CaseID,
            c.Name AS CaseName,         -- Now fetching Case Name
            c.Description,              -- Now fetching Description
            cr.Name AS CriminalName,
            o.Name AS OfficerName,
            c.Status,
            c.Crime_Date                -- Now fetching Crime Date
        FROM Case c
        JOIN Criminal cr ON c.CriminalID = cr.CriminalID
        JOIN Officer o ON c.CaseID = o.CaseID
        ORDER BY c.CaseID DESC
    """)
    # Format date for display
    results = []
    for row in cursor.fetchall():
        crime_date = row.Crime_Date.strftime('%Y-%m-%d') if row.Crime_Date else ''
        results.append((row.CaseID, row.CaseName, row.Description, row.CriminalName, row.OfficerName, row.Status, crime_date))
    return results

def insert_case_tk(case_name, description, criminal_name, criminal_age, crime_type, victim_name, status, officer_name, officer_rank, officer_department, crime_date):
    conn.autocommit = False # Start transaction for atomicity
    try:
        # Convert crime_date string to date object if not empty
        crime_date_obj = None
        if crime_date:
            try:
                crime_date_obj = datetime.strptime(crime_date, '%Y-%m-%d').date()
            except ValueError:
                # Handle invalid date format if necessary, or let DB handle if nullable
                pass

        # Insert Criminal
        cursor.execute("INSERT INTO Criminal (Name, Age, Crime_Type) VALUES (?, ?, ?)",
                       (criminal_name, criminal_age, crime_type))
        criminal_id = cursor.execute("SELECT @@IDENTITY").fetchval()

        # Insert Case - now includes Case Name, Description, Crime_Date
        cursor.execute("INSERT INTO Case (CriminalID, Name, Description, Victim_Name, Status, Crime_Date) VALUES (?, ?, ?, ?, ?, ?)",
                       (criminal_id, case_name, description, victim_name, status, crime_date_obj))
        case_id = cursor.execute("SELECT @@IDENTITY").fetchval()

        # Insert Officer
        cursor.execute("INSERT INTO Officer (Name, Rank, Department, CaseID) VALUES (?, ?, ?, ?)",
                       (officer_name, officer_rank, officer_department, case_id))

        conn.commit() # Commit transaction
        return True
    except Exception as e:
        conn.rollback() # Rollback on error
        messagebox.showerror("Database Error", f"Failed to add case: {e}")
        return False
    finally:
        conn.autocommit = True # Always reset autocommit

# --- GUI Windows ---
def show_login_page():
    login_win = tk.Tk()
    login_win.title("Login")
    login_win.geometry("300x150") # Give it a fixed size

    tk.Label(login_win, text="Username").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(login_win, text="Password").grid(row=1, column=0, padx=10, pady=5)

    username_entry = tk.Entry(login_win)
    password_entry = tk.Entry(login_win, show='*')
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    def handle_login():
        if login(username_entry.get(), password_entry.get()):
            login_win.destroy()
            show_manage_records_page_tk() # Corrected call
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")

    tk.Button(login_win, text="Login", command=handle_login).grid(row=2, column=1, pady=10)
    login_win.mainloop()

def show_manage_records_page_tk(): # Renamed for clarity
    manage_win = tk.Tk()
    manage_win.title("Manage Records")
    manage_win.geometry("400x600") # Adjust size to fit more fields

    # Entry fields for new case - Adjusted to include new Case fields
    fields = {
        "Case Name": tk.StringVar(),
        "Description": tk.StringVar(),
        "Criminal Name": tk.StringVar(),
        "Criminal Age": tk.StringVar(),
        "Crime Type": tk.StringVar(),
        "Victim Name": tk.StringVar(),
        "Status": tk.StringVar(),
        "Officer Name": tk.StringVar(),
        "Officer Rank": tk.StringVar(),
        "Officer Department": tk.StringVar(),
        "Crime Date (YYYY-MM-DD)": tk.StringVar() # Changed label for clarity
    }

    # Set default for Status
    fields["Status"].set("Open") # Default status to Open

    for idx, (label, var) in enumerate(fields.items()):
        tk.Label(manage_win, text=label).grid(row=idx, column=0, padx=5, pady=2, sticky='w')
        if label == "Status":
            status_options = ["Open", "Closed", "Under Investigation", "Arrest Made"]
            ttk.Combobox(manage_win, textvariable=var, values=status_options).grid(row=idx, column=1, padx=5, pady=2, sticky='ew')
        else:
            tk.Entry(manage_win, textvariable=var).grid(row=idx, column=1, padx=5, pady=2, sticky='ew')

    def handle_submit():
        try:
            # Validate age and crime date
            criminal_age = int(fields["Criminal Age"].get())
            crime_date_str = fields["Crime Date (YYYY-MM-DD)"].get()
            if crime_date_str:
                datetime.strptime(crime_date_str, '%Y-%m-%d') # Just validate format

            inserted = insert_case_tk(
                case_name=fields["Case Name"].get(),
                description=fields["Description"].get(),
                criminal_name=fields["Criminal Name"].get(),
                criminal_age=criminal_age,
                crime_type=fields["Crime Type"].get(),
                victim_name=fields["Victim Name"].get(),
                status=fields["Status"].get(),
                officer_name=fields["Officer Name"].get(),
                officer_rank=fields["Officer Rank"].get(),
                officer_department=fields["Officer Department"].get(),
                crime_date=crime_date_str
            )
            if inserted:
                messagebox.showinfo("Success", "Case added successfully!")
                # Clear fields after successful submission
                for var in fields.values():
                    var.set("")
                fields["Status"].set("Open") # Reset status to default
            else:
                messagebox.showerror("Error", "Failed to add case. See console for details.")
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Invalid input: {ve}. Please check age and date format.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    tk.Button(manage_win, text="Add New Record", command=handle_submit).grid(row=len(fields), column=1, pady=10)
    tk.Button(manage_win, text="Go To Records Page", command=lambda:[manage_win.destroy(), show_records_page_tk()]).grid(row=len(fields)+1, column=1, pady=5)
    tk.Button(manage_win, text="Log Out", command=lambda:[manage_win.destroy(), show_login_page()]).grid(row=len(fields)+2, column=1, pady=5)

    manage_win.columnconfigure(1, weight=1) # Allow second column to expand
    manage_win.mainloop()

def show_records_page_tk(): # Renamed for clarity
    records_win = tk.Tk()
    records_win.title("Criminal Cases")
    records_win.geometry("800x400") # Adjust size for more columns

    # Added new columns for Treeview
    cols = ('CaseID', 'Case Name', 'Description', 'Criminal Name', 'Officer Name', 'Status', 'Crime Date')
    tree = ttk.Treeview(records_win, columns=cols, show='headings')

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100) # Adjust column width

    # Use the new fetch function for Tkinter
    records = fetch_all_cases_tk()
    for row in records:
        tree.insert("", tk.END, values=row)

    tree.pack(expand=True, fill='both')

    # Add scrollbars
    vsb = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    tk.Button(records_win, text="Log Out", command=lambda:[records_win.destroy(), show_login_page()]).pack(pady=10)

    records_win.mainloop()

# --- Start App ---
show_login_page()