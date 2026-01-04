"""SQLi-035: MySQL OOB DNS Exfiltration via LOAD_FILE"""
from flask import Flask, request, render_template_string
import pymysql
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'webapp',          # User bạn đã tạo có quyền FILE
    'password': 'password123', # Password bạn đã đặt
    'database': 'corpdb',     # Tên DB bạn đã tạo
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🏢 CorpTech Enterprise Solutions</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #a0c4ff; font-size: 1.1em; }
        .hint {
            background: rgba(255,193,7,0.15);
            border-left: 4px solid #ffc107;
            padding: 15px 20px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 30px;
        }
        .hint-title { color: #ffc107; font-weight: bold; margin-bottom: 5px; }
        .product-nav {
            background: rgba(255,255,255,0.1);
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .product-nav a {
            color: #a0c4ff;
            text-decoration: none;
            margin: 0 10px;
            padding: 5px 15px;
            border-radius: 4px;
            transition: all 0.3s;
        }
        .product-nav a:hover {
            background: rgba(255,255,255,0.2);
            color: #fff;
        }
        .content-box {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status-msg {
            color: #90EE90;
            text-align: center;
            padding: 20px;
            font-size: 1.1em;
        }
        .tech-info {
            margin-top: 30px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            font-size: 0.9em;
            color: #ccc;
        }
        .tech-info code {
            background: rgba(255,255,255,0.1);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏢 CorpTech Enterprise Solutions</h1>
            <p class="subtitle">Enterprise IT Infrastructure Products</p>
        </header>
        
        <div class="hint">
            <div class="hint-title">💡 Lab: MySQL OOB DNS Exfiltration</div>
            <p>Kỹ thuật: LOAD_FILE() với UNC path để trigger DNS lookup</p>
        </div>
        
        <div class="product-nav">
            📦 Products: 
            <a href="?id=1">Server</a> |
            <a href="?id=2">Switch</a> |
            <a href="?id=3">Firewall</a> |
            <a href="?id=4">Storage</a> |
            <a href="?id=5">Backup</a>
        </div>
        
        <div class="content-box">
            <!-- Response is always the same - no output difference -->
            <p class="status-msg">✅ Product catalog query processed successfully.</p>
        </div>
        
        <div class="tech-info">
            <strong>🖥️ System Info:</strong><br>
            Server: Windows Server 2019 | Database: MySQL 8.0<br>
            <code>FILE_PRIV: ON</code> | <code>secure_file_priv: NULL</code>
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
        # VULNERABLE: SQL Injection - response always same (OOB required)
        sql = f"SELECT name, description, price FROM products WHERE id = {pid}"
        print(f"[DEBUG] Executing SQL: {sql}", flush=True)
        cursor.execute(sql)
        result = cursor.fetchone()  # Result ignored - same response always
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", flush=True)
    
    # Always return same response - only OOB channel can exfiltrate data
    return render_template_string(TEMPLATE)

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
