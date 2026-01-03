"""SQLi-027: MySQL Boolean Blind via ORDER BY"""
from flask import Flask, request, render_template_string
import pymysql
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'rootpass'),
    'database': os.environ.get('MYSQL_DATABASE', 'shopdb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🛍️ Product Shop</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; }
        .hint {
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .sort-bar {
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .sort-bar a {
            color: #fff;
            margin-right: 15px;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 4px;
        }
        .sort-bar a:hover, .sort-bar a.active { background: rgba(255,255,255,0.2); }
        .product {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }
        .product .name { font-weight: bold; }
        .product .price { color: #ffc107; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛍️ Product Shop</h1>
        <div class="hint">💡 Lab: MySQL Boolean Blind via ORDER BY</div>
        <div class="sort-bar">
            Sort by:
            <a href="?sort=name">Name</a>
            <a href="?sort=price">Price</a>
            <a href="?sort=rating">Rating</a>
        </div>
        {% for p in products %}
        <div class="product">
            <span class="name">{{ p.name }}</span>
            <span class="price">${{ p.price }} | ⭐{{ p.rating }}</span>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/products')
def products():
    sort_col = request.args.get('sort', 'name')
    products = []
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE: ORDER BY injection
        sql = f"SELECT name, price, rating FROM products ORDER BY {sort_col}"
        cursor.execute(sql)
        rows = cursor.fetchall()
        products = [{'name': r[0], 'price': r[1], 'rating': r[2]} for r in rows]
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()

    
    return render_template_string(TEMPLATE, products=products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
