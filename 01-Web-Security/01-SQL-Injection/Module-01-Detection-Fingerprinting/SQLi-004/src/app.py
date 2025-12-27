"""
SQLi-004: Comment-based SQL Injection Detection
Vulnerable Product API Application (Oracle)

WARNING: This application is intentionally vulnerable for educational purposes.
DO NOT use this code in production!
"""

from flask import Flask, request, jsonify, render_template_string
import oracledb
import os

app = Flask(__name__)

# Database configuration
ORACLE_HOST = os.environ.get('ORACLE_HOST', 'localhost')
ORACLE_PORT = os.environ.get('ORACLE_PORT', '1521')
ORACLE_SERVICE = os.environ.get('ORACLE_SERVICE', 'XEPDB1')
ORACLE_USER = os.environ.get('ORACLE_USER', 'app_user')
ORACLE_PASSWORD = os.environ.get('ORACLE_PASSWORD', 'app_password')

def get_db_connection():
    dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"
    return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn)

# HTML Template for home page
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Product API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Consolas', monospace; 
            background: #1e1e1e;
            min-height: 100vh;
            color: #d4d4d4;
        }
        .header {
            background: #c74634;
            padding: 25px;
            text-align: center;
            color: #fff;
        }
        .header h1 { font-size: 2em; }
        .header p { opacity: 0.9; margin-top: 5px; }
        .container { max-width: 900px; margin: 0 auto; padding: 30px 20px; }
        .api-doc {
            background: #252526;
            border-radius: 8px;
            padding: 25px;
            margin: 20px 0;
            border: 1px solid #3c3c3c;
        }
        .api-doc h2 { color: #c74634; margin-bottom: 15px; }
        .endpoint {
            background: #1e1e1e;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-family: monospace;
        }
        .method { 
            color: #6a9955; 
            font-weight: bold; 
        }
        .url { color: #ce9178; }
        .param { color: #9cdcfe; }
        .response-box {
            background: #1e1e1e;
            border: 1px solid #3c3c3c;
            border-radius: 5px;
            padding: 20px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-family: monospace;
            overflow-x: auto;
        }
        .error { color: #f14c4c; }
        .success { color: #6a9955; }
        .try-it {
            background: #252526;
            border-radius: 8px;
            padding: 25px;
            margin: 20px 0;
            border: 1px solid #3c3c3c;
        }
        .try-it h3 { color: #c74634; margin-bottom: 15px; }
        .try-it input {
            background: #1e1e1e;
            border: 1px solid #3c3c3c;
            padding: 12px;
            width: 200px;
            color: #d4d4d4;
            border-radius: 4px;
        }
        .try-it button {
            background: #c74634;
            color: #fff;
            border: none;
            padding: 12px 25px;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        .hint-box {
            background: #3c3c00;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            color: #ffc107;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔴 Oracle Enterprise API</h1>
        <p>Product Information Service</p>
    </div>
    
    <div class="container">
        <div class="hint-box">
            💡 <strong>Lab Hint:</strong> This API might be vulnerable to SQL Injection.
            Try using comment characters like <code>--</code> or <code>/* */</code>
            Note: Oracle does NOT support <code>#</code> comments!
        </div>
        
        <div class="api-doc">
            <h2>📡 API Endpoints</h2>
            <div class="endpoint">
                <span class="method">GET</span> 
                <span class="url">/api/product?id=<span class="param">{product_id}</span></span>
            </div>
            <p>Returns product information for the specified ID.</p>
        </div>
        
        <div class="try-it">
            <h3>🧪 Try It</h3>
            <form action="/api/product" method="GET">
                <label>Product ID: </label>
                <input type="text" name="id" value="1" placeholder="Enter product ID">
                <button type="submit">Send Request</button>
            </form>
        </div>
        
        {% if result %}
        <div class="response-box">
{{ result }}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, result=None)

@app.route('/api/product')
def get_product():
    product_id = request.args.get('id', '')
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # VULNERABLE: Direct string concatenation - SQL Injection possible!
        sql = f"SELECT * FROM products WHERE id = {product_id}"
        
        cursor.execute(sql)
        result = cursor.fetchall()
        
        if result:
            products = []
            for row in result:
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2] if row[2] else "",
                    "price": float(row[3]) if row[3] else 0,
                    "category": row[4],
                    "sku": row[5],
                    "stock": row[6]
                })
            
            cursor.close()
            conn.close()
            return jsonify({"status": "success", "data": products})
        else:
            return jsonify({"status": "success", "data": [], "message": "No product found"})
            
    except oracledb.Error as err:
        # VULNERABLE: Exposing detailed Oracle error messages
        error_msg = str(err)
        return jsonify({
            "status": "error",
            "error": error_msg,
            "database": "Oracle"
        }), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok", "database": "Oracle"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
