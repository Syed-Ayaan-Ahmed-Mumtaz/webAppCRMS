import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# This file simulates database operations for the Flask application.
# In a real application, you would replace these functions with actual
# pyodbc (or SQLAlchemy, etc.) calls to your SQL Server database.

# Mock data storage (in-memory lists of dictionaries)
# In a real scenario, this would be your database tables.
mock_users_db = [
    {'username': 'admin', 'password_hash': generate_password_hash('admin')},
    {'username': 'testuser', 'password_hash': generate_password_hash('password123')}
]

mock_records_db = [
    {'id': 1, 'name': 'Robbery at Central Bank', 'description': 'Suspect stole cash from vault.', 'status': 'Open', 'officer_name': 'Officer Mehmood', 'crime_date': '2023-01-01'},
    {'id': 2, 'name': 'Shoplifting at Grand Mall', 'description': 'Minor theft of electronics.', 'status': 'Closed', 'officer_name': 'Officer Shazia', 'crime_date': '2023-01-05'},
    {'id': 3, 'name': 'Assault in Park', 'description': 'Verbal and physical altercation.', 'status': 'Under Investigation', 'officer_name': 'Officer Khan', 'crime_date': '2023-02-10'},
    {'id': 4, 'name': 'Vandalism on Main Street', 'description': 'Graffiti on public property.', 'status': 'Arrest Made', 'officer_name': 'Officer Patel', 'crime_date': '2023-03-15'},
    {'id': 5, 'name': 'Missing Person Report', 'description': 'Child reported missing from home.', 'status': 'Open', 'officer_name': 'Officer Mehmood', 'crime_date': '2023-04-20'},
]

next_record_id = max([r['id'] for r in mock_records_db]) + 1 if mock_records_db else 1

def login_user(username, password):
    """
    Simulates logging in a user by checking credentials against mock_users_db.
    In a real app, this would query your Users table.
    """
    for user in mock_users_db:
        if user['username'] == username and check_password_hash(user['password_hash'], password):
            return True
    return False

def fetch_all_records():
    """
    Simulates fetching all criminal records.
    In a real app, this would be a SELECT * FROM CriminalRecords.
    """
    return sorted(mock_records_db, key=lambda x: x['id'])

def fetch_record_by_id(record_id):
    """
    Simulates fetching a single criminal record by ID.
    """
    return next((r for r in mock_records_db if r['id'] == record_id), None)

def add_record(name, description, status, officer_name, crime_date):
    """
    Simulates adding a new criminal record.
    In a real app, this would be an INSERT statement.
    """
    global next_record_id
    new_record = {
        'id': next_record_id,
        'name': name,
        'description': description,
        'status': status,
        'officer_name': officer_name,
        'crime_date': crime_date # Assuming date is passed as 'YYYY-MM-DD' string
    }
    mock_records_db.append(new_record)
    next_record_id += 1
    return new_record

def update_record(record_id, name, description, status, officer_name, crime_date):
    """
    Simulates updating an existing criminal record.
    In a real app, this would be an UPDATE statement.
    """
    for i, record in enumerate(mock_records_db):
        if record['id'] == record_id:
            mock_records_db[i]['name'] = name
            mock_records_db[i]['description'] = description
            mock_records_db[i]['status'] = status
            mock_records_db[i]['officer_name'] = officer_name
            mock_records_db[i]['crime_date'] = crime_date
            return True
    return False

def delete_record(record_id):
    """
    Simulates deleting a criminal record.
    In a real app, this would be a DELETE statement.
    """
    global mock_records_db
    initial_len = len(mock_records_db)
    mock_records_db = [r for r in mock_records_db if r['id'] != record_id]
    return len(mock_records_db) < initial_len # True if a record was deleted

def search_records(name=None, officer_name=None, status=None):
    """
    Simulates searching and filtering criminal records.
    In a real app, this would be a SELECT with WHERE clauses.
    """
    results = mock_records_db
    
    if name:
        results = [r for r in results if name.lower() in r['name'].lower()]
    if officer_name:
        results = [r for r in results if officer_name.lower() in r['officer_name'].lower()]
    if status:
        results = [r for r in results if r['status'].lower() == status.lower()]
    
    return sorted(results, key=lambda x: x['id'])

# Example of adding a user if you wanted to add programmatically (not used by app.py)
def register_user(username, password):
    """
    Simulates registering a new user.
    """
    if any(u['username'] == username for u in mock_users_db):
        return False # User already exists
    mock_users_db.append({'username': username, 'password_hash': generate_password_hash(password)})
    return True