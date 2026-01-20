"""SQLi-042: PostgreSQL OOB HTTP via dblink"""
from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DB', 'productdb')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🛍️ Product Catalog</title>
    <style>
        body { font-family: sans-serif; background: #5d4037; color: #fff; padding: 40px; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { text-align: center; }
        .hint { background: rgba(121,85,72,0.5); padding: 15px; border-radius: 8px; margin: 20px 0; }
        .nav { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #bcaaa4; text-decoration: none; margin: 0 10px; }
        .result { background: rgba(255,255,255,0.05); padding: 30px; border-radius: 8px; text-align: center; }
        .info { margin-top: 20px; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛍️ Product Catalog</h1>
        <div class="hint">💡 Lab: PostgreSQL OOB HTTP via dblink Extension</div>
        <div class="nav">
            Products: <a href="?id=1">Laptop</a> | <a href="?id=2">Mouse</a> | <a href="?id=3">USB Hub</a>
        </div>
        <div class="result">✅ Product query processed.</div>
        <div class="info">
            <strong>Extensions:</strong> dblink (enabled) | Stacked Queries: ON
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/product')
def product():
    pid = request.args.get('id', '1')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = f"SELECT name, price, category FROM products WHERE id = {pid}"
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
