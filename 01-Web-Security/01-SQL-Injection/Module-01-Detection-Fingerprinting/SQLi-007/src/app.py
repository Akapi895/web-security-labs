"""SQLi-007: Time-based DBMS Fingerprinting (MSSQL)"""

from flask import Flask, request, jsonify, render_template_string
import pyodbc
import os

app = Flask(__name__)

MSSQL_HOST = os.environ.get('MSSQL_HOST', 'localhost')
MSSQL_USER = os.environ.get('MSSQL_USER', 'sa')
MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD', 'YourStrong@Passw0rd')
MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE', 'apidb')

def get_connection():
    conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={MSSQL_HOST};DATABASE={MSSQL_DATABASE};UID={MSSQL_USER};PWD={MSSQL_PASSWORD};TrustServerCertificate=yes'
    return pyodbc.connect(conn_str)

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>User API</title>
    <style>
        body { font-family: monospace; background: #1a1a2e; color: #eee; padding: 40px; }
        .container { max-width: 800px; margin: auto; }
        h1 { color: #0ff; }
        .endpoint { background: #16213e; padding: 20px; border-radius: 8px; margin: 15px 0; }
        code { background: #0f3460; padding: 5px 10px; border-radius: 4px; }
        .hint { background: #3c3c00; padding: 15px; border-radius: 5px; margin: 15px 0; color: #ff0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 User API</h1>
        <div class="hint">💡 Hint: Try time-based fingerprinting: SLEEP(), WAITFOR DELAY, pg_sleep()</div>
        <div class="endpoint">
            <strong>GET</strong> <code>/api/user?id={user_id}</code>
            <p>Returns user information by ID</p>
        </div>
        <p>Example: <a href="/api/user?id=1">/api/user?id=1</a></p>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/api/user')
def get_user():
    user_id = request.args.get('id', '')
    
    if not user_id:
        return jsonify({"error": "ID required"}), 400
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE - supports stacked queries
        sql = f"SELECT * FROM users WHERE id = {user_id}"
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return jsonify({"id": result[0], "username": result[1], "email": result[2], "status": result[3]})
        return jsonify({"message": "User not found"})
    except Exception as e:
        # No error message exposed - blind scenario
        return jsonify({"message": "User not found"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
