"""SQLi-044: PostgreSQL Whitespace Filter Bypass"""
from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os
import re

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DATABASE', 'apidb')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# WAF: Block ALL whitespace characters
def waf_check(user_input):
    """WAF that blocks all whitespace characters"""
    # Match any whitespace: space, tab, newline, carriage return, etc.
    if re.search(r'\s', user_input):
        return False, "Whitespace characters are not allowed in API requests."
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔌 SecureAPI - User Management</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { text-align: center; color: rgba(255,255,255,0.7); margin-bottom: 30px; }
        .warning {
            background: rgba(255,193,7,0.2);
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .api-box {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
        .endpoint {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            margin: 10px 0;
        }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
            font-family: monospace;
        }
        button {
            padding: 15px 30px;
            background: #7c3aed;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover { background: #6d28d9; }
        .error {
            background: rgba(220,53,69,0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 4px solid #dc3545;
        }
        .result {
            background: rgba(0,0,0,0.4);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .json-key { color: #7dd3fc; }
        .json-value { color: #86efac; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 SecureAPI</h1>
        <p class="subtitle">Enterprise User Management API v2.0</p>
        
        <div class="warning">
            🛡️ <strong>Protected API:</strong> All whitespace characters are filtered for security.
        </div>
        
        <div class="api-box">
            <h3>📡 API Endpoints</h3>
            <div class="endpoint">GET /api/user?id={user_id}</div>
            <div class="endpoint">GET /api/users</div>
            
            <form method="GET" action="/api/user" style="margin-top: 20px;">
                <label>User ID:</label>
                <input type="text" name="id" placeholder="Enter user ID (e.g., 1)" value="{{ user_id or '' }}">
                <button type="submit">🔍 Fetch User</button>
            </form>
            
            {% if error %}
            <div class="error">⚠️ {{ error }}</div>
            {% endif %}
            
            {% if result %}
            <div class="result">{{ result }}</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, user_id=None, result=None, error=None)

@app.route('/api/user')
def get_user():
    user_id = request.args.get('id', '')
    result = None
    error = None
    
    if user_id:
        # WAF Check - Block all whitespace
        is_safe, waf_error = waf_check(user_id)
        if not is_safe:
            return render_template_string(TEMPLATE, user_id=user_id, result=None, error=waf_error)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # VULNERABLE: SQL Injection (whitespace filter can be bypassed with parentheses)
            sql = f"SELECT id, username, email, status FROM users WHERE id = {user_id}"
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            if rows:
                result_data = []
                for row in rows:
                    result_data.append({
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "status": row[3]
                    })
                result = str(result_data)
            else:
                result = "No user found"
            
            cursor.close()
            conn.close()
        except Exception as e:
            error = f"Query error: {str(e)}"
    
    return render_template_string(TEMPLATE, user_id=user_id, result=result, error=error)

@app.route('/api/users')
def get_users():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, status FROM users")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        users = [{"id": r[0], "username": r[1], "email": r[2], "status": r[3]} for r in rows]
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
