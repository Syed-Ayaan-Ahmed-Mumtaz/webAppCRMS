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
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Invalid credentials")

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
