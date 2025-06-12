
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime

# Import the mock database manager
# In a real application, you would replace this with your pyodbc database connection and query functions.
import mock_db_manager

app = Flask(__name__)
# IMPORTANT: Use a strong, random secret key in production.
# This is used for signing the session cookie.
app.secret_key = os.urandom(24) 

# --- Before Request Hook for Authentication ---
@app.before_request
def require_login():
    """
    This function runs before every request. It checks if the user is logged in
    and redirects to the login page if not, unless the endpoint is for login or static files.
    """
    # List of endpoints that do NOT require login
    allowed_endpoints = ['home', 'login', 'static']
    
    if request.endpoint not in allowed_endpoints and not session.get('logged_in'):
        flash('You need to be logged in to access this page.', 'info')
        return redirect(url_for('home'))

# --- Routes ---

@app.route('/')
def home():
    """
    Renders the login page. This is the entry point for the application.
    """
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """
    Handles user login.
    Authenticates user against the mock database and sets a session variable upon success.
    """
    username = request.form['username']
    password = request.form['password']

    # Authenticate user using the mock database manager
    if mock_db_manager.login_user(username, password):
        session['logged_in'] = True
        session['username'] = username  # Store username in session
        flash('Login successful!', 'success')
        return redirect(url_for('records'))
    else:
        flash('Invalid username or password. Please try again.', 'danger')
        return render_template('login.html') # No need to pass 'error', flash handles it

@app.route('/logout')
def logout():
    """
    Logs out the user by clearing the session.
    """
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/records')
def records():
    """
    Displays all criminal records.
    Fetches data using the mock database manager.
    """
    # Fetch all records from the mock database
    all_records = mock_db_manager.fetch_all_records()
    return render_template('records.html', records=all_records)

@app.route('/queries', methods=['GET', 'POST'])
def queries():
    """
    Handles searching and filtering of criminal records.
    """
    filtered_records = []
    if request.method == 'POST':
        # Get filter parameters from the form
        name = request.form.get('name')
        officer_name = request.form.get('officer_name')
        status = request.form.get('status')

        # Use the mock database manager to search/filter records
        filtered_records = mock_db_manager.search_records(
            name=name if name else None,
            officer_name=officer_name if officer_name else None,
            status=status if status else None
        )
        if not filtered_records:
            flash("No records found matching your criteria.", 'info')

    # If it's a GET request, or after a POST request, show all records initially
    # or the filtered results.
    # If no POST search was performed, show all records as initial view for queries page.
    if request.method == 'GET' and not filtered_records:
        filtered_records = mock_db_manager.fetch_all_records()

    return render_template('queries.html', records=filtered_records)

@app.route('/manage', methods=['GET', 'POST'])
def manage_records():
    """
    Handles adding new criminal records and displays existing records.
    """
    if request.method == 'POST':
        # Get form data for new record
        name = request.form['name']
        description = request.form['description']
        status = request.form['status']
        officer_name = request.form['officer_name']
        crime_date = request.form['crime_date']

        # Basic validation (more robust validation would be needed)
        if not all([name, description, status, officer_name, crime_date]):
            flash('All fields are required!', 'danger')
        else:
            try:
                # Validate date format (optional, but good practice)
                datetime.datetime.strptime(crime_date, '%Y-%m-%d')
                # Add record using the mock database manager
                mock_db_manager.add_record(name, description, status, officer_name, crime_date)
                flash('Record added successfully!', 'success')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')

        # Redirect back to the manage page to show updated list
        return redirect(url_for('manage_records'))
    
    # For GET request, fetch and display all records
    all_records = mock_db_manager.fetch_all_records()
    return render_template('manage.html', records=all_records)

@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    """
    Handles editing an existing criminal record.
    """
    record = mock_db_manager.fetch_record_by_id(record_id)
    if not record:
        flash('Record not found.', 'danger')
        return redirect(url_for('manage_records'))

    if request.method == 'POST':
        # Get updated data from the form
        name = request.form['name']
        description = request.form['description']
        status = request.form['status']
        officer_name = request.form['officer_name']
        crime_date = request.form['crime_date']

        if not all([name, description, status, officer_name, crime_date]):
            flash('All fields are required!', 'danger')
        else:
            try:
                datetime.datetime.strptime(crime_date, '%Y-%m-%d')
                # Update record using the mock database manager
                success = mock_db_manager.update_record(record_id, name, description, status, officer_name, crime_date)
                if success:
                    flash('Record updated successfully!', 'success')
                    return redirect(url_for('manage_records'))
                else:
                    flash('Failed to update record.', 'danger')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')
        
        # If update failed or validation error, re-render the edit form with current data
        # (This would typically be a separate edit_record.html template)
        return render_template('edit_record_form.html', record=request.form) # You'd need this template

    # For GET request, display the edit form with existing record data
    # For simplicity, I'm providing a minimal HTML for edit.
    # Ideally, this would be a separate template.
    edit_form_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Record</title>
        <link rel="stylesheet" href="{ url_for('static', filename='css/styles.css') }}/">
    </head>
    <body>
        <div class="banner">
            <img src="{ url_for('static', filename='images/logo.svg') }" alt="logo" class="logo">
            <h1 class="banner-text">Edit Record - CRMS</h1>
        </div>
        <div class="records-container">
            <h2>Edit Record (ID: {record.get('id', '')})</h2>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <ul class="flash-messages">
                        {% for category, message in messages %}
                            <li class="flash-message {{ category }}">{{ message }}</li>
                        {% endfor %}
                    </ul>
                {% endif %}
            {% endwith %}
            <form method="POST" action="{ url_for('edit_record', record_id=record_id) }}/">
                <input type="text" name="name" placeholder="Case Name" value="{record.get('name', '')}" required>
                <textarea name="description" placeholder="Description" rows="3" required>{record.get('description', '')}</textarea>
                <select name="status" required>
                    <option value="Open" {'selected' if record.get('status') == 'Open' else ''}>Open</option>
                    <option value="Closed" {'selected' if record.get('status') == 'Closed' else ''}>Closed</option>
                    <option value="Under Investigation" {'selected' if record.get('status') == 'Under Investigation' else ''}>Under Investigation</option>
                    <option value="Arrest Made" {'selected' if record.get('status') == 'Arrest Made' else ''}>Arrest Made</option>
                </select>
                <input type="text" name="officer_name" placeholder="Officer Name" value="{record.get('officer_name', '')}" required>
                <input type="date" name="crime_date" value="{record.get('crime_date', '')}" required>
                <button type="submit">Update Record</button>
            </form>
            <p><a href="{ url_for('manage_records') }}/"><button>Back to Manage Records</button></a></p>
        </div>
    </body>
    </html>
    """
    return edit_form_html


@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    """
    Handles deleting a criminal record.
    """
    success = mock_db_manager.delete_record(record_id)
    if success:
        flash('Record deleted successfully!', 'success')
    else:
        flash('Failed to delete record.', 'danger')
    return redirect(url_for('manage_records'))

# --- Main Run Block ---
if __name__ == '__main__':
    # This will run the Flask app in debug mode.
    # For production, you'd use a production-ready WSGI server like Gunicorn.
    app.run(debug=True)
