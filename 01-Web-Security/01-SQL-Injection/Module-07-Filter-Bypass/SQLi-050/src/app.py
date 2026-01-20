"""SQLi-050: MSSQL Double URL Encoding Bypass"""
from flask import Flask, request, render_template_string
from urllib.parse import unquote
import pyodbc
import os

app = Flask(__name__)

DB_CONFIG = {
    'server': os.environ.get('MSSQL_HOST', 'localhost'),
    'user': os.environ.get('MSSQL_USER', 'sa'),
    'password': os.environ.get('MSSQL_PASSWORD', 'YourStrong@Passw0rd'),
    'database': os.environ.get('MSSQL_DATABASE', 'searchdb')
}

def get_connection():
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['user']};PWD={DB_CONFIG['password']};TrustServerCertificate=yes"
    return pyodbc.connect(conn_str)

def waf_check(user_input):
    """WAF that checks AFTER first decode"""
    if "'" in user_input or '"' in user_input or '--' in user_input:
        return False, "SQL injection attempt detected!"
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔎 Product Search</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #3a1c71, #d76d77, #ffaf7b); min-height: 100vh; color: #fff; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .box { background: rgba(0,0,0,0.3); padding: 30px; border-radius: 15px; }
        input { width: 100%; padding: 15px; border: none; border-radius: 8px; margin-bottom: 15px; }
        button { padding: 15px 30px; background: #fff; color: #333; border: none; border-radius: 8px; cursor: pointer; }
        .error { background: rgba(220,53,69,0.3); padding: 15px; border-radius: 8px; margin: 15px 0; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔎 Product Search</h1>
        <div class="box">
            <form method="GET" action="/search">
                <input type="text" name="q" placeholder="Search..." value="{{ query or '' }}">
                <button type="submit">Search</button>
            </form>
            {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
            {% if results %}
            <table>
                <tr><th>ID</th><th>Name</th><th>Description</th></tr>
                {% for r in results %}
                <tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td></tr>
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

@app.route('/search')
def search():
    # First decode happens automatically by Flask
    q = request.args.get('q', '')
    results = None
    error = None
    
    if q:
        # WAF check on first-decoded input
        is_safe, waf_error = waf_check(q)
        if not is_safe:
            return render_template_string(TEMPLATE, query=q, results=None, error=waf_error)
        
        # Second decode (vulnerable behavior)
        q_decoded = unquote(q)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = f"SELECT id, name, description FROM products WHERE name LIKE '%{q_decoded}%'"
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, query=q, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
