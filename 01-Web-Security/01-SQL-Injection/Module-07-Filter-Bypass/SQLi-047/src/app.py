"""SQLi-047: MSSQL Double Keyword Bypass"""
from flask import Flask, request, render_template_string
import pyodbc
import os
import re

app = Flask(__name__)

DB_CONFIG = {
    'server': os.environ.get('MSSQL_HOST', 'localhost'),
    'user': os.environ.get('MSSQL_USER', 'sa'),
    'password': os.environ.get('MSSQL_PASSWORD', 'YourStrong@Passw0rd'),
    'database': os.environ.get('MSSQL_DATABASE', 'employeedb')
}

def get_connection():
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['user']};PWD={DB_CONFIG['password']};TrustServerCertificate=yes"
    return pyodbc.connect(conn_str)

def waf_sanitize(user_input):
    """WAF that REMOVES (not blocks) UNION and SELECT keywords"""
    # Remove UNION (case-insensitive)
    sanitized = re.sub(r'union', '', user_input, flags=re.IGNORECASE)
    # Remove SELECT (case-insensitive)
    sanitized = re.sub(r'select', '', sanitized, flags=re.IGNORECASE)
    return sanitized

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🏢 Employee Directory</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; }
        .box {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
        }
        .alert { background: rgba(255,193,7,0.2); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        input[type="text"] { width: 100%; padding: 15px; border: none; border-radius: 8px; margin-bottom: 15px; }
        button { padding: 15px 30px; background: #3498db; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        .error { background: rgba(220,53,69,0.3); padding: 15px; border-radius: 8px; margin: 15px 0; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 Employee Directory</h1>
        <div class="box">
            <div class="alert">🛡️ <strong>Enterprise WAF:</strong> SQL keywords are sanitized for security.</div>
            <form method="GET" action="/employee">
                <input type="text" name="id" placeholder="Employee ID..." value="{{ query or '' }}">
                <button type="submit">🔍 Search</button>
            </form>
            {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
            {% if results %}
            <table>
                <tr><th>ID</th><th>Name</th><th>Department</th><th>Salary</th></tr>
                {% for r in results %}
                <tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td><td>${{ r[3] }}</td></tr>
                {% endfor %}
            </table>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, query=None, results=None, error=None)

@app.route('/employee')
def employee():
    emp_id = request.args.get('id', '')
    results = None
    error = None
    
    if emp_id:
        # WAF sanitize - removes UNION and SELECT
        sanitized = waf_sanitize(emp_id)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = f"SELECT id, name, department, salary FROM employees WHERE id = {sanitized}"
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, query=emp_id, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
