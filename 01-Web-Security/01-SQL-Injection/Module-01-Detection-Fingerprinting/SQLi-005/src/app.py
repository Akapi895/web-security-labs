"""
SQLi-005: Error-based DBMS Fingerprinting
"""

from flask import Flask, request, render_template_string
import mysql.connector
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'shop_user'),
    'password': os.environ.get('MYSQL_PASSWORD', 'shop_password'),
    'database': os.environ.get('MYSQL_DATABASE', 'shopdb')
}

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>TechShop Search</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; padding: 40px; }
        .container { max-width: 800px; margin: auto; background: #fff; padding: 30px; border-radius: 10px; }
        h1 { color: #333; }
        input[type="text"] { padding: 12px; width: 300px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 12px 25px; background: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer; }
        .error { background: #fee; border: 1px solid #fcc; padding: 15px; margin: 20px 0; border-radius: 5px; color: #c00; font-family: monospace; white-space: pre-wrap; }
        .item { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .hint { background: #ffc; padding: 15px; margin: 20px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 TechShop Search</h1>
        <form method="GET" action="/search">
            <input type="text" name="q" value="{{ query or '' }}" placeholder="Search products...">
            <button type="submit">Search</button>
        </form>
        <div class="hint">💡 Hint: Try to fingerprint the database by analyzing error messages!</div>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        {% for item in items %}
        <div class="item">
            <strong>{{ item[1] }}</strong> - ${{ item[3] }}<br>
            <small>{{ item[2] }}</small>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(TEMPLATE, items=[], query=None, error=None)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    items = []
    error = None
    
    if query:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # VULNERABLE
            sql = f"SELECT * FROM items WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
            cursor.execute(sql)
            items = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            # Expose detailed error for fingerprinting
            error = f"Database Error:\n{str(err)}"
    
    return render_template_string(TEMPLATE, items=items, query=query, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
