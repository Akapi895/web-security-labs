"""SQLi-022: PostgreSQL Union-based - Multi Row (STRING_AGG)"""
from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DATABASE', 'corporate')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🏢 Corporate Directory</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #11998e, #38ef7d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { text-align: center; color: #aaa; margin-bottom: 30px; }
        .hint {
            background: linear-gradient(90deg, rgba(17,153,142,0.2), rgba(56,239,125,0.2));
            border-left: 4px solid #38ef7d;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .dept-nav {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .dept-nav h3 { margin-bottom: 15px; }
        .dept-links { display: flex; gap: 10px; flex-wrap: wrap; }
        .dept-links a {
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 8px;
            color: #38ef7d;
            text-decoration: none;
            transition: background 0.2s;
        }
        .dept-links a:hover { background: rgba(255,255,255,0.2); }
        .dept-info {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .dept-info h2 { color: #38ef7d; margin-bottom: 5px; }
        .dept-info .location { color: #888; }
        .employees {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
        }
        .employees h3 { color: #38ef7d; margin-bottom: 15px; }
        .employee {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .employee .info .name { font-weight: bold; color: #fff; }
        .employee .info .email { color: #888; font-size: 0.9em; }
        .employee .position { color: #38ef7d; font-size: 0.9em; }
        .error {
            background: rgba(220,53,69,0.2);
            border-left: 4px solid #dc3545;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .no-results { color: #888; text-align: center; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 Corporate Directory</h1>
        <p class="subtitle">Employee Management System</p>
        
        <div class="hint">
            💡 <strong>Lab:</strong> PostgreSQL Union-based SQLi - Multi Row (STRING_AGG)
        </div>
        
        <div class="dept-nav">
            <h3>📁 Departments</h3>
            <div class="dept-links">
                <a href="/department?id=1">Engineering</a>
                <a href="/department?id=2">Marketing</a>
                <a href="/department?id=3">HR</a>
                <a href="/department?id=4">Finance</a>
            </div>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% elif department %}
        <div class="dept-info">
            <h2>{{ department.name }}</h2>
            <p class="location">📍 {{ department.location }}</p>
        </div>
        
        <div class="employees">
            <h3>👥 Employees ({{ employees|length }})</h3>
            {% for emp in employees %}
            <div class="employee">
                <div class="info">
                    <div class="name">{{ emp.name }}</div>
                    <div class="email">{{ emp.email }}</div>
                </div>
                <div class="position">{{ emp.position }}</div>
            </div>
            {% endfor %}
            {% if not employees %}
            <div class="no-results">No employees in this department</div>
            {% endif %}
        </div>
        {% elif id %}
        <div class="dept-info">
            <div class="no-results">Department not found</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, id=None, department=None, employees=[], error=None)

@app.route('/department')
def department():
    dept_id = request.args.get('id', '')
    department = None
    employees = []
    error = None
    
    if dept_id:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Get department info
            cursor.execute(f"SELECT id, name, location FROM departments WHERE id = {dept_id}")
            row = cursor.fetchone()
            if row:
                department = {'id': row[0], 'name': row[1], 'location': row[2]}
            
            # VULNERABLE: Get employees - returns multiple rows
            sql = f"SELECT name, email, position FROM employees WHERE department_id = {dept_id}"
            cursor.execute(sql)
            rows = cursor.fetchall()
            employees = [{'name': r[0], 'email': r[1], 'position': r[2]} for r in rows]
            
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, id=dept_id, department=department, employees=employees, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
