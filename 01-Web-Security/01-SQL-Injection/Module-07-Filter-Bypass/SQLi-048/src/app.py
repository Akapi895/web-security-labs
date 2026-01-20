"""SQLi-048: MySQL Comment Filter Bypass"""
from flask import Flask, request, render_template_string
import pymysql
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'appuser'),
    'password': os.environ.get('MYSQL_PASSWORD', 'apppass123'),
    'database': os.environ.get('MYSQL_DATABASE', 'profiledb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def waf_check(user_input):
    """WAF that blocks -- comment syntax"""
    if '--' in user_input:
        return False, "SQL comment syntax '--' is blocked!"
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>👤 User Profiles</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: #fff; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .box { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; }
        input { width: 100%; padding: 15px; border: none; border-radius: 8px; margin-bottom: 15px; }
        button { padding: 15px 30px; background: #e94560; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        .error { background: rgba(220,53,69,0.3); padding: 15px; border-radius: 8px; margin: 15px 0; }
        .profile { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>👤 User Profiles</h1>
        <div class="box">
            <form method="GET" action="/profile">
                <input type="text" name="user" placeholder="Username..." value="{{ query or '' }}">
                <button type="submit">🔍 View Profile</button>
            </form>
            {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
            {% if results %}
                {% for r in results %}
                <div class="profile">
                    <h3>{{ r[1] }}</h3>
                    <p>{{ r[2] }}</p>
                    <small>ID: {{ r[0] }}</small>
                </div>
                {% endfor %}
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, query=None, results=None, error=None)

@app.route('/profile')
def profile():
    user = request.args.get('user', '')
    results = None
    error = None
    
    if user:
        is_safe, waf_error = waf_check(user)
        if not is_safe:
            return render_template_string(TEMPLATE, query=user, results=None, error=waf_error)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = f"SELECT id, username, bio FROM profiles WHERE username = '{user}'"
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, query=user, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
