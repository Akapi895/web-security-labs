"""SQLi-051: MySQL AND/OR Filter Bypass"""
from flask import Flask, request, render_template_string
import pymysql
import os
import re

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'appuser'),
    'password': os.environ.get('MYSQL_PASSWORD', 'apppass123'),
    'database': os.environ.get('MYSQL_DATABASE', 'productdb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def waf_check(user_input):
    """WAF that blocks AND/OR keywords"""
    if re.search(r'\b(and|or)\b', user_input, re.IGNORECASE):
        return False, "AND/OR keywords are blocked!"
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🛍️ Products</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #11998e, #38ef7d); min-height: 100vh; color: #fff; padding: 40px; }
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
        <h1>🛍️ Product Catalog</h1>
        <div class="box">
            <form method="GET" action="/product">
                <input type="text" name="id" placeholder="Product ID..." value="{{ query or '' }}">
                <button type="submit">View Product</button>
            </form>
            {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
            {% if results %}
            <table>
                <tr><th>ID</th><th>Name</th><th>Price</th></tr>
                {% for r in results %}
                <tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>${{ r[2] }}</td></tr>
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

@app.route('/product')
def product():
    pid = request.args.get('id', '')
    results = None
    error = None
    
    if pid:
        is_safe, waf_error = waf_check(pid)
        if not is_safe:
            return render_template_string(TEMPLATE, query=pid, results=None, error=waf_error)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = f"SELECT id, name, price FROM products WHERE id = {pid}"
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, query=pid, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
