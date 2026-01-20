"""SQLi-043: MySQL Space Filter Bypass"""
from flask import Flask, request, render_template_string
import pymysql
import os
import re

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'appuser'),
    'password': os.environ.get('MYSQL_PASSWORD', 'apppass123'),
    'database': os.environ.get('MYSQL_DATABASE', 'shopdb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

# WAF: Block spaces in query parameter
def waf_check(user_input):
    """Simple WAF that blocks space characters"""
    if ' ' in user_input:
        return False, "Invalid characters detected! Space is not allowed."
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🛒 TechShop - Product Search</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { text-align: center; color: rgba(255,255,255,0.7); margin-bottom: 30px; }
        .warning {
            background: rgba(255,193,7,0.2);
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .search-box {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
        }
        button {
            width: 100%;
            padding: 15px;
            background: #0d6efd;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { background: #0b5ed7; }
        .error {
            background: rgba(220,53,69,0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 4px solid #dc3545;
        }
        .results {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            overflow: hidden;
        }
        .results h3 {
            background: rgba(255,255,255,0.1);
            padding: 15px 20px;
            margin: 0;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 20px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { background: rgba(255,255,255,0.05); }
        tr:hover { background: rgba(255,255,255,0.05); }
        .no-results { padding: 30px; text-align: center; color: rgba(255,255,255,0.5); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 TechShop</h1>
        <p class="subtitle">Find the best tech products</p>
        
        <div class="warning">
            🛡️ <strong>Protected by WAF:</strong> This search is protected against SQL injection attacks.
        </div>
        
        <div class="search-box">
            <form method="GET" action="/search">
                <input type="text" name="q" placeholder="Search products..." value="{{ query or '' }}">
                <button type="submit">🔍 Search</button>
            </form>
            
            {% if error %}
            <div class="error">
                ⚠️ {{ error }}
            </div>
            {% endif %}
        </div>
        
        {% if products is not none %}
        <div class="results">
            <h3>📦 Search Results for "{{ query }}"</h3>
            {% if products %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Product Name</th>
                        <th>Description</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    {% for product in products %}
                    <tr>
                        <td>{{ product[0] }}</td>
                        <td>{{ product[1] }}</td>
                        <td>{{ product[2] }}</td>
                        <td>${{ product[3] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="no-results">No products found.</div>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, query=None, products=None, error=None)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    products = None
    error = None
    
    if query:
        # WAF Check - Block spaces
        is_safe, waf_error = waf_check(query)
        if not is_safe:
            return render_template_string(TEMPLATE, query=query, products=None, error=waf_error)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # VULNERABLE: SQL Injection (space filter can be bypassed)
            sql = f"SELECT id, name, description, price FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
            cursor.execute(sql)
            products = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            error = f"Database error: {str(e)}"
    
    return render_template_string(TEMPLATE, query=query, products=products, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
