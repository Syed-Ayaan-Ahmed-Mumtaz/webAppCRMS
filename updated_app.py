# updated_app.py
# This code is a refactored version of crime_records_app.py and app.py combined to match the updated SQL schema
# This is the Flask web app portion

from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc
import os
from datetime import datetime # Import datetime for date formatting

app = Flask(__name__)
app.secret_key = os.urandom(24)

# SQL Server Connection
# Make sure this server name is correct for your setup!
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};' # Ensure you have this driver installed
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
    # Adjusted to fetch Case Name, Description, Crime Date and Criminal Name
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
    # Convert rows to dictionaries for easier access in templates
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        record = dict(zip(columns, row))
        # Format date for HTML input type="date"
        if record['Crime_Date']:
            record['Crime_Date'] = record['Crime_Date'].strftime('%Y-%m-%d')
        results.append(record)
    return results

def fetch_single_case_details(case_id):
    # Fetch all necessary details for a single case including newly added columns
    cursor.execute("""
        SELECT
            c.CaseID,
            c.Name AS CaseName,          -- Case's specific name
            c.Description,
            c.Victim_Name,
            c.Status,
            c.Crime_Date,                -- Crime date
            cr.CriminalID,
            cr.Name AS CriminalName,     -- Criminal's name
            cr.Age AS CriminalAge,
            cr.Crime_Type AS CrimeType,
            o.OfficerID,
            o.Name AS OfficerName,
            o.Rank AS OfficerRank,
            o.Department AS OfficerDepartment
        FROM Case c
        JOIN Criminal cr ON c.CriminalID = cr.CriminalID
        JOIN Officer o ON c.CaseID = o.CaseID -- This assumes 1:1 case-officer, handled by UNIQUE on Officer.CaseID
        WHERE c.CaseID = ?
    """, (case_id,))
    row = cursor.fetchone()
    if row:
        record = {
            'id': row.CaseID,
            'name': row.CaseName,         # 'name' in HTML maps to Case.Name
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
    conn.autocommit = False # Start transaction
    try:
        # Insert Criminal
        cursor.execute("INSERT INTO Criminal (Name, Age, Crime_Type) VALUES (?, ?, ?)",
                       (criminal_name, criminal_age, crime_type))
        criminal_id = cursor.execute("SELECT @@IDENTITY").fetchval()

        # Insert Case - now includes Case Name, Description, Crime_Date
        cursor.execute("INSERT INTO Case (CriminalID, Name, Description, Victim_Name, Status, Crime_Date) VALUES (?, ?, ?, ?, ?, ?)",
                       (criminal_id, case_name, description, victim_name, status, crime_date))
        case_id = cursor.execute("SELECT @@IDENTITY").fetchval()

        # Insert Officer
        cursor.execute("INSERT INTO Officer (Name, Rank, Department, CaseID) VALUES (?, ?, ?, ?)",
                       (officer_name, officer_rank, officer_department, case_id))

        conn.commit() # Commit transaction
        return True
    except Exception as e:
        conn.rollback() # Rollback on error
        print(f"Error adding case: {e}")
        return False
    finally:
        conn.autocommit = True # Always reset autocommit

def update_case_details(case_id, new_case_name, new_description, new_status, new_officer_name, new_crime_date):
    conn.autocommit = False # Start transaction
    try:
        # Fetch current CriminalID and OfficerID linked to this CaseID
        cursor.execute("SELECT CriminalID FROM Case WHERE CaseID = ?", (case_id,))
        criminal_id = cursor.fetchone()[0]

        cursor.execute("SELECT OfficerID FROM Officer WHERE CaseID = ?", (case_id,))
        officer_id = cursor.fetchone()[0]

        # Update Criminal (assuming 'name' in edit form refers to Criminal.Name as shown in fetch_all_cases)
        # If 'name' on the edit form is truly for Case.Name, then this part should be removed/adjusted.
        # Given the HTML edit_record.html uses 'name' for Case Name and officer_name for Officer Name
        # And the fetch_single_case_details maps Case.Name to 'name' in record, and Criminal.Name to 'criminal_name'
        # The update logic will prioritize updating Case.Name with 'new_case_name'
        # and Officer.Name with 'new_officer_name'.

        # UPDATE Case table first
        cursor.execute("""
            UPDATE Case
            SET Name = ?, Description = ?, Status = ?, Crime_Date = ?
            WHERE CaseID = ?
        """, (new_case_name, new_description, new_status, new_crime_date, case_id))

        # Update Officer table
        cursor.execute("UPDATE Officer SET Name = ? WHERE OfficerID = ?", (new_officer_name, officer_id))

        # We are NOT updating Criminal.Name directly from edit_record.html's 'name' input,
        # because the 'name' input is mapped to Case.Name (newly added column).
        # If you needed to edit Criminal.Name from this form, you'd need another input field.

        conn.commit() # Commit transaction
        return True
    except Exception as e:
        conn.rollback() # Rollback on error
        print(f"Error updating case: {e}")
        return False
    finally:
        conn.autocommit = True # Always reset autocommit

def delete_case(case_id):
    conn.autocommit = False # Start transaction
    try:
        # Due to foreign key constraints, delete in reverse order of creation
        # First, find CriminalID associated with the Case
        cursor.execute("SELECT CriminalID FROM Case WHERE CaseID = ?", (case_id,))
        criminal_id_row = cursor.fetchone()
        criminal_id = criminal_id_row[0] if criminal_id_row else None

        # Delete from Suspect (if linked to this CaseID)
        cursor.execute("DELETE FROM Suspect WHERE CaseID = ?", (case_id,))
        # Delete from Report (if linked to this CaseID)
        cursor.execute("DELETE FROM Report WHERE CaseID = ?", (case_id,))
        # Delete from Officer (if linked to this CaseID)
        cursor.execute("DELETE FROM Officer WHERE CaseID = ?", (case_id,))
        # Delete the Case itself
        cursor.execute("DELETE FROM Case WHERE CaseID = ?", (case_id,))

        # Finally, delete from Criminal if no other cases refer to this criminal (optional, but good for cleanup)
        # This part requires more complex logic to check if criminal_id is still referenced.
        # For simplicity, we'll assume a criminal might have only one case or won't be deleted if referenced by other cases.
        # If your Criminal.Name and Case.Name are distinct, deleting the Case doesn't necessarily mean deleting the Criminal.
        # Given the current 1:1 nature of Case and Criminal (from your add_case logic),
        # we can consider deleting the criminal as well for a complete record removal.
        if criminal_id:
             cursor.execute("DELETE FROM Criminal WHERE CriminalID = ?", (criminal_id,))

        conn.commit() # Commit transaction
        return True
    except Exception as e:
        conn.rollback() # Rollback on error
        print(f"Error deleting case: {e}")
        return False
    finally:
        conn.autocommit = True # Always reset autocommit

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
        FROM Case c
        JOIN Criminal cr ON c.CriminalID = cr.CriminalID
        JOIN Officer o ON c.CaseID = o.CaseID
        WHERE 1=1 -- dummy condition to easily append AND clauses
    """
    params = []

    if case_name_query:
        base_query += " AND c.Name LIKE ? COLLATE SQL_Latin1_General_CP1_CI_AS" # Case-insensitive search
        params.append(f"%{case_name_query}%")
    if officer_name_query:
        base_query += " AND o.Name LIKE ? COLLATE SQL_Latin1_General_CP1_CI_AS" # Case-insensitive search
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
        return redirect(url_for('records')) # If already logged in, go to records
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

# Renamed route to 'manage_records' to match HTML url_for calls
@app.route('/manage_records', methods=['GET', 'POST'])
def manage_records():
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = request.form
        try:
            # Note: The form now sends 'case_name' (for Case.Name) and other new fields
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
        return redirect(url_for('manage_records')) # Always redirect after POST

    # For GET request or after POST redirect
    all_cases = fetch_all_cases()
    return render_template('manage.html', records=all_cases)


@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Handle form submission for updating the record
        new_case_name = request.form['name']
        new_description = request.form['description']
        new_status = request.form['status']
        new_officer_name = request.form['officer_name']
        new_crime_date = request.form['crime_date']

        if update_case_details(record_id, new_case_name, new_description, new_status, new_officer_name, new_crime_date):
            flash('Record updated successfully!', 'success')
            return redirect(url_for('manage_records')) # Redirect to manage page after update
        else:
            flash('Error updating record. Please check server logs.', 'danger')
            # Fetch the record again to show the current state even after error
            record = fetch_single_case_details(record_id)
            return render_template('edit_record.html', record=record)

    else: # GET request
        # Display the form to edit the record
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
    return redirect(url_for('manage_records')) # Always redirect after POST for delete


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
             flash('No records found matching your query.', 'info') # Use info flash for no results
    else: # GET request for initial page load
        # You might want to show all records initially or keep it empty
        # For now, we'll keep it empty on initial GET, user must run query.
        pass

    return render_template('queries.html', records=records)


if __name__ == '__main__':
    # When running locally, ensure your SQL Server Express instance is running.
    app.run(debug=True)