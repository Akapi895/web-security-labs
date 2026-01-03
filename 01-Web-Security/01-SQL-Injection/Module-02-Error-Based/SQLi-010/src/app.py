"""SQLi-010: MySQL UPDATEXML() Error-based SQLi"""
from flask import Flask, request, render_template_string
import mysql.connector
import os

app = Flask(__name__)
DB_CONFIG = {'host': os.environ.get('MYSQL_HOST', 'localhost'), 'user': os.environ.get('MYSQL_USER', 'app_user'), 'password': os.environ.get('MYSQL_PASSWORD', 'app_password'), 'database': os.environ.get('MYSQL_DATABASE', 'userdb')}

TEMPLATE = '''
<!DOCTYPE html><html><head><title>User Profile</title>
<style>body{font-family:Arial;background:#1a1a2e;color:#fff;padding:20px}.container{max-width:700px;margin:auto;background:#16213e;padding:30px;border-radius:10px}.profile{background:#0f3460;padding:20px;border-radius:8px;margin:20px 0}.error{background:#5c1a1a;padding:15px;border-radius:5px;font-family:monospace;white-space:pre-wrap}.hint{background:#3d3d00;padding:15px;border-radius:5px}a{color:#00d4ff}</style>
</head><body><div class="container"><h1>👤 User Profile</h1><div class="hint">💡 Lab: UPDATEXML() Error-based SQLi</div>
<p>Users: <a href="?uid=1">Alice</a> | <a href="?uid=2">Bob</a> | <a href="?uid=3">Admin</a></p>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
{% if user %}<div class="profile"><h2>{{ user[1] }}</h2><p>📧 {{ user[2] }}</p><p>📝 {{ user[3] }}</p></div>{% endif %}
</div></body></html>
'''

@app.route('/')
@app.route('/profile')
def profile():
    uid = request.args.get('uid', '1')
    user, error = None, None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = '{uid}'")
        user = cursor.fetchone()
        cursor.close(); conn.close()
    except mysql.connector.Error as err:
        error = str(err)
    return render_template_string(TEMPLATE, user=user, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
