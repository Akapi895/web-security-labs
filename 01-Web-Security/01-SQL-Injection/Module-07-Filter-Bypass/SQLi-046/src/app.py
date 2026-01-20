"""SQLi-046: MySQL SELECT Filter Bypass with Version Comments"""
from flask import Flask, request, render_template_string
import pymysql
import os
import re

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'appuser'),
    'password': os.environ.get('MYSQL_PASSWORD', 'apppass123'),
    'database': os.environ.get('MYSQL_DATABASE', 'inventorydb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def waf_check(user_input):
    """WAF that blocks SELECT keyword"""
    if re.search(r'select', user_input, re.IGNORECASE):
        return False, "SELECT keyword is blocked by WAF!"
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📦 Inventory Management</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; }
        .box {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        button {
            width: 100%;
            padding: 15px;
            background: #2ecc71;
            color: #fff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .error { background: rgba(220,53,69,0.3); padding: 15px; border-radius: 8px; margin: 15px 0; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Inventory Management</h1>
        <div class="box">
            <form method="GET" action="/inventory">
                <input type="text" name="item" placeholder="Search inventory..." value="{{ query or '' }}">
                <button type="submit">🔍 Search</button>
            </form>
            {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
            {% if results %}
            <table>
                <tr><th>ID</th><th>Item</th><th>Quantity</th><th>Location</th></tr>
                {% for r in results %}
                <tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td><td>{{ r[3] }}</td></tr>
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

@app.route('/inventory')
def inventory():
    item = request.args.get('item', '')
    results = None
    error = None
    
    if item:
        is_safe, waf_error = waf_check(item)
        if not is_safe:
            return render_template_string(TEMPLATE, query=item, results=None, error=waf_error)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = f"SELECT id, item_name, quantity, location FROM inventory WHERE item_name LIKE '%{item}%'"
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, query=item, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
