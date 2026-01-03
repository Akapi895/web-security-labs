"""SQLi-008: Concatenation-based DBMS Fingerprinting (Oracle)"""

from flask import Flask, request, jsonify, render_template_string
import oracledb
import os

app = Flask(__name__)

ORACLE_HOST = os.environ.get('ORACLE_HOST', 'localhost')
ORACLE_PORT = os.environ.get('ORACLE_PORT', '1521')
ORACLE_SERVICE = os.environ.get('ORACLE_SERVICE', 'XEPDB1')
ORACLE_USER = os.environ.get('ORACLE_USER', 'app_user')
ORACLE_PASSWORD = os.environ.get('ORACLE_PASSWORD', 'app_password')

def get_connection():
    dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"
    return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn)

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Service Query API</title>
    <style>
        body { font-family: Consolas; background: #2d2d2d; color: #f0f0f0; padding: 40px; }
        .container { max-width: 800px; margin: auto; }
        h1 { color: #c74634; }
        .endpoint { background: #1a1a1a; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #c74634; }
        code { background: #0a0a0a; padding: 3px 8px; border-radius: 3px; color: #ffcc00; }
        .hint { background: #3c3c00; padding: 15px; border-radius: 5px; margin: 15px 0; color: #ffcc00; }
        input, button { padding: 10px; margin: 5px; }
        input { width: 200px; }
        button { background: #c74634; color: #fff; border: none; cursor: pointer; }
        .response { background: #1a1a1a; padding: 15px; margin: 15px 0; border-radius: 5px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔴 Oracle Service API</h1>
        <div class="hint">💡 Hint: Different DBMSs use different concatenation syntax: || vs + vs CONCAT()</div>
        <div class="endpoint">
            <strong>GET</strong> <code>/api/service?name={service_name}</code>
        </div>
        <form action="/api/service" method="GET">
            <input type="text" name="name" placeholder="Service name...">
            <button type="submit">Query</button>
        </form>
        {% if result %}
        <div class="response">{{ result }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, result=None)

@app.route('/api/service')
def get_service():
    name = request.args.get('name', '')
    
    if not name:
        return jsonify({"error": "Name required"}), 400
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE
        sql = f"SELECT * FROM services WHERE name = '{name}'"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if result:
            services = [{"id": r[0], "name": r[1], "description": r[2], "status": r[3]} for r in result]
            return jsonify({"services": services})
        return jsonify({"services": []})
    except oracledb.Error as e:
        return jsonify({"error": str(e), "database": "Oracle"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
