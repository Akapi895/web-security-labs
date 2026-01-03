"""SQLi-006: Version Query Fingerprinting (PostgreSQL)"""

from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://app_user:app_password@localhost:5432/authdb')

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login Portal</title>
    <style>
        body { font-family: Arial; background: #2c3e50; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .login-box { background: #fff; padding: 40px; border-radius: 10px; width: 350px; }
        h2 { text-align: center; color: #333; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #3498db; color: #fff; border: none; border-radius: 5px; cursor: pointer; }
        .error { background: #fee; padding: 15px; margin: 15px 0; border-radius: 5px; color: #c00; font-family: monospace; font-size: 12px; white-space: pre-wrap; }
        .success { background: #dfd; padding: 15px; margin: 15px 0; border-radius: 5px; color: #060; }
        .hint { background: #ffc; padding: 10px; margin: 15px 0; border-radius: 5px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔐 Login</h2>
        <div class="hint">💡 Try version queries: @@version, version(), etc.</div>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" value="{{ username or '' }}">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        {% if success %}<div class="success">{{ success }}</div>{% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    success = None
    username = ''
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            # VULNERABLE
            sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result:
                success = f"Welcome, {result[1]}! Role: {result[3]}"
            else:
                error = "Invalid credentials"
            
            cursor.close()
            conn.close()
        except psycopg2.Error as err:
            error = f"Database Error:\\n{str(err)}"
    
    return render_template_string(TEMPLATE, error=error, success=success, username=username)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
