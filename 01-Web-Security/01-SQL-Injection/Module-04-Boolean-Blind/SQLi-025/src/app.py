"""SQLi-025: MySQL Boolean Blind via Cookie"""
from flask import Flask, request, render_template_string, redirect, url_for
import pymysql
import os
import secrets

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'rootpass'),
    'database': os.environ.get('MYSQL_DATABASE', 'analyticsdb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 Analytics Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2.5em; margin-bottom: 30px; }
        .hint {
            background: rgba(255,255,255,0.1);
            border-left: 4px solid #00d2ff;
            padding: 15px;
            margin-bottom: 20px;
        }
        .welcome {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
        }
        .welcome.returning { border: 2px solid #28a745; }
        .welcome.new { border: 2px solid #ffc107; }
        .views { font-size: 2em; color: #00d2ff; margin: 20px 0; }
        .login-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #00d2ff;
            color: #000;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        .login-link:hover { background: #00a8cc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Analytics Dashboard</h1>
        <div class="hint">💡 Lab: MySQL Boolean Blind via Cookie (tracking_id)</div>
        <div class="welcome {{ 'returning' if is_returning else 'new' }}">
            {% if is_returning %}
            <h2>👋 Welcome back!</h2>
            <div class="views">{{ page_views }} page views</div>
            {% else %}
            <h2>🆕 Welcome, new visitor!</h2>
            <p>Set your tracking_id cookie to track your visits.</p>
            <a href="/login" class="login-link">🔐 Admin Login</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔐 Admin Login</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { max-width: 400px; width: 100%; }
        h1 { text-align: center; font-size: 2.5em; margin-bottom: 30px; }
        .login-box {
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 15px;
            border: 2px solid #00d2ff;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 5px;
            background: rgba(255,255,255,0.9);
            color: #000;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #00d2ff;
            color: #000;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { background: #00a8cc; }
        .error {
            background: rgba(255,0,0,0.2);
            border-left: 4px solid #ff0000;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .hint {
            background: rgba(255,255,255,0.1);
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Admin Login</h1>
        <div class="login-box">
            {% if error %}
            <div class="error">❌ {{ error }}</div>
            {% endif %}
            <form method="POST" action="/authenticate">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            <div class="hint">💡 Hint: Check the database for admin credentials</div>
        </div>
    </div>
</body>
</html>
'''

SUCCESS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>✅ Login Success</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { max-width: 600px; width: 100%; }
        h1 { text-align: center; font-size: 2.5em; margin-bottom: 30px; }
        .success-box {
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 15px;
            border: 2px solid #28a745;
        }
        .cookie-display {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }
        .cookie-label {
            color: #00d2ff;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .cookie-value {
            color: #28a745;
            font-size: 18px;
            user-select: all;
        }
        .copy-btn {
            width: 100%;
            padding: 12px;
            background: #00d2ff;
            color: #000;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        .copy-btn:hover { background: #00a8cc; }
        .info {
            background: rgba(255,255,255,0.1);
            border-left: 4px solid #00d2ff;
            padding: 15px;
            margin-top: 20px;
            font-size: 14px;
        }
        .home-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #302b63;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }
        .home-link:hover { background: #24243e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ Login Successful!</h1>
        <div class="success-box">
            <h2 style="text-align: center; margin-top: 0;">Welcome, {{ username }}!</h2>
            <p style="text-align: center;">Your tracking cookie has been generated:</p>
            
            <div class="cookie-display">
                <div class="cookie-label">🍪 Tracking Cookie:</div>
                <div class="cookie-value" id="cookieValue">{{ tracking_id }}</div>
                <button class="copy-btn" onclick="copyCookie()">📋 Copy Cookie</button>
            </div>
            
            <div class="info">
                ✅ <strong>Cookie Automatically Set!</strong><br>
                The tracking cookie has been saved to your browser automatically.<br>
                Click "Back to Dashboard" to see your tracking status.<br><br>
                💡 <strong>For manual exploitation:</strong><br>
                Use this cookie value in your tools:<br>
                <code style="color: #00d2ff;">curl -b "tracking_id={{ tracking_id }}" http://localhost:5025/</code>
            </div>
            
            <a href="/" class="home-link">🏠 Back to Dashboard</a>
        </div>
    </div>
    
    <script>
        function copyCookie() {
            const cookieValue = document.getElementById('cookieValue').textContent;
            navigator.clipboard.writeText(cookieValue).then(() => {
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '✅ Copied!';
                setTimeout(() => {
                    btn.textContent = '📋 Copy Cookie';
                }, 2000);
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    tracking_id = request.cookies.get('tracking_id', '')
    is_returning = False
    page_views = 0
    
    if tracking_id:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # VULNERABLE: Cookie value used directly in SQL
            sql = f"SELECT page_views FROM tracking WHERE tracking_id = '{tracking_id}'"
            cursor.execute(sql)
            row = cursor.fetchone()
            if row:
                is_returning = True
                page_views = row[0]
            cursor.close()
            conn.close()
        except:
            pass
    
    return render_template_string(TEMPLATE, is_returning=is_returning, page_views=page_views)

@app.route('/login')
def login():
    error = request.args.get('error', '')
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if not username or not password:
        return redirect(url_for('login', error='Please provide both username and password'))
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validate credentials
        sql = "SELECT username, role FROM admin_users WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, password))
        row = cursor.fetchone()
        
        if row:
            # Generate or retrieve tracking ID for this user
            tracking_id = secrets.token_urlsafe(16)
            
            # Insert the tracking ID into the database
            insert_sql = "INSERT INTO tracking (tracking_id, page_views) VALUES (%s, 1)"
            cursor.execute(insert_sql, (tracking_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # Show success page with the tracking cookie
            response = render_template_string(SUCCESS_TEMPLATE, username=row[0], tracking_id=tracking_id)
            # Set cookie automatically in browser
            resp = app.make_response(response)
            resp.set_cookie('tracking_id', tracking_id, max_age=3600*24*7)  # Cookie valid for 7 days
            return resp
        else:
            cursor.close()
            conn.close()
            return redirect(url_for('login', error='Invalid username or password'))
            
    except Exception as e:
        return redirect(url_for('login', error='Database error occurred'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
