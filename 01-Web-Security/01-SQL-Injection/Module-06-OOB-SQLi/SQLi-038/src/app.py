"""SQLi-038: Oracle OOB HTTP via UTL_HTTP"""
from flask import Flask, request, render_template_string
import cx_Oracle
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('ORACLE_HOST', 'localhost'),
    'port': os.environ.get('ORACLE_PORT', '1521'),
    'service': os.environ.get('ORACLE_SERVICE', 'XEPDB1'),
    'user': os.environ.get('ORACLE_USER', 'app_user'),
    'password': os.environ.get('ORACLE_PASSWORD', 'AppPass123')
}

def get_connection():
    dsn = cx_Oracle.makedsn(DB_CONFIG['host'], DB_CONFIG['port'], service_name=DB_CONFIG['service'])
    return cx_Oracle.connect(DB_CONFIG['user'], DB_CONFIG['password'], dsn)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>☕ Java Enterprise CRM</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #c62828 0%, #ad1457 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; }
        .hint {
            background: rgba(255,87,34,0.3);
            border-left: 4px solid #ff5722;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 20px;
        }
        .nav { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #ffab91; text-decoration: none; margin: 0 10px; }
        .result { background: rgba(255,255,255,0.05); padding: 30px; border-radius: 12px; text-align: center; }
        .success { color: #a5d6a7; }
        .info { margin-top: 20px; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>☕ Java Enterprise CRM</h1>
        <div class="hint">
            <strong>💡 Lab:</strong> Oracle OOB HTTP via UTL_HTTP.REQUEST
        </div>
        <div class="nav">
            Customers: <a href="?id=1">Acme</a> | <a href="?id=2">TechStart</a> | <a href="?id=3">Global</a>
        </div>
        <div class="result">
            <p class="success">✅ Customer query processed.</p>
        </div>
        <div class="info">
            <strong>System:</strong> Oracle 21c XE | UTL_HTTP: Enabled | ACL: Configured
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/customer')
def customer():
    cid = request.args.get('id', '1')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = f"SELECT name, email, tier FROM customers WHERE id = {cid}"
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
