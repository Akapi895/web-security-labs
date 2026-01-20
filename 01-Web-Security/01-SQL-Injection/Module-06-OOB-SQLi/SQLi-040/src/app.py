"""SQLi-040: Oracle OOB HTTP via HTTPURITYPE"""
from flask import Flask, request, render_template_string
import cx_Oracle
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('ORACLE_HOST', 'localhost'),
    'port': os.environ.get('ORACLE_PORT', '1521'),
    'service': os.environ.get('ORACLE_SERVICE', 'XEPDB1'),
    'user': os.environ.get('ORACLE_USER', 'invoice_user'),
    'password': os.environ.get('ORACLE_PASSWORD', 'InvoicePass123')
}

def get_connection():
    dsn = cx_Oracle.makedsn(DB_CONFIG['host'], DB_CONFIG['port'], service_name=DB_CONFIG['service'])
    return cx_Oracle.connect(DB_CONFIG['user'], DB_CONFIG['password'], dsn)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>💰 Invoice System</title>
    <style>
        body { font-family: sans-serif; background: #004d40; color: #fff; padding: 40px; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { text-align: center; }
        .hint { background: rgba(0,150,136,0.3); padding: 15px; border-radius: 8px; margin: 20px 0; }
        .result { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 8px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 Invoice System</h1>
        <div class="hint">💡 Lab: Oracle OOB HTTP via HTTPURITYPE</div>
        <div class="result">✅ Invoice query processed.</div>
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/invoice')
def invoice():
    iid = request.args.get('id', '1')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT customer, amount FROM invoices WHERE id = {iid}")
        cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
    return render_template_string(TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
