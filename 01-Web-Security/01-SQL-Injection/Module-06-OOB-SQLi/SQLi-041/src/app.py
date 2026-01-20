"""SQLi-041: PostgreSQL OOB DNS via COPY TO PROGRAM"""
from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DB', 'userdb')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>👤 User Directory</title>
    <style>
        body { font-family: sans-serif; background: #37474f; color: #fff; padding: 40px; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { text-align: center; }
        .hint { background: rgba(96,125,139,0.5); padding: 15px; border-radius: 8px; margin: 20px 0; }
        .nav { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #80cbc4; text-decoration: none; margin: 0 10px; }
        .result { background: rgba(255,255,255,0.05); padding: 30px; border-radius: 8px; text-align: center; }
        .info { margin-top: 20px; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>👤 User Directory</h1>
        <div class="hint">💡 Lab: PostgreSQL OOB DNS via COPY TO PROGRAM</div>
        <div class="nav">
            Users: <a href="?id=1">John</a> | <a href="?id=2">Jane</a> | <a href="?id=3">Bob</a>
        </div>
        <div class="result">✅ User query processed.</div>
        <div class="info">
            <strong>System:</strong> PostgreSQL 15 | User: postgres (superuser) | Stacked Queries: ON
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/user')
def user():
    uid = request.args.get('id', '1')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = f"SELECT username, email, role FROM users WHERE id = {uid}"
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
