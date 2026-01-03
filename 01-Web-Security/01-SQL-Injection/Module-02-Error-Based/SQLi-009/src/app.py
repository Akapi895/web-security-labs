"""SQLi-009: MySQL EXTRACTVALUE() Error-based SQLi"""
from flask import Flask, request, render_template_string
import mysql.connector
import os

app = Flask(__name__)
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'app_user'),
    'password': os.environ.get('MYSQL_PASSWORD', 'app_password'),
    'database': os.environ.get('MYSQL_DATABASE', 'shopdb')
}

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>TechShop - Product Details</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .product { background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .product h2 { margin: 0 0 10px 0; color: #007bff; }
        .price { font-size: 24px; color: #28a745; font-weight: bold; }
        .error { background: #fee; padding: 15px; border-radius: 5px; color: #c00; font-family: monospace; white-space: pre-wrap; margin: 20px 0; }
        .hint { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        a { color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 TechShop</h1>
        <div class="hint">💡 Lab: Error-based SQLi với EXTRACTVALUE()</div>
        <p>Products: 
            <a href="?id=1">Product 1</a> | 
            <a href="?id=2">Product 2</a> | 
            <a href="?id=3">Product 3</a>
        </p>
        {% if error %}
        <div class="error">⚠️ Database Error:\n{{ error }}</div>
        {% endif %}
        {% if product %}
        <div class="product">
            <h2>{{ product[1] }}</h2>
            <p>{{ product[2] }}</p>
            <p class="price">${{ "%.2f"|format(product[3]) }}</p>
            <p>Category: {{ product[4] }} | Stock: {{ product[5] }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/product')
def product():
    product_id = request.args.get('id', '1')
    product = None
    error = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # VULNERABLE
        sql = f"SELECT * FROM products WHERE id = '{product_id}'"
        cursor.execute(sql)
        product = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        error = str(err)
    return render_template_string(TEMPLATE, product=product, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
