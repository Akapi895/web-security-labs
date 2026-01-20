"""SQLi-052: PostgreSQL Equals Filter Bypass"""
from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DATABASE', 'userdb')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def waf_check(user_input):
    """WAF that blocks = character"""
    if '=' in user_input:
        return False, "Equals sign (=) is blocked!"
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>👥 User Directory</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #4b6cb7, #182848); min-height: 100vh; color: #fff; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .box { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; }
        input { width: 100%; padding: 15px; border: none; border-radius: 8px; margin-bottom: 15px; }
        button { padding: 15px 30px; background: #fff; color: #333; border: none; border-radius: 8px; cursor: pointer; }
        .error { background: rgba(220,53,69,0.3); padding: 15px; border-radius: 8px; margin: 15px 0; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <div class="container">
        <h1>👥 User Directory</h1>
        <div class="box">
            <form method="GET" action="/user">
                <input type="text" name="id" placeholder="User ID..." value="{{ query or '' }}">
                <button type="submit">View User</button>
            </form>
            {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
            {% if results %}
            <table>
                <tr><th>ID</th><th>Username</th><th>Email</th></tr>
                {% for r in results %}
                <tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td></tr>
                {% endfor %}
            </table>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, query=None, results=None, error=None)

@app.route('/user')
def user():
    uid = request.args.get('id', '')
    results = None
    error = None
    
    if uid:
        is_safe, waf_error = waf_check(uid)
        if not is_safe:
            return render_template_string(TEMPLATE, query=uid, results=None, error=waf_error)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = f"SELECT id, username, email FROM users WHERE id = {uid}"
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, query=uid, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
