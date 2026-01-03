"""SQLi-024: Oracle Boolean Blind - SUBSTR Extraction"""
from flask import Flask, request, render_template_string
import oracledb
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('ORACLE_HOST', 'localhost'),
    'port': os.environ.get('ORACLE_PORT', '1521'),
    'service': os.environ.get('ORACLE_SERVICE', 'XEPDB1'),
    'user': os.environ.get('ORACLE_USER', 'app_user'),
    'password': os.environ.get('ORACLE_PASSWORD', 'app_password')
}

def get_connection():
    dsn = f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['service']}"
    return oracledb.connect(user=DB_CONFIG['user'], password=DB_CONFIG['password'], dsn=dsn)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔐 Session Validator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2.5em; margin-bottom: 30px; }
        .hint {
            background: rgba(255,255,255,0.2);
            border-left: 4px solid #fff;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .validator {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
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
            background: #fff;
            color: #f5576c;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .valid { background: rgba(40,167,69,0.4); }
        .invalid { background: rgba(220,53,69,0.4); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Session Validator</h1>
        <div class="hint">💡 Lab: Oracle Boolean Blind - SUBSTR + ROWNUM</div>
        <div class="validator">
            <form method="GET" action="/validate">
                <input type="text" name="token" placeholder="Enter session token..." value="{{ token or '' }}">
                <button type="submit">Validate Session</button>
            </form>
            {% if result is not none %}
            <div class="result {{ 'valid' if result else 'invalid' }}">
                {% if result %}✅ Session is valid{% else %}❌ Session is invalid{% endif %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, token=None, result=None)

@app.route('/validate')
def validate():
    token = request.args.get('token', '')
    result = None
    
    if token:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # VULNERABLE: Boolean Blind
            sql = f"SELECT 1 FROM sessions WHERE session_token = '{token}' AND is_valid = 1"
            cursor.execute(sql)
            row = cursor.fetchone()
            result = row is not None
            cursor.close()
            conn.close()
        except:
            result = False
    
    return render_template_string(TEMPLATE, token=token, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
