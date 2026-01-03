"""
SQLi-001: Quote-based SQL Injection Detection
Vulnerable E-commerce Search Application

WARNING: This application is intentionally vulnerable for educational purposes.
DO NOT use this code in production!
"""

from flask import Flask, request, render_template_string
import mysql.connector
import os

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'app_user'),
    'password': os.environ.get('MYSQL_PASSWORD', 'app_password'),
    'database': os.environ.get('MYSQL_DATABASE', 'ecommerce')
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TechShop - E-commerce</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 { color: #00d4ff; font-size: 2.5em; }
        .header p { color: #888; margin-top: 5px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .search-box {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .search-box h2 { margin-bottom: 20px; color: #00d4ff; }
        .search-form { display: flex; gap: 10px; }
        .search-input {
            flex: 1;
            padding: 15px 20px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .search-input::placeholder { color: #888; }
        .search-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #00d4ff, #0099cc);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .search-btn:hover { transform: scale(1.05); }
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        .product-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s;
        }
        .product-card:hover { transform: translateY(-5px); }
        .product-card h3 { color: #00d4ff; margin-bottom: 10px; }
        .product-card .price { 
            font-size: 1.5em; 
            color: #4ade80; 
            margin: 10px 0;
        }
        .product-card .category {
            display: inline-block;
            padding: 5px 12px;
            background: rgba(0,212,255,0.2);
            border-radius: 20px;
            font-size: 0.85em;
            color: #00d4ff;
        }
        .product-card .stock { color: #888; margin-top: 10px; }
        .error-box {
            background: rgba(255,0,0,0.1);
            border: 1px solid rgba(255,0,0,0.3);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            color: #ff6b6b;
        }
        .no-results {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        .hint-box {
            background: rgba(255,193,7,0.1);
            border: 1px solid rgba(255,193,7,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            color: #ffc107;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛒 TechShop</h1>
        <p>Your favorite electronics store</p>
    </div>
    <div class="container">
        <div class="search-box">
            <h2>🔍 Search Products</h2>
            <form class="search-form" action="/search" method="GET">
                <input type="text" name="q" class="search-input" 
                       placeholder="Search for products... (try: laptop, mouse, keyboard)"
                       value="{{ query or '' }}">
                <button type="submit" class="search-btn">Search</button>
            </form>
            <div class="hint-box">
                💡 <strong>Lab Hint:</strong> This search function might be vulnerable to SQL Injection. 
                Try testing with special characters!
            </div>
        </div>
        
        {% if error %}
        <div class="error-box">
            <strong>⚠️ Database Error:</strong><br>
            {{ error }}
        </div>
        {% endif %}
        
        {% if products %}
        <div class="products-grid">
            {% for product in products %}
            <div class="product-card">
                <h3>{{ product[1] }}</h3>
                <p>{{ product[2][:100] }}...</p>
                <div class="price">${{ "%.2f"|format(product[3]) }}</div>
                <span class="category">{{ product[4] }}</span>
                <div class="stock">📦 {{ product[5] }} in stock</div>
            </div>
            {% endfor %}
        </div>
        {% elif query and not error %}
        <div class="no-results">
            <h3>No products found for "{{ query }}"</h3>
            <p>Try a different search term</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, products=None, query=None, error=None)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    products = None
    error = None
    
    if query:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # VULNERABLE: Direct string concatenation - SQL Injection possible!
            sql = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
            
            cursor.execute(sql)
            products = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
        except mysql.connector.Error as err:
            # VULNERABLE: Exposing detailed error messages
            error = str(err)
    
    return render_template_string(HOME_TEMPLATE, products=products, query=query, error=error)

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
