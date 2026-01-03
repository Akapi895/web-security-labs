"""SQLi-029: MySQL Time-based Blind - SLEEP/BENCHMARK"""
from flask import Flask, request, render_template_string
import pymysql
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'rootpass'),
    'database': os.environ.get('MYSQL_DATABASE', 'webshop'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🛒 WebShop</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; }
        .hint { background: rgba(255,193,7,0.2); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .product { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; }
        .msg { color: #888; text-align: center; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 WebShop</h1>
        <div class="hint">💡 Lab: MySQL Time-based Blind (SLEEP/BENCHMARK)</div>
        <p>Products: <a href="?id=1">1</a> | <a href="?id=2">2</a> | <a href="?id=3">3</a></p>
        <div class="product">
            <!-- Response is always the same regardless of query result -->
            <p class="msg">Product information loaded.</p>
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
        # VULNERABLE: Time-based blind - no output difference
        sql = f"SELECT name, price FROM products WHERE id = {pid}"
        cursor.execute(sql)
        cursor.fetchone()  # Result ignored - same response always
        cursor.close()
        conn.close()
    except:
        pass
    
    # Always return same response - only time differs
    return render_template_string(TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
