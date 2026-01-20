"""SQLi-037: MSSQL OOB DNS via xp_fileexist/xp_subdirs"""
from flask import Flask, request, render_template_string
import pyodbc
import os

app = Flask(__name__)

DB_CONFIG = {
    'server': os.environ.get('MSSQL_HOST', 'localhost'),
    'user': os.environ.get('MSSQL_USER', 'sa'),
    'password': os.environ.get('MSSQL_PASSWORD', 'YourStr0ng!Passw0rd'),
    'database': os.environ.get('MSSQL_DATABASE', 'reporting')
}

def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['user']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate=yes"
    )
    return pyodbc.connect(conn_str)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 Report Management System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #4a0e4e 0%, #2d1b69 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; }
        .hint {
            background: rgba(156, 39, 176, 0.3);
            border-left: 4px solid #9c27b0;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 20px;
        }
        .nav { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #ce93d8; text-decoration: none; margin: 0 10px; }
        .result { background: rgba(255,255,255,0.05); padding: 30px; border-radius: 12px; text-align: center; }
        .success { color: #81c784; }
        .info { margin-top: 20px; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Report Management System</h1>
        <div class="hint">
            <strong>💡 Lab:</strong> MSSQL OOB DNS via xp_fileexist/xp_subdirs
        </div>
        <div class="nav">
            Reports: <a href="?id=1">Q4 Sales</a> | <a href="?id=2">Security Audit</a> | <a href="?id=3">HR</a>
        </div>
        <div class="result">
            <p class="success">✅ Report query executed successfully.</p>
        </div>
        <div class="info">
            <strong>Note:</strong> xp_dirtree restricted. Alternative: <code>xp_fileexist</code>, <code>xp_subdirs</code>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/report')
def report():
    rid = request.args.get('id', '1')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = f"SELECT title, category FROM reports WHERE id = {rid}"
        print(f"[DEBUG] SQL: {sql}", flush=True)
        cursor.execute(sql)
        cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
    
    return render_template_string(TEMPLATE)

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
