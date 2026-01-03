"""SQLi-026: PostgreSQL Boolean Blind via JSON Body"""
from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os
import json

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DATABASE', 'apidb')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔌 REST API - Product Search</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            opacity: 0.9;
            margin-bottom: 40px;
        }
        .hint {
            background: rgba(255,255,255,0.1);
            border-left: 4px solid #00d2ff;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
        }
        .search-box {
            background: rgba(255,255,255,0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            color: #333;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #667eea;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
            box-sizing: border-box;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102,126,234,0.4);
        }
        .result-box {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            display: none;
        }
        .result-box.show {
            display: block;
        }
        .result-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #667eea;
        }
        .json-display {
            background: #2d3748;
            color: #48bb78;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-break: break-all;
            margin-top: 10px;
        }
        .status-found {
            color: #48bb78;
            font-weight: bold;
        }
        .status-not-found {
            color: #f56565;
            font-weight: bold;
        }
        .api-info {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
        }
        .api-info code {
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        .examples {
            margin-top: 15px;
        }
        .example-item {
            background: rgba(0,0,0,0.2);
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .example-item:hover {
            background: rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 REST API Product Search</h1>
        <div class="subtitle">PostgreSQL Boolean Blind via JSON Body</div>
        
        <div class="hint">
            💡 <strong>Lab:</strong> Test Boolean Blind SQLi through JSON API endpoint
        </div>
        
        <div class="search-box">
            <h2 style="color: #667eea; margin-top: 0;">Search Product</h2>
            
            <form id="searchForm">
                <div class="form-group">
                    <label for="productId">Product ID:</label>
                    <input type="text" id="productId" name="productId" placeholder="Enter product ID (e.g., 1)" required>
                </div>
                <button type="submit" class="btn">🔍 Search Product</button>
            </form>
            
            <div id="resultBox" class="result-box">
                <div class="result-title">API Response:</div>
                <div id="statusText"></div>
                <div class="json-display" id="jsonResult"></div>
            </div>
        </div>
        
        <div class="api-info">
            <h3 style="margin-top: 0;">📡 API Endpoint Information</h3>
            <p><strong>Endpoint:</strong> <code>POST /api/product</code></p>
            <p><strong>Content-Type:</strong> <code>application/json</code></p>
            <p><strong>Request Body:</strong> <code>{"id": "value"}</code></p>
            
            <div class="examples">
                <strong>Try these examples:</strong>
                <div class="example-item" onclick="setProductId('1')">
                    ✅ Valid ID: <code>1</code> - Should find product
                </div>
                <div class="example-item" onclick="setProductId('999')">
                    ❌ Invalid ID: <code>999</code> - Not found
                </div>
                <div class="example-item" onclick="setProductId(\"1 AND '1'='1'\")">
                    🔓 SQLi Test: <code>1 AND '1'='1'</code> - Boolean TRUE
                </div>
                <div class="example-item" onclick="setProductId(\"1 AND '1'='2'\")">
                    🔓 SQLi Test: <code>1 AND '1'='2'</code> - Boolean FALSE
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function setProductId(value) {
            document.getElementById('productId').value = value;
        }
        
        document.getElementById('searchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const productId = document.getElementById('productId').value;
            const resultBox = document.getElementById('resultBox');
            const statusText = document.getElementById('statusText');
            const jsonResult = document.getElementById('jsonResult');
            
            try {
                const response = await fetch('/api/product', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id: productId })
                });
                
                const data = await response.json();
                
                // Show result box
                resultBox.classList.add('show');
                
                // Display status
                if (data.status === 'found') {
                    statusText.innerHTML = '<span class="status-found">✅ Product Found</span>';
                } else if (data.status === 'not_found') {
                    statusText.innerHTML = '<span class="status-not-found">❌ Product Not Found</span>';
                } else {
                    statusText.innerHTML = '<span class="status-not-found">⚠️ Error</span>';
                }
                
                // Display JSON
                jsonResult.textContent = JSON.stringify(data, null, 2);
                
            } catch (error) {
                resultBox.classList.add('show');
                statusText.innerHTML = '<span class="status-not-found">❌ Request Failed</span>';
                jsonResult.textContent = 'Error: ' + error.message;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HOME_TEMPLATE)

@app.route('/api/product', methods=['POST'])
def get_product():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"status": "error", "message": "Missing id"}), 400
    
    product_id = data['id']
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE: JSON value in SQL query
        sql = f"SELECT name, price FROM products WHERE id = {product_id}"
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return jsonify({"status": "found", "name": row[0], "price": float(row[1])})
        else:
            return jsonify({"status": "not_found"})
    except:
        return jsonify({"status": "not_found"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
