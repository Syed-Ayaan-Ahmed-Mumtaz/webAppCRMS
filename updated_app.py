# This code is a refactored version of crime_records_app.py and app.py combined to match the updated SQL schema
# This is the Flask web app portion

from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# SQL Server Connection
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-MVSQUSI\\SQLEXPRESS;'
    'DATABASE=RECORDS;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# --- Helper Functions ---
def login_user(username, password):
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

def add_case(criminal_name, criminal_age, crime_type, officer_name, rank, department, victim_name, status):
    # Insert Criminal
    cursor.execute("INSERT INTO Criminal (Name, Age, Crime_Type) VALUES (?, ?, ?)",
                   (criminal_name, criminal_age, crime_type))
    criminal_id = cursor.execute("SELECT @@IDENTITY").fetchval()

    # Insert Case
    cursor.execute("INSERT INTO Case (CriminalID, Victim_Name, Status) VALUES (?, ?, ?)",
                   (criminal_id, victim_name, status))
    case_id = cursor.execute("SELECT @@IDENTITY").fetchval()

    # Insert Officer
    cursor.execute("INSERT INTO Officer (Name, Rank, Department, CaseID) VALUES (?, ?, ?, ?)",
                   (officer_name, rank, department, case_id))

    conn.commit()

# --- Flask Routes ---
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if login_user(username, password):
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('records'))
    else:
        flash('Invalid username or password.', 'danger')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/records')
def records():
    all_cases = fetch_all_cases()
    return render_template('records.html', records=all_cases)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        data = request.form
        try:
            add_case(
                criminal_name=data['criminal_name'],
                criminal_age=int(data['criminal_age']),
                crime_type=data['crime_type'],
                officer_name=data['officer_name'],
                rank=data['rank'],
                department=data['department'],
                victim_name=data['victim_name'],
                status=data['status']
            )
            flash("Case added successfully!", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        return redirect(url_for('manage'))

    all_cases = fetch_all_cases()
    return render_template('manage.html', records=all_cases)

if __name__ == '__main__':
    app.run(debug=True)
