from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

#login user
VALID_USERNAME = "admin"
VALID_PASSWORD = "admin"

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        return redirect(url_for('records'))
    else:
        return render_template('login.html', error="Invalid credentials")
    
#records page
@app.route('/records')
def records():
    dummy_data= [
        {"id": 1, "name": "Case A", "description": "Robbery", "date": "2023-01-01", "status": "Open"},
        {"id": 2, "name": "Case B", "description": "Theft", "date": "2023-01-05", "status": "Closed"},
    ]
    return render_template('records.html', records=dummy_data)

#queries page
@app.route('/queries')
def queries():
    return render_template('queries.html')

if __name__ == '__main__':
    app.run(debug=True)