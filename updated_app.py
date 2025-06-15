from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# SQL Server Connection
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
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
        SELECT
            c.CaseID,
            c.Name AS CaseName,
            c.Description,
            cr.Name AS CriminalName,
            o.Name AS OfficerName,
            c.Status,
            c.Crime_Date
        FROM [Case] c
        JOIN Criminal cr ON c.CriminalID = cr.CriminalID
        JOIN Officer o ON c.CaseID = o.CaseID
        ORDER BY c.CaseID DESC
    """)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        record = dict(zip(columns, row))
        if record['Crime_Date']:
            record['Crime_Date'] = record['Crime_Date'].strftime('%Y-%m-%d')
        results.append(record)
    return results

def fetch_single_case_details(case_id):
    cursor.execute("""
        SELECT
            c.CaseID,
            c.Name AS CaseName,
            c.Description,
            c.Victim_Name,
            c.Status,
            c.Crime_Date,
            cr.CriminalID,
            cr.Name AS CriminalName,
            cr.Age AS CriminalAge,
            cr.Crime_Type AS CrimeType,
            o.OfficerID,
            o.Name AS OfficerName,
            o.Rank AS OfficerRank,
            o.Department AS OfficerDepartment
        FROM [Case] c
        JOIN Criminal cr ON c.CriminalID = cr.CriminalID
        JOIN Officer o ON c.CaseID = o.CaseID
        WHERE c.CaseID = ?
    """, (case_id,))
    row = cursor.fetchone()
    if row:
        record = {
            'id': row.CaseID,
            'name': row.CaseName,
            'description': row.Description,
            'status': row.Status,
            'officer_name': row.OfficerName,
            'crime_date': row.Crime_Date.strftime('%Y-%m-%d') if row.Crime_Date else '',
            'criminal_name': row.CriminalName,
            'criminal_age': row.CriminalAge,
            'crime_type': row.CrimeType,
            'victim_name': row.Victim_Name,
            'officer_rank': row.OfficerRank,
            'officer_department': row.OfficerDepartment,
            'criminal_id': row.CriminalID,
            'officer_id': row.OfficerID
        }
        return record
    return None

def add_case(case_name, description, criminal_name, criminal_age, crime_type, victim_name, status, officer_name, officer_rank, officer_department, crime_date):
    conn.autocommit = False
    try:
        cursor.execute("INSERT INTO Criminal (Name, Age, Crime_Type) VALUES (?, ?, ?)",
                       (criminal_name, criminal_age, crime_type))
        criminal_id = cursor.execute("SELECT @@IDENTITY").fetchval()

        cursor.execute("INSERT INTO [Case] (CriminalID, Name, Description, Victim_Name, Status, Crime_Date) VALUES (?, ?, ?, ?, ?, ?)",
                       (criminal_id, case_name, description, victim_name, status, crime_date))
        case_id = cursor.execute("SELECT @@IDENTITY").fetchval()

        cursor.execute("INSERT INTO Officer (Name, Rank, Department, CaseID) VALUES (?, ?, ?, ?)",
                       (officer_name, officer_rank, officer_department, case_id))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error adding case: {e}")
        return False
    finally:
        conn.autocommit = True

def update_case_details(case_id, new_case_name, new_description, new_status, new_officer_name, new_crime_date):
    conn.autocommit = False
    try:
        cursor.execute("SELECT OfficerID FROM Officer WHERE CaseID = ?", (case_id,))
        officer_id = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE [Case]
            SET Name = ?, Description = ?, Status = ?, Crime_Date = ?
            WHERE CaseID = ?
        """, (new_case_name, new_description, new_status, new_crime_date, case_id))

        cursor.execute("UPDATE Officer SET Name = ? WHERE OfficerID = ?", (new_officer_name, officer_id))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating case: {e}")
        return False
    finally:
        conn.autocommit = True

def delete_case(case_id):
    conn.autocommit = False
    try:
        cursor.execute("SELECT CriminalID FROM [Case] WHERE CaseID = ?", (case_id,))
        criminal_id_row = cursor.fetchone()
        criminal_id = criminal_id_row[0] if criminal_id_row else None

        cursor.execute("DELETE FROM Suspect WHERE CaseID = ?", (case_id,))
        cursor.execute("DELETE FROM Report WHERE CaseID = ?", (case_id,))
        cursor.execute("DELETE FROM Officer WHERE CaseID = ?", (case_id,))
        cursor.execute("DELETE FROM [Case] WHERE CaseID = ?", (case_id,))

        if criminal_id:
            cursor.execute("DELETE FROM Criminal WHERE CriminalID = ?", (criminal_id,))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting case: {e}")
        return False
    finally:
        conn.autocommit = True

