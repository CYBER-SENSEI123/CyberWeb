from flask import Flask, request, render_template_string, redirect, session, send_from_directory
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'any-secret-key'

USERS_FILE = 'users.json'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure folders/files exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump([], f)
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# ------------------- Helpers -------------------
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------- Templates -------------------
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
<!DOCTYPE html>
<html>
<head>
<title>Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { font-family:'Courier New', monospace; margin:0; padding:0; background:linear-gradient(135deg,#1f1c2c,#928dab); color:#fff; }
.top-bar { background:#2c2a3c; padding:12px 20px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 6px rgba(0,0,0,0.4); position:sticky; top:0; z-index:100; }
.top-bar img { border-radius:50%; width:40px; margin-right:10px; vertical-align:middle; }
.top-bar button { background:#444; color:#fff; border:none; padding:8px 16px; cursor:pointer; margin-left:8px; border-radius:5px; font-weight:bold; transition:0.3s; }
.top-bar button:hover { background:#666; }
.grid { display:grid; grid-template-columns: repeat(2,1fr); gap:20px; padding:30px; }
.block { background:#fff; color:#333; padding:50px 0; text-align:center; border-radius:12px; font-weight:bold; font-size:18px; cursor:pointer; box-shadow:0 4px 10px rgba(0,0,0,0.3); transition:0.3s; text-decoration:none; display:flex; align-items:center; justify-content:center; }
.block:hover { transform:translateY(-5px); box-shadow:0 6px 15px rgba(0,0,0,0.35); }
@media(max-width:600px){ .grid{ grid-template-columns: 1fr; padding:15px; } .block{ padding:40px 0; font-size:16px; } }
</style>
</head>
<body>
<div class="top-bar">
    <div>
        {% if profile_pic %}
            <img src="/uploads/{{ profile_pic }}">
        {% endif %}
        Welcome, {{ username }}
    </div>
    <div>
        <button onclick="location.href='/'">Dashboard</button>
        <button onclick="location.href='/profile'">Profile</button>
        <button onclick="location.href='/logout'">Logout</button>
    </div>
</div>
<div class="grid">
    <a class="block" href="/kali">Kali Linux</a>
    <a class="block" href="/termux">Termux</a>
    <a class="block" href="/terminal">Terminal</a>
    <a class="block" href="/other">Other</a>
</div>
</body>
</html>

"""

page_template = """
<!DOCTYPE html>
<html>
<head>
<title>{{ title }}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { font-family:'Courier New', monospace; margin:0; padding:0; background:linear-gradient(135deg,#1f1c2c,#928dab); color:#fff; }
.top-bar { background:#2c2a3c; padding:12px 20px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 6px rgba(0,0,0,0.4); position:sticky; top:0; z-index:100; }
.top-bar button { background:#444; color:#fff; border:none; padding:8px 16px; cursor:pointer; margin-left:8px; border-radius:5px; font-weight:bold; transition:0.3s; }
.top-bar button:hover { background:#666; }
.content { padding:30px; max-width:900px; margin:auto; line-height:1.5; }
.content h2 { margin-top:0; }
.content ul { list-style-type:square; margin-left:20px; }
.connect { margin-top:40px; padding:20px; background:#fff; color:#333; border-radius:8px; box-shadow:0 3px 8px rgba(0,0,0,0.2); display:flex; flex-wrap:wrap; align-items:center; gap:15px; }
.connect a { color:#1a73e8; text-decoration:none; font-weight:bold; padding:6px 12px; background:#eee; border-radius:5px; transition:0.2s; }
.connect a:hover { background:#ddd; text-decoration:none; }
@media(max-width:600px){ .content{ padding:15px; } .connect{ flex-direction:column; } }
</style>
</head>
<body>
<div class="top-bar">
    <div>{{ title }}</div>
 <div>
    <button onclick="location.href='/profile'">Profile</button>
    <button onclick="location.href='/logout'">Logout</button>
</div>
</div>
<div class="content">
    {{ content|safe }}
    <div class="connect">
        <h3>Connect with us:</h3>
        <a href="mailto:support@ktmundzimwe@gmail.com">Email</a>
        <a href="https://twitter.com">Twitter</a>
        <a href="https://github.com">GitHub</a>
        <a href="https://wa.me/263783870518" target="_blank">WhatsApp</a>
    </div>
</div>
</body>
</html>
"""

# ------------------- Routes -------------------
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
        users.append({'username':u,'password':p})
        save_users(users)
        return redirect('/login')
    return register_html

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u = request.form['username']
        p = request.form['password']
        users = load_users()
        user = next((user for user in users if user['username']==u and user['password']==p), None)
        if user:
            session['username'] = u
            return redirect('/dashboard')
        return "Invalid login!"
    return login_html

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    users = load_users()
    user = next(u for u in users if u['username']==session['username'])
    profile_pic = user.get('profile_pic', None)
    return render_template_string(dashboard_html, username=session['username'], profile_pic=profile_pic)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

# ------------------- Profile & Upload -------------------
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/login')
    users = load_users()
    user = next(u for u in users if u['username']==session['username'])
    pic_html = ""
    if 'profile_pic' in user:
        pic_html = f"<img src='/uploads/{user['profile_pic']}' width='120' style='border-radius:50%;'><br>"
    content = f"""
        {pic_html}
        <p>Username: {user['username']}</p>
        <a href='/upload_pic'>Change Profile Picture</a>
    """
    return render_template_string(page_template, title="Profile", content=content)

@app.route('/upload_pic', methods=['GET','POST'])
def upload_pic():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file selected"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(session['username'] + "_" + file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            users = load_users()
            for user in users:
                if user['username'] == session['username']:
                    user['profile_pic'] = filename
            save_users(users)
            return redirect('/profile')
    return '''
    <h2>Upload Profile Picture</h2>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="image/*"><br><br>
        <button type="submit">Upload</button>
    </form>
    <a href='/profile'>Back</a>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------- Content Pages -------------------
@app.route('/termux')
def termux():
    if 'username' not in session:
        return redirect('/login')
    content = """
    <h2>Termux</h2>
    <p>Termux commands & tricks:</p>
    <ul>
        <li>pkg install python</li>
        <li>apt update && apt upgrade</li>
        <li>ls, cd, mkdir - standard Linux commands</li>
        <li>termux-setup-storage - grant storage access</li>
        <li>pip install &lt;package&gt; - install Python packages</li>
        <li>ssh user@host - connect via SSH</li>
    </ul>
    """
    return render_template_string(page_template, title="Termux", content=content)


@app.route('/terminal')
def terminal():
    if 'username' not in session:
        return redirect('/login')
    content = """
    <h2>Terminal</h2>
    <p>Terminal shortcuts and tips:</p>
    <ul>
        <li>Ctrl+C - stop process</li>
        <li>Ctrl+Z - pause process</li>
        <li>history - show command history</li>
        <li>man &lt;command&gt; - show manual</li>
        <li>grep 'text' file - search text in files</li>
        <li>top - monitor running processes</li>
    </ul>
    """
    return render_template_string(page_template, title="Terminal", content=content)


@app.route('/other')
def other():
    if 'username' not in session:
        return redirect('/login')
    content = """
    <h2>Other</h2>
    <p>Miscellaneous tips & tools:</p>
    <ul>
        <li>vim/nano - text editors</li>
        <li>wget/curl - download files</li>
        <li>git clone &lt;repo&gt; - clone repositories</li>
        <li>htop - advanced process manager</li>
        <li>curl ifconfig.me - check public IP</li>
    </ul>
    """
    return render_template_string(page_template, title="Other", content=content)


@app.route('/kali')
def kali():
    if 'username' not in session:
        return redirect('/login')
    content = """
    <h2>Kali Linux</h2>
    <p>Some common Kali Linux commands:</p>
    <ul>
        <li>ifconfig / ip addr - show network interfaces</li>
        <li>nmap &lt;target&gt; - scan networks</li>
        <li>hydra -l user -P passlist.txt host service</li>
        <li>aircrack-ng capture.cap - crack Wi-Fi (on your own network)</li>
        <li>msfconsole - start Metasploit</li>
    </ul>
    """
    return render_template_string(page_template, title="Kali Linux", content=content)
# ------------------- Run App -------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or default 5000
    app.run(host="0.0.0.0", port=port)