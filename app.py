from flask import Flask, request, render_template_string, redirect, jsonify
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'any-secret-key'

# users.json file path
USERS_FILE = 'users.json'

# create users.json if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump([], f)

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# HTML templates inside Python
home_html = """
<h1>Home Page</h1>
<a href='/login'>Login</a> | <a href='/register'>Register</a>
"""

register_html = """
<h1>Register</h1>
<form method='POST'>
<input name='username' placeholder='Username' required><br>
<input name='password' placeholder='Password' type='password' required><br>
<button type='submit'>Register</button>
</form>
<a href='/login'>Already have an account? Login</a>
"""

login_html = """
<h1>Login</h1>
<form method='POST'>
<input name='username' placeholder='Username' required><br>
<input name='password' placeholder='Password' type='password' required><br>
<button type='submit'>Login</button>
</form>
<a href='/register'>Don't have an account? Register</a>
"""

dashboard_html = """
<h1>Dashboard</h1>
<p>Welcome, {{ username }}!</p>
<a href='/'>Logout</a>
"""

@app.route('/')
def home():
    return home_html

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        users = load_users()
        if any(user['username']==u for user in users):
            return "User exists!"
        users.append({'username': u, 'password': p})
        save_users(users)
        return redirect('/login')
    return register_html

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        users = load_users()
        user = next((user for user in users if user['username']==u and user['password']==p), None)
        if user:
            return render_template_string(dashboard_html, username=u)
        return "Invalid login!"
    return login_html

if __name__ == '__main__':
    # run server on your local network IP
    import socket
    host_ip = socket.gethostbyname(socket.gethostname())
    app.run(host=host_ip, port=5000, debug=True)