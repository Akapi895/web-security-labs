"""SQLi-020: Oracle Union-based - Single Column (|| Operator)"""
from flask import Flask, request, render_template_string
import oracledb
import os

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('ORACLE_HOST', 'localhost'),
    'port': os.environ.get('ORACLE_PORT', '1521'),
    'service': os.environ.get('ORACLE_SERVICE', 'XEPDB1'),
    'user': os.environ.get('ORACLE_USER', 'app_user'),
    'password': os.environ.get('ORACLE_PASSWORD', 'app_password')
}

def get_connection():
    dsn = f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['service']}"
    return oracledb.connect(user=DB_CONFIG['user'], password=DB_CONFIG['password'], dsn=dsn)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📄 Invoice Lookup</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #f093fb, #f5576c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { text-align: center; color: #888; margin-bottom: 30px; }
        .search-box {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
        .hint {
            background: linear-gradient(90deg, rgba(240,147,251,0.2), rgba(245,87,108,0.2));
            border-left: 4px solid #f093fb;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .invoice-links {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .invoice-links a {
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 8px;
            color: #f093fb;
            text-decoration: none;
            transition: background 0.2s;
        }
        .invoice-links a:hover { background: rgba(255,255,255,0.2); }
        .result {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
        }
        .result h2 { margin-bottom: 15px; color: #f093fb; }
        .invoice-number {
            font-size: 1.5em;
            font-weight: bold;
            color: #f5576c;
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .error {
            background: rgba(220,53,69,0.2);
            border-left: 4px solid #dc3545;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            font-family: monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .no-results { color: #888; text-align: center; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 Invoice Lookup</h1>
        <p class="subtitle">Enterprise Billing System</p>
        
        <div class="hint">
            💡 <strong>Lab:</strong> Oracle Union-based SQLi - Single Column (|| Operator)
        </div>
        
        <div class="search-box">
            <p style="margin-bottom: 15px;">Select an invoice to view:</p>
            <div class="invoice-links">
                <a href="/invoice?id=1">INV-2024-001</a>
                <a href="/invoice?id=2">INV-2024-002</a>
                <a href="/invoice?id=3">INV-2024-003</a>
                <a href="/invoice?id=4">INV-2024-004</a>
                <a href="/invoice?id=5">INV-2024-005</a>
            </div>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% elif invoice_number %}
        <div class="result">
            <h2>📋 Invoice Details</h2>
            <div class="invoice-number">{{ invoice_number }}</div>
        </div>
        {% elif id %}
        <div class="result">
            <div class="no-results">No invoice found with ID: {{ id }}</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, id=None, invoice_number=None, error=None)

@app.route('/invoice')
def invoice():
    inv_id = request.args.get('id', '')
    invoice_number = None
    error = None
    
    if inv_id:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # VULNERABLE: Direct string concatenation
            # Chỉ SELECT invoice_number (1 column)
            sql = f"SELECT invoice_number FROM invoices WHERE id = {inv_id}"
            cursor.execute(sql)
            row = cursor.fetchone()
            if row:
                invoice_number = row[0]
            cursor.close()
            conn.close()
        except oracledb.Error as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, id=inv_id, invoice_number=invoice_number, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
