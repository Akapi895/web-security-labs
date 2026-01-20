"""SQLi-049: MySQL Quote Filter Bypass with Hex Encoding"""
from flask import Flask, request, render_template_string
import pymysql
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'appuser'),
    'password': os.environ.get('MYSQL_PASSWORD', 'apppass123'),
    'database': os.environ.get('MYSQL_DATABASE', 'logindb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def waf_check(user_input):
    """WAF that blocks quote characters"""
    if "'" in user_input or '"' in user_input:
        return False, "Quote characters are blocked!"
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔐 Login Portal</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: #fff; padding: 40px; }
        .container { max-width: 500px; margin: 0 auto; }
        .box { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; }
        input { width: 100%; padding: 15px; border: none; border-radius: 8px; margin-bottom: 15px; }
        button { width: 100%; padding: 15px; background: #fff; color: #764ba2; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .error { background: rgba(220,53,69,0.3); padding: 15px; border-radius: 8px; margin: 15px 0; }
        .success { background: rgba(40,167,69,0.3); padding: 15px; border-radius: 8px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align:center">🔐 Login Portal</h1>
        <div class="box">
            <form method="GET" action="/login">
                <input type="text" name="user" placeholder="Username" value="{{ user or '' }}">
                <input type="password" name="pass" placeholder="Password">
                <button type="submit">Login</button>
            </form>
            {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
            {% if success %}<div class="success">✅ {{ success }}</div>{% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, user=None, error=None, success=None)

@app.route('/login')
def login():
    user = request.args.get('user', '')
    password = request.args.get('pass', '')
    error = None
    success = None
    
    if user:
        # WAF Check - Block quotes
        is_safe, waf_error = waf_check(user)
        if not is_safe:
            return render_template_string(TEMPLATE, user=user, error=waf_error, success=None)
        
        is_safe, waf_error = waf_check(password)
        if not is_safe:
            return render_template_string(TEMPLATE, user=user, error=waf_error, success=None)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # VULNERABLE: Numeric context allows hex bypass
            sql = f"SELECT id, username, password FROM users WHERE username = '{user}' AND password = '{password}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result:
                success = f"Welcome {result[1]}! Password: {result[2]}"
            else:
                error = "Invalid credentials"
            
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, user=user, error=error, success=success)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
