"""SQLi-036: MSSQL OOB DNS Exfiltration via xp_dirtree"""
from flask import Flask, request, render_template_string
import pyodbc
import os

app = Flask(__name__)

DB_CONFIG = {
    'server': os.environ.get('MSSQL_HOST', 'localhost'),
    'user': os.environ.get('MSSQL_USER', 'sa'),
    'password': os.environ.get('MSSQL_PASSWORD', 'YourStr0ng!Passw0rd'),
    'database': os.environ.get('MSSQL_DATABASE', 'corpintranet')
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
    <title>🏢 CorpNet Intranet</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            min-height: 100vh;
            color: #ecf0f1;
            padding: 40px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #bdc3c7; font-size: 1.1em; }
        .hint {
            background: rgba(52, 152, 219, 0.2);
            border-left: 4px solid #3498db;
            padding: 15px 20px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 30px;
        }
        .hint-title { color: #3498db; font-weight: bold; margin-bottom: 5px; }
        .nav-links {
            background: rgba(255,255,255,0.1);
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .nav-links a {
            color: #3498db;
            text-decoration: none;
            margin: 0 10px;
            padding: 5px 15px;
            border-radius: 4px;
            transition: all 0.3s;
        }
        .nav-links a:hover {
            background: rgba(52, 152, 219, 0.3);
            color: #fff;
        }
        .content-box {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .status-msg {
            color: #2ecc71;
            text-align: center;
            padding: 20px;
            font-size: 1.1em;
        }
        .system-info {
            margin-top: 30px;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            font-size: 0.9em;
            color: #95a5a6;
        }
        .system-info code {
            background: rgba(255,255,255,0.1);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏢 CorpNet Intranet</h1>
            <p class="subtitle">Corporate Employee Directory</p>
        </header>
        
        <div class="hint">
            <div class="hint-title">💡 Lab: MSSQL OOB DNS via xp_dirtree</div>
            <p>Kỹ thuật: xp_dirtree với UNC path để DNS exfiltration</p>
        </div>
        
        <div class="nav-links">
            👤 Employees: 
            <a href="?id=1">John</a> |
            <a href="?id=2">Jane</a> |
            <a href="?id=3">Bob</a> |
            <a href="?id=4">Alice</a> |
            <a href="?id=5">Charlie</a>
        </div>
        
        <div class="content-box">
            <!-- Response is always the same - stacked queries with xp_dirtree for OOB -->
            <p class="status-msg">✅ Employee query processed successfully.</p>
        </div>
        
        <div class="system-info">
            <strong>🖥️ System Info:</strong><br>
            Domain: CORP.LOCAL | Database: MSSQL 2019<br>
            <code>xp_dirtree: ENABLED</code> | <code>Stacked Queries: SUPPORTED</code>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/employee')
def employee():
    eid = request.args.get('id', '1')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE: SQL Injection with stacked queries support
        # Response always same - need OOB via xp_dirtree
        sql = f"SELECT name, department, email FROM employees WHERE id = {eid}"
        print(f"[DEBUG] Executing SQL: {sql}", flush=True)
        cursor.execute(sql)
        result = cursor.fetchone()  # Result ignored
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", flush=True)
    
    # Always return same response
    return render_template_string(TEMPLATE)

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
