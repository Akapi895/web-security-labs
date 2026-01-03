"""SQLi-023: PostgreSQL Boolean Blind - SUBSTRING Extraction"""
from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DATABASE', 'userdb')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>👤 Username Validator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { text-align: center; color: rgba(255,255,255,0.8); margin-bottom: 30px; }
        .hint {
            background: rgba(255,255,255,0.2);
            border-left: 4px solid #fff;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .check-box {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 15px;
            background: #fff;
            color: #764ba2;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { opacity: 0.9; }
        .result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 1.2em;
        }
        .result.taken { background: rgba(220,53,69,0.3); }
        .result.available { background: rgba(40,167,69,0.3); }
    </style>
</head>
<body>
    <div class="container">
        <h1>👤 Username Validator</h1>
        <p class="subtitle">Check if your username is available</p>
        
        <div class="hint">
            💡 <strong>Lab:</strong> PostgreSQL Boolean Blind SQLi - SUBSTRING Extraction
        </div>
        
        <div class="check-box">
            <form method="GET" action="/check">
                <div class="form-group">
                    <label>Enter Username:</label>
                    <input type="text" name="username" placeholder="e.g., john_doe" value="{{ username or '' }}">
                </div>
                <button type="submit">🔍 Check Availability</button>
            </form>
            
            {% if result is not none %}
            <div class="result {{ 'taken' if result else 'available' }}">
                {% if result %}
                ❌ Username "<strong>{{ username }}</strong>" is taken!
                {% else %}
                ✅ Username "<strong>{{ username }}</strong>" is available!
                {% endif %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, username=None, result=None)

@app.route('/check')
def check():
    username = request.args.get('username', '')
    result = None
    
    if username:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # VULNERABLE: Boolean Blind SQLi
            sql = f"SELECT 1 FROM users WHERE username = '{username}'"
            cursor.execute(sql)
            row = cursor.fetchone()
            result = row is not None  # True = taken, False = available
            cursor.close()
            conn.close()
        except Exception:
            result = False  # Hide errors, return "available"
    
    return render_template_string(TEMPLATE, username=username, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
