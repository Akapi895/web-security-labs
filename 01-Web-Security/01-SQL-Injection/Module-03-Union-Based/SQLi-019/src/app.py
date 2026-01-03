"""SQLi-019: MySQL Union-based - Single Column (CONCAT/CONCAT_WS)"""
from flask import Flask, request, render_template_string
import pymysql
import os

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'rootpass'),
    'database': os.environ.get('MYSQL_DATABASE', 'ecommerce'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🛒 E-Shop Search</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { 
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .search-box {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
        .search-form {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px 20px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            background: rgba(255,255,255,0.9);
            color: #333;
        }
        button {
            padding: 15px 30px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.05); }
        .hint {
            background: linear-gradient(90deg, rgba(255,193,7,0.2), rgba(255,152,0,0.2));
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .results {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
        }
        .results h2 { margin-bottom: 15px; color: #00d2ff; }
        .result-item {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            transition: background 0.2s;
        }
        .result-item:hover { background: rgba(255,255,255,0.15); }
        .error {
            background: rgba(220,53,69,0.2);
            border-left: 4px solid #dc3545;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            font-family: monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .no-results {
            color: #888;
            text-align: center;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 E-Shop Search</h1>
        <p class="subtitle">Find the best products at amazing prices</p>
        
        <div class="hint">
            💡 <strong>Lab:</strong> MySQL Union-based SQLi - Single Column (CONCAT/CONCAT_WS)
        </div>
        
        <div class="search-box">
            <form class="search-form" method="GET" action="/search">
                <input type="text" name="q" placeholder="Search products..." value="{{ query or '' }}">
                <button type="submit">🔍 Search</button>
            </form>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% elif results %}
        <div class="results">
            <h2>📦 Search Results ({{ results|length }} found)</h2>
            {% for item in results %}
            <div class="result-item">{{ item }}</div>
            {% endfor %}
        </div>
        {% elif query %}
        <div class="results">
            <div class="no-results">No products found for "{{ query }}"</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, query=None, results=None, error=None)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    error = None
    
    if query:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # VULNERABLE: Direct string concatenation
            # Kết quả chỉ hiển thị tên sản phẩm (1 column) 
            sql = f"SELECT name FROM products WHERE name LIKE '%{query}%'"
            cursor.execute(sql)
            rows = cursor.fetchall()
            results = [row[0] for row in rows]
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, query=query, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
