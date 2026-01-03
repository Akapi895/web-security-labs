"""SQLi-033: MySQL Time-based via Cookie"""
from flask import Flask, request, make_response
import pymysql
import os
import secrets

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'rootpass'),
    'database': os.environ.get('MYSQL_DATABASE', 'sessiondb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

@app.route('/')
def index():
    session_id = request.cookies.get('session_id', '')
    
    # Generate session if empty (for first visit)
    generated = False
    if not session_id:
        session_id = 'sess_' + secrets.token_hex(8)
        generated = True
    
    user_id = None
    authenticated = False
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE: Cookie injection point
        sql = f"SELECT user_id FROM sessions WHERE session_id = '{session_id}'"
        print(f"[DEBUG] SQL: {sql}", flush=True)
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            authenticated = True
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", flush=True)
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Session Manager</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #fff;
                padding: 40px;
                min-height: 100vh;
            }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            h1 {{ text-align: center; }}
            .hint {{ background: rgba(255,193,7,0.2); padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .session-info {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; }}
            .status {{ color: {'#4CAF50' if authenticated else '#ff5252'}; }}
            code {{ background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Session Manager</h1>
            <div class="hint">💡 Lab: MySQL Time-based Blind via Cookie</div>
            <div class="session-info">
                <p><strong>Your Session ID:</strong> <code>{session_id}</code></p>
                <p><strong>Status:</strong> <span class="status">{'✅ Authenticated' if authenticated else '❌ Not Authenticated'}</span></p>
                {f'<p><strong>User ID:</strong> {user_id}</p>' if authenticated else ''}
            </div>
        </div>
    </body>
    </html>
    '''
    
    response = make_response(html)
    # Only set cookie if it was generated (not provided by user)
    if generated:
        response.set_cookie('session_id', session_id, max_age=3600)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