def search_cases(case_name_query=None, officer_name_query=None, status_query=None):
    base_query = """
        SELECT
            c.CaseID,
            c.Name AS CaseName,
            c.Description,
            cr.Name AS CriminalName,
            o.Name AS OfficerName,
            c.Status,
            c.Crime_Date
        FROM [Case] c
        JOIN Criminal cr ON c.CriminalID = cr.CriminalID
        JOIN Officer o ON c.CaseID = o.CaseID
        WHERE 1=1
    """
    params = []

    if case_name_query:
        base_query += " AND c.Name LIKE ? COLLATE SQL_Latin1_General_CP1_CI_AS"
        params.append(f"%{case_name_query}%")
    if officer_name_query:
        base_query += " AND o.Name LIKE ? COLLATE SQL_Latin1_General_CP1_CI_AS"
        params.append(f"%{officer_name_query}%")
    if status_query:
        base_query += " AND c.Status = ?"
        params.append(status_query)

    cursor.execute(base_query, tuple(params))
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        record = dict(zip(columns, row))
        if record['Crime_Date']:
            record['Crime_Date'] = record['Crime_Date'].strftime('%Y-%m-%d')
        results.append(record)
    return results

# --- Flask Routes ---
@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('records'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if login_user(username, password):
        session['logged_in'] = True
        session['username'] = username
        flash('Logged in successfully!', 'success')
        return redirect(url_for('records'))
    else:
        flash('Invalid username or password.', 'danger')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/records')
def records():
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('home'))
    all_cases = fetch_all_cases()
    return render_template('records.html', records=all_cases)

@app.route('/manage_records', methods=['GET', 'POST'])
def manage_records():
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = request.form
        try:
            added = add_case(
                case_name=data['case_name'],
                description=data['description'],
                criminal_name=data['criminal_name'],
                criminal_age=int(data['criminal_age']),
                crime_type=data['crime_type'],
                victim_name=data['victim_name'],
                status=data['status'],
                officer_name=data['officer_name'],
                officer_rank=data['officer_rank'],
                officer_department=data['officer_department'],
                crime_date=data['crime_date']
            )
            if added:
                flash("Case added successfully!", "success")
            else:
                flash("Failed to add case due to a database error.", "danger")
        except ValueError:
            flash("Invalid input for age. Please enter a number.", "danger")
        except Exception as e:
            flash(f"Error adding case: {e}", "danger")
        return redirect(url_for('manage_records'))

    all_cases = fetch_all_cases()
    return render_template('manage.html', records=all_cases)

@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        new_case_name = request.form['name']
        new_description = request.form['description']
        new_status = request.form['status']
        new_officer_name = request.form['officer_name']
        new_crime_date = request.form['crime_date']

        if update_case_details(record_id, new_case_name, new_description, new_status, new_officer_name, new_crime_date):
            flash('Record updated successfully!', 'success')
            return redirect(url_for('manage_records'))
        else:
            flash('Error updating record. Please check server logs.', 'danger')
            record = fetch_single_case_details(record_id)
            return render_template('edit_record.html', record=record)
    else:
        record = fetch_single_case_details(record_id)
        if record:
            return render_template('edit_record.html', record=record)
        else:
            flash('Record not found.', 'danger')
            return redirect(url_for('manage_records'))

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('home'))

    if delete_case(record_id):
        flash('Record deleted successfully!', 'success')
    else:
        flash('Error deleting record. It might be linked to other data.', 'danger')
    return redirect(url_for('manage_records'))

@app.route('/queries', methods=['GET', 'POST'])
def queries():
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('home'))

    records = []
    if request.method == 'POST':
        case_name = request.form.get('case_name')
        officer_name = request.form.get('officer_name')
        status = request.form.get('status')

        records = search_cases(case_name, officer_name, status)
        if not records:
             flash('No records found matching your query.', 'info')
    return render_template('queries.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
