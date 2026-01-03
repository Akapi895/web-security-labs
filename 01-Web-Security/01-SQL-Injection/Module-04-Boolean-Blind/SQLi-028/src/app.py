"""SQLi-028: MSSQL Boolean Blind via Dynamic Column"""
from flask import Flask, request, render_template_string
import pyodbc
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MSSQL_HOST', 'localhost'),
    'user': os.environ.get('MSSQL_USER', 'sa'),
    'password': os.environ.get('MSSQL_PASSWORD', 'YourStrong@Passw0rd'),
    'database': os.environ.get('MSSQL_DATABASE', 'exportdb')
}

def get_connection():
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_CONFIG['host']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['user']};PWD={DB_CONFIG['password']};TrustServerCertificate=yes"
    return pyodbc.connect(conn_str)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 Data Export</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #232526 0%, #414345 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; }
        .hint {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .column-select {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .column-select a {
            color: #00d2ff;
            margin-right: 15px;
        }
        .data-row {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Data Export</h1>
        <div class="hint">💡 Lab: MSSQL Boolean Blind via Dynamic Column</div>
        <div class="column-select">
            Export column:
            <a href="?column=report_name">Report Name</a>
            <a href="?column=created_by">Created By</a>
            <a href="?column=status">Status</a>
        </div>
        {% for row in data %}
        <div class="data-row">{{ row }}</div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/export')
def export():
    column = request.args.get('column', 'report_name')
    data = []
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE: Dynamic column injection
        sql = f"SELECT {column} FROM reports"
        cursor.execute(sql)
        rows = cursor.fetchall()
        data = [row[0] for row in rows]
        cursor.close()
        conn.close()
    except:
        pass
    
    return render_template_string(TEMPLATE, data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
