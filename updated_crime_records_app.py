import pyodbc
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# --- SQL Server Connection ---
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-MVSQUSI\\SQLEXPRESS;'
    'DATABASE=RECORDS;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# --- Backend Functions ---

def login(username, password):
    cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (username, password))
    return cursor.fetchone() is not None

def fetch_all_cases_tk():
    cursor.execute("""
        SELECT
            c.CaseID,
            c.Name AS CaseName,
            c.Description,
            ISNULL(cr.Name, 'N/A') AS CriminalName,
            ISNULL(o.Name, 'N/A') AS OfficerName,
            c.Status,
            c.Crime_Date
        FROM [Case] c
        LEFT JOIN Criminal cr ON c.CriminalID = cr.CriminalID
        LEFT JOIN Officer o ON c.CaseID = o.CaseID
        ORDER BY c.CaseID DESC
    """)
    results = []
    for row in cursor.fetchall():
        crime_date = row.Crime_Date.strftime('%Y-%m-%d') if row.Crime_Date else ''
        results.append((row.CaseID, row.CaseName, row.Description, row.CriminalName, row.OfficerName, row.Status, crime_date))
    return results

def insert_case_tk(case_name, description, criminal_name, criminal_age, crime_type, victim_name, status, officer_name, officer_rank, officer_department, crime_date):
    conn.autocommit = False  # Start transaction

    try:
        # Parse date safely
        crime_date_obj = None
        if crime_date:
            crime_date_obj = datetime.strptime(crime_date, '%Y-%m-%d').date()

        # Insert Criminal
        cursor.execute("INSERT INTO Criminal (Name, Age, Crime_Type) VALUES (?, ?, ?)",
                       (criminal_name, criminal_age, crime_type))
        criminal_id = cursor.execute("SELECT SCOPE_IDENTITY()").fetchval()

        # Insert Case
        cursor.execute("""
            INSERT INTO Case (CriminalID, Name, Description, Victim_Name, Status, Crime_Date) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (criminal_id, case_name, description, victim_name, status, crime_date_obj))
        case_id = cursor.execute("SELECT SCOPE_IDENTITY()").fetchval()

        # Insert Officer
        cursor.execute("""
            INSERT INTO Officer (Name, Rank, Department, CaseID) 
            VALUES (?, ?, ?, ?)""",
            (officer_name, officer_rank, officer_department, case_id))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Database Error", f"Failed to add case: {e}")
        return False
    finally:
        conn.autocommit = True

# --- GUI ---

def show_login_page():
    login_win = tk.Tk()
    login_win.title("Login")
    login_win.geometry("300x150")

    tk.Label(login_win, text="Username").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(login_win, text="Password").grid(row=1, column=0, padx=10, pady=5)

    username_entry = tk.Entry(login_win)
    password_entry = tk.Entry(login_win, show='*')
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    def handle_login():
        if login(username_entry.get(), password_entry.get()):
            login_win.destroy()
            show_manage_records_page_tk()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")

    tk.Button(login_win, text="Login", command=handle_login).grid(row=2, column=1, pady=10)
    login_win.mainloop()

def show_manage_records_page_tk():
    manage_win = tk.Tk()
    manage_win.title("Manage Records")
    manage_win.geometry("400x600")

    fields = {
        "Case Name": tk.StringVar(),
        "Description": tk.StringVar(),
        "Criminal Name": tk.StringVar(),
        "Criminal Age": tk.StringVar(),
        "Crime Type": tk.StringVar(),
        "Victim Name": tk.StringVar(),
        "Status": tk.StringVar(value="Open"),
        "Officer Name": tk.StringVar(),
        "Officer Rank": tk.StringVar(),
        "Officer Department": tk.StringVar(),
        "Crime Date (YYYY-MM-DD)": tk.StringVar()
    }

    for idx, (label, var) in enumerate(fields.items()):
        tk.Label(manage_win, text=label).grid(row=idx, column=0, padx=5, pady=2, sticky='w')
        if label == "Status":
            options = ["Open", "Closed", "Under Investigation", "Arrest Made"]
            ttk.Combobox(manage_win, textvariable=var, values=options).grid(row=idx, column=1, padx=5, pady=2, sticky='ew')
        else:
            tk.Entry(manage_win, textvariable=var).grid(row=idx, column=1, padx=5, pady=2, sticky='ew')

    def handle_submit():
        try:
            criminal_age = int(fields["Criminal Age"].get())
            crime_date_str = fields["Crime Date (YYYY-MM-DD)"].get()
            if crime_date_str:
                datetime.strptime(crime_date_str, '%Y-%m-%d')  # Validate date

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
                for var in fields.values():
                    var.set("")
                fields["Status"].set("Open")
            else:
                messagebox.showerror("Error", "Failed to add case.")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input. Check Criminal Age and Date format (YYYY-MM-DD).")
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))

    tk.Button(manage_win, text="Add New Record", command=handle_submit).grid(row=len(fields), column=1, pady=10)
    tk.Button(manage_win, text="Go To Records Page", command=lambda: [manage_win.destroy(), show_records_page_tk()]).grid(row=len(fields)+1, column=1, pady=5)
    tk.Button(manage_win, text="Log Out", command=lambda: [manage_win.destroy(), show_login_page()]).grid(row=len(fields)+2, column=1, pady=5)

    manage_win.columnconfigure(1, weight=1)
    manage_win.mainloop()

def show_records_page_tk():
    records_win = tk.Tk()
    records_win.title("Criminal Cases")
    records_win.geometry("900x400")

    cols = ('CaseID', 'Case Name', 'Description', 'Criminal Name', 'Officer Name', 'Status', 'Crime Date')
    tree = ttk.Treeview(records_win, columns=cols, show='headings')

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    records = fetch_all_cases_tk()
    for row in records:
        tree.insert("", tk.END, values=row)

    tree.pack(expand=True, fill='both')

    vsb = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    tk.Button(records_win, text="Log Out", command=lambda: [records_win.destroy(), show_login_page()]).pack(pady=10)

    records_win.mainloop()

# --- Start ---
show_login_page()
