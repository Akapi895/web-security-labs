"""
SQLi-003: Arithmetic-based SQL Injection Detection
Vulnerable Corporate Directory Application (MSSQL)

WARNING: This application is intentionally vulnerable for educational purposes.
DO NOT use this code in production!
"""

from flask import Flask, request, render_template_string
import pyodbc
import os

app = Flask(__name__)

# Database configuration
MSSQL_HOST = os.environ.get('MSSQL_HOST', 'localhost')
MSSQL_USER = os.environ.get('MSSQL_USER', 'sa')
MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD', 'YourStrong@Passw0rd')
MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE', 'corporate')

def get_db_connection():
    conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={MSSQL_HOST};DATABASE={MSSQL_DATABASE};UID={MSSQL_USER};PWD={MSSQL_PASSWORD};TrustServerCertificate=yes'
    return pyodbc.connect(conn_str)

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corporate Directory</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #f0f2f5;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #0078d4 0%, #004578 100%);
            padding: 25px;
            text-align: center;
            color: #fff;
        }
        .header h1 { font-size: 2.2em; }
        .header p { color: rgba(255,255,255,0.8); margin-top: 5px; }
        .container { max-width: 900px; margin: 0 auto; padding: 30px 20px; }
        .employee-list {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .employee-list h2 {
            background: #0078d4;
            color: #fff;
            padding: 15px 20px;
        }
        .employee-item {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }
        .employee-item:hover { background: #f5f5f5; }
        .employee-item .avatar {
            width: 50px;
            height: 50px;
            background: #0078d4;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-weight: bold;
            margin-right: 15px;
        }
        .employee-item .info { flex: 1; }
        .employee-item .name { font-weight: bold; color: #333; }
        .employee-item .position { color: #666; font-size: 0.9em; }
        .employee-item a {
            background: #0078d4;
            color: #fff;
            padding: 8px 20px;
            border-radius: 5px;
            text-decoration: none;
        }
        .profile-card {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
            text-align: center;
        }
        .profile-card .avatar {
            width: 100px;
            height: 100px;
            background: #0078d4;
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 2.5em;
            font-weight: bold;
        }
        .profile-card h2 { color: #333; margin-bottom: 5px; }
        .profile-card .position { color: #0078d4; margin-bottom: 20px; }
        .profile-card .details {
            text-align: left;
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
        }
        .profile-card .detail-item {
            display: flex;
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }
        .profile-card .detail-item:last-child { border-bottom: none; }
        .profile-card .detail-item .label {
            width: 120px;
            font-weight: bold;
            color: #666;
        }
        .error-box {
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            color: #b91c1c;
        }
        .hint-box {
            background: #fffbeb;
            border: 1px solid #fbbf24;
            border-radius: 8px;
            padding: 15px 20px;
            margin: 20px 0;
            color: #92400e;
        }
        .back-btn {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 25px;
            background: #6b7280;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏢 Corporate Directory</h1>
        <p>Employee Information System</p>
    </div>
    
    <div class="container">
        <div class="hint-box">
            💡 <strong>Lab Hint:</strong> The employee profile page uses an ID parameter. 
            Try testing with arithmetic operations like <code>/1</code>, <code>/0</code>, <code>*1</code>, or <code>-0</code>
        </div>
        
        {% if error %}
        <div class="error-box">
            <strong>⚠️ Database Error:</strong><br>
            {{ error }}
        </div>
        {% endif %}
        
        {% if employee %}
        <div class="profile-card">
            <div class="avatar">{{ employee[1][0] }}{{ employee[2][0] }}</div>
            <h2>{{ employee[1] }} {{ employee[2] }}</h2>
            <div class="position">{{ employee[5] }}</div>
            <div class="details">
                <div class="detail-item">
                    <span class="label">Department:</span>
                    <span>{{ employee[4] }}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Email:</span>
                    <span>{{ employee[3] }}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Phone:</span>
                    <span>{{ employee[6] }}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Hire Date:</span>
                    <span>{{ employee[7] }}</span>
                </div>
            </div>
            <a href="/" class="back-btn">← Back to Directory</a>
        </div>
        {% elif not error %}
        <div class="employee-list">
            <h2>👥 All Employees</h2>
            {% for emp in employees %}
            <div class="employee-item">
                <div class="avatar">{{ emp[1][0] }}{{ emp[2][0] }}</div>
                <div class="info">
                    <div class="name">{{ emp[1] }} {{ emp[2] }}</div>
                    <div class="position">{{ emp[5] }} - {{ emp[4] }}</div>
                </div>
                <a href="/profile?id={{ emp[0] }}">View Profile</a>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    employees = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        pass
    
    return render_template_string(HOME_TEMPLATE, employees=employees, employee=None, error=None)

@app.route('/profile')
def profile():
    emp_id = request.args.get('id', '')
    employee = None
    error = None
    
    if emp_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # VULNERABLE: Direct string concatenation - SQL Injection possible!
            sql = f"SELECT * FROM employees WHERE id = {emp_id}"
            
            cursor.execute(sql)
            employee = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
        except pyodbc.Error as err:
            # VULNERABLE: Exposing detailed MSSQL error messages
            error = str(err)
    
    return render_template_string(HOME_TEMPLATE, employees=[], employee=employee, error=error)

@app.route('/health')
def health():
    return {'status': 'ok', 'database': 'MSSQL'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
